import numpy as np

from parallex.spatial.coverage import grid_coverage, select_spatially_distributed
from parallex.validation.quality import quality_decision


def test_coverage():
    points = np.array([
        [10, 10],
        [90, 10],
        [10, 90],
        [90, 90],
    ], dtype=np.float32)

    result = grid_coverage(points, (100, 100), rows=2, cols=2)

    assert result.coverage_ratio == 1.0


def test_selection():
    rng = np.random.default_rng(0)
    points = rng.random((300, 2)) * 100

    indices = select_spatially_distributed(
        points,
        target_count=50
    )

    assert len(indices) == 50
    assert len(np.unique(indices)) == 50


def test_quality_reject():
    result = quality_decision(
        rmse_px=5,
        inlier_count=3,
        inlier_ratio=0.1,
        coverage_ratio=0.1,
        uniformity=0.1
    )

    assert result.label == "REJECT"
