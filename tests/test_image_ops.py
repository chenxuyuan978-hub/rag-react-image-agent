from pathlib import Path

import cv2
import numpy as np
import pytest

from app.image_ops.image_loader import load_image
from app.image_ops.processors import (
    edge_detect,
    gaussian_blur,
    histogram_equalization,
    median_blur,
    sharpen,
)


def make_test_image() -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(12, 12, 3), dtype=np.uint8)


def test_load_image_returns_rgb_array() -> None:
    image_rgb = np.zeros((4, 4, 3), dtype=np.uint8)
    image_rgb[0, 0] = [255, 0, 0]
    image_path = Path(__file__).parent / "sample_test_image.png"
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    try:
        success, encoded_image = cv2.imencode(".png", image_bgr)
        assert success
        encoded_image.tofile(str(image_path))

        loaded = load_image(str(image_path))

        assert isinstance(loaded, np.ndarray)
        assert loaded.shape == image_rgb.shape
        assert np.array_equal(loaded[0, 0], np.array([255, 0, 0], dtype=np.uint8))
    finally:
        image_path.unlink(missing_ok=True)


def test_load_image_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_image("missing_image.png")


def test_load_image_raises_for_unsupported_format() -> None:
    image_path = Path(__file__).parent / "sample_test_image.gif"

    try:
        image_path.write_bytes(b"not a supported image")

        with pytest.raises(ValueError):
            load_image(str(image_path))
    finally:
        image_path.unlink(missing_ok=True)


def test_gaussian_blur_returns_same_shape_and_dtype() -> None:
    image = make_test_image()

    result = gaussian_blur(image, kernel_size=3)

    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape
    assert result.dtype == image.dtype


def test_median_blur_returns_same_shape_and_dtype() -> None:
    image = make_test_image()

    result = median_blur(image, kernel_size=3)

    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape
    assert result.dtype == image.dtype


def test_sharpen_returns_same_shape_and_dtype() -> None:
    image = make_test_image()

    result = sharpen(image)

    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape
    assert result.dtype == image.dtype


def test_edge_detect_returns_grayscale_edges() -> None:
    image = make_test_image()

    result = edge_detect(image)

    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape[:2]
    assert result.dtype == np.uint8


def test_histogram_equalization_returns_same_shape_and_dtype() -> None:
    image = make_test_image()

    result = histogram_equalization(image)

    assert isinstance(result, np.ndarray)
    assert result.shape == image.shape
    assert result.dtype == image.dtype


def test_invalid_kernel_size_raises_value_error() -> None:
    image = make_test_image()

    with pytest.raises(ValueError):
        gaussian_blur(image, kernel_size=4)

    with pytest.raises(ValueError):
        median_blur(image, kernel_size=0)
