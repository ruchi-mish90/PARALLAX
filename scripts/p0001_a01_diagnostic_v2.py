from pathlib import Path
import numpy as np
import cv2

TMC2_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18")
IIRS_ROOT = Path(r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18")

OUT = Path("results/P0001_A01_DIAGNOSTIC_V2")
OUT.mkdir(parents=True, exist_ok=True)

# Geometry-derived sampling ratios
X_SCALE = 0.460565000000031 / 0.04757649999999103
Y_SCALE = 0.13453065000000208 / 0.01645109999999761

TMC2_LINE = 119200
TMC2_SAMPLE = 2300

IIRS_LINE = 1450
IIRS_SAMPLE = 50

TMC2_SIZE = 1001
IIRS_SIZE = 101


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
    x = cv2.GaussianBlur(x.astype(np.float32), (0, 0), 1.5)
    gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3)
    return np.sqrt(gx * gx + gy * gy)


def correlation(a, b):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()

    good = np.isfinite(a) & np.isfinite(b)
    a = a[good]
    b = b[good]

    if len(a) < 10:
        return 0.0

    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0

    return float(np.corrcoef(a, b)[0, 1])


def find_file(root, extension):
    files = list(root.rglob(extension))
    if not files:
        raise FileNotFoundError(f"No {extension} file under {root}")
    return files[0]


def load_tmc2():
    p = find_file(TMC2_ROOT, "*.img")

    print("TMC2:", p)

    expected = 153244 * 4000

    arr = np.memmap(
        p,
        dtype="<u2",
        mode="r",
        shape=(153244, 4000),
        order="C"
    )

    print("TMC2 shape:", arr.shape)
    print("TMC2 dtype:", arr.dtype)
    print("TMC2 expected pixels:", expected)

    return arr


def load_iirs():
    p = find_file(IIRS_ROOT, "*.qub")

    print("IIRS:", p)

    arr = np.memmap(
        p,
        dtype="<f4",
        mode="r",
        shape=(256, 10075, 250),
        order="C"
    )

    print("IIRS shape:", arr.shape)
    print("IIRS dtype:", arr.dtype)

    return arr


def extract_tmc2(arr):
    half = TMC2_SIZE // 2

    y0 = TMC2_LINE - half
    y1 = y0 + TMC2_SIZE

    x0 = TMC2_SAMPLE - half
    x1 = x0 + TMC2_SIZE

    patch = np.asarray(arr[y0:y1, x0:x1], dtype=np.float32)

    print("TMC2 patch:", patch.shape)

    if patch.shape != (TMC2_SIZE, TMC2_SIZE):
        raise RuntimeError(f"Invalid TMC2 patch: {patch.shape}")

    return norm01(patch)


def extract_iirs(arr):
    half = IIRS_SIZE // 2

    y0 = IIRS_LINE - half
    y1 = y0 + IIRS_SIZE

    x0 = IIRS_SAMPLE - half
    x1 = x0 + IIRS_SIZE

    cube = np.asarray(
        arr[:, y0:y1, x0:x1],
        dtype=np.float32
    )

    print("IIRS local cube:", cube.shape)

    if cube.shape != (256, IIRS_SIZE, IIRS_SIZE):
        raise RuntimeError(f"Invalid IIRS cube: {cube.shape}")

    reps = {}

    reps["spectral_mean"] = np.nanmean(cube, axis=0)
    reps["spectral_std"] = np.nanstd(cube, axis=0)

    reps["spectral_range"] = (
        np.nanmax(cube, axis=0)
        - np.nanmin(cube, axis=0)
    )

    reps["spectral_gradient"] = np.nanmean(
        np.abs(np.diff(cube, axis=0)),
        axis=0
    )

    for band in [32, 64, 96, 128, 160, 192, 224]:
        reps[f"band_{band}"] = cube[band - 1]

    # PCA1
    X = cube.reshape(256, -1).T
    X = np.nan_to_num(X)

    X -= X.mean(axis=0, keepdims=True)

    try:
        _, _, vt = np.linalg.svd(
            X,
            full_matrices=False
        )

        pca1 = X @ vt[0]

        reps["PCA1"] = pca1.reshape(
            IIRS_SIZE,
            IIRS_SIZE
        )

    except Exception as e:
        print("PCA failed:", e)
        reps["PCA1"] = reps["spectral_mean"]

    return {
        k: norm01(v)
        for k, v in reps.items()
    }


def save_image(path, x):
    x = norm01(x)
    cv2.imwrite(
        str(path),
        (x * 255).astype(np.uint8)
    )


def main():

    print("=" * 60)
    print("PARALLAX A01 V2 - GEOMETRY-AWARE COMPARISON")
    print("=" * 60)

    print(f"TMC2 -> IIRS X scale: {X_SCALE:.4f}")
    print(f"TMC2 -> IIRS Y scale: {Y_SCALE:.4f}")

    tmc2 = load_tmc2()
    iirs = load_iirs()

    tmc2_patch = extract_tmc2(tmc2)
    iirs_reps = extract_iirs(iirs)

    print()
    print("Geometry-aware TMC2 reduction")

    sigma_x = X_SCALE / 2.0
    sigma_y = Y_SCALE / 2.0

    print(f"sigma_x: {sigma_x:.4f}")
    print(f"sigma_y: {sigma_y:.4f}")

    # Low-pass TMC2 before spatial reduction.
    tmc2_blur = cv2.GaussianBlur(
        tmc2_patch,
        (0, 0),
        sigmaX=sigma_x,
        sigmaY=sigma_y
    )

    # Physical-scale reduction.
    reduced_w = max(
        8,
        int(round(TMC2_SIZE / X_SCALE))
    )

    reduced_h = max(
        8,
        int(round(TMC2_SIZE / Y_SCALE))
    )

    print(
        "Reduced TMC2 grid:",
        reduced_h,
        "x",
        reduced_w
    )

    tmc2_low = cv2.resize(
        tmc2_blur,
        (reduced_w, reduced_h),
        interpolation=cv2.INTER_AREA
    )

    # Put both representations onto the same diagnostic grid.
    tmc2_iirs_grid = cv2.resize(
        tmc2_low,
        (IIRS_SIZE, IIRS_SIZE),
        interpolation=cv2.INTER_LINEAR
    )

    tmc2_grad = gradient(tmc2_iirs_grid)

    save_image(
        OUT / "A01_TMC2_geometry_downsampled.png",
        tmc2_iirs_grid
    )

    save_image(
        OUT / "A01_TMC2_geometry_gradient.png",
        tmc2_grad
    )

    results = []

    print()
    print("=" * 60)
    print("REPRESENTATION RESULTS")
    print("=" * 60)

    for name, rep in iirs_reps.items():

        rep = norm01(rep)

        rep_grad = gradient(rep)

        intensity = correlation(
            rep,
            tmc2_iirs_grid
        )

        grad_corr = correlation(
            rep_grad,
            tmc2_grad
        )

        results.append(
            (
                name,
                intensity,
                grad_corr
            )
        )

        print(
            f"{name:20s}"
            f" intensity={intensity: .5f}"
            f" gradient={grad_corr: .5f}"
        )

    results.sort(
        key=lambda x: abs(x[2]),
        reverse=True
    )

    print()
    print("=" * 60)
    print("TOP REPRESENTATIONS")
    print("=" * 60)

    for name, intensity, grad_corr in results[:5]:
        print(
            f"{name:20s}"
            f" gradient={grad_corr:.5f}"
        )

    best = results[0]

    with open(
        OUT / "A01_v2_results.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("PARALLAX A01 V2\n")
        f.write("============================\n")
        f.write(f"X_SCALE={X_SCALE}\n")
        f.write(f"Y_SCALE={Y_SCALE}\n")
        f.write(f"sigma_x={sigma_x}\n")
        f.write(f"sigma_y={sigma_y}\n")
        f.write(
            f"reduced_grid={reduced_h}x{reduced_w}\n\n"
        )

        for name, intensity, grad_corr in results:
            f.write(
                f"{name}: "
                f"intensity={intensity:.6f}, "
                f"gradient={grad_corr:.6f}\n"
            )

        f.write(
            f"\nBEST_GRADIENT={best[0]} "
            f"{best[2]:.6f}\n"
        )

    print()
    print("Best representation:", best[0])
    print("Best gradient correlation:", f"{best[2]:.5f}")
    print()
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
