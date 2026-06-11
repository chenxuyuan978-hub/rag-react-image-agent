import math

import numpy as np
from skimage.metrics import structural_similarity


def _validate_same_shape(image_a: np.ndarray, image_b: np.ndarray) -> None:
    if image_a.shape != image_b.shape:
        raise ValueError("image_a and image_b must have the same shape")


def mse(image_a: np.ndarray, image_b: np.ndarray) -> float:
    """Calculate the mean squared error between two images."""
    _validate_same_shape(image_a, image_b)
    difference = image_a.astype(np.float64) - image_b.astype(np.float64)
    return float(np.mean(difference**2))


def psnr(
    image_a: np.ndarray,
    image_b: np.ndarray,
    data_range: float = 255.0,
) -> float:
    """Calculate the peak signal-to-noise ratio between two images."""
    error = mse(image_a, image_b)
    if error == 0:
        return float("inf")

    return float(20 * math.log10(data_range / math.sqrt(error)))


def ssim(
    image_a: np.ndarray,
    image_b: np.ndarray,
    data_range: float = 255.0,
) -> float:
    """Calculate the structural similarity index between two images."""
    _validate_same_shape(image_a, image_b)
    channel_axis = -1 if image_a.ndim == 3 else None

    return float(
        structural_similarity(
            image_a,
            image_b,
            data_range=data_range,
            channel_axis=channel_axis,
        )
    )
