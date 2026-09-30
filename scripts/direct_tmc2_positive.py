from pathlib import Path
import numpy as np
import cv2
import json
import time

from parallex.io.pds4_image import open_pds4_image
from parallex.matching.sift import SIFTMatcher
from parallex.matching.rift import RIFTMatcher
from parallex.matching.hopc import HOPCMatcher
from parallex.matching.cfog import CFOGMatcher


ROOT = Path(r"C:\Users\graj6\Downloads\parallex\data\real_pairs")

A_DIR = ROOT / "ch2_tmc_nca_20221209T2305274611_d_img_d32"
B_DIR = ROOT / "ch2_tmc_ncn_20221209T2305274611_d_img_d32"

A_GEO = next(A_DIR.rglob("*_g_grd_*.csv"))
B_GEO = next(B_DIR.rglob("*_g_grd_*.csv"))

OUT = Path("results/TMC2_NCA_NCN_DIRECT_GEOMETRY")
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 75)
print("PARALLAX — REAL TMC2 NCA ↔ NCN DIRECT-GEOMETRY BENCHMARK")
print("=" * 75)


def load_geo(path):

    d = np.genfromtxt(
        path,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8",
    )

    return {
        "lat": np.asarray(
            d["Latitude"],
            dtype=np.float64,
        ),
        "lon": np.asarray(
            d["Longitude"],
            dtype=np.float64,
        ),
        "pixel": np.asarray(
            d["Pixel"],
            dtype=np.float64,
        ),
        "scan": np.asarray(
            d["Scan"],
            dtype=np.float64,
        ),
    }


A = load_geo(A_GEO)
B = load_geo(B_GEO)

print("A geometry:", len(A["lat"]))
print("B geometry:", len(B["lat"]))

print(
    "A extent:",
    A["lat"].min(),
    A["lat"].max(),
    A["lon"].min(),
    A["lon"].max(),
)

print(
    "B extent:",
    B["lat"].min(),
    B["lat"].max(),
    B["lon"].min(),
    B["lon"].max(),
)


def valid(g):

    return (
        np.isfinite(g["lat"])
        & np.isfinite(g["lon"])
    )


ma = valid(A)
mb = valid(B)

for k in A:
    A[k] = A[k][ma]

for k in B:
    B[k] = B[k][mb]


def geo_dist2(
    lat0,
    lon0,
    lat,
    lon,
):

    dlat = lat - lat0

    dlon = (
        (lon - lon0 + 180)
        % 360
    ) - 180

    scale = np.cos(
        np.deg2rad(lat0)
    )

    return (
        dlat * dlat
        + (dlon * scale) ** 2
    )


# ------------------------------------------------------------
# Find real geographic pairs
# ------------------------------------------------------------

pairs = []

# Sample A geometry points.
step = max(
    1,
    len(A["lat"]) // 1500,
)

for i in range(
    0,
    len(A["lat"]),
    step,
):

    lat0 = A["lat"][i]
    lon0 = A["lon"][i]

    d2 = geo_dist2(
        lat0,
        lon0,
        B["lat"],
        B["lon"],
    )

    j = int(
        np.argmin(d2)
    )

    pairs.append(
        (
            float(np.sqrt(d2[j])),
            i,
            j,
        )
    )

pairs.sort(
    key=lambda x: x[0]
)

print()
print(
    "Sampled A points:",
    len(range(
        0,
        len(A["lat"]),
        step,
    )),
)

print(
    "Best geographic errors:"
)

for p in pairs[:10]:

    print(
        f"{p[0]:.6f} deg",
        "A=(",
        f"{A['scan'][p[1]]:.0f},",
        f"{A['pixel'][p[1]]:.0f})",
        "B=(",
        f"{B['scan'][p[2]]:.0f},",
        f"{B['pixel'][p[2]]:.0f})",
    )


# ------------------------------------------------------------
# Spatially diverse anchors
# ------------------------------------------------------------

selected = []

for p in pairs:

    err, ia, ib = p

    if err > 0.02:
        break

    lat = A["lat"][ia]
    lon = A["lon"][ia]

    duplicate = False

    for old in selected:

        oldlat = A["lat"][old[1]]
        oldlon = A["lon"][old[1]]

        if np.sqrt(
            geo_dist2(
                lat,
                lon,
                oldlat,
                oldlon,
            )
        ) < 0.05:

            duplicate = True
            break

    if duplicate:
        continue

    selected.append(p)

    if len(selected) >= 6:
        break


print()
print(
    "SELECTED REAL GEOGRAPHIC ANCHORS:",
    len(selected),
)


# ------------------------------------------------------------
# Open images
# ------------------------------------------------------------

ra = open_pds4_image(A_DIR)
rb = open_pds4_image(B_DIR)

print("A image:", ra.shape)
print("B image:", rb.shape)


def norm(x):

    x = np.asarray(
        x,
        dtype=np.float32,
    )

    x = np.nan_to_num(
        x,
        nan=0,
        posinf=0,
        neginf=0,
    )

    lo, hi = np.percentile(
        x,
        [2, 98],
    )

    if hi <= lo:
        return np.zeros(
            x.shape,
            dtype=np.uint8,
        )

    return (
        np.clip(
            (x - lo) / (hi - lo),
            0,
            1,
        ) * 255
    ).astype(
        np.uint8
    )


# TMC2 resolution is ~5 m/px.
# 401x401 is ~2 km context.
HALF = 200

results = []


# ------------------------------------------------------------
# Matching
# ------------------------------------------------------------

matchers = [
    ("sift", SIFTMatcher()),
    ("rift", RIFTMatcher()),
    ("hopc", HOPCMatcher()),
    ("cfog", CFOGMatcher()),
]


for n, (
    geo_err,
    ia,
    ib,
) in enumerate(
    selected,
    1,
):

    sa = int(
        round(A["scan"][ia])
    )

    pa = int(
        round(A["pixel"][ia])
    )

    sb = int(
        round(B["scan"][ib])
    )

    pb = int(
        round(B["pixel"][ib])
    )

    print()
    print("-" * 75)

    print(
        f"A{n:02d}",
        "geo_error=",
        f"{geo_err:.6f}",
    )

    print(
        "A:",
        sa,
        pa,
        "geo=",
        A["lat"][ia],
        A["lon"][ia],
    )

    print(
        "B:",
        sb,
        pb,
        "geo=",
        B["lat"][ib],
        B["lon"][ib],
    )

    try:

        img_a = ra.read_window(
            max(
                0,
                sa - HALF,
            ),
            max(
                0,
                pa - HALF,
            ),
            2 * HALF + 1,
            2 * HALF + 1,
        )

        img_b = rb.read_window(
            max(
                0,
                sb - HALF,
            ),
            max(
                0,
                pb - HALF,
            ),
            2 * HALF + 1,
            2 * HALF + 1,
        )

        img_a = norm(img_a)
        img_b = norm(img_b)

        # Save visual evidence.
        cv2.imwrite(
            str(
                OUT
                / f"A{n:02d}_A.png"
            ),
            img_a,
        )

        cv2.imwrite(
            str(
                OUT
                / f"A{n:02d}_B.png"
            ),
            img_b,
        )

        # Downsample for fast classical matching.
        img_a_small = cv2.resize(
            img_a,
            (512, 512),
            interpolation=cv2.INTER_AREA,
        )

        img_b_small = cv2.resize(
            img_b,
            (512, 512),
            interpolation=cv2.INTER_AREA,
        )

        anchor_result = {
            "id": f"A{n:02d}",
            "geo_error": geo_err,
            "a_scan": sa,
            "a_pixel": pa,
            "b_scan": sb,
            "b_pixel": pb,
            "matchers": {},
        }

        for name, matcher in matchers:

            print(
                "  ",
                name,
                "...",
                end=" ",
                flush=True,
            )

            t0 = time.perf_counter()

            try:

                r = matcher.match(
                    img_a_small,
                    img_b_small,
                )

                elapsed = (
                    time.perf_counter()
                    - t0
                )

                # Support both object and dict results.
                if hasattr(
                    r,
                    "points_a",
                ):

                    pa_out = r.points_a
                    pb_out = r.points_b

                elif isinstance(
                    r,
                    dict,
                ):

                    pa_out = r.get(
                        "points_a",
                        [],
                    )

                    pb_out = r.get(
                        "points_b",
                        [],
                    )

                else:

                    pa_out = []
                    pb_out = []

                count = min(
                    len(pa_out),
                    len(pb_out),
                )

                print(
                    count,
                    "matches",
                    f"({elapsed:.2f}s)",
                )

                anchor_result[
                    "matchers"
                ][name] = {
                    "matches": int(count),
                    "runtime_sec":
                        elapsed,
                }

            except Exception as e:

                elapsed = (
                    time.perf_counter()
                    - t0
                )

                print(
                    "ERROR",
                    type(e).__name__,
                )

                anchor_result[
                    "matchers"
                ][name] = {
                    "matches": 0,
                    "runtime_sec":
                        elapsed,
                    "error":
                        (
                            f"{type(e).__name__}: "
                            f"{e}"
                        ),
                }

        results.append(
            anchor_result
        )

    except Exception as e:

        print(
            "ROI ERROR:",
            type(e).__name__,
            str(e),
        )


with open(
    OUT / "benchmark.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        results,
        f,
        indent=2,
    )


print()
print("=" * 75)
print("FINAL DIRECT-GEOMETRY RESULTS")
print("=" * 75)

for r in results:

    print()
    print(
        r["id"],
        "geo_error=",
        f"{r['geo_error']:.6f}",
    )

    for name, x in r[
        "matchers"
    ].items():

        print(
            " ",
            name,
            "matches=",
            x["matches"],
        )

print()
print(
    "OUTPUT:",
    OUT.resolve(),
)
