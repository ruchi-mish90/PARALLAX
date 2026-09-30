from pathlib import Path

import numpy as np

from ..pds4.reader import read_product, text_by_local_name
from .image_loader import open_raw_image, open_iirs_cube


def _find_data_file(product_dir, label_path):
    """
    Find the science data file associated with the primary PDS4 label.

    Supported science formats:
        .img
        .qub
        .tif
        .tiff
    """

    label_path = Path(label_path)
    product_dir = Path(product_dir)

    supported = {
        ".img",
        ".qub",
        ".tif",
        ".tiff",
    }

    # 1. Exact same-stem science file.
    for extension in supported:
        candidate = label_path.with_suffix(extension)

        if candidate.exists():
            return candidate

    # 2. Science file in the same directory.
    for extension in supported:
        files = sorted(
            label_path.parent.glob(f"*{extension}")
        )

        if files:
            return files[0]

    # 3. Science file anywhere inside the product.
    for extension in supported:
        files = sorted(
            product_dir.rglob(f"*{extension}")
        )

        if files:
            return files[0]

    raise FileNotFoundError(
        f"No supported science data file found in: {product_dir}"
    )

def _extract_dimensions(root):
    """Extract Line/Sample dimensions from the PDS4 array structure."""
    dimensions = {}

    elements = list(root.iter())

    for i, element in enumerate(elements):
        tag = element.tag

        if not isinstance(tag, str):
            continue

        if tag.split("}")[-1] != "axis_name":
            continue

        axis_name = (element.text or "").strip()

        if not axis_name:
            continue

        for following in elements[i + 1:]:
            following_tag = following.tag

            if (
                isinstance(following_tag, str)
                and following_tag.split("}")[-1] == "elements"
            ):
                try:
                    dimensions[axis_name] = int(
                        (following.text or "").strip()
                    )
                except ValueError:
                    pass
                break

            if (
                isinstance(following_tag, str)
                and following_tag.split("}")[-1] == "axis_name"
            ):
                break

    return dimensions


def _pds4_dtype(data_type):
    """
    Map the PDS4 data_type used by the Chandrayaan-2 labels
    to a NumPy dtype.
    """
    normalized = data_type.strip().lower()

    mapping = {
        "unsignedlsb2": np.dtype("<u2"),
        "unsignedmsb2": np.dtype(">u2"),
        "signedlsb2": np.dtype("<i2"),
        "signedmsb2": np.dtype(">i2"),
        "unsignedlsb4": np.dtype("<u4"),
        "unsignedmsb4": np.dtype(">u4"),
        "signedlsb4": np.dtype("<i4"),
        "signedmsb4": np.dtype(">i4"),
        "unsignedbyte": np.dtype("u1"),
        "ieee754lsbsingle": np.dtype("<f4"),
        "ieee754msbsingle": np.dtype(">f4"),
    }

    if normalized not in mapping:
        raise ValueError(
            f"Unsupported PDS4 data_type: {data_type}"
        )

    return mapping[normalized]


def open_pds4_image(product_dir):
    """
    Open the primary PDS4 science product.

    Returns:
        RawImageReader for 2-D .img products.
        IIRSCubeReader for 3-D IIRS .qub products.
    """
    product = read_product(product_dir)
    root = product.root

    data_type = text_by_local_name(root, "data_type")

    if not data_type:
        raise ValueError(
            "PDS4 label does not contain data_type"
        )

    dimensions = _extract_dimensions(root)

    byte_offset_text = text_by_local_name(root, "offset")

    try:
        byte_offset = int(byte_offset_text or 0)
    except ValueError:
        byte_offset = 0

    dtype = _pds4_dtype(data_type)

    data_path = _find_data_file(
        product_dir,
        product.label_path,
    )

    suffix = data_path.suffix.lower()

    # IIRS spectral QUBE
    if suffix == ".qub":
        bands = dimensions.get("BAND")
        lines = dimensions.get("LINE")
        samples = dimensions.get("SAMPLE")

        if bands is None or lines is None or samples is None:
            raise ValueError(
                "IIRS QUBE requires BAND, LINE and SAMPLE dimensions. "
                f"Found: {dimensions}"
            )

        return open_iirs_cube(
            path=data_path,
            bands=bands,
            lines=lines,
            samples=samples,
            dtype=dtype,
            byte_offset=byte_offset,
        )

    # Normal 2-D image
    lines = dimensions.get("Line")
    samples = dimensions.get("Sample")

    if lines is None or samples is None:
        raise ValueError(
            f"Could not determine image dimensions: {dimensions}"
        )

    return open_raw_image(
        path=data_path,
        lines=lines,
        samples=samples,
        dtype=dtype,
        byte_offset=byte_offset,
    )






