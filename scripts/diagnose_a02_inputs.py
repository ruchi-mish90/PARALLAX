from pathlib import Path
import cv2
import numpy as np

ROOT = Path("results/P0001_REAL_A02")

tmc = cv2.imread(
    str(ROOT / "tmc2_a02_scaled.png"),
    cv2.IMREAD_GRAYSCALE,
)

print("=" * 60)
print("A02 MATCHING INPUT DIAGNOSTIC")
print("=" * 60)

print("TMC2 scaled:", None if tmc is None else tmc.shape)

for p in sorted(ROOT.glob("iirs_a02_*.png")):

    img = cv2.imread(
        str(p),
        cv2.IMREAD_GRAYSCALE,
    )

    if img is None:
        continue

    # Gradient strength
    gx = cv2.Sobel(
        img,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    gy = cv2.Sobel(
        img,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    grad = np.sqrt(gx * gx + gy * gy)

    # SIFT count
    sift = cv2.SIFT_create(
        nfeatures=1000
    )

    kp = sift.detect(img, None)

    print()
    print(p.name)
    print("shape:", img.shape)
    print("min:", int(img.min()))
    print("max:", int(img.max()))
    print("std:", float(img.std()))
    print("gradient mean:", float(grad.mean()))
    print("gradient std:", float(grad.std()))
    print("SIFT keypoints:", len(kp))

print()
print("=" * 60)

if tmc is not None:

    gx = cv2.Sobel(
        tmc,
        cv2.CV_32F,
        1,
        0,
        ksize=3,
    )

    gy = cv2.Sobel(
        tmc,
        cv2.CV_32F,
        0,
        1,
        ksize=3,
    )

    grad = np.sqrt(gx * gx + gy * gy)

    sift = cv2.SIFT_create(
        nfeatures=1000
    )

    kp = sift.detect(tmc, None)

    print("TMC2")
    print("std:", float(tmc.std()))
    print("gradient mean:", float(grad.mean()))
    print("gradient std:", float(grad.std()))
    print("SIFT keypoints:", len(kp))

print("=" * 60)
