from pathlib import Path


def test_streamlit_app_file_exists() -> None:
    """Check that the Streamlit frontend entry file exists."""
    assert Path("frontend/streamlit_app.py").is_file()
