from .base import SensorAdapter


class IIRSAdapter(SensorAdapter):
    sensor_name = "IIRS"

    def representation_info(self):
        return {
            "type": "spectral_cube",
            "axes": ("band", "line", "sample"),
            "band_count": int(self.shape[0]),
            "line_count": int(self.shape[1]),
            "sample_count": int(self.shape[2]),
        }

    def read_window(self, row, col, height, width, band, copy=True):
        return self.product.read_window(
            row=row,
            col=col,
            height=height,
            width=width,
            band=band,
            copy=copy,
        )

    def read_band(self, band, copy=True):
        return self.product.read_band(
            band=band,
            copy=copy,
        )
