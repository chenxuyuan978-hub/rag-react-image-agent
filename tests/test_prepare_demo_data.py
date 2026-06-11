import shutil
from pathlib import Path

from app.image_ops.image_loader import load_image
from scripts.prepare_demo_data import prepare_demo_data


def test_prepare_demo_data_generates_input_and_reference() -> None:
    temp_dir = Path("tests") / "_demo_data_temp"

    try:
        input_path, reference_path = prepare_demo_data(str(temp_dir))

        assert input_path.is_file()
        assert reference_path.is_file()

        input_image = load_image(str(input_path))
        reference_image = load_image(str(reference_path))

        assert input_image.shape == reference_image.shape
        assert input_image.shape == (128, 128, 3)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
