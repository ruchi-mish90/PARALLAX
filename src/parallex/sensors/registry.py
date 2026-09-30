from .iirs import IIRSAdapter
from .ohrc import OHRCAdapter
from .tmc2 import TMC2Adapter


_ADAPTERS = {
    "IIRS": IIRSAdapter,
    "OHRC": OHRCAdapter,
    "TMC2": TMC2Adapter,
}


def get_sensor_adapter(product):
    sensor = str(product.sensor).upper()

    adapter_class = _ADAPTERS.get(sensor)

    if adapter_class is None:
        raise ValueError(
            f"Unsupported sensor: {product.sensor}"
        )

    return adapter_class(product)
