from pathlib import Path
import cv2
import numpy as np

from parallex.io.pds4_image import open_pds4_image
from parallex.io.roi import ROI, memory_safe_window
from parallex.matching.superpoint_lightglue import SuperPointLightGlueMatcher
from parallex.verification.geometric import verify_matches


def normalize_image(x):
    x = x.astype(np.float32)
    lo, hi = np.percentile(x, [1, 99])
    return np.clip(
        (x - lo) * 255.0 / max(hi - lo, 1e-6),
        0,
        255,
    ).astype(np.uint8)


root = Path(r"data\real_pairs")
out = root / "registration_results"
out.mkdir(exist_ok=True)

a = open_pds4_image(
    root / "ch2_tmc_nca_20221209T2305274611_d_img_d32"
)
b = open_pds4_image(
    root / "ch2_tmc_ncn_20221209T2305274611_d_img_d32"
)

roi_a = ROI(57576, 59624, 2975, 4000)
roi_b = ROI(67176, 69224, 2975, 4000)

image_a = memory_safe_window(
    a, roi_a, max_height=2048, max_width=2048
)
image_b = memory_safe_window(
    b, roi_b, max_height=2048, max_width=2048
)

matcher = SuperPointLightGlueMatcher(
    max_keypoints=512,
    device="cuda",
)

matches_result = matcher.match(image_a, image_b)

verification = verify_matches(
    matches_result.keypoints_a,
    matches_result.keypoints_b,
    matches_result.matches,
    model="affine",
)

A = normalize_image(image_a)
B = normalize_image(image_b)

keypoints_a = np.asarray(matches_result.keypoints_a)
keypoints_b = np.asarray(matches_result.keypoints_b)
matches = np.asarray(matches_result.matches)


# ---------------------------------------------------------
# 1. RAW MATCHES
# ---------------------------------------------------------

raw_canvas = cv2.hconcat([A, B])

for i, j in matches:
    p1 = (
        int(keypoints_a[i, 0]),
        int(keypoints_a[i, 1]),
    )
    p2 = (
        int(keypoints_b[j, 0]) + A.shape[1],
        int(keypoints_b[j, 1]),
    )

    cv2.line(
        raw_canvas,
        p1,
        p2,
        255,
        1,
    )

cv2.imwrite(
    str(out / "raw_matches.png"),
    raw_canvas,
)


# ---------------------------------------------------------
# 2. VERIFIED MATCHES
# ---------------------------------------------------------

verified_canvas = cv2.hconcat([A, B])

inlier_matches = matches[verification.inlier_mask]

for i, j in inlier_matches:
    p1 = (
        int(keypoints_a[i, 0]),
        int(keypoints_a[i, 1]),
    )
    p2 = (
        int(keypoints_b[j, 0]) + A.shape[1],
        int(keypoints_b[j, 1]),
    )

    cv2.line(
        verified_canvas,
        p1,
        p2,
        255,
        2,
    )

cv2.imwrite(
    str(out / "verified_matches.png"),
    verified_canvas,
)


# ---------------------------------------------------------
# 3. REGISTERED OVERLAY
# ---------------------------------------------------------

warped = cv2.warpAffine(
    A,
    verification.matrix,
    (B.shape[1], B.shape[0]),
)

overlay = cv2.addWeighted(
    warped,
    0.5,
    B,
    0.5,
    0,
)

cv2.imwrite(
    str(out / "registered_overlay.png"),
    overlay,
)


# ---------------------------------------------------------
# 4. METRICS
# ---------------------------------------------------------

metrics = f"""PARALLAX REAL-DATA REGISTRATION RESULT

Sensor Pair:
TMC-2 NCA 20221209
TMC-2 NCN 20221209

ROI A:
{roi_a}

ROI B:
{roi_b}

Keypoints A:
{len(keypoints_a)}

Keypoints B:
{len(keypoints_b)}

Raw matches:
{verification.num_matches}

Geometric inliers:
{verification.num_inliers}

Inlier ratio:
{verification.inlier_ratio:.4f}

Reprojection RMSE (px):
{verification.reprojection_error:.4f}

RANSAC success:
{verification.success}

Model:
{verification.model_name}

Affine matrix:
{verification.matrix}
"""

(out / "registration_metrics.txt").write_text(
    metrics,
    encoding="utf-8",
)

print("REGISTRATION COMPLETE")
print("RAW MATCHES:", out / "raw_matches.png")
print("VERIFIED MATCHES:", out / "verified_matches.png")
print("REGISTERED OVERLAY:", out / "registered_overlay.png")
print("METRICS:", out / "registration_metrics.txt")
print("INLIERS:", verification.num_inliers)
print("RMSE:", verification.reprojection_error)
