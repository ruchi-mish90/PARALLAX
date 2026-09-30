from pathlib import Path
import numpy as np
import cv2

TMC2_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18")
IIRS_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18")

OUT = Path("results/P0001_A01_MULTISCALE")
OUT.mkdir(parents=True, exist_ok=True)

# A01 geographic mapping
TMC2_LINE = 119200
TMC2_SAMPLE = 2300
IIRS_LINE = 1450
IIRS_SAMPLE = 50

# Geometry-derived spatial sampling ratio
X_SCALE = 9.6805
Y_SCALE = 8.1776

# IIRS template
TEMPLATE_SIZE = 61

# TMC2 search region
SEARCH_TMC2_SIZE = 1801


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
    x = cv2.GaussianBlur(
        x.astype(np.float32),
        (0, 0),
        1.2
    )

    gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3)

    return cv2.magnitude(gx, gy).astype(np.float32)


def load_products():

    tmc2_path = next(TMC2_ROOT.rglob("*.img"))
    iirs_path = next(IIRS_ROOT.rglob("*.qub"))

    print("TMC2:", tmc2_path)
    print("IIRS:", iirs_path)

    tmc2 = np.memmap(
        tmc2_path,
        dtype="<u2",
        mode="r",
        shape=(153244, 4000),
        order="C"
    )

    iirs = np.memmap(
        iirs_path,
        dtype="<f4",
        mode="r",
        shape=(256, 10075, 250),
        order="C"
    )

    return tmc2, iirs


def extract_iirs(cube):

    h = TEMPLATE_SIZE // 2

    local = np.asarray(
        cube[
            :,
            IIRS_LINE - h:IIRS_LINE + h + 1,
            IIRS_SAMPLE - h:IIRS_SAMPLE + h + 1
        ],
        dtype=np.float32
    )

    reps = {}

    for band in [128, 160, 192, 224]:
        reps[f"band_{band}"] = local[band - 1]

    reps["spectral_gradient"] = np.nanmean(
        np.abs(np.diff(local, axis=0)),
        axis=0
    )

    return {
        k: norm01(v)
        for k, v in reps.items()
    }


def extract_tmc2(tmc2):

    h = SEARCH_TMC2_SIZE // 2

    patch = np.asarray(
        tmc2[
            TMC2_LINE - h:TMC2_LINE + h + 1,
            TMC2_SAMPLE - h:TMC2_SAMPLE + h + 1
        ],
        dtype=np.float32
    )

    patch = norm01(patch)

    # Physical-scale smoothing.
    patch = cv2.GaussianBlur(
        patch,
        (0, 0),
        sigmaX=X_SCALE / 2,
        sigmaY=Y_SCALE / 2
    )

    # Reduce to approximately IIRS spatial sampling.
    new_w = int(round(
        patch.shape[1] / X_SCALE
    ))

    new_h = int(round(
        patch.shape[0] / Y_SCALE
    ))

    reduced = cv2.resize(
        patch,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    return norm01(reduced)


def clahe(x):

    u8 = (
        norm01(x) * 255
    ).astype(np.uint8)

    c = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return c.apply(u8).astype(np.float32) / 255.0


def match(template, search):

    template = np.ascontiguousarray(
        clahe(template),
        dtype=np.float32
    )

    search = np.ascontiguousarray(
        clahe(search),
        dtype=np.float32
    )

    result_i = cv2.matchTemplate(
        search,
        template,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_i, _, loc_i = cv2.minMaxLoc(result_i)

    template_g = np.ascontiguousarray(
        norm01(gradient(template)),
        dtype=np.float32
    )

    search_g = np.ascontiguousarray(
        norm01(gradient(search)),
        dtype=np.float32
    )

    result_g = cv2.matchTemplate(
        search_g,
        template_g,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_g, _, loc_g = cv2.minMaxLoc(result_g)

    combined = (
        0.35 * result_i +
        0.65 * result_g
    )

    _, max_c, _, loc_c = cv2.minMaxLoc(combined)

    return {
        "intensity": float(max_i),
        "gradient": float(max_g),
        "combined": float(max_c),
        "loc_intensity": loc_i,
        "loc_gradient": loc_g,
        "loc_combined": loc_c
    }


def main():

    print("=" * 70)
    print("PARALLAX A01 MULTISCALE CORRESPONDENCE")
    print("=" * 70)

    print("A01:")
    print("  IIRS  =", IIRS_LINE, IIRS_SAMPLE)
    print("  TMC2  =", TMC2_LINE, TMC2_SAMPLE)
    print()

    tmc2, iirs = load_products()

    iirs_reps = extract_iirs(iirs)
    tmc2_search = extract_tmc2(tmc2)

    print("TMC2 reduced search:", tmc2_search.shape)

    rows = []

    for name, template in iirs_reps.items():

        result = match(
            template,
            tmc2_search
        )

        rows.append(
            (
                name,
                result["intensity"],
                result["gradient"],
                result["combined"],
                result["loc_combined"]
            )
        )

        print()
        print(name)
        print(
            "  intensity NCC :",
            f"{result['intensity']:.5f}"
        )
        print(
            "  gradient NCC  :",
            f"{result['gradient']:.5f}"
        )
        print(
            "  combined      :",
            f"{result['combined']:.5f}"
        )
        print(
            "  best location :",
            result["loc_combined"]
        )

    rows.sort(
        key=lambda x: x[3],
        reverse=True
    )

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    for row in rows:
        print(
            f"{row[0]:20s}"
            f" combined={row[3]:.5f}"
            f" gradient={row[2]:.5f}"
            f" intensity={row[1]:.5f}"
            f" location={row[4]}"
        )

    best = rows[0]

    with open(
        OUT / "results.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "PARALLAX A01 MULTISCALE RESULTS\n"
        )
        f.write(
            "================================\n"
        )

        for row in rows:
            f.write(
                f"{row[0]} "
                f"combined={row[3]:.6f} "
                f"gradient={row[2]:.6f} "
                f"intensity={row[1]:.6f} "
                f"location={row[4]}\n"
            )

    print()
    print("BEST:", best[0])
    print("BEST COMBINED:", f"{best[3]:.5f}")
    print("Saved:", OUT)


if __name__ == "__main__":
    main()




