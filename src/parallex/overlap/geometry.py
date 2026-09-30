from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


@dataclass
class GeometryGrid:
    longitude: np.ndarray
    latitude: np.ndarray
    scan_values: np.ndarray
    pixel_values: np.ndarray


def load_geometry(csv_path):
    csv_path = Path(csv_path)

    rows = np.genfromtxt(
        csv_path,
        delimiter=",",
        names=True,
        dtype=float,
        encoding="utf-8",
    )

    longitude = np.asarray(rows["Longitude"], dtype=float)
    latitude = np.asarray(rows["Latitude"], dtype=float)
    pixel = np.asarray(rows["Pixel"], dtype=float)
    scan = np.asarray(rows["Scan"], dtype=float)

    valid = (
        np.isfinite(longitude)
        & np.isfinite(latitude)
        & np.isfinite(pixel)
        & np.isfinite(scan)
    )

    longitude = longitude[valid]
    latitude = latitude[valid]
    pixel = pixel[valid]
    scan = scan[valid]

    scan_unique = np.unique(scan)
    pixel_unique = np.unique(pixel)

    longitude_grid = np.full(
        (len(scan_unique), len(pixel_unique)),
        np.nan,
        dtype=float,
    )

    latitude_grid = np.full(
        (len(scan_unique), len(pixel_unique)),
        np.nan,
        dtype=float,
    )

    scan_index = {
        value: i
        for i, value in enumerate(scan_unique)
    }

    pixel_index = {
        value: i
        for i, value in enumerate(pixel_unique)
    }

    for lon, lat, px, sc in zip(
        longitude,
        latitude,
        pixel,
        scan,
    ):
        i = scan_index[sc]
        j = pixel_index[px]

        longitude_grid[i, j] = lon % 360.0
        latitude_grid[i, j] = lat

    grid = GeometryGrid(
        longitude=longitude_grid,
        latitude=latitude_grid,
        scan_values=scan_unique,
        pixel_values=pixel_unique,
    )

    validate_geometry(grid)

    return grid


def validate_geometry(grid):
    if grid.latitude.ndim != 2:
        raise ValueError(
            f"Latitude grid must be 2D, got {grid.latitude.shape}"
        )

    if grid.longitude.ndim != 2:
        raise ValueError(
            f"Longitude grid must be 2D, got {grid.longitude.shape}"
        )

    if grid.longitude.shape != grid.latitude.shape:
        raise ValueError(
            "Longitude and latitude grids have different shapes."
        )

    if len(grid.scan_values) == 0:
        raise ValueError("No scan coordinates found.")

    if len(grid.pixel_values) == 0:
        raise ValueError("No pixel coordinates found.")

    if not np.isfinite(grid.latitude).any():
        raise ValueError("Geometry contains no valid latitude values.")

    if not np.isfinite(grid.longitude).any():
        raise ValueError("Geometry contains no valid longitude values.")

    return True


def _normalize_lon(lon):
    return float(lon) % 360.0


def _longitude_distance(lon_a, lon_b):
    difference = np.abs(
        np.asarray(lon_a, dtype=float)
        - np.asarray(lon_b, dtype=float)
    )

    return np.minimum(
        difference,
        360.0 - difference,
    )


def _geo_distance_sq(
    lat_a,
    lon_a,
    lat_b,
    lon_b,
):
    dlat = (
        np.asarray(lat_a, dtype=float)
        - float(lat_b)
    )

    dlon = _longitude_distance(
        lon_a,
        float(lon_b),
    )

    return dlat * dlat + dlon * dlon


def _bilinear_geo(grid, scan, pixel):
    """Evaluate latitude/longitude at fractional scan/pixel coordinates."""
    scans = grid.scan_values
    pixels = grid.pixel_values

    if scan < scans[0] or scan > scans[-1]:
        raise ValueError("scan outside geometry extent")
    if pixel < pixels[0] or pixel > pixels[-1]:
        raise ValueError("pixel outside geometry extent")

    i1 = int(np.searchsorted(scans, scan, side="right"))
    j1 = int(np.searchsorted(pixels, pixel, side="right"))

    i1 = min(max(i1, 1), len(scans) - 1)
    j1 = min(max(j1, 1), len(pixels) - 1)

    i0 = i1 - 1
    j0 = j1 - 1

    s0, s1 = scans[i0], scans[i1]
    p0, p1 = pixels[j0], pixels[j1]

    if s1 == s0:
        a = 0.0
    else:
        a = (scan - s0) / (s1 - s0)

    if p1 == p0:
        b = 0.0
    else:
        b = (pixel - p0) / (p1 - p0)

    lat_block = grid.latitude[i0:i1 + 1, j0:j1 + 1]
    lon_block = grid.longitude[i0:i1 + 1, j0:j1 + 1]

    block = np.array([
        lat_block[0, 0],
        lat_block[0, 1],
        lat_block[1, 0],
        lat_block[1, 1],
        lon_block[0, 0],
        lon_block[0, 1],
        lon_block[1, 0],
        lon_block[1, 1],
    ], dtype=float)

    if not np.all(np.isfinite(block)):
        raise ValueError("geometry cell contains invalid values")

    lat = (
        (1-a)*(1-b)*lat_block[0, 0]
        + (1-a)*b*lat_block[0, 1]
        + a*(1-b)*lat_block[1, 0]
        + a*b*lat_block[1, 1]
    )

    # Geometry longitude is stored in [0,360).  Unwrap the local
    # four-corner cell around its first corner before interpolation.
    lons = lon_block.copy()
    ref = lons[0, 0]
    lons = ref + ((lons - ref + 180.0) % 360.0 - 180.0)

    lon = (
        (1-a)*(1-b)*lons[0, 0]
        + (1-a)*b*lons[0, 1]
        + a*(1-b)*lons[1, 0]
        + a*b*lons[1, 1]
    )

    return float(lat), float(lon % 360.0)


def _geo_error(target_lat, target_lon, pred_lat, pred_lon):
    """Latitude/longitude residual with circular longitude handling."""
    dlat = pred_lat - target_lat
    dlon = (pred_lon - target_lon + 180.0) % 360.0 - 180.0
    return np.array([dlat, dlon], dtype=float)


def geo_to_pixel(grid, latitude, longitude):
    """
    Continuous geographic -> image-coordinate inversion.

    Uses the nearest valid geometry sample only as an initial estimate,
    then performs bounded local least-squares inversion against the
    bilinearly interpolated geometry surface.
    """
    validate_geometry(grid)

    target_lat = float(latitude)
    target_lon = float(_normalize_lon(longitude))

    finite = np.isfinite(grid.latitude) & np.isfinite(grid.longitude)

    if not finite.any():
        raise ValueError(
            "geometry grid contains no valid geographic samples"
        )

    dlat = grid.latitude - target_lat
    dlon = (
        grid.longitude - target_lon + 180.0
    ) % 360.0 - 180.0

    distance = dlat * dlat + dlon * dlon
    distance = np.where(finite, distance, np.inf)

    idx = np.unravel_index(
        int(np.argmin(distance)),
        distance.shape,
    )

    x0 = np.array([
        float(grid.scan_values[idx[0]]),
        float(grid.pixel_values[idx[1]]),
    ])

    lower = np.array([
        float(grid.scan_values[0]),
        float(grid.pixel_values[0]),
    ])

    upper = np.array([
        float(grid.scan_values[-1]),
        float(grid.pixel_values[-1]),
    ])

    def residual(x):
        scan, pixel = x

        # Find surrounding geometry cell.
        i1 = int(np.searchsorted(
            grid.scan_values,
            scan,
            side="right",
        ))

        j1 = int(np.searchsorted(
            grid.pixel_values,
            pixel,
            side="right",
        ))

        i1 = min(
            max(i1, 1),
            len(grid.scan_values) - 1,
        )

        j1 = min(
            max(j1, 1),
            len(grid.pixel_values) - 1,
        )

        i0 = i1 - 1
        j0 = j1 - 1

        s0 = grid.scan_values[i0]
        s1 = grid.scan_values[i1]

        p0 = grid.pixel_values[j0]
        p1 = grid.pixel_values[j1]

        a = 0.0 if s1 == s0 else (
            scan - s0
        ) / (s1 - s0)

        b = 0.0 if p1 == p0 else (
            pixel - p0
        ) / (p1 - p0)

        lat_block = grid.latitude[
            i0:i1 + 1,
            j0:j1 + 1,
        ]

        lon_block = grid.longitude[
            i0:i1 + 1,
            j0:j1 + 1,
        ]

        if not (
            np.all(np.isfinite(lat_block))
            and np.all(np.isfinite(lon_block))
        ):
            return np.array([1e3, 1e3])

        lat = (
            (1-a)*(1-b)*lat_block[0, 0]
            + (1-a)*b*lat_block[0, 1]
            + a*(1-b)*lat_block[1, 0]
            + a*b*lat_block[1, 1]
        )

        # Local longitude unwrapping.
        ref = lon_block[0, 0]

        lons = ref + (
            (lon_block - ref + 180.0)
            % 360.0 - 180.0
        )

        lon = (
            (1-a)*(1-b)*lons[0, 0]
            + (1-a)*b*lons[0, 1]
            + a*(1-b)*lons[1, 0]
            + a*b*lons[1, 1]
        )

        dlat = lat - target_lat

        dlon = (
            lon - target_lon + 180.0
        ) % 360.0 - 180.0

        return np.array([
            float(dlat),
            float(dlon),
        ])

    try:
        from scipy.optimize import least_squares

        result = least_squares(
            residual,
            x0,
            bounds=(lower, upper),
            method="trf",
            max_nfev=40,
            xtol=1e-10,
            ftol=1e-10,
            gtol=1e-10,
        )

    except Exception as exc:
        raise ValueError(
            f"geo_to_pixel inversion failed: {exc}"
        )

    if not result.success:
        raise ValueError(
            f"geo_to_pixel inversion failed: "
            f"{result.message}"
        )

    scan, pixel = map(
        float,
        result.x,
    )

    error = residual(
        np.array([scan, pixel])
    )

    if np.linalg.norm(error) > 0.01:
        raise ValueError(
            "geo_to_pixel inversion residual too large: "
            f"{np.linalg.norm(error):.6f} degrees"
        )

    return scan, pixel

def pixel_to_geo(
    grid,
    scan,
    pixel,
):
    """
    Convert image scan/pixel coordinates to the nearest
    geometry-grid latitude/longitude.
    """

    validate_geometry(grid)

    scan = float(scan)
    pixel = float(pixel)

    scan_distance = (
        grid.scan_values[:, None] - scan
    ) ** 2

    pixel_distance = (
        grid.pixel_values[None, :] - pixel
    ) ** 2

    distances = (
        scan_distance
        + pixel_distance
    )

    index = np.unravel_index(
        int(np.argmin(distances)),
        distances.shape,
    )

    i, j = index

    return (
        float(grid.latitude[i, j]),
        float(grid.longitude[i, j]) % 360.0,
    )


def geometry_bounds(grid):
    """
    Return conservative geographic bounds.

    The return value is a dictionary because spatial.py accesses
    the bounds using named keys.
    """

    validate_geometry(grid)

    valid_lat = grid.latitude[
        np.isfinite(grid.latitude)
    ]

    valid_lon = grid.longitude[
        np.isfinite(grid.longitude)
    ]

    return {
        "latitude_min": float(np.min(valid_lat)),
        "latitude_max": float(np.max(valid_lat)),
        "longitude_min": float(np.min(valid_lon)),
        "longitude_max": float(np.max(valid_lon)),
    }


def _safe_roi(
    scan,
    pixel,
    image_shape,
    tile_size,
):
    height, width = image_shape[:2]

    tile_height = min(
        int(tile_size),
        int(height),
    )

    tile_width = min(
        int(tile_size),
        int(width),
    )

    center_y = int(round(scan))
    center_x = int(round(pixel))

    y0 = center_y - tile_height // 2
    x0 = center_x - tile_width // 2

    y0 = max(
        0,
        min(
            y0,
            height - tile_height,
        ),
    )

    x0 = max(
        0,
        min(
            x0,
            width - tile_width,
        ),
    )

    return (
        int(y0),
        int(y0 + tile_height),
        int(x0),
        int(x0 + tile_width),
    )


def overlap_tiles(
    grid_a,
    grid_b,
    latitude_min,
    latitude_max,
    longitude_intervals,
    tile_size=2048,
    samples_lat=6,
    samples_lon=6,
):
    """
    Generate paired ROIs around identical geographic anchors.

    The same geographic anchor is independently projected into
    both images before constructing the corresponding ROI.
    """

    validate_geometry(grid_a)
    validate_geometry(grid_b)

    lat_min = max(
        float(latitude_min),
        float(np.nanmin(grid_a.latitude)),
        float(np.nanmin(grid_b.latitude)),
    )

    lat_max = min(
        float(latitude_max),
        float(np.nanmax(grid_a.latitude)),
        float(np.nanmax(grid_b.latitude)),
    )

    if lat_min > lat_max:
        return []

    lat_samples = np.linspace(
        lat_min,
        lat_max,
        int(samples_lat),
    )

    lon_samples = []

    for start, end in longitude_intervals:

        start = float(start) % 360.0
        end = float(end) % 360.0

        if end < start:
            end += 360.0

        values = np.linspace(
            start,
            end,
            int(samples_lon),
        )

        lon_samples.extend(
            [
                float(value % 360.0)
                for value in values
            ]
        )

    height_a = int(
        np.nanmax(grid_a.scan_values)
    ) + 1

    width_a = int(
        np.nanmax(grid_a.pixel_values)
    ) + 1

    height_b = int(
        np.nanmax(grid_b.scan_values)
    ) + 1

    width_b = int(
        np.nanmax(grid_b.pixel_values)
    ) + 1

    class ROI:
        def __init__(
            self,
            y0,
            y1,
            x0,
            x1,
        ):
            self.y0 = int(y0)
            self.y1 = int(y1)
            self.x0 = int(x0)
            self.x1 = int(x1)

        @property
        def height(self):
            return self.y1 - self.y0

        @property
        def width(self):
            return self.x1 - self.x0

    tiles = []
    seen = set()

    for latitude in lat_samples:

        for longitude in lon_samples:

            scan_a, pixel_a = geo_to_pixel(
                grid_a,
                latitude,
                longitude,
            )

            scan_b, pixel_b = geo_to_pixel(
                grid_b,
                latitude,
                longitude,
            )

            roi_a_tuple = _safe_roi(
                scan_a,
                pixel_a,
                (height_a, width_a),
                tile_size,
            )

            roi_b_tuple = _safe_roi(
                scan_b,
                pixel_b,
                (height_b, width_b),
                tile_size,
            )

            key = (
                roi_a_tuple,
                roi_b_tuple,
            )

            if key in seen:
                continue

            seen.add(key)

            roi_a = ROI(*roi_a_tuple)
            roi_b = ROI(*roi_b_tuple)

            tiles.append(
                (
                    roi_a,
                    roi_b,
                    float(latitude),
                    float(longitude),
                )
            )

    return tiles
