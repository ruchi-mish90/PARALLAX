from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DifficultyResult:
    score: float
    label: str


def estimate_difficulty(
    *,
    texture_score: float,
    illumination_difference: float,
    scale_ratio: float,
    viewpoint_difference: float,
    terrain_complexity: float,
    valid_pixel_ratio: float,
) -> DifficultyResult:

    # Normalize scale logarithmically so large GSD differences
    # do not immediately saturate the difficulty score.
    scale_score = min(1.0, max(0.0, scale_ratio / 25.0))

    texture_difficulty = 1.0 - max(0.0, min(1.0, texture_score))
    validity_difficulty = 1.0 - max(0.0, min(1.0, valid_pixel_ratio))

    score = (
        0.20 * texture_difficulty
        + 0.20 * illumination_difference
        + 0.20 * scale_score
        + 0.15 * viewpoint_difference
        + 0.15 * terrain_complexity
        + 0.10 * validity_difficulty
    )

    score = max(0.0, min(1.0, score))

    if score < 0.33:
        label = "easy"
    elif score < 0.66:
        label = "medium"
    elif score < 0.85:
        label = "hard"
    else:
        label = "extreme"

    return DifficultyResult(
        score=float(score),
        label=label,
    )
