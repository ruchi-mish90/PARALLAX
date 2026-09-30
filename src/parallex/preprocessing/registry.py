from dataclasses import dataclass
from typing import Dict, Optional

from .processor import PreprocessingConfig, Preprocessor


@dataclass(frozen=True)
class RepresentationSpec:
    name: str
    sensors: tuple[str, ...]
    description: str
    requires_band: bool = False


class RepresentationRegistry:
    """Central registry for PARALLAX image representations."""

    def __init__(self):
        self._items: Dict[str, RepresentationSpec] = {}

        self.register(RepresentationSpec(
            "native",
            ("OHRC", "TMC2", "IIRS"),
            "Native image representation.",
        ))

        self.register(RepresentationSpec(
            "band",
            ("IIRS",),
            "Single IIRS spectral band.",
            True,
        ))

        self.register(RepresentationSpec(
            "gradient",
            ("OHRC", "TMC2"),
            "Spatial gradient magnitude.",
        ))

        self.register(RepresentationSpec(
            "spectral_mean",
            ("IIRS",),
            "Mean across available IIRS bands.",
        ))

        self.register(RepresentationSpec(
            "spectral_gradient",
            ("IIRS",),
            "Gradient magnitude of IIRS spectral mean.",
        ))

    def register(self, spec: RepresentationSpec):
        self._items[spec.name.lower()] = spec

    def get(self, name: str) -> RepresentationSpec:
        key = name.lower()

        if key not in self._items:
            raise KeyError(
                f"Unknown representation: {name}"
            )

        return self._items[key]

    def available(self, sensor: Optional[str] = None):
        if sensor is None:
            return tuple(self._items.values())

        sensor = sensor.upper()

        return tuple(
            spec
            for spec in self._items.values()
            if sensor in spec.sensors
        )

    def validate(
        self,
        sensor: str,
        representation: str,
    ):
        spec = self.get(representation)
        sensor = sensor.upper()

        if sensor not in spec.sensors:
            raise ValueError(
                f"Representation '{representation}' is not "
                f"supported for sensor '{sensor}'"
            )

        return spec


DEFAULT_REGISTRY = RepresentationRegistry()


def create_preprocessor(
    product,
    representation: str,
    band: Optional[int] = None,
    registry: RepresentationRegistry = DEFAULT_REGISTRY,
    **config_kwargs,
):
    """Create a validated Preprocessor from a representation name."""

    registry.validate(
        product.sensor,
        representation,
    )

    config = PreprocessingConfig(
        representation=representation,
        band=band,
        **config_kwargs,
    )

    return Preprocessor(
        product,
        config=config,
    )
