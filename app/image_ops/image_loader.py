from pathlib import Path

import cv2
import numpy as np

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def load_image(path: str) -> np.ndarray:
    """Load an image file as an RGB numpy array."""
    image_path = Path(path)

    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported image format: {image_path.suffix}")

    image_data = np.fromfile(str(image_path), dtype=np.uint8)
    image_bgr = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError(f"Failed to read image file: {path}")

    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
