from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class ImageInfo:
    path: Path
    lines: int
    samples: int
    dtype: np.dtype
    byte_offset: int = 0

    @property
    def shape(self):
        return self.lines, self.samples


class RawImageReader:
    """
    Memory-mapped reader for large PDS4 raw/calibrated image files.

    Only requested windows are brought into memory.
    """

    def __init__(self, info: ImageInfo):
        self.info = info

        if not self.info.path.exists():
            raise FileNotFoundError(
                f"Image file not found: {self.info.path}"
            )

        self._data = np.memmap(
            self.info.path,
            dtype=self.info.dtype,
            mode="r",
            offset=self.info.byte_offset,
            shape=self.info.shape,
            order="C",
        )

    @property
    def shape(self):
        return self.info.shape

    @property
    def dtype(self):
        return self.info.dtype

    def read_window(self, row, col, height, width, copy=True):
        """
        Read a bounded image window.

        Parameters are zero-based pixel coordinates.
        """
        if row < 0 or col < 0:
            raise ValueError("row and col must be >= 0")

        if height <= 0 or width <= 0:
            raise ValueError("height and width must be > 0")

        row_end = min(row + height, self.info.lines)
        col_end = min(col + width, self.info.samples)

        if row >= self.info.lines or col >= self.info.samples:
            raise ValueError("Requested window starts outside the image")

        window = self._data[row:row_end, col:col_end]

        return np.array(window) if copy else window

    def close(self):
        mmap_obj = getattr(self._data, "_mmap", None)

        if mmap_obj is not None:
            mmap_obj.close()

        self._data = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def open_raw_image(
    path,
    lines,
    samples,
    dtype=np.uint16,
    byte_offset=0,
):
    """
    Open a raw PDS4 image using memory mapping.
    """
    info = ImageInfo(
        path=Path(path),
        lines=int(lines),
        samples=int(samples),
        dtype=np.dtype(dtype),
        byte_offset=int(byte_offset),
    )

    return RawImageReader(info)

@dataclass
class IIRSCubeInfo:
    path: Path
    bands: int
    lines: int
    samples: int
    dtype: np.dtype
    byte_offset: int = 0

    @property
    def shape(self):
        return self.bands, self.lines, self.samples


class IIRSCubeReader:
    """
    Memory-mapped reader for a 3-D IIRS PDS4 QUBE.

    Shape:
        BAND x LINE x SAMPLE
    """

    def __init__(self, info: IIRSCubeInfo):
        self.info = info

        if not self.info.path.exists():
            raise FileNotFoundError(
                f"IIRS QUBE not found: {self.info.path}"
            )

        self._data = np.memmap(
            self.info.path,
            dtype=self.info.dtype,
            mode="r",
            offset=self.info.byte_offset,
            shape=self.info.shape,
            order="C",
        )

    @property
    def shape(self):
        return self.info.shape

    @property
    def dtype(self):
        return self.info.dtype

    def read_band(self, band, copy=True):
        if band < 0 or band >= self.info.bands:
            raise ValueError(
                f"Band must be between 0 and {self.info.bands - 1}"
            )

        data = self._data[band, :, :]

        return np.array(data) if copy else data

    def read_band_window(
        self,
        band,
        row,
        col,
        height,
        width,
        copy=True,
    ):
        if band < 0 or band >= self.info.bands:
            raise ValueError("Invalid band")

        if row < 0 or col < 0:
            raise ValueError("row and col must be >= 0")

        row_end = min(row + height, self.info.lines)
        col_end = min(col + width, self.info.samples)

        if row >= self.info.lines or col >= self.info.samples:
            raise ValueError(
                "Requested window starts outside the cube"
            )

        data = self._data[
            band,
            row:row_end,
            col:col_end,
        ]

        return np.array(data) if copy else data

    def close(self):
        if self._data is not None:
            mmap_obj = getattr(self._data, "_mmap", None)

            if mmap_obj is not None:
                mmap_obj.close()

            self._data = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def open_iirs_cube(
    path,
    bands,
    lines,
    samples,
    dtype=np.float32,
    byte_offset=0,
):
    info = IIRSCubeInfo(
        path=Path(path),
        bands=int(bands),
        lines=int(lines),
        samples=int(samples),
        dtype=np.dtype(dtype),
        byte_offset=int(byte_offset),
    )

    return IIRSCubeReader(info)
