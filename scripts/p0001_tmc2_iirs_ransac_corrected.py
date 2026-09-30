import numpy as np
import cv2
import time

SX, SY = 9.6805, 8.1776

# Each entry:
# (anchor, IIRS local offset x,y, observed TMC2 local-match displacement x,y, score)
DATA = [
    ("A01",-10,-10, 17,15,0.1645),
    ("A01",  0,-10,  6, 6,0.2762),
    ("A01", 10,-10,  6, 6,0.3065),
    ("A01",-10,  0,  0,10,0.1786),
    ("A01",  0,  0,  0, 0,0.3354),
    ("A01", 10,  0, -1,0,0.3459),
    ("A01",-10, 10, 17,15,0.1745),
    ("A01",  0, 10,  0, 0,0.3576),
    ("A01", 10, 10, -1,0,0.3732),

    ("A03", 0,-10, 0,20,0.2245),
    ("A03",10,-10, 0, 9,0.1909),
    ("A03", 0,  0, 0, 0,0.2303),
    ("A03",10,  0, 0, 1,0.1913),
    ("A03", 0, 10, 0, 0,0.2398),
    ("A03",10, 10, 0,-11,0.1912),
]

# Geometry seed displacement measured previously.
SEED = {
    "A01": (6,-5),
    "A03": (3,18),
}

src = []
dst = []
scores = []

for name, ox, oy, dx, dy, score in DATA:

    # IIRS local coordinates.
    p_iirs = np.array([ox, oy], dtype=np.float32)

    # Observed correspondence displacement expressed in IIRS-scale pixels.
    #
    # seed = coarse geometry-constrained displacement
    # local = fine template-match displacement
    #
    # Both are expressed in the same IIRS-scale frame.
    sx, sy = SEED[name]

    observed = np.array([
        sx + ox + dx,
        sy + oy + dy
    ], dtype=np.float32)

    src.append(p_iirs)
    dst.append(observed)
    scores.append(score)

src = np.asarray(src)
dst = np.asarray(dst)
scores = np.asarray(scores)

print("="*70)
print("PARALLAX CORRECTED LOCAL-FRAME RANSAC")
print("="*70)

# Fit translation first because the geometry has already removed
# most scale/rotation differences.
M, mask = cv2.estimateAffinePartial2D(
    src,
    dst,
    method=cv2.RANSAC,
    ransacReprojThreshold=4.0,
    maxIters=1000,
    confidence=0.99
)

if M is None:
    print("RANSAC FAILED")
    raise SystemExit

mask = mask.ravel().astype(bool)

pred = cv2.transform(
    src.reshape(-1,1,2),
    M
).reshape(-1,2)

errors = np.linalg.norm(pred-dst, axis=1)

print()
print(f"CORRESPONDENCES : {len(src)}")
print(f"INLIERS          : {mask.sum()}/{len(mask)}")
print(f"INLIER RATIO     : {mask.mean():.4f}")
print(f"MEDIAN ERROR     : {np.median(errors):.4f} IIRS px")
print(f"MEAN ERROR       : {np.mean(errors):.4f} IIRS px")

if mask.any():
    print(f"MAX INLIER ERROR : {np.max(errors[mask]):.4f} IIRS px")

print()
print("LOCAL TRANSFORM")
print(M)

print()
print("CORRESPONDENCE RESIDUALS")

for i in range(len(src)):
    status = "INLIER" if mask[i] else "OUTLIER"
    print(
        f"{i+1:02d} {status:7s} "
        f"{DATA[i][0]} "
        f"IIRS=({src[i,0]:+.0f},{src[i,1]:+.0f}) "
        f"OBS=({dst[i,0]:+.1f},{dst[i,1]:+.1f}) "
        f"err={errors[i]:.3f} "
        f"score={scores[i]:.4f}"
    )

print()
print("="*70)
print(f"TOTAL TIME: {0:.3f}s")
print("CORRECTED GEOMETRIC VERIFICATION COMPLETE")
print("="*70)
