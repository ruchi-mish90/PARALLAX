from pathlib import Path
import json
import time
import cv2
import numpy as np

from parallex.io.pds4_image import open_pds4_image
from parallex.matching.sift import SIFTMatcher
from parallex.matching.rift import RIFTMatcher
from parallex.matching.hopc import HOPCMatcher
from parallex.matching.cfog import CFOGMatcher
from parallex.matching.loftr import LoFTRMatcher


ROOT = Path(r"C:\Users\graj6\Downloads\P0001")
OUT = Path("results/P0001_REAL_A02")
OUT.mkdir(parents=True, exist_ok=True)

TMC2_IMG = next(ROOT.rglob("*tmc_ncn*_d_img_n18.img"))
IIRS_QUB = next(ROOT.rglob("*iir_nci*_d_img_n18.qub"))

TMC2_SCAN = 60200
TMC2_PIXEL = 900

IIRS_SCAN = 5050
IIRS_PIXEL = 150

IIRS_HALF = 15
TMC2_HALF_ROW = 125
TMC2_HALF_COL = 145


def robust_u8(x):
    x = np.asarray(x, dtype=np.float32)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)

    lo, hi = np.percentile(x, [2, 98])

    if hi <= lo:
        return np.zeros_like(x, dtype=np.uint8)

    return (
        np.clip((x - lo) / (hi - lo), 0, 1) * 255
    ).astype(np.uint8)


def read_window(reader, row, col, height, width):
    return reader.read_window(
        row,
        col,
        height,
        width,
    )


def build_representations(cube):

    cube = np.asarray(cube, dtype=np.float32)

    cube = np.nan_to_num(
        cube,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    bands = cube.shape[0]

    spectral_mean = np.mean(cube, axis=0)

    spectral_std = np.std(cube, axis=0)

    spectral_range = (
        np.percentile(cube, 95, axis=0)
        - np.percentile(cube, 5, axis=0)
    )

    X = cube.reshape(bands, -1).T
    X -= X.mean(axis=0, keepdims=True)

    try:
        _, _, vt = np.linalg.svd(
            X,
            full_matrices=False,
        )

        pc1 = (X @ vt[0]).reshape(
            cube.shape[1],
            cube.shape[2],
        )

    except Exception:
        pc1 = spectral_mean.copy()

    spectral_gradient = np.mean(
        np.abs(np.diff(cube, axis=0)),
        axis=0,
    )

    return {
        "spectral_mean": spectral_mean,
        "spectral_std": spectral_std,
        "spectral_range": spectral_range,
        "pc1": pc1,
        "spectral_gradient": spectral_gradient,
    }


print("=" * 70)
print("PARALLAX REAL P0001 — TMC2 ↔ IIRS A02")
print("=" * 70)

print("TMC2:", TMC2_IMG)
print("IIRS:", IIRS_QUB)

# ------------------------------------------------------------
# Load using actual PDS4-aware loader
# ------------------------------------------------------------

tmc2 = open_pds4_image(TMC2_IMG.parents[3])
iirs = open_pds4_image(IIRS_QUB.parents[3])

print("TMC2 reader:", type(tmc2).__name__)
print("TMC2 shape:", tmc2.shape)
print("IIRS reader:", type(iirs).__name__)
print("IIRS shape:", iirs.shape)

# ------------------------------------------------------------
# TMC2 A02
# ------------------------------------------------------------

tmc2_full = read_window(
    tmc2, TMC2_SCAN - TMC2_HALF_ROW, TMC2_PIXEL - TMC2_HALF_COL, 2 * TMC2_HALF_ROW + 1, 2 * TMC2_HALF_COL + 1,
)

print("TMC2 raw ROI:", tmc2_full.shape)

# ------------------------------------------------------------
# IIRS A02
# ------------------------------------------------------------

iirs_row = IIRS_SCAN - IIRS_HALF
iirs_col = IIRS_PIXEL - IIRS_HALF
iirs_size = 2 * IIRS_HALF + 1

cube = np.stack(
    [
        iirs.read_band_window(
            band,
            iirs_row,
            iirs_col,
            iirs_size,
            iirs_size,
        )
        for band in range(iirs.shape[0])
    ],
    axis=0,
)

print("IIRS cube:", cube.shape)

# ------------------------------------------------------------
# IIRS representations
# ------------------------------------------------------------

representations = build_representations(cube)

target_size = (128, 128)

# ------------------------------------------------------------
# Downsample TMC2 to IIRS spatial scale
# ------------------------------------------------------------

tmc2_scaled = cv2.resize(
    tmc2_full.astype(np.float32),
    target_size,
    interpolation=cv2.INTER_AREA,
)

tmc2_u8 = robust_u8(tmc2_scaled)

cv2.imwrite(
    str(OUT / "tmc2_a02_scaled.png"),
    tmc2_u8,
)

for name, image in representations.items():

    np.save(
        OUT / f"iirs_a02_{name}.npy",
        image.astype(np.float32),
    )

    cv2.imwrite(
        str(OUT / f"iirs_a02_{name}.png"),
        robust_u8(image),
    )

# ------------------------------------------------------------
# Matcher test
# ------------------------------------------------------------

matchers = {
    "sift": SIFTMatcher,
    "rift": RIFTMatcher,
    "hopc": HOPCMatcher,
    "cfog": CFOGMatcher,
    "loftr": LoFTRMatcher,
}

results = []

for rep_name in [
    "spectral_mean",
    "pc1",
    "spectral_gradient",
]:

    moving = robust_u8(
        representations[rep_name]
    )

    print()
    print("=" * 70)
    print("REPRESENTATION:", rep_name)
    print("TMC2:", tmc2_u8.shape)
    print("IIRS:", moving.shape)
    print("=" * 70)

    for matcher_name, matcher_cls in matchers.items():

        print()
        print("MATCHER:", matcher_name)

        start = time.perf_counter()

        try:

            matcher = matcher_cls()

            result = matcher.match(
                tmc2_u8,
                moving,
            )

            elapsed = time.perf_counter() - start

            points_a = getattr(
                result,
                "points_a",
                None,
            )

            confidence = getattr(
                result,
                "confidence",
                None,
            )

            n = (
                0
                if points_a is None
                else len(points_a)
            )

            conf_mean = None

            if confidence is not None:

                confidence = np.asarray(
                    confidence
                )

                if confidence.size:
                    conf_mean = float(
                        np.nanmean(confidence)
                    )

            row = {
                "representation": rep_name,
                "matcher": matcher_name,
                "matches": int(n),
                "mean_confidence": conf_mean,
                "runtime_seconds": float(
                    elapsed
                ),
            }

            results.append(row)

            print("matches:", n)
            print("mean confidence:", conf_mean)
            print(
                "runtime:",
                round(elapsed, 3),
                "s",
            )

        except Exception as exc:

            elapsed = (
                time.perf_counter() - start
            )

            row = {
                "representation": rep_name,
                "matcher": matcher_name,
                "matches": 0,
                "mean_confidence": None,
                "runtime_seconds": float(
                    elapsed
                ),
                "error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            }

            results.append(row)

            print(
                "ERROR:",
                type(exc).__name__,
                str(exc),
            )

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

with open(
    OUT / "matching_results.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        results,
        f,
        indent=2,
    )

print()
print("=" * 70)
print("REAL A02 MATCHING TEST COMPLETE")
print("OUTPUT:", OUT.resolve())
print("=" * 70)

for row in results:
    print(row)







