import math

import numpy as np
import pytest

from app.image_ops.metrics import mse, psnr, ssim


def test_same_image_mse_is_zero() -> None:
    image = np.zeros((8, 8), dtype=np.uint8)

    assert mse(image, image) == 0.0


def test_different_images_mse_is_positive() -> None:
    image_a = np.zeros((8, 8), dtype=np.uint8)
    image_b = np.ones((8, 8), dtype=np.uint8) * 10

    assert mse(image_a, image_b) > 0.0


def test_same_image_psnr_is_infinite() -> None:
    image = np.zeros((8, 8), dtype=np.uint8)

    assert math.isinf(psnr(image, image))


def test_same_image_ssim_is_close_to_one() -> None:
    image = np.full((8, 8), 128, dtype=np.uint8)

    assert ssim(image, image) == pytest.approx(1.0)


def test_shape_mismatch_raises_value_error() -> None:
    image_a = np.zeros((8, 8), dtype=np.uint8)
    image_b = np.zeros((8, 7), dtype=np.uint8)

    with pytest.raises(ValueError):
        mse(image_a, image_b)

    with pytest.raises(ValueError):
        psnr(image_a, image_b)

    with pytest.raises(ValueError):
        ssim(image_a, image_b)


def test_rgb_image_can_calculate_ssim() -> None:
    image_a = np.full((8, 8, 3), 100, dtype=np.uint8)
    image_b = image_a.copy()
    image_b[0, 0] = [120, 110, 100]

    result = ssim(image_a, image_b)

    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
