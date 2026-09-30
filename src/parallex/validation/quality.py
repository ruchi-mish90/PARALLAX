from __future__ import annotations
from dataclasses import dataclass

@dataclass
class QualityDecision:
    label: str
    score: float
    reasons: list[str]

def quality_decision(
    rmse_px,
    inlier_count,
    inlier_ratio,
    coverage_ratio,
    uniformity,
    confidence=1.0,
):
    reasons = []
    score = 0.0

    if rmse_px < 1.0:
        score += 0.30
    elif rmse_px < 2.0:
        score += 0.18
    else:
        reasons.append("high reprojection error")

    if inlier_count >= 100:
        score += 0.20
    elif inlier_count >= 30:
        score += 0.12
    else:
        reasons.append("insufficient inliers")

    if inlier_ratio >= 0.50:
        score += 0.20
    elif inlier_ratio >= 0.30:
        score += 0.10
    else:
        reasons.append("low inlier ratio")

    if coverage_ratio >= 0.70:
        score += 0.15
    elif coverage_ratio >= 0.40:
        score += 0.08
    else:
        reasons.append("poor spatial coverage")

    if uniformity >= 0.70:
        score += 0.10
    elif uniformity >= 0.45:
        score += 0.05
    else:
        reasons.append("clustered correspondences")

    score += 0.05 * max(0.0, min(1.0, float(confidence)))

    if (
        rmse_px < 1.0
        and inlier_count >= 100
        and inlier_ratio >= 0.50
        and coverage_ratio >= 0.70
    ):
        label = "ACCEPT"
    elif (
        inlier_count >= 30
        and inlier_ratio >= 0.30
        and coverage_ratio >= 0.40
    ):
        label = "PARTIAL"
    else:
        label = "REJECT"

    return QualityDecision(label, min(score, 1.0), reasons)
