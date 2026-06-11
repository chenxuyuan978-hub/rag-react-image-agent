import csv
import json
import shutil
from pathlib import Path

from app.reports.report_generator import ReportInput, generate_markdown_report


def make_report_temp_dir() -> Path:
    """Create a clean workspace-local directory for report tests."""
    temp_dir = Path("tests") / "_report_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    return temp_dir


def write_summary(path: Path, metrics_path: str | None = None) -> None:
    """Write a small experiment summary JSON for report tests."""
    summary = {
        "experiment_name": "demo_report_experiment",
        "output_dir": "data/outputs/demo_report_experiment",
        "output_images": [
            "data/outputs/demo_report_experiment/step_01_gaussian_blur.png"
        ],
        "metrics_path": metrics_path,
        "summary_path": str(path),
    }
    path.write_text(json.dumps(summary), encoding="utf-8")


def write_metrics(path: Path) -> None:
    """Write a small metrics CSV for report tests."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerow({"metric": "psnr", "value": "32.5"})
        writer.writerow({"metric": "ssim", "value": "0.91"})


def test_generate_report_from_summary_and_metrics() -> None:
    temp_dir = make_report_temp_dir()

    try:
        summary_path = temp_dir / "summary.json"
        metrics_path = temp_dir / "metrics.csv"
        report_path = temp_dir / "report.md"
        write_metrics(metrics_path)
        write_summary(summary_path, str(metrics_path))

        generated_path = generate_markdown_report(
            ReportInput(
                summary_path=str(summary_path),
                metrics_path=str(metrics_path),
                paper_context=[
                    "Gaussian blur with kernel size 5 reports PSNR and SSIM."
                ],
                output_path=str(report_path),
            )
        )

        content = Path(generated_path).read_text(encoding="utf-8")
        assert Path(generated_path).is_file()
        assert "demo_report_experiment" in content
        assert "psnr" in content.lower() or "ssim" in content.lower()
        assert "Gaussian blur" in content
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_report_without_metrics_path() -> None:
    temp_dir = make_report_temp_dir()

    try:
        summary_path = temp_dir / "summary.json"
        report_path = temp_dir / "report.md"
        write_summary(summary_path, None)

        generated_path = generate_markdown_report(
            ReportInput(
                summary_path=str(summary_path),
                metrics_path=None,
                paper_context=None,
                output_path=str(report_path),
            )
        )

        content = Path(generated_path).read_text(encoding="utf-8")
        assert Path(generated_path).is_file()
        assert "demo_report_experiment" in content
        assert "未提供评价指标" in content
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
