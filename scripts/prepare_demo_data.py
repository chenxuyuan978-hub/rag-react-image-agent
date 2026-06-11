from pathlib import Path

import cv2
import numpy as np


def save_png(path: Path, image: np.ndarray) -> None:
    """Save an RGB image as PNG with Windows Chinese path compatibility."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    success, encoded_image = cv2.imencode(".png", image_bgr)
    if not success:
        raise ValueError(f"Failed to encode image: {path}")
    path.write_bytes(encoded_image.tobytes())


def create_reference_image(size: int = 128) -> np.ndarray:
    """Create a simple RGB reference image with gradients and shapes."""
    x_gradient = np.linspace(0, 255, size, dtype=np.uint8)
    y_gradient = np.linspace(255, 0, size, dtype=np.uint8)
    red = np.tile(x_gradient, (size, 1))
    green = np.tile(y_gradient.reshape(size, 1), (1, size))
    blue = np.full((size, size), 96, dtype=np.uint8)
    image = np.stack([red, green, blue], axis=-1)

    image[32:72, 32:72] = [240, 80, 80]
    center = size // 2
    radius = size // 6
    y_indices, x_indices = np.ogrid[:size, :size]
    circle_mask = (x_indices - center) ** 2 + (y_indices - center) ** 2 <= radius**2
    image[circle_mask] = [60, 180, 230]

    return image


def create_noisy_input(reference_image: np.ndarray, noise_level: int = 8) -> np.ndarray:
    """Create an input image by adding light noise to the reference image."""
    rng = np.random.default_rng(42)
    noise = rng.integers(
        -noise_level,
        noise_level + 1,
        size=reference_image.shape,
        dtype=np.int16,
    )
    noisy_image = reference_image.astype(np.int16) + noise
    return np.clip(noisy_image, 0, 255).astype(np.uint8)


def prepare_demo_data(output_dir: str = "data/images") -> tuple[Path, Path]:
    """Generate demo input and reference images under the output directory."""
    image_dir = Path(output_dir)
    reference_image = create_reference_image()
    input_image = create_noisy_input(reference_image)

    input_path = image_dir / "input.png"
    reference_path = image_dir / "reference.png"
    save_png(reference_path, reference_image)
    save_png(input_path, input_image)

    return input_path, reference_path


def main() -> int:
    """Generate the default demo images and print their paths."""
    input_path, reference_path = prepare_demo_data()
    print(f"input_image: {input_path}")
    print(f"reference_image: {reference_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
