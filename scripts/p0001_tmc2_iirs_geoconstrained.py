from pathlib import Path
import numpy as np
import cv2

TMC2_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18")
IIRS_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18")

OUT = Path("results/P0001_TMC2_IIRS_GEOCONSTRAINED")
OUT.mkdir(parents=True, exist_ok=True)

X_SCALE = 9.6805
Y_SCALE = 8.1776

# (IIRS line, sample, TMC2 line, sample)
CANDIDATES = {
    "A01": (1450, 50, 119200, 2300),
    "A02": (3700, 100, 82300, 1200),
    "A03": (1800, 0, 113500, 1200),
    "A04": (5250, 200, 56900, 1600),
    "A05": (750, 50, 130700, 2900),
}

BANDS = [128, 160, 192, 224]

IIRS_SIZE = 101
TMC2_SIZE = 1001

# Search only around the geometry-predicted position.
SEARCH_RADIUS = 35


def norm01(x):
    x = np.asarray(x, dtype=np.float32)
    good = np.isfinite(x)

    if not good.any():
        return np.zeros_like(x)

    lo, hi = np.percentile(x[good], [2, 98])

    if hi <= lo:
        return np.zeros_like(x)

    return np.clip((x - lo) / (hi - lo), 0, 1)


def gradient(x):
    x = cv2.GaussianBlur(x.astype(np.float32), (0, 0), 1.2)
    gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, 3)
    gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, 3)
    return cv2.magnitude(gx, gy).astype(np.float32)


def clahe(x):
    u8 = (norm01(x) * 255).astype(np.uint8)
    c = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return c.apply(u8).astype(np.float32) / 255.0


def load():
    tmc2_path = next(TMC2_ROOT.rglob("*.img"))
    iirs_path = next(IIRS_ROOT.rglob("*.qub"))

    tmc2 = np.memmap(
        tmc2_path, dtype="<u2", mode="r",
        shape=(153244, 4000), order="C"
    )

    iirs = np.memmap(
        iirs_path, dtype="<f4", mode="r",
        shape=(256, 10075, 250), order="C"
    )

    return tmc2, iirs


def get_iirs(cube, line, sample, band):
    h = IIRS_SIZE // 2

    x = np.asarray(
        cube[
            band - 1,
            line - h:line + h + 1,
            sample - h:sample + h + 1
        ],
        dtype=np.float32
    )

    return norm01(x)


def get_tmc2(tmc2, line, sample):
    h = TMC2_SIZE // 2

    x = np.asarray(
        tmc2[
            line - h:line + h + 1,
            sample - h:sample + h + 1
        ],
        dtype=np.float32
    )

    x = norm01(x)

    x = cv2.GaussianBlur(
        x, (0, 0),
        sigmaX=X_SCALE / 2,
        sigmaY=Y_SCALE / 2
    )

    # Convert to IIRS spatial scale.
    w = int(round(TMC2_SIZE / X_SCALE))
    h2 = int(round(TMC2_SIZE / Y_SCALE))

    x = cv2.resize(
        x, (w, h2),
        interpolation=cv2.INTER_AREA
    )

    return norm01(x)


def search(template, search):

    template = clahe(template)
    search = clahe(search)

    tg = norm01(gradient(template))
    sg = norm01(gradient(search))

    tg = np.ascontiguousarray(tg, dtype=np.float32)
    sg = np.ascontiguousarray(sg, dtype=np.float32)

    # Intensity and gradient NCC.
    ri = cv2.matchTemplate(
        search, template,
        cv2.TM_CCOEFF_NORMED
    )

    rg = cv2.matchTemplate(
        sg, tg,
        cv2.TM_CCOEFF_NORMED
    )

    combined = (
        0.35 * ri +
        0.65 * rg
    )

    _, ci, _, li = cv2.minMaxLoc(ri)
    _, cg, _, lg = cv2.minMaxLoc(rg)
    _, cc, _, lc = cv2.minMaxLoc(combined)

    return {
        "intensity": float(ci),
        "gradient": float(cg),
        "combined": float(cc),
        "location": lc
    }


def main():

    print("=" * 70)
    print("PARALLAX GEOMETRY-CONSTRAINED TMC2 <-> IIRS")
    print("=" * 70)

    tmc2, iirs = load()

    rows = []

    for name, (iline, isample, tline, tsample) in CANDIDATES.items():

        print()
        print("=" * 60)
        print(name)
        print(
            f"IIRS=({iline},{isample}) "
            f"TMC2=({tline},{tsample})"
        )

        # Large TMC2 context, reduced to IIRS scale.
        tmc2_img = get_tmc2(
            tmc2,
            tline,
            tsample
        )

        # Put the IIRS template at the same grid scale.
        # The geometry-derived neighborhood is centered here.
        for band in BANDS:

            template = get_iirs(
                iirs,
                iline,
                isample,
                band
            )

            # Search around the central predicted location.
            h, w = template.shape

            sh, sw = tmc2_img.shape

            if sh <= h or sw <= w:
                continue

            result = search(
                template,
                tmc2_img
            )

            rows.append(
                (
                    name,
                    band,
                    result["combined"],
                    result["gradient"],
                    result["intensity"],
                    result["location"]
                )
            )

            print(
                f"band_{band}: "
                f"combined={result['combined']:.5f} "
                f"gradient={result['gradient']:.5f} "
                f"intensity={result['intensity']:.5f} "
                f"loc={result['location']}"
            )

    rows.sort(key=lambda x: x[2], reverse=True)

    print()
    print("=" * 70)
    print("GLOBAL RESULTS")
    print("=" * 70)

    for row in rows:
        print(
            f"{row[0]:4s} "
            f"band_{row[1]:3d} "
            f"combined={row[2]:.5f} "
            f"gradient={row[3]:.5f} "
            f"intensity={row[4]:.5f} "
            f"loc={row[5]}"
        )

    with open(
        OUT / "results.csv",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "candidate,band,combined,gradient,"
            "intensity,location\n"
        )

        for r in rows:
            f.write(
                f"{r[0]},{r[1]},"
                f"{r[2]:.6f},{r[3]:.6f},"
                f"{r[4]:.6f},\"{r[5]}\"\n"
            )

    print()
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
