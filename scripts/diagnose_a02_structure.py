from pathlib import Path
import cv2
import numpy as np

ROOT = Path("results/P0001_REAL_A02")
OUT = ROOT / "diagnostic"
OUT.mkdir(exist_ok=True)

def normalize(x):
    x = np.asarray(x, dtype=np.float32)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)

    lo, hi = np.percentile(x, [2, 98])

    if hi <= lo:
        return np.zeros_like(x, dtype=np.uint8)

    return (
        np.clip((x - lo) / (hi - lo), 0, 1) * 255
    ).astype(np.uint8)


def edges(x):
    x = normalize(x)
    return cv2.Canny(x, 30, 100)


tmc = cv2.imread(
    str(ROOT / "tmc2_a02_scaled.png"),
    cv2.IMREAD_GRAYSCALE,
)

print("=" * 60)
print("PARALLAX A02 STRUCTURAL DIAGNOSTIC")
print("=" * 60)

if tmc is None:
    raise FileNotFoundError("TMC2 scaled image not found")

print("TMC2:", tmc.shape)

for name in [
    "spectral_mean",
    "pc1",
    "spectral_gradient",
]:

    p = ROOT / f"iirs_a02_{name}.png"

    img = cv2.imread(
        str(p),
        cv2.IMREAD_GRAYSCALE,
    )

    if img is None:
        print("MISSING:", p)
        continue

    print()
    print(name)

    print("shape:", img.shape)
    print("TMC2 std:", float(tmc.std()))
    print("IIRS std:", float(img.std()))

    # Resize only for diagnostic comparison.
    iirs_resized = cv2.resize(
        img,
        (tmc.shape[1], tmc.shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )

    # Correlation
    a = tmc.astype(np.float32).ravel()
    b = iirs_resized.astype(np.float32).ravel()

    if np.std(a) > 0 and np.std(b) > 0:
        corr = float(
            np.corrcoef(a, b)[0, 1]
        )
    else:
        corr = 0.0

    print("global intensity correlation:", corr)

    # Edge correlation
    ea = edges(tmc).astype(np.float32)
    eb = edges(iirs_resized).astype(np.float32)

    if np.std(ea) > 0 and np.std(eb) > 0:
        edge_corr = float(
            np.corrcoef(
                ea.ravel(),
                eb.ravel(),
            )[0, 1]
        )
    else:
        edge_corr = 0.0

    print("edge correlation:", edge_corr)

    # Save side-by-side diagnostic.
    panel = np.hstack([
        tmc,
        iirs_resized,
        ea.astype(np.uint8),
        eb.astype(np.uint8),
    ])

    cv2.imwrite(
        str(OUT / f"{name}_comparison.png"),
        panel,
    )

print()
print("OUTPUT:", OUT.resolve())
print("=" * 60)
