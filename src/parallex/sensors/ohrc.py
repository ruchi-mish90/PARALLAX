from .base import SensorAdapter


class OHRCAdapter(SensorAdapter):
    sensor_name = "OHRC"

    def representation_info(self):
        return {
            "type": "panchromatic_image",
            "axes": ("line", "sample"),
            "line_count": int(self.shape[0]),
            "sample_count": int(self.shape[1]),
        }

    def read_window(self, row, col, height, width, copy=True):
        return self.product.read_window(
            row=row,
            col=col,
            height=height,
            width=width,
            copy=copy,
        )
