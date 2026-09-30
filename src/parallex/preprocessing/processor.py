from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class PreprocessingConfig:
    """Configuration for generic PARALLAX image preprocessing."""

    representation: str = "native"
    band: Optional[int] = None
    clip_percentiles: tuple[float, float] = (1.0, 99.0)
    normalize: bool = True
    gradient_sigma: float = 1.0


@dataclass
class PreprocessingResult:
    """2-D representation produced for registration."""

    image: np.ndarray
    representation: str
    sensor: str
    metadata: dict


class Preprocessor:
    """
    Generic, window-aware preprocessing interface.

    Full-image processing remains available through run(), while
    run_window() keeps large products tile/window based.
    """

    def __init__(self, product, config=None):
        self.product = product
        self.config = config or PreprocessingConfig()

    def run(self):
        """Process the complete product.

        Intended for small products or explicit full-image workflows.
        Large-image registration should use run_window().
        """
        h, w = self._spatial_shape()

        return self.run_window(
            row=0,
            col=0,
            height=h,
            width=w,
        )

    def run_window(self, row, col, height, width):
        """Process a spatial window without loading the full product."""
        if row < 0 or col < 0:
            raise ValueError("row and col must be non-negative")

        if height <= 0 or width <= 0:
            raise ValueError("height and width must be positive")

        h, w = self._spatial_shape()

        if row >= h or col >= w:
            raise ValueError(
                f"Window origin ({row}, {col}) is outside image "
                f"shape {(h, w)}"
            )

        height = min(height, h - row)
        width = min(width, w - col)

        sensor = self.product.sensor.upper()
        representation = self.config.representation.lower()

        if sensor == "IIRS":
            image = self._iirs_window(
                representation,
                row,
                col,
                height,
                width,
            )
        elif sensor in {"OHRC", "TMC2"}:
            image = self._panchromatic_window(
                representation,
                row,
                col,
                height,
                width,
            )
        else:
            raise ValueError(f"Unsupported sensor: {sensor}")

        image = np.asarray(image, dtype=np.float32)

        if image.ndim != 2:
            raise ValueError(
                f"Preprocessing must produce a 2-D image, got {image.shape}"
            )

        if self.config.normalize:
            image = self._normalize(image)

        return PreprocessingResult(
            image=image,
            representation=representation,
            sensor=sensor,
            metadata={
                "shape": tuple(image.shape),
                "dtype": str(image.dtype),
                "representation": representation,
                "row": row,
                "col": col,
                "height": height,
                "width": width,
            },
        )

    def _spatial_shape(self):
        shape = self.product.shape

        if self.product.sensor.upper() == "IIRS":
            return int(shape[1]), int(shape[2])

        return int(shape[0]), int(shape[1])

    def _panchromatic_window(
        self,
        representation,
        row,
        col,
        height,
        width,
    ):
        if representation not in {
            "native",
            "normalized",
            "gradient",
        }:
            raise ValueError(
                f"Representation '{representation}' is not valid for "
                f"{self.product.sensor}"
            )

        image = self.product.read_window(
            row,
            col,
            height,
            width,
        )

        if representation == "gradient":
            return self._gradient(image)

        return image

    def _iirs_window(
        self,
        representation,
        row,
        col,
        height,
        width,
    ):
        if representation in {"native", "band"}:
            if self.config.band is None:
                raise ValueError(
                    "IIRS band representation requires config.band"
                )

            return self.product.read_window(
                row,
                col,
                height,
                width,
                band=self.config.band,
            )

        if representation == "spectral_mean":
            return self._iirs_spectral_mean_window(
                row,
                col,
                height,
                width,
            )

        if representation == "spectral_gradient":
            image = self._iirs_spectral_mean_window(
                row,
                col,
                height,
                width,
            )
            return self._gradient(image)

        raise ValueError(
            f"Unsupported IIRS representation: {representation}"
        )

    def _iirs_spectral_mean_window(
        self,
        row,
        col,
        height,
        width,
    ):
        reader = self.product.reader()
        bands = int(self.product.shape[0])

        accum = np.zeros(
            (height, width),
            dtype=np.float64,
        )
        counts = np.zeros(
            (height, width),
            dtype=np.uint16,
        )

        for band in range(bands):
            data = np.asarray(
                reader.read_band_window(
                    band,
                    row,
                    col,
                    height,
                    width,
                ),
                dtype=np.float32,
            )

            finite = np.isfinite(data)

            if not np.any(finite):
                continue

            accum[finite] += data[finite]
            counts[finite] += 1

        output = np.zeros(
            (height, width),
            dtype=np.float32,
        )

        valid = counts > 0
        output[valid] = (
            accum[valid] / counts[valid]
        ).astype(np.float32)

        return output

    def _normalize(self, image):
        finite = np.isfinite(image)

        if not np.any(finite):
            raise ValueError("Image contains no finite pixels")

        values = image[finite]

        low, high = np.percentile(
            values,
            self.config.clip_percentiles,
        )

        if not np.isfinite(low) or not np.isfinite(high):
            raise ValueError("Invalid normalization percentiles")

        if high <= low:
            output = np.zeros_like(
                image,
                dtype=np.float32,
            )
        else:
            output = (
                (image - low) / (high - low)
            ).astype(np.float32)

            output = np.clip(
                output,
                0.0,
                1.0,
            )

        output[~finite] = 0.0

        return output

    def _gradient(self, image):
        image = np.asarray(
            image,
            dtype=np.float32,
        )

        finite = np.isfinite(image)

        if not np.any(finite):
            raise ValueError(
                "Cannot calculate gradient of empty image"
            )

        safe = image.copy()

        fill = float(
            np.nanmedian(safe)
        )

        safe[~finite] = fill

        gy, gx = np.gradient(safe)

        magnitude = np.hypot(
            gx,
            gy,
        )

        magnitude[~finite] = 0.0

        return magnitude.astype(np.float32)
