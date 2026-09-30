from pathlib import Path
import json
import cv2
import numpy as np

from parallex.io.image_loader import open_raw_image


ROOT = Path.cwd()
P0001 = ROOT.parent / "P0001"

TMC2 = next(
    P0001.rglob(
        "ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
    )
)

print("=" * 78)
print("PARALLAX P0001 - CONTROLLED POSITIVE PIPELINE TEST")
print("=" * 78)

print("\n[1] LOAD REAL P0001 TMC2")

reader = open_raw_image(
    TMC2,
    153244,
    4000,
    dtype=np.uint16,
)

# Use a manageable real-image ROI.
# This is still directly extracted from P0001.
row = 70000
col = 1200
height = 1200
width = 1200

image_a = reader.read_window(
    row,
    col,
    height,
    width,
)

image_a = np.asarray(image_a)

print("source:", TMC2)
print("ROI:", image_a.shape)
print("dtype:", image_a.dtype)
print(
    "range:",
    float(np.nanmin(image_a)),
    float(np.nanmax(image_a)),
)

# Normalize for feature matching.
image_a = cv2.normalize(
    image_a,
    None,
    0,
    255,
    cv2.NORM_MINMAX,
).astype(np.uint8)

# ------------------------------------------------------------
# 2. KNOWN CONTROLLED TRANSFORMATION
# ------------------------------------------------------------

angle = 2.0
scale = 1.0
tx = 18.0
ty = -12.0

h, w = image_a.shape[:2]

center = (w / 2.0, h / 2.0)

matrix = cv2.getRotationMatrix2D(
    center,
    angle,
    scale,
)

matrix[0, 2] += tx
matrix[1, 2] += ty

image_b = cv2.warpAffine(
    image_a,
    matrix,
    (w, h),
    flags=cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_REFLECT,
)

print("\n[2] CONTROLLED TRANSFORMATION")

print("angle_deg:", angle)
print("scale:", scale)
print("translation_x:", tx)
print("translation_y:", ty)
print("matrix:")
print(matrix)

# ------------------------------------------------------------
# 3. PIPELINE
# ------------------------------------------------------------

from parallex.pipeline.registration import RegistrationPipeline

pipeline = RegistrationPipeline()

metadata_a = {
    "sensor": "TMC2",
    "instrument": "TMC2",
    "resolution": 5.0,
}

metadata_b = {
    "sensor": "TMC2",
    "instrument": "TMC2",
    "resolution": 5.0,
}

print("\n[3] RUN REGISTRATION PIPELINE")

decision, result = pipeline.run(
    image_a,
    image_b,
    metadata_a,
    metadata_b,
    overlap_ratio=1.0,
    valid_pixel_ratio=1.0,
)

print("\n[4] DECISION")

print("rejected:", decision.rejected)
print("selected_matcher:", decision.selected_matcher)
print("difficulty:", decision.difficulty)
print("confidence:", decision.confidence)
print("reason:", decision.reason)
print("rejection_reason:", decision.rejection_reason)

print("\n[5] ATTEMPTS")

for i, attempt in enumerate(decision.attempts, 1):
    print("\nAttempt", i)

    for key in [
        "matcher",
        "status",
        "raw_matches",
        "filtered_matches",
        "confidence_threshold",
        "inliers",
        "inlier_ratio",
        "reprojection_error_px",
        "coverage_ratio",
        "uniformity",
        "refinement_success",
        "refinement_success_ratio_a",
        "refinement_success_ratio_b",
        "mean_subpixel_shift_a",
        "mean_subpixel_shift_b",
        "refined_reprojection_error_px",
        "quality_score",
        "quality_decision",
        "quality_reasons",
    ]:
        if key in attempt:
            print(f"{key}: {attempt[key]}")

# ------------------------------------------------------------
# 6. RESULT SUMMARY
# ------------------------------------------------------------

print("\n[6] RESULT")

print("result type:", type(result))

if result is not None:

    print("result attributes:")

    for name in [
        "matches",
        "keypoints_a",
        "keypoints_b",
        "scores",
        "inlier_mask",
        "model_name",
        "metadata",
    ]:
        if hasattr(result, name):
            value = getattr(result, name)

            try:
                print(
                    name,
                    "shape=",
                    np.asarray(value).shape,
                )
            except Exception:
                print(name, "=", value)

# ------------------------------------------------------------
# 7. SAVE REPORT
# ------------------------------------------------------------

out = ROOT / "results" / "P0001_CONTROLLED_POSITIVE"

out.mkdir(
    parents=True,
    exist_ok=True,
)

report = {
    "test": "P0001 controlled positive pipeline",
    "source": str(TMC2),
    "roi": {
        "row": row,
        "col": col,
        "height": height,
        "width": width,
    },
    "known_transform": {
        "angle_deg": angle,
        "scale": scale,
        "translation_x": tx,
        "translation_y": ty,
        "matrix": matrix.tolist(),
    },
    "decision": {
        "rejected": bool(decision.rejected),
        "selected_matcher": decision.selected_matcher,
        "difficulty": decision.difficulty,
        "confidence": float(decision.confidence),
        "reason": decision.reason,
        "rejection_reason": decision.rejection_reason,
    },
    "attempts": decision.attempts,
}

(out / "report.json").write_text(
    json.dumps(
        report,
        indent=2,
        default=str,
    ),
    encoding="utf-8",
)

print("\nReport:", out / "report.json")

print("\n" + "=" * 78)
print("CONTROLLED TEST COMPLETE")
print("=" * 78)

