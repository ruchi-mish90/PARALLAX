from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parallex.io.pds4_image import open_pds4_image
from parallex.pds4.metadata import extract_metadata


@dataclass(frozen=True)
class ProductCapabilities:
    """Capabilities exposed by a PARALLAX product."""

    window_read: bool = True
    full_read: bool = False
    multispectral: bool = False
    geometry: bool = False
    metadata: bool = True


class Product:
    """
    Generic PARALLAX product abstraction.

    This wraps the existing PDS4 metadata and image readers so that
    downstream registration code does not need to know whether the
    product is OHRC, TMC2, IIRS, or another supported PDS4 product.
    """

    def __init__(self, product_dir):
        self.product_dir = Path(product_dir)

        if not self.product_dir.exists():
            raise FileNotFoundError(
                f"Product directory not found: {self.product_dir}"
            )

        self.metadata = extract_metadata(self.product_dir)
        self.sensor = self.metadata.get("sensor", "UNKNOWN")

        self._reader = None

        self.capabilities = ProductCapabilities(
            window_read=True,
            full_read=False,
            multispectral=self.sensor == "IIRS",
            geometry=bool(self.metadata.get("geometry_files")),
            metadata=True,
        )

    @property
    def product_id(self):
        return self.metadata.get("product_id")

    @property
    def shape(self):
        if self._reader is None:
            self._reader = open_pds4_image(self.product_dir)

        return self._reader.shape

    @property
    def dtype(self):
        if self._reader is None:
            self._reader = open_pds4_image(self.product_dir)

        return self._reader.dtype

    @property
    def is_multispectral(self):
        return self.capabilities.multispectral

    def reader(self):
        """Return the existing memory-mapped image reader."""
        if self._reader is None:
            self._reader = open_pds4_image(self.product_dir)

        return self._reader

    def read_window(
        self,
        row,
        col,
        height,
        width,
        band=None,
        copy=True,
    ):
        """
        Read a bounded image window.

        For IIRS, band is required.
        For 2-D products, band must be omitted.
        """
        reader = self.reader()

        if self.is_multispectral:
            if band is None:
                raise ValueError(
                    "band is required for multispectral products"
                )

            return reader.read_band_window(
                band=band,
                row=row,
                col=col,
                height=height,
                width=width,
                copy=copy,
            )

        if band is not None:
            raise ValueError(
                "band is only valid for multispectral products"
            )

        return reader.read_window(
            row=row,
            col=col,
            height=height,
            width=width,
            copy=copy,
        )

    def read_band(self, band, copy=True):
        """Read a complete IIRS band."""
        if not self.is_multispectral:
            raise ValueError(
                "read_band() is only valid for multispectral products"
            )

        return self.reader().read_band(
            band=band,
            copy=copy,
        )

    def close(self):
        if self._reader is not None:
            self._reader.close()
            self._reader = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def summary(self) -> dict[str, Any]:
        """Return a JSON-friendly product summary."""
        return {
            "product_id": self.product_id,
            "sensor": self.sensor,
            "shape": tuple(self.shape),
            "dtype": str(self.dtype),
            "multispectral": self.is_multispectral,
            "capabilities": {
                "window_read": self.capabilities.window_read,
                "full_read": self.capabilities.full_read,
                "multispectral": self.capabilities.multispectral,
                "geometry": self.capabilities.geometry,
                "metadata": self.capabilities.metadata,
            },
        }
