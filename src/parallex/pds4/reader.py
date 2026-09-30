from pathlib import Path
import xml.etree.ElementTree as ET


class PDS4Product:
    """Lightweight representation of a local PDS4 product."""

    def __init__(self, product_dir):
        self.product_dir = Path(product_dir)

        if not self.product_dir.exists():
            raise FileNotFoundError(
                f"Product directory not found: {self.product_dir}"
            )

        self.label_path = find_label(self.product_dir)
        self.tree = ET.parse(self.label_path)
        self.root = self.tree.getroot()

    @property
    def product_id(self):
        return text_by_local_name(self.root, "logical_identifier")

    def find_files(self):
        return discover_files(self.product_dir)


def text_by_local_name(root, local_name):
    """Find the first XML element matching local_name, ignoring namespace."""
    for element in root.iter():
        tag = element.tag

        if not isinstance(tag, str):
            continue

        if tag.split("}")[-1] == local_name:
            if element.text:
                return element.text.strip()

    return None


def find_label(product_dir):
    """
    Find the primary PDS4 science/data XML label.

    Priority:
    1. XML in a data directory with a matching .img file.
    2. XML in a data directory.
    3. Geometry XML.
    4. Browse XML.
    """

    product_dir = Path(product_dir)

    all_xml = sorted(product_dir.rglob("*.xml"))

    if not all_xml:
        raise FileNotFoundError(
            f"No PDS4 XML label found in: {product_dir}"
        )

    # 1. Prefer the science/data label that has a matching image file.
    data_xml = [
        xml
        for xml in all_xml
        if "data" in {part.lower() for part in xml.parts}
    ]

    for xml in data_xml:
        matching_img = xml.with_suffix(".img")

        if matching_img.exists():
            return xml

        # Fallback: look for an IMG with the same stem in the same folder.
        same_stem = list(xml.parent.glob(f"{xml.stem}.img"))

        if same_stem:
            return xml

    # 2. If no matching IMG was found, prefer XML under data/.
    if data_xml:
        return data_xml[0]

    # 3. Geometry XML.
    geometry_xml = [
        xml
        for xml in all_xml
        if "geometry" in {part.lower() for part in xml.parts}
    ]

    if geometry_xml:
        return geometry_xml[0]

    # 4. Last resort: browse XML.
    browse_xml = [
        xml
        for xml in all_xml
        if "browse" in {part.lower() for part in xml.parts}
    ]

    if browse_xml:
        return browse_xml[0]

    return all_xml[0]


def discover_files(product_dir):
    """Return all files belonging to a local PDS4 product."""
    product_dir = Path(product_dir)

    return sorted(
        p for p in product_dir.rglob("*")
        if p.is_file()
    )


def read_product(product_dir):
    """Read a local PDS4 product and return a PDS4Product object."""
    return PDS4Product(product_dir)
