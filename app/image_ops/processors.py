import cv2
import numpy as np


def _validate_kernel_size(kernel_size: int) -> None:
    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError("kernel_size must be a positive odd integer")


def gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Apply Gaussian blur to an image."""
    _validate_kernel_size(kernel_size)
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Apply median blur to an image."""
    _validate_kernel_size(kernel_size)
    return cv2.medianBlur(image, kernel_size)


def sharpen(image: np.ndarray) -> np.ndarray:
    """Sharpen an image with a simple convolution kernel."""
    kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )
    return cv2.filter2D(image, -1, kernel)


def edge_detect(image: np.ndarray) -> np.ndarray:
    """Detect image edges using the Canny algorithm."""
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image

    return cv2.Canny(gray_image, 100, 200)


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    """Apply histogram equalization to a grayscale or RGB image."""
    if image.ndim == 2:
        return cv2.equalizeHist(image)

    ycrcb_image = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    y_channel, cr_channel, cb_channel = cv2.split(ycrcb_image)
    equalized_y = cv2.equalizeHist(y_channel)
    equalized_image = cv2.merge((equalized_y, cr_channel, cb_channel))

    return cv2.cvtColor(equalized_image, cv2.COLOR_YCrCb2RGB)
