from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class ConfidenceResult:
    matches: np.ndarray
    scores: np.ndarray
    mask: np.ndarray
    threshold: float
    retained_ratio: float


def filter_matches_by_confidence(
    matches,
    scores,
    threshold=0.0,
    percentile=None,
    min_matches=4,
):
    matches = np.asarray(matches)

    if matches.size == 0:
        matches = np.empty((0, 2), dtype=np.int32)

    scores = np.asarray(scores, dtype=np.float32).reshape(-1)

    if len(matches) != len(scores):
        raise ValueError(
            "matches and scores must have the same length"
        )

    if len(scores) == 0:
        return ConfidenceResult(
            matches,
            scores,
            np.zeros(0, dtype=bool),
            float(threshold),
            0.0,
        )

    if percentile is not None:
        percentile = float(np.clip(percentile, 0.0, 100.0))
        threshold = max(
            float(threshold),
            float(np.percentile(scores, percentile)),
        )

    mask = scores >= float(threshold)

    # Never allow the confidence filter to destroy
    # the minimum correspondence set needed for geometry.
    if int(mask.sum()) < min_matches and len(scores) >= min_matches:
        order = np.argsort(-scores)
        mask = np.zeros(len(scores), dtype=bool)
        mask[order[:min_matches]] = True

    retained = int(mask.sum())

    return ConfidenceResult(
        matches=matches[mask],
        scores=scores[mask],
        mask=mask,
        threshold=float(threshold),
        retained_ratio=retained / float(len(scores)),
    )
