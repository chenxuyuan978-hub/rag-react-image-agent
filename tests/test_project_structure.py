from pathlib import Path


def test_core_directories_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]
    expected_dirs = [
        "app",
        "app/core",
        "app/rag",
        "app/react",
        "app/image_ops",
        "app/experiments",
        "app/reports",
        "app/utils",
        "data/papers",
        "data/images",
        "data/indexes",
        "data/outputs",
        "examples",
        "scripts",
        "tests",
    ]

    for relative_path in expected_dirs:
        assert (project_root / relative_path).is_dir()
