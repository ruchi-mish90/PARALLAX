from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class SubpixelResult:
    points: np.ndarray
    shifts: np.ndarray
    mean_shift: float
    success_ratio: float


def refine_points(
    image,
    points,
    radius=3,
    min_variation=1e-6,
):
    image = np.asarray(image, dtype=np.float32)
    points = np.asarray(points, dtype=np.float32).reshape(-1, 2)

    refined = points.copy()
    shifts = np.zeros_like(points)

    h, w = image.shape[:2]
    successes = 0

    for i, (x, y) in enumerate(points):
        xi = int(round(float(x)))
        yi = int(round(float(y)))

        x0 = max(0, xi - radius)
        x1 = min(w, xi + radius + 1)
        y0 = max(0, yi - radius)
        y1 = min(h, yi + radius + 1)

        patch = image[y0:y1, x0:x1]

        if patch.size < 9:
            continue

        weights = patch - float(patch.min())

        if float(weights.max()) < min_variation:
            continue

        yy, xx = np.mgrid[y0:y1, x0:x1]

        weight_sum = float(weights.sum())

        if weight_sum <= min_variation:
            continue

        refined_y = float((yy * weights).sum() / weight_sum)
        refined_x = float((xx * weights).sum() / weight_sum)

        shift = np.array(
            [refined_x - x, refined_y - y],
            dtype=np.float32,
        )

        # Reject implausibly large local shifts.
        if float(np.linalg.norm(shift)) > radius:
            continue

        refined[i] = np.array(
            [refined_x, refined_y],
            dtype=np.float32,
        )
        shifts[i] = shift
        successes += 1

    mean_shift = (
        float(np.mean(np.linalg.norm(shifts, axis=1)))
        if len(shifts)
        else 0.0
    )

    success_ratio = (
        successes / float(len(points))
        if len(points)
        else 0.0
    )

    return SubpixelResult(
        points=refined,
        shifts=shifts,
        mean_shift=mean_shift,
        success_ratio=success_ratio,
    )
