import numpy as np


def robust_normalize(image, valid_mask=None, low=1.0, high=99.0):
    """
    Robustly scale valid image pixels to [0, 1].

    Percentiles are computed only over valid finite pixels.
    """
    image = np.asarray(image, dtype=np.float32)

    if valid_mask is None:
        valid_mask = np.isfinite(image)

    valid_mask = valid_mask & np.isfinite(image)

    if not np.any(valid_mask):
        return np.zeros_like(image, dtype=np.float32)

    values = image[valid_mask]

    lo, hi = np.percentile(values, [low, high])

    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        result = np.zeros_like(image, dtype=np.float32)
        result[valid_mask] = 0.5
        return result

    result = (image - lo) / (hi - lo)
    result = np.clip(result, 0.0, 1.0)

    result[~valid_mask] = 0.0

    return result.astype(np.float32)


def valid_mask(image, nodata=None):
    """
    Construct a validity mask for an image.
    """
    image = np.asarray(image)

    mask = np.isfinite(image)

    if nodata is not None:
        mask &= image != nodata

    return mask


def local_standardize(image, valid=None, eps=1e-6):
    """
    Global valid-pixel standardization.

    This is intentionally conservative; later experiments can add
    local/windowed normalization where justified by the benchmark.
    """
    image = np.asarray(image, dtype=np.float32)

    if valid is None:
        valid = np.isfinite(image)

    valid = valid & np.isfinite(image)

    if not np.any(valid):
        return np.zeros_like(image, dtype=np.float32)

    values = image[valid]

    mean = np.mean(values)
    std = np.std(values)

    result = np.zeros_like(image, dtype=np.float32)

    if std < eps:
        result[valid] = 0.0
        return result

    result[valid] = (image[valid] - mean) / (std + eps)

    return result


def preprocess_window(image, nodata=None):
    """
    Standard PARALLAX preprocessing entry point.

    Returns:
        normalized image,
        valid mask
    """
    mask = valid_mask(image, nodata=nodata)
    normalized = robust_normalize(image, valid_mask=mask)

    return normalized, mask
