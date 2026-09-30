import numpy as np

from parallex.matching.base import MatchResult


def filter_confident_matches(
    result: MatchResult,
    min_score: float = 0.0,
    max_reprojection_error: float | None = None,
):
    """
    Filter correspondences using available confidence signals.

    RANSAC inliers are required when an inlier mask is available.
    Thresholds are intentionally configurable; final PARALLAX
    thresholds must be established experimentally.
    """

    n = result.num_matches

    if n == 0:
        result.metadata["confidence_filter"] = {
            "input_matches": 0,
            "accepted_matches": 0,
        }
        return result

    keep = np.ones(n, dtype=bool)

    if result.inlier_mask is not None:
        keep &= np.asarray(
            result.inlier_mask,
            dtype=bool,
        )

    if result.scores is not None:
        keep &= np.asarray(
            result.scores,
            dtype=np.float32,
        ) >= float(min_score)

    if max_reprojection_error is not None:
        errors = result.metadata.get(
            "reprojection_errors"
        )

        if errors is not None:
            errors = np.asarray(
                errors,
                dtype=np.float32,
            )

            if len(errors) == n:
                keep &= errors <= float(
                    max_reprojection_error
                )

    result.metadata["confidence_filter"] = {
        "input_matches": int(n),
        "accepted_matches": int(keep.sum()),
        "accepted_ratio": float(
            keep.sum() / n
        ),
        "min_score": float(min_score),
        "max_reprojection_error": (
            None
            if max_reprojection_error is None
            else float(max_reprojection_error)
        ),
    }

    result.metadata["accepted_mask"] = keep

    return result
