from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import cv2

ROOT = Path(r"C:\Users\graj6\Downloads\parallex")
P0001 = Path(r"C:\Users\graj6\Downloads\P0001")

sys.path.insert(0, str(ROOT / "src"))

from parallex.io.image_loader import open_raw_image, open_iirs_cube
from scipy.ndimage import sobel, gaussian_filter


# ============================================================
# P0001 A01 ONLY
# ============================================================

TMC2 = (
    P0001
    / "ch2_tmc_ncn_20230605T1503198538_d_img_n18"
    / "data"
    / "calibrated"
    / "20230605"
    / "ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
)

IIRS_QUB = (
    P0001
    / "ch2_iir_nci_20221209T1908498944_d_img_n18"
    / "data"
    / "calibrated"
    / "20221209"
    / "ch2_iir_nci_20221209T1908498944_d_img_n18.qub"
)

OUT = ROOT / "results" / "P0001_A01_DIAGNOSTIC"
OUT.mkdir(parents=True, exist_ok=True)

IIRS_SCAN = 1450
IIRS_PIXEL = 50

TMC2_SCAN = 119200
TMC2_PIXEL = 2300

print("=" * 70)
print("PARALLAX P0001 — A01 TMC2 ↔ IIRS DIAGNOSTIC")
print("=" * 70)

print(f"IIRS : scan={IIRS_SCAN}, pixel={IIRS_PIXEL}")
print(f"TMC2 : scan={TMC2_SCAN}, pixel={TMC2_PIXEL}")
print("Geo error = 0.000179 degrees")


# ============================================================
# NORMALIZATION
# ============================================================

def norm(a):
    a = np.asarray(a, dtype=np.float32)

    good = np.isfinite(a)

    if not good.any():
        return np.zeros_like(a)

    lo, hi = np.nanpercentile(a, [2, 98])

    if hi <= lo:
        return np.zeros_like(a)

    out = (a - lo) / (hi - lo)

    return np.clip(np.nan_to_num(out), 0, 1)


# ============================================================
# TMC2
# ============================================================

print("\nLoading TMC2...")

tmc_reader = open_raw_image(
    TMC2,
    153244,
    4000,
    dtype=np.uint16
)

print("TMC2 reader:", type(tmc_reader))
print("TMC2 shape:", tmc_reader.info.shape)
print("TMC2 dtype:", tmc_reader.info.dtype)

T = 1001
half = T // 2

r0 = TMC2_SCAN - half
r1 = TMC2_SCAN + half + 1

c0 = TMC2_PIXEL - half
c1 = TMC2_PIXEL + half + 1

tmc_patch = np.asarray(
    tmc_reader._data[r0:r1, c0:c1],
    dtype=np.float32
)

tmc_norm = norm(tmc_patch)

print("TMC2 local patch:", tmc_norm.shape)


# ============================================================
# IIRS
# ============================================================

print("\nLoading IIRS...")

iirs_reader = open_iirs_cube(
    IIRS_QUB,
    256,
    10075,
    250,
    dtype=np.float32
)

print("IIRS reader:", type(iirs_reader))
print("IIRS bands:", iirs_reader.info.bands)
print("IIRS lines:", iirs_reader.info.lines)
print("IIRS samples:", iirs_reader.info.samples)


# ============================================================
# LOCAL IIRS CUBE
# ============================================================

SIZE = 101
h = SIZE // 2

print("\nReading IIRS local spectral cube...")

cube = []

for b in range(256):

    line0 = max(0, IIRS_SCAN - h)
    col0 = max(0, IIRS_PIXEL - h)

    height = min(
        SIZE,
        iirs_reader.info.lines - line0
    )

    width = min(
        SIZE,
        iirs_reader.info.samples - col0
    )

    arr = iirs_reader.read_band_window(
        b,
        line0,
        col0,
        height,
        width
    )

    arr = np.asarray(
        arr,
        dtype=np.float32
    )

    arr[~np.isfinite(arr)] = np.nan
    cube.append(arr)

cube = np.stack(cube, axis=0)

print("Local cube:", cube.shape)


# ============================================================
# IIRS REPRESENTATIONS
# ============================================================

print("\nBuilding IIRS representations...")

spectral_mean = np.nanmean(cube, axis=0)

spectral_std = np.nanstd(cube, axis=0)

spectral_gradient = np.nanmean(
    np.abs(np.diff(cube, axis=0)),
    axis=0
)

representations = {
    "spectral_mean": spectral_mean,
    "spectral_std": spectral_std,
    "spectral_gradient": spectral_gradient,
    "band_32": cube[32],
    "band_64": cube[64],
    "band_96": cube[96],
    "band_128": cube[128],
    "band_160": cube[160],
    "band_192": cube[192],
    "band_224": cube[224],
}


# ============================================================
# PCA-1
# ============================================================

print("Computing PCA-1...")

X = cube.reshape(
    256,
    -1
).T

X = np.nan_to_num(X)

X -= X.mean(
    axis=0,
    keepdims=True
)

_, _, vt = np.linalg.svd(
    X,
    full_matrices=False
)

pca1 = (
    X @ vt[0]
).reshape(
    SIZE,
    SIZE
)

representations["PCA1"] = pca1


# ============================================================
# TMC2 GRADIENT
# ============================================================

tmc_smooth = gaussian_filter(
    tmc_norm,
    sigma=2
)

tx = sobel(
    tmc_smooth,
    axis=1
)

ty = sobel(
    tmc_smooth,
    axis=0
)

tmc_gradient = np.sqrt(
    tx * tx + ty * ty
)

tmc_gradient = norm(
    tmc_gradient
)


# ============================================================
# RESIZE
# ============================================================

def resize_iirs(x):

    return cv2.resize(
        norm(x),
        (
            tmc_norm.shape[1],
            tmc_norm.shape[0]
        ),
        interpolation=cv2.INTER_LINEAR
    )


# ============================================================
# CORRELATION
# ============================================================

print("\n" + "=" * 70)
print("REPRESENTATION CORRELATIONS")
print("=" * 70)

scores = []

for name, rep in representations.items():

    rr = resize_iirs(rep)

    gx = sobel(
        rr,
        axis=1
    )

    gy = sobel(
        rr,
        axis=0
    )

    grad = np.sqrt(
        gx * gx +
        gy * gy
    )

    a = grad.ravel()
    b = tmc_gradient.ravel()

    good = (
        np.isfinite(a) &
        np.isfinite(b)
    )

    if good.sum() > 10:

        corr = np.corrcoef(
            a[good],
            b[good]
        )[0, 1]

    else:

        corr = np.nan

    scores.append(
        (name, corr)
    )

    print(
        f"{name:20s} "
        f"gradient correlation = "
        f"{corr: .5f}"
    )


scores.sort(
    key=lambda x: (
        -999
        if not np.isfinite(x[1])
        else x[1]
    ),
    reverse=True
)

print("\nTop representations:")

for name, score in scores[:5]:

    print(
        f"  {name:20s} "
        f"{score: .5f}"
    )


# ============================================================
# FIGURE 1
# ============================================================

fig, axes = plt.subplots(
    3,
    4,
    figsize=(16, 12)
)

names = list(representations.keys())

for ax, name in zip(
    axes.flat,
    names
):

    ax.imshow(
        norm(representations[name]),
        cmap="gray"
    )

    ax.set_title(name)
    ax.axis("off")

for ax in axes.flat[len(names):]:
    ax.axis("off")

fig.suptitle(
    "P0001 A01 — IIRS Spectral Representations"
)

fig.tight_layout()

f1 = (
    OUT /
    "A01_IIRS_representations.png"
)

fig.savefig(
    f1,
    dpi=160,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSaved:", f1)


# ============================================================
# FIGURE 2
# ============================================================

top_names = [
    x[0]
    for x in scores[:3]
]

fig, axes = plt.subplots(
    5,
    2,
    figsize=(12, 24)
)

axes[0, 0].imshow(
    tmc_norm,
    cmap="gray"
)

axes[0, 0].set_title(
    "TMC2 intensity — A01"
)

axes[0, 0].axis("off")


axes[0, 1].imshow(
    tmc_gradient,
    cmap="gray"
)

axes[0, 1].set_title(
    "TMC2 gradient"
)

axes[0, 1].axis("off")


axes[1, 0].imshow(
    norm(spectral_mean),
    cmap="gray"
)

axes[1, 0].set_title(
    "IIRS spectral mean"
)

axes[1, 0].axis("off")


axes[1, 1].imshow(
    norm(spectral_gradient),
    cmap="gray"
)

axes[1, 1].set_title(
    "IIRS spectral gradient"
)

axes[1, 1].axis("off")


for row, name in enumerate(
    top_names,
    start=2
):

    rr = resize_iirs(
        representations[name]
    )

    gx = sobel(
        rr,
        axis=1
    )

    gy = sobel(
        rr,
        axis=0
    )

    grad = norm(
        np.sqrt(
            gx * gx +
            gy * gy
        )
    )

    axes[row, 0].imshow(
        rr,
        cmap="gray"
    )

    axes[row, 0].set_title(
        f"IIRS {name}"
    )

    axes[row, 0].axis("off")

    axes[row, 1].imshow(
        grad,
        cmap="gray"
    )

    axes[row, 1].set_title(
        f"IIRS {name} gradient"
    )

    axes[row, 1].axis("off")


fig.suptitle(
    "P0001 A01 — TMC2 ↔ IIRS Structural Diagnostic"
)

fig.tight_layout()

f2 = (
    OUT /
    "A01_TMC2_IIRS_structural_comparison.png"
)

fig.savefig(
    f2,
    dpi=160,
    bbox_inches="tight"
)

plt.close(fig)

print("Saved:", f2)


# ============================================================
# SUMMARY
# ============================================================

summary = (
    OUT /
    "A01_diagnostic.txt"
)

with open(
    summary,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "P0001 A01 TMC2-IIRS diagnostic\n"
    )

    f.write(
        "IIRS scan=1450 pixel=50\n"
    )

    f.write(
        "TMC2 scan=119200 pixel=2300\n"
    )

    f.write(
        "geo_error=0.000179 degrees\n\n"
    )

    for name, score in scores:

        f.write(
            f"{name}: "
            f"gradient_correlation="
            f"{score}\n"
        )


print("\n" + "=" * 70)
print("A01 DIAGNOSTIC COMPLETE")
print("=" * 70)
print("OUTPUT:", OUT)


