import numpy as np

from parallex.matching.base import MatchResult


def spatial_coverage(
    result: MatchResult,
    image_shape,
    grid_rows: int = 4,
    grid_cols: int = 4,
):
    """
    Measure spatial distribution of verified correspondences.

    Coverage is computed from RANSAC inliers only.

    Returns a dictionary containing:
      - occupied_cells
      - total_cells
      - occupied_ratio
      - bbox_ratio
      - coverage_score

    This is a distribution diagnostic, not a guarantee of uniformity.
    """

    if result.inlier_mask is None:
        raise ValueError(
            "spatial_coverage requires an inlier_mask"
        )

    if result.num_matches == 0:
        return {
            "occupied_cells": 0,
            "total_cells": grid_rows * grid_cols,
            "occupied_ratio": 0.0,
            "bbox_ratio": 0.0,
            "coverage_score": 0.0,
        }

    inlier_mask = np.asarray(
        result.inlier_mask,
        dtype=bool,
    )

    matches = result.matches[inlier_mask]

    if len(matches) == 0:
        return {
            "occupied_cells": 0,
            "total_cells": grid_rows * grid_cols,
            "occupied_ratio": 0.0,
            "bbox_ratio": 0.0,
            "coverage_score": 0.0,
        }

    height, width = image_shape[:2]

    points = np.asarray(
        result.keypoints_a[matches[:, 0]],
        dtype=np.float32,
    )

    x = np.clip(
        points[:, 0],
        0,
        max(width - 1, 0),
    )

    y = np.clip(
        points[:, 1],
        0,
        max(height - 1, 0),
    )

    cell_x = np.minimum(
        (x / width * grid_cols).astype(int),
        grid_cols - 1,
    )

    cell_y = np.minimum(
        (y / height * grid_rows).astype(int),
        grid_rows - 1,
    )

    occupied = set(
        zip(
            cell_y.tolist(),
            cell_x.tolist(),
        )
    )

    total_cells = grid_rows * grid_cols
    occupied_cells = len(occupied)

    occupied_ratio = (
        occupied_cells / total_cells
    )

    x_range = float(x.max() - x.min())
    y_range = float(y.max() - y.min())

    bbox_ratio = (
        (x_range / width) *
        (y_range / height)
    )

    # Conservative combined diagnostic score.
    coverage_score = float(
        0.5 * occupied_ratio +
        0.5 * bbox_ratio
    )

    return {
        "occupied_cells": occupied_cells,
        "total_cells": total_cells,
        "occupied_ratio": float(occupied_ratio),
        "bbox_ratio": float(bbox_ratio),
        "coverage_score": coverage_score,
    }


def add_spatial_coverage(
    result: MatchResult,
    image_shape,
    grid_rows: int = 4,
    grid_cols: int = 4,
):
    """
    Calculate spatial coverage and attach it to MatchResult.metadata.
    """

    coverage = spatial_coverage(
        result,
        image_shape,
        grid_rows=grid_rows,
        grid_cols=grid_cols,
    )

    result.metadata["spatial_coverage"] = coverage

    return result
