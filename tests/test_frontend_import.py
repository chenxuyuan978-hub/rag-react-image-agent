import importlib.util
from pathlib import Path


def test_streamlit_app_can_be_imported() -> None:
    """Check that the Streamlit frontend entry file can be imported."""
    app_path = Path("frontend/streamlit_app.py")
    spec = importlib.util.spec_from_file_location("streamlit_app", app_path)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "main")
