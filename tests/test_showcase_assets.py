import shutil
from pathlib import Path

from app.image_ops.image_loader import load_image
from scripts.prepare_showcase_assets import prepare_showcase_assets


def test_prepare_showcase_assets_creates_expected_files() -> None:
    """Check that showcase assets are generated with matching image shapes."""
    output_dir = Path("tests") / "_showcase_assets_temp"

    try:
        paths = prepare_showcase_assets(str(output_dir))

        assert paths["paper"].is_file()
        assert paths["input"].is_file()
        assert paths["reference"].is_file()
        assert paths["task"].is_file()
        assert paths["readme"].is_file()

        paper_text = paths["paper"].read_text(encoding="utf-8")
        assert "Gaussian blur" in paper_text
        assert "kernel size 5" in paper_text
        assert "MSE" in paper_text
        assert "PSNR" in paper_text
        assert "SSIM" in paper_text

        input_image = load_image(str(paths["input"]))
        reference_image = load_image(str(paths["reference"]))
        assert input_image.shape == reference_image.shape
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
