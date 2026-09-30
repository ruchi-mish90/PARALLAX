from dataclasses import dataclass
from pathlib import Path

from .geometry import GeometryGrid, geometry_bounds, load_geometry


@dataclass
class SpatialOverlapResult:
    overlaps: bool
    latitude_min: float | None
    latitude_max: float | None
    longitude_intervals: list[tuple[float, float]]
    reason: str


def _normalize_lon(lon):
    """Normalize longitude to [0, 360)."""
    return lon % 360.0


def _longitude_intervals(grid):
    """
    Estimate longitude coverage as circular intervals.

    Returns intervals in [0, 360), allowing at most two intervals
    when the footprint crosses the 0/360 boundary.
    """
    lon = grid.longitude.ravel()

    # Convert to [-180, 180) for detecting circular coverage.
    signed = ((lon + 180.0) % 360.0) - 180.0

    lo = float(signed.min())
    hi = float(signed.max())

    # If the footprint is compact in signed longitude,
    # convert it back to [0,360).
    if hi - lo < 180.0:
        a = _normalize_lon(lo)
        b = _normalize_lon(hi)

        if a <= b:
            return [(a, b)]

        return [(a, 360.0), (0.0, b)]

    # Wide longitude coverage is ambiguous for a simple bounding interval.
    # In that case, use the native 0-360 range conservatively.
    native_lo = float(lon.min())
    native_hi = float(lon.max())

    if native_hi - native_lo < 180.0:
        return [(native_lo, native_hi)]

    return [(0.0, 360.0)]


def _interval_intersection(a, b):
    """Return intersection of two ordinary longitude intervals."""
    lo = max(a[0], b[0])
    hi = min(a[1], b[1])

    if lo > hi:
        return None

    return lo, hi


def spatial_co_location(
    grid_a: GeometryGrid,
    grid_b: GeometryGrid,
):
    """
    Perform a conservative geographic co-location test.

    This is a fast gate, not the final pixel-accurate ROI solver.
    """
    bounds_a = geometry_bounds(grid_a)
    bounds_b = geometry_bounds(grid_b)

    # Latitude intersection.
    lat_min = max(
        bounds_a["latitude_min"],
        bounds_b["latitude_min"],
    )

    lat_max = min(
        bounds_a["latitude_max"],
        bounds_b["latitude_max"],
    )

    if lat_min > lat_max:
        return SpatialOverlapResult(
            overlaps=False,
            latitude_min=None,
            latitude_max=None,
            longitude_intervals=[],
            reason=(
                "No latitude overlap between the two geometry footprints"
            ),
        )

    intervals_a = _longitude_intervals(grid_a)
    intervals_b = _longitude_intervals(grid_b)

    intersections = []

    for interval_a in intervals_a:
        for interval_b in intervals_b:
            intersection = _interval_intersection(
                interval_a,
                interval_b,
            )

            if intersection is not None:
                intersections.append(intersection)

    if not intersections:
        return SpatialOverlapResult(
            overlaps=False,
            latitude_min=None,
            latitude_max=None,
            longitude_intervals=[],
            reason=(
                "Latitude overlaps, but longitude footprints do not overlap"
            ),
        )

    return SpatialOverlapResult(
        overlaps=True,
        latitude_min=lat_min,
        latitude_max=lat_max,
        longitude_intervals=intersections,
        reason="Geographic footprints overlap",
    )


def spatial_co_location_from_csv(
    geometry_a_csv,
    geometry_b_csv,
):
    """Load two geometry CSVs and perform the co-location gate."""
    grid_a = load_geometry(Path(geometry_a_csv))
    grid_b = load_geometry(Path(geometry_b_csv))

    return spatial_co_location(grid_a, grid_b)
