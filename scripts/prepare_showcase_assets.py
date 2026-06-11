from pathlib import Path

import cv2
import numpy as np

PAPER_TEXT = """# Gaussian Blur Image Denoising Experiment

## Abstract

This showcase paper describes an image denoising experiment based on Gaussian
blur. The goal is to reduce light random noise from a synthetic RGB image while
preserving the main shapes and edges.

## Experiment Setting

The experiment setting uses one noisy input image and one clean reference image.
The denoising method is Gaussian blur with kernel size 5. The output image is
compared with the clean reference image after filtering.

## Metrics

The experiment reports MSE, PSNR, and SSIM. MSE should be lower for better
pixel-level reconstruction. PSNR should be higher for better signal quality.
SSIM should be closer to 1 when the restored image is structurally similar to
the clean reference image.
"""

TASK_TEXT = "根据论文中 Gaussian Blur 去噪实验的设置，先检索实验参数和评价指标，然后对示例图像运行图像处理实验，最后分析指标并生成 Markdown 复现实验报告。"

SHOWCASE_README = """# Showcase Assets

这些文件用于 Streamlit 前端展示。

## 前端上传文件

请在前端上传：

- 论文文件：`showcase/demo_denoising_paper.md`
- 输入图像：`showcase/input.png`
- 参考图像：`showcase/reference.png`

## 任务描述

请把 `showcase/showcase_task.txt` 中的内容复制到前端任务描述输入框。

## 推荐启动方式

```bash
streamlit run frontend/streamlit_app.py
```
"""


def save_png(path: Path, image: np.ndarray) -> None:
    """Save an RGB PNG image with Windows Chinese path compatibility."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    success, encoded_image = cv2.imencode(".png", image_bgr)
    if not success:
        raise ValueError(f"Failed to encode image: {path}")
    path.write_bytes(encoded_image.tobytes())


def create_reference_image(size: int = 160) -> np.ndarray:
    """Create a clean RGB image for showcase denoising."""
    x_gradient = np.linspace(20, 230, size, dtype=np.uint8)
    y_gradient = np.linspace(230, 30, size, dtype=np.uint8)
    red = np.tile(x_gradient, (size, 1))
    green = np.tile(y_gradient.reshape(size, 1), (1, size))
    blue = np.full((size, size), 120, dtype=np.uint8)
    image = np.stack([red, green, blue], axis=-1)

    image[28:76, 28:76] = [235, 80, 70]
    image[92:132, 96:140] = [70, 190, 115]
    center = size // 2
    radius = size // 7
    y_indices, x_indices = np.ogrid[:size, :size]
    circle = (x_indices - center) ** 2 + (y_indices - center) ** 2 <= radius**2
    image[circle] = [70, 130, 235]

    return image


def create_noisy_image(
    reference_image: np.ndarray, noise_level: int = 18
) -> np.ndarray:
    """Create a noisy RGB input image from a clean reference image."""
    rng = np.random.default_rng(2025)
    noise = rng.normal(0, noise_level, size=reference_image.shape)
    noisy_image = reference_image.astype(np.float32) + noise
    return np.clip(noisy_image, 0, 255).astype(np.uint8)


def prepare_showcase_assets(output_dir: str = "showcase") -> dict[str, Path]:
    """Generate all showcase files and return their paths."""
    showcase_dir = Path(output_dir)
    showcase_dir.mkdir(parents=True, exist_ok=True)

    reference_image = create_reference_image()
    input_image = create_noisy_image(reference_image)

    paper_path = showcase_dir / "demo_denoising_paper.md"
    input_path = showcase_dir / "input.png"
    reference_path = showcase_dir / "reference.png"
    task_path = showcase_dir / "showcase_task.txt"
    readme_path = showcase_dir / "README.md"

    paper_path.write_text(PAPER_TEXT, encoding="utf-8")
    task_path.write_text(TASK_TEXT, encoding="utf-8")
    readme_path.write_text(SHOWCASE_README, encoding="utf-8")
    save_png(reference_path, reference_image)
    save_png(input_path, input_image)

    return {
        "paper": paper_path,
        "input": input_path,
        "reference": reference_path,
        "task": task_path,
        "readme": readme_path,
    }


def main() -> int:
    """Generate showcase assets and print created paths."""
    paths = prepare_showcase_assets()
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
