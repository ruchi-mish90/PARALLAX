from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class CoverageResult:
    coverage_ratio: float
    occupied_cells: int
    total_cells: int
    uniformity: float
    counts: np.ndarray


def grid_coverage(points, image_shape, rows=8, cols=8):
    points = np.asarray(points, dtype=np.float32).reshape(-1, 2)

    height = int(image_shape[0])
    width = int(image_shape[1])

    counts = np.zeros((rows, cols), dtype=np.int32)

    if len(points) == 0:
        return CoverageResult(
            0.0, 0, rows * cols, 0.0, counts
        )

    x = np.clip(points[:, 0], 0, width - 1)
    y = np.clip(points[:, 1], 0, height - 1)

    col = np.minimum(
        (x / width * cols).astype(int),
        cols - 1
    )

    row = np.minimum(
        (y / height * rows).astype(int),
        rows - 1
    )

    np.add.at(counts, (row, col), 1)

    occupied = int(np.count_nonzero(counts))
    coverage_ratio = occupied / float(rows * cols)

    nonzero = counts[counts > 0].astype(np.float32)

    if len(nonzero) <= 1:
        uniformity = 1.0 if len(nonzero) == 1 else 0.0
    else:
        uniformity = float(
            1.0 / (
                1.0 +
                np.std(nonzero) /
                (np.mean(nonzero) + 1e-6)
            )
        )

    return CoverageResult(
        coverage_ratio,
        occupied,
        rows * cols,
        uniformity,
        counts
    )


def select_spatially_distributed(
    points,
    scores=None,
    target_count=150,
    rows=8,
    cols=8,
):
    points = np.asarray(
        points,
        dtype=np.float32
    ).reshape(-1, 2)

    n = len(points)

    if n <= target_count:
        return np.arange(
            n,
            dtype=np.int64
        )

    if scores is None:
        scores = np.ones(
            n,
            dtype=np.float32
        )
    else:
        scores = np.asarray(
            scores,
            dtype=np.float32
        )

    xmin, ymin = points.min(axis=0)
    xmax, ymax = points.max(axis=0)

    span = np.maximum(
        [xmax - xmin, ymax - ymin],
        1e-6
    )

    cell = np.floor(
        (points - [xmin, ymin])
        / span
        * [cols - 1e-6, rows - 1e-6]
    ).astype(int)

    cell[:, 0] = np.clip(
        cell[:, 0],
        0,
        cols - 1
    )

    cell[:, 1] = np.clip(
        cell[:, 1],
        0,
        rows - 1
    )

    order = np.argsort(-scores)

    quota = max(
        1,
        int(np.ceil(
            target_count /
            float(rows * cols)
        ))
    )

    chosen = []
    used = {}

    for index in order:
        key = (
            int(cell[index, 1]),
            int(cell[index, 0])
        )

        if used.get(key, 0) < quota:
            chosen.append(int(index))
            used[key] = used.get(key, 0) + 1

            if len(chosen) == target_count:
                break

    if len(chosen) < target_count:
        selected = set(chosen)

        for index in order:
            index = int(index)

            if index not in selected:
                chosen.append(index)

                if len(chosen) == target_count:
                    break

    return np.asarray(
        chosen,
        dtype=np.int64
    )
