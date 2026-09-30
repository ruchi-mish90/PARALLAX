from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ObservabilityResult:
    observable: bool
    score: float
    reasons: list[str]


def observability_gate(
    *,
    overlap_ratio: float,
    valid_pixel_ratio: float,
    texture_score: float,
    geometric_valid: bool = True,
    min_overlap: float = 0.01,
    min_valid_pixels: float = 0.05,
    min_texture: float = 0.02,
) -> ObservabilityResult:

    reasons = []

    overlap_ratio = max(0.0, min(1.0, float(overlap_ratio)))
    valid_pixel_ratio = max(0.0, min(1.0, float(valid_pixel_ratio)))
    texture_score = max(0.0, min(1.0, float(texture_score)))

    if overlap_ratio < min_overlap:
        reasons.append("insufficient_spatial_overlap")

    if valid_pixel_ratio < min_valid_pixels:
        reasons.append("insufficient_valid_pixels")

    if texture_score < min_texture:
        reasons.append("insufficient_texture")

    if not geometric_valid:
        reasons.append("invalid_geometry")

    if reasons:
        score = 0.0
    else:
        score = (
            0.40 * overlap_ratio
            + 0.30 * valid_pixel_ratio
            + 0.20 * texture_score
            + 0.10 * float(geometric_valid)
        )
        score = max(0.0, min(1.0, score))

    return ObservabilityResult(
        observable=len(reasons) == 0,
        score=float(score),
        reasons=reasons,
    )
