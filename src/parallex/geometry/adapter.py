from dataclasses import dataclass
from pathlib import Path

import numpy as np

from parallex.overlap.geometry import (
    GeometryGrid,
    geometry_bounds,
    geo_to_pixel,
    load_geometry,
    overlap_tiles,
    pixel_to_geo,
)


@dataclass(frozen=True)
class GeometryInfo:
    """Summary of a product geometry grid."""

    path: str
    rows: int
    columns: int
    valid_ratio: float


class GeometryAdapter:
    """
    Generic geometry interface for a PARALLAX Product.

    Uses the existing overlap.geometry implementation and adds
    product-level discovery and a stable interface.
    """

    def __init__(self, product):
        self.product = product
        self.grid = self._load_product_geometry()

    def _find_geometry_file(self):
        files = [
            Path(p)
            for p in self.product.metadata.get(
                "geometry_files",
                [],
            )
        ]

        csv_files = [
            p for p in files
            if p.suffix.lower() == ".csv"
        ]

        if not csv_files:
            raise FileNotFoundError(
                f"No geometry CSV found for product "
                f"{self.product.product_id}"
            )

        # Prefer files whose name indicates ground-referenced geometry.
        preferred = [
            p for p in csv_files
            if "_g_" in p.name.lower()
            or "geometry" in p.name.lower()
        ]

        return preferred[0] if preferred else csv_files[0]

    def _load_product_geometry(self):
        path = self._find_geometry_file()
        return load_geometry(path)

    @property
    def path(self):
        return self._find_geometry_file()

    @property
    def shape(self):
        return self.grid.latitude.shape

    @property
    def scan_values(self):
        return self.grid.scan_values

    @property
    def pixel_values(self):
        return self.grid.pixel_values

    @property
    def valid_ratio(self):
        total = self.grid.latitude.size

        if total == 0:
            return 0.0

        valid = np.isfinite(self.grid.latitude) & np.isfinite(
            self.grid.longitude
        )

        return float(np.count_nonzero(valid) / total)

    def info(self):
        return GeometryInfo(
            path=str(self.path),
            rows=int(self.shape[0]),
            columns=int(self.shape[1]),
            valid_ratio=self.valid_ratio,
        )

    def bounds(self):
        return geometry_bounds(self.grid)

    def geo_to_pixel(self, latitude, longitude):
        return geo_to_pixel(
            self.grid,
            latitude,
            longitude,
        )

    def pixel_to_geo(self, scan, pixel):
        return pixel_to_geo(
            self.grid,
            scan,
            pixel,
        )

    def overlap_tiles(
        self,
        other,
        latitude_min,
        latitude_max,
        longitude_intervals,
        tile_size=2048,
        samples_lat=6,
        samples_lon=6,
    ):
        return overlap_tiles(
            self.grid,
            other.grid,
            latitude_min,
            latitude_max,
            longitude_intervals,
            tile_size=tile_size,
            samples_lat=samples_lat,
            samples_lon=samples_lon,
        )

    def summary(self):
        info = self.info()
        bounds = self.bounds()

        return {
            "path": info.path,
            "shape": (info.rows, info.columns),
            "valid_ratio": info.valid_ratio,
            "bounds": bounds,
        }
