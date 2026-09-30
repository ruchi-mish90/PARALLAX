from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ROI:
    y0: int
    y1: int
    x0: int
    x1: int

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def area(self) -> int:
        return self.height * self.width

    def clamp(self, shape: Tuple[int, int]) -> "ROI":
        h, w = shape
        return ROI(
            max(0, min(self.y0, h)),
            max(0, min(self.y1, h)),
            max(0, min(self.x0, w)),
            max(0, min(self.x1, w)),
        )


def sensor_aware_roi(
    shape: Tuple[int, int],
    sensor: str,
    margin_ratio: float = 0.05,
) -> ROI:
    """
    Select a computation-friendly ROI while preserving the useful
    central imaging region of the sensor.

    This is intentionally conservative: geometry-based overlap should
    determine the true common region before registration.
    """
    h, w = shape
    sensor = sensor.upper()

    margin_y = int(h * margin_ratio)
    margin_x = int(w * margin_ratio)

    if sensor == "OHRC":
        # OHRC is very high resolution; retain the central region
        # to avoid unnecessary full-frame matching.
        return ROI(
            margin_y,
            h - margin_y,
            margin_x,
            w - margin_x,
        ).clamp(shape)

    if sensor == "TMC2":
        # TMC-2 is a long push-broom image. Preserve the full scan
        # direction while trimming only the sample edges.
        return ROI(
            0,
            h,
            margin_x,
            w - margin_x,
        ).clamp(shape)

    if sensor == "IIRS":
        return ROI(
            margin_y,
            h - margin_y,
            margin_x,
            w - margin_x,
        ).clamp(shape)

    return ROI(
        margin_y,
        h - margin_y,
        margin_x,
        w - margin_x,
    ).clamp(shape)


def crop(image, roi: ROI):
    return image[roi.y0:roi.y1, roi.x0:roi.x1]
from typing import Optional


def intersect_rois(roi_a: ROI, roi_b: ROI) -> Optional[ROI]:
    """
    Return the intersection of two image-space ROIs.

    The ROIs must belong to the same image coordinate system.
    """
    y0 = max(roi_a.y0, roi_b.y0)
    y1 = min(roi_a.y1, roi_b.y1)
    x0 = max(roi_a.x0, roi_b.x0)
    x1 = min(roi_a.x1, roi_b.x1)

    if y1 <= y0 or x1 <= x0:
        return None

    return ROI(y0, y1, x0, x1)


def memory_safe_window(
    image_reader,
    roi: ROI,
    *,
    max_height: int = 2048,
    max_width: int = 2048,
):
    """
    Read a bounded image window from a PDS4 memmap-backed reader.

    The returned array is limited to max_height x max_width.
    """
    h = min(roi.height, max_height)
    w = min(roi.width, max_width)

    if h <= 0 or w <= 0:
        raise ValueError("ROI has no valid area.")

    return image_reader.read_window(
        roi.y0,
        roi.x0,
        h,
        w,
    )
