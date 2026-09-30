from pathlib import Path
import cv2
import numpy as np

print("=" * 70)
print("PARALLAX SPATIAL CONSENSUS VERIFICATION")
print("=" * 70)

# P0001 TMC2 ↔ IIRS geometry-valid anchors
anchors = {
    "A01": {"iirs": (50, 1450), "tmc2": (2300, 119200)},
    "A02": {"iirs": (100, 3700), "tmc2": (1200, 82300)},
    "A03": {"iirs": (0, 1800), "tmc2": (1200, 113500)},
    "A04": {"iirs": (200, 5250), "tmc2": (1600, 56900)},
    "A05": {"iirs": (50, 750), "tmc2": (2900, 130700)},
}

# Existing geometry-constrained observations.
# Empty means the anchor has not yet produced enough independent matches.
observations = {
    "A01": [
        ((0, 0), (6, -5)),
        ((10, 0), (15, -5)),
        ((0, 10), (6, 5)),
        ((10, 10), (15, 5)),
    ],
    "A02": [],
    "A03": [
        ((0, 0), (3, 18)),
        ((10, 0), (13, 19)),
        ((0, 10), (3, 28)),
        ((10, 10), (13, 17)),
    ],
    "A04": [],
    "A05": [],
}

results = []

for name, anchor in anchors.items():
    pts = observations[name]

    print(f"\n{name}")
    print(f"  IIRS anchor : {anchor['iirs']}")
    print(f"  TMC2 anchor : {anchor['tmc2']}")

    if len(pts) < 4:
        print("  status      : INSUFFICIENT INDEPENDENT CORRESPONDENCES")
        results.append({
            "anchor": name,
            "supported": False,
            "inliers": 0,
            "total": len(pts),
        })
        continue

    src = np.float32([p[0] for p in pts])
    dst = np.float32([p[1] for p in pts])

    M, mask = cv2.estimateAffinePartial2D(
        src,
        dst,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=2000,
        confidence=0.99,
    )

    if M is None or mask is None:
        print("  status      : RANSAC FAILED")
        results.append({
            "anchor": name,
            "supported": False,
            "inliers": 0,
            "total": len(pts),
        })
        continue

    predicted = cv2.transform(
        src.reshape(-1, 1, 2), M
    ).reshape(-1, 2)

    errors = np.linalg.norm(predicted - dst, axis=1)
    inliers = mask.ravel().astype(bool)

    n_inliers = int(inliers.sum())
    ratio = n_inliers / len(pts)
    median_error = float(np.median(errors))
    max_inlier_error = (
        float(np.max(errors[inliers]))
        if n_inliers else float("inf")
    )

    supported = (
        n_inliers >= 4
        and ratio >= 0.50
        and max_inlier_error <= 3.0
    )

    print(f"  correspondences : {len(pts)}")
    print(f"  inliers         : {n_inliers}/{len(pts)}")
    print(f"  inlier ratio    : {ratio:.4f}")
    print(f"  median error    : {median_error:.4f} px")
    print(f"  max inlier err  : {max_inlier_error:.4f} px")
    print(f"  local transform :")
    print(M)
    print(
        f"  local status   : "
        f"{'SUPPORTED' if supported else 'REJECTED'}"
    )

    results.append({
        "anchor": name,
        "supported": supported,
        "inliers": n_inliers,
        "total": len(pts),
    })

print("\n" + "=" * 70)
print("SPATIAL CONSENSUS")
print("=" * 70)

supported = [r for r in results if r["supported"]]

print(
    f"SUPPORTED ANCHORS : "
    f"{len(supported)}/{len(results)}"
)

for r in results:
    print(
        f"{r['anchor']:>4}  "
        f"{r['inliers']}/{r['total']}  "
        f"{'SUPPORTED' if r['supported'] else 'REJECTED'}"
    )

# Require support from at least three independent spatial locations.
global_supported = len(supported) >= 3

print()
print(
    "GLOBAL STATUS     : "
    + (
        "GLOBAL REGISTRATION SUPPORTED"
        if global_supported
        else "GLOBAL REGISTRATION REJECTED"
    )
)

print("=" * 70)
print("SPATIAL VERIFICATION COMPLETE")
print("=" * 70)
