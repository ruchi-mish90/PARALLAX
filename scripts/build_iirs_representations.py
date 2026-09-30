from pathlib import Path
import numpy as np
import cv2

ROOT = Path("results/P0001_ROI_FAST")
OUT = ROOT / "iirs_representations"
OUT.mkdir(parents=True, exist_ok=True)


def norm01(x):
    x = np.asarray(x, dtype=np.float32)
    finite = np.isfinite(x)

    if not finite.any():
        return np.zeros_like(x, dtype=np.float32)

    vals = x[finite]
    lo, hi = np.percentile(vals, [2, 98])

    if hi <= lo:
        return np.zeros_like(x, dtype=np.float32)

    y = (x - lo) / (hi - lo)
    return np.clip(y, 0, 1).astype(np.float32)


def save_img(name, x):
    x = np.asarray(x, dtype=np.float32)

    np.save(OUT / f"{name}.npy", x)

    y = (norm01(x) * 255).astype(np.uint8)
    cv2.imwrite(str(OUT / f"{name}.png"), y)


def build_representations(cube):
    """
    Input:
        BAND x LINE x SAMPLE

    Output:
        multiple 2-D representations
    """

    cube = np.asarray(cube, dtype=np.float32)

    cube = np.nan_to_num(
        cube,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    bands = cube.shape[0]

    # ---------------------------------------------------------
    # 1. Spectral mean
    # ---------------------------------------------------------
    spectral_mean = np.mean(cube, axis=0)

    # ---------------------------------------------------------
    # 2. Spectral standard deviation
    # ---------------------------------------------------------
    spectral_std = np.std(cube, axis=0)

    # ---------------------------------------------------------
    # 3. Robust spectral range
    # ---------------------------------------------------------
    p95 = np.percentile(cube, 95, axis=0)
    p05 = np.percentile(cube, 5, axis=0)

    spectral_range = p95 - p05

    # ---------------------------------------------------------
    # 4. First PCA component
    # ---------------------------------------------------------
    X = cube.reshape(bands, -1).T

    X -= np.mean(X, axis=0, keepdims=True)

    try:
        _, _, vt = np.linalg.svd(
            X,
            full_matrices=False
        )

        pc1 = X @ vt[0]
        pc1 = pc1.reshape(
            cube.shape[1],
            cube.shape[2]
        )

    except Exception:
        pc1 = spectral_mean.copy()

    # ---------------------------------------------------------
    # 5. Spectral gradient
    # ---------------------------------------------------------
    if bands > 1:
        spectral_gradient = np.mean(
            np.abs(np.diff(cube, axis=0)),
            axis=0
        )
    else:
        spectral_gradient = np.zeros_like(
            spectral_mean
        )

    return {
        "spectral_mean": spectral_mean,
        "spectral_std": spectral_std,
        "spectral_range": spectral_range,
        "pc1": pc1,
        "spectral_gradient": spectral_gradient,
    }


print("=" * 60)
print("PARALLAX IIRS REPRESENTATION TEST")
print("=" * 60)

print("ROOT:", ROOT.resolve())

if not ROOT.exists():
    print("ERROR: ROI directory does not exist.")
    raise SystemExit(1)

files = (
    list(ROOT.rglob("*.npy"))
    + list(ROOT.rglob("*.npz"))
)

print("FILES FOUND:", len(files))

if not files:
    print("NO NUMPY ROI FILES FOUND.")
    print("Run the FAST ROI extraction first.")
    raise SystemExit(1)

processed = 0

for path in files:

    try:

        if path.suffix.lower() == ".npz":

            data = np.load(path)

            arrays = {
                key: data[key]
                for key in data.files
            }

        else:

            arrays = {
                "array": np.load(path)
            }

        for key, arr in arrays.items():

            # We only process 3-D IIRS cubes.
            if arr.ndim != 3:
                continue

            # Real IIRS cube has 256 bands.
            if arr.shape[0] != 256:
                continue

            print()
            print("-" * 60)
            print("IIRS ROI :", path)
            print("KEY      :", key)
            print("SHAPE    :", arr.shape)
            print("DTYPE    :", arr.dtype)

            reps = build_representations(arr)

            stem = path.stem + "_" + key

            for name, image in reps.items():

                save_img(
                    f"{stem}_{name}",
                    image
                )

                print(
                    f"{name:20s}"
                    f" shape={image.shape}"
                    f" min={float(np.nanmin(image)):.6g}"
                    f" max={float(np.nanmax(image)):.6g}"
                    f" mean={float(np.nanmean(image)):.6g}"
                    f" std={float(np.nanstd(image)):.6g}"
                )

            processed += 1

    except Exception as exc:

        print()
        print("ERROR PROCESSING:", path)
        print(type(exc).__name__, ":", exc)


print()
print("=" * 60)
print("IIRS REPRESENTATION TEST COMPLETE")
print("PROCESSED:", processed)
print("OUTPUT:", OUT.resolve())
print("=" * 60)
