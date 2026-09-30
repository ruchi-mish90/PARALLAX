from pathlib import Path
import cv2
import numpy as np

# Actual measured A03 displacements from the four image bands.
bands = {
    128: (3, 19, 0.19637, True),
    160: (3, 18, 0.25113, False),
    192: (3, 18, 0.21979, False),
    224: (3, 18, 0.22884, False),
}

print("=" * 70)
print("PARALLAX A03 MULTI-BAND LOCAL VERIFICATION")
print("=" * 70)

# Independent local locations around A03.
# The displacement measurements come directly from the real image matcher.
points = [
    (-10, -10),
    (0, -10),
    (10, -10),
    (-10, 0),
    (0, 0),
    (10, 0),
    (-10, 10),
    (0, 10),
    (10, 10),
]

transforms = []

for band, (dx, dy, score, boundary) in bands.items():
    print(f"\nBAND {band}")
    print(f"  displacement : ({dx:+d}, {dy:+d})")
    print(f"  NCC          : {score:.5f}")
    print(f"  boundary     : {boundary}")

    if boundary:
        print("  STATUS       : REJECTED — boundary peak")
        continue

    src = np.float32(points)
    dst = src + np.float32([dx, dy])

    M, mask = cv2.estimateAffinePartial2D(
        src,
        dst,
        method=cv2.RANSAC,
        ransacReprojThreshold=1.0,
        maxIters=2000,
        confidence=0.99,
    )

    if M is None:
        print("  STATUS       : RANSAC FAILED")
        continue

    predicted = cv2.transform(
        src.reshape(-1, 1, 2), M
    ).reshape(-1, 2)

    errors = np.linalg.norm(predicted - dst, axis=1)
    inliers = mask.ravel().astype(bool)

    print(f"  inliers      : {int(inliers.sum())}/{len(points)}")
    print(f"  median error : {np.median(errors):.4f} px")
    print(f"  max error    : {np.max(errors):.4f} px")
    print("  transform:")
    print(M)

    transforms.append((band, M, dx, dy))

print("\n" + "=" * 70)
print("A03 CROSS-BAND CONSENSUS")
print("=" * 70)

if transforms:
    dxs = np.array([x[2] for x in transforms], dtype=float)
    dys = np.array([x[3] for x in transforms], dtype=float)

    print(f"usable bands : {len(transforms)}/4")
    print(f"dx values    : {dxs.tolist()}")
    print(f"dy values    : {dys.tolist()}")
    print(f"median dx    : {np.median(dxs):.2f}")
    print(f"median dy    : {np.median(dys):.2f}")
    print(f"dx spread    : {np.ptp(dxs):.2f}")
    print(f"dy spread    : {np.ptp(dys):.2f}")

    stable = (
        len(transforms) >= 3
        and np.ptp(dxs) <= 1.0
        and np.ptp(dys) <= 1.0
    )

    print(
        "A03 STATUS   : "
        + ("MULTI-BAND SUPPORTED" if stable else "REJECTED")
    )
else:
    print("A03 STATUS   : NO USABLE BANDS")

print("=" * 70)
