from abc import ABC, abstractmethod


class SensorAdapter(ABC):
    """Common sensor-specific interface."""

    sensor_name = "UNKNOWN"

    def __init__(self, product):
        self.product = product

    @property
    def metadata(self):
        return self.product.metadata

    @property
    def shape(self):
        return self.product.shape

    @property
    def dtype(self):
        return self.product.dtype

    @property
    def is_multispectral(self):
        return self.product.is_multispectral

    @abstractmethod
    def representation_info(self):
        """Describe the sensor image representation."""
        raise NotImplementedError

    def summary(self):
        return {
            "sensor": self.sensor_name,
            "product_id": self.product.product_id,
            "shape": tuple(self.shape),
            "dtype": str(self.dtype),
            "multispectral": bool(self.is_multispectral),
            "representation": self.representation_info(),
        }
