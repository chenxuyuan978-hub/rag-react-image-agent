import csv
from pathlib import Path

import matplotlib.pyplot as plt

plt.switch_backend("Agg")

SUPPORTED_METRICS = ("mse", "psnr", "ssim")


def _read_metric_rows(metrics_csv: str) -> list[dict[str, str]]:
    """Read comparison metric rows from a CSV file."""
    path = Path(metrics_csv)
    if not path.is_file():
        raise FileNotFoundError(f"Metrics CSV not found: {metrics_csv}")

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _filter_rows_by_metric(
    rows: list[dict[str, str]],
    metric_name: str,
) -> list[dict[str, str]]:
    """Return rows for one metric name, using case-insensitive matching."""
    return [
        row for row in rows if str(row.get("metric", "")).strip().lower() == metric_name
    ]


def _generate_single_chart(
    metric_name: str,
    rows: list[dict[str, str]],
    output_dir: Path,
) -> str:
    """Generate one metric comparison chart and return its path."""
    methods = [str(row.get("method", "")) for row in rows]
    values = [float(row.get("value", 0.0)) for row in rows]

    plt.figure(figsize=(8, 5))
    plt.bar(methods, values)
    plt.title(f"{metric_name.upper()} Comparison")
    plt.xlabel("Method")
    plt.ylabel(metric_name.upper())
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    chart_path = output_dir / f"{metric_name}_comparison.png"
    plt.savefig(chart_path)
    plt.close()
    return str(chart_path)


def generate_metric_charts(metrics_csv: str, output_dir: str) -> list[str]:
    """Generate MSE, PSNR, and SSIM comparison charts from comparison metrics."""
    rows = _read_metric_rows(metrics_csv)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    chart_paths: list[str] = []
    for metric_name in SUPPORTED_METRICS:
        metric_rows = _filter_rows_by_metric(rows, metric_name)
        if metric_rows:
            chart_paths.append(
                _generate_single_chart(metric_name, metric_rows, output_path)
            )

    return chart_paths
