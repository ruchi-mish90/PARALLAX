from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class MatchResult:
    """
    Standard output shared by every PARALLAX matcher.
    """

    keypoints_a: np.ndarray = field(
        default_factory=lambda: np.empty((0, 2), dtype=np.float32)
    )

    keypoints_b: np.ndarray = field(
        default_factory=lambda: np.empty((0, 2), dtype=np.float32)
    )

    matches: np.ndarray = field(
        default_factory=lambda: np.empty((0, 2), dtype=np.int32)
    )

    scores: np.ndarray = field(
        default_factory=lambda: np.empty((0,), dtype=np.float32)
    )

    inlier_mask: Optional[np.ndarray] = None

    model_name: str = ""

    runtime_ms: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def num_keypoints_a(self):
        return len(self.keypoints_a)

    @property
    def num_keypoints_b(self):
        return len(self.keypoints_b)

    @property
    def num_matches(self):
        return len(self.matches)

    @property
    def num_inliers(self):
        if self.inlier_mask is None:
            return 0

        return int(np.count_nonzero(self.inlier_mask))

    @property
    def inlier_ratio(self):
        if self.num_matches == 0:
            return 0.0

        return self.num_inliers / self.num_matches


class Matcher(ABC):
    """
    Common interface for all PARALLAX correspondence engines.
    """

    name = "base"

    @abstractmethod
    def match(self, image_a, image_b) -> MatchResult:
        """
        Compute correspondences between two image windows.
        """
        raise NotImplementedError
