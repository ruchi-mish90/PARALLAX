from pathlib import Path
from .reader import read_product, text_by_local_name


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first(root, *names):
    for name in names:
        value = text_by_local_name(root, name)
        if value is not None:
            return value
    return None


def _find_name_by_type(root, type_value):
    """
    Find a PDS4 <name> associated with a specific <type>.

    Example:
        type = Instrument
        name = terrain mapping camera
    """
    elements = list(root.iter())

    for i, element in enumerate(elements):
        tag = element.tag

        if not isinstance(tag, str):
            continue

        if tag.split("}")[-1] != "type":
            continue

        if (element.text or "").strip().lower() != type_value.lower():
            continue

        # Usually <name> and <type> occur within the same context.
        parent = None

        for candidate in elements:
            if element in list(candidate):
                parent = candidate
                break

        if parent is not None:
            for child in parent.iter():
                child_tag = child.tag
                if (
                    isinstance(child_tag, str)
                    and child_tag.split("}")[-1] == "name"
                    and child.text
                ):
                    return child.text.strip()

    return None


def _extract_axis_elements(root):
    """
    Extract PDS4 array dimensions while preserving axis meaning.

    Returns:
        {
            "Line": 275051,
            "Sample": 4000
        }
    """
    result = {}

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

        # Find the nearest following <elements>.
        for following in elements[i + 1:]:
            following_tag = following.tag

            if (
                isinstance(following_tag, str)
                and following_tag.split("}")[-1] == "elements"
            ):
                value = _int((following.text or "").strip())

                if value is not None:
                    result[axis_name] = value

                break

            # Stop when another axis begins.
            if (
                isinstance(following_tag, str)
                and following_tag.split("}")[-1] == "axis_name"
            ):
                break

    return result


def _extract_corners(root):
    """
    Extract the four geographic corner coordinates separately.

    This deliberately does NOT calculate longitude_min/max because
    lunar footprints can cross the 0/360-degree longitude boundary.
    """
    corners = {}

    corner_names = [
        "upper_left",
        "upper_right",
        "lower_left",
        "lower_right",
    ]

    for corner in corner_names:
        lat = _first(
            root,
            f"{corner}_latitude",
            f"{corner}_lat",
        )

        lon = _first(
            root,
            f"{corner}_longitude",
            f"{corner}_lon",
        )

        corners[corner] = {
            "latitude": _float(lat),
            "longitude": _float(lon),
        }

    return corners


def extract_metadata(product_dir):
    """
    Extract important PDS4 metadata from an OHRC or TMC-2 product.

    Returns a plain dictionary suitable for JSON/CSV serialization.
    """
    product = read_product(product_dir)
    root = product.root

    product_id = product.product_id

    if product_id is None:
        product_id = Path(product_dir).name

    product_id_lower = product_id.lower()

    if "_ohr_" in product_id_lower:
        sensor = "OHRC"
    elif "_tmc_" in product_id_lower:
        sensor = "TMC2"
    elif "_iir_" in product_id_lower or "_iirs_" in product_id_lower:
        sensor = "IIRS"
    else:
        sensor = "UNKNOWN"

    dimensions = _extract_axis_elements(root)
    corners = _extract_corners(root)

    metadata = {
        "product_id": product_id,
        "sensor": sensor,

        "mission": _first(root, "mission_name"),
        "title": _first(root, "title"),

        "instrument": _find_name_by_type(root, "Instrument"),

        "processing_level": _first(
            root,
            "processing_level",
            "processing_level_id",
        ),

        "start_time": _first(
            root,
            "start_date_time",
            "start_time",
        ),

        "stop_time": _first(
            root,
            "stop_date_time",
            "stop_time",
        ),

        "orbit_number": _float(
            _first(
                root,
                "imaging_orbit_number",
                "orbit_number",
                "orbit",
            )
        ),

        "orbit_direction": _first(
            root,
            "orbit_limb_direction",
            "orbit_direction",
        ),

        "pixel_resolution_m": _float(
            _first(
                root,
                "pixel_resolution",
                "ground_sample_distance",
                "gsd",
            )
        ),

        "spacecraft_altitude_km": _float(
            _first(
                root,
                "spacecraft_altitude",
                "altitude",
            )
        ),

        "sun_azimuth_deg": _float(
            _first(root, "sun_azimuth")
        ),

        "sun_elevation_deg": _float(
            _first(root, "sun_elevation", "solar_elevation")
        ),

        "solar_incidence_deg": _float(
            _first(
                root,
                "solar_incidence",
                "solar_incidence_angle",
                "incidence_angle",
            )
        ),

        "roll_deg": _float(_first(root, "roll")),
        "pitch_deg": _float(_first(root, "pitch")),
        "yaw_deg": _float(_first(root, "yaw")),

        "projection": _first(root, "projection", "map_projection"),
        "area": _first(root, "area", "region"),

        "corners": corners,

        "line_elements": dimensions.get("Line"),
        "sample_elements": dimensions.get("Sample"),

        "data_type": _first(root, "data_type"),
        "axis_index_order": _first(root, "axis_index_order"),

        "label_path": str(product.label_path),
    }

    files = product.find_files()

    metadata["file_count"] = len(files)

    metadata["xml_files"] = [
        str(p)
        for p in files
        if p.suffix.lower() == ".xml"
    ]

    metadata["data_files"] = [
        str(p)
        for p in files
        if "data" in {part.lower() for part in p.parts}
    ]

    metadata["geometry_files"] = [
        str(p)
        for p in files
        if "geometry" in {part.lower() for part in p.parts}
    ]

    metadata["browse_files"] = [
        str(p)
        for p in files
        if "browse" in {part.lower() for part in p.parts}
    ]

    return metadata


def extract_tmc2_metadata(product_dir):
    metadata = extract_metadata(product_dir)

    if metadata["sensor"] != "TMC2":
        raise ValueError(
            f"Expected TMC-2 product, detected {metadata['sensor']}"
        )

    return metadata


def extract_ohrc_metadata(product_dir):
    metadata = extract_metadata(product_dir)

    if metadata["sensor"] != "OHRC":
        raise ValueError(
            f"Expected OHRC product, detected {metadata['sensor']}"
        )

    return metadata

