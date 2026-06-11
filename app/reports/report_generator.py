import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReportInput:
    """Input paths and optional paper context for Markdown report generation."""

    summary_path: str
    metrics_path: str | None
    paper_context: list[str] | None
    output_path: str


def _read_summary(summary_path: str) -> dict:
    """Read experiment summary JSON."""
    path = Path(summary_path)
    if not path.is_file():
        raise FileNotFoundError(f"Summary file not found: {summary_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_metrics(metrics_path: str) -> list[dict[str, str]]:
    """Read metric rows from a CSV file."""
    path = Path(metrics_path)
    if not path.is_file():
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _format_metrics_table(metrics_path: str | None) -> str:
    """Format metrics as a Markdown table, or return a fallback message."""
    if not metrics_path:
        return "未提供评价指标。"

    rows = _read_metrics(metrics_path)
    if not rows:
        return "未提供评价指标。"

    lines = ["| Metric | Value |", "| --- | --- |"]
    for row in rows:
        metric = row.get("metric", "")
        value = row.get("value", "")
        lines.append(f"| {metric} | {value} |")

    return "\n".join(lines)


def _format_output_images(output_images: list[str]) -> str:
    """Format output image paths as a Markdown list."""
    if not output_images:
        return "- 未生成输出图像。"

    return "\n".join(f"- `{image_path}`" for image_path in output_images)


def _format_paper_context(paper_context: list[str] | None) -> str:
    """Format optional retrieved paper snippets."""
    if not paper_context:
        return "未提供论文相关片段。"

    return "\n\n".join(f"> {snippet}" for snippet in paper_context)


def generate_markdown_report(report_input: ReportInput) -> str:
    """Generate a Markdown reproduction report and return its path."""
    summary = _read_summary(report_input.summary_path)
    output_path = Path(report_input.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    experiment_name = summary.get("experiment_name", "unknown_experiment")
    output_dir = summary.get("output_dir", "")
    output_images = summary.get("output_images", [])
    metrics_table = _format_metrics_table(report_input.metrics_path)
    paper_context = _format_paper_context(report_input.paper_context)

    markdown = f"""# 实验复现报告

## 实验名称

{experiment_name}

## 实验目的

复现并分析本地图像处理实验，记录处理流程、输出图像和评价指标结果。

## 实验配置摘要

- 输出目录：`{output_dir}`
- Summary 文件：`{report_input.summary_path}`
- Metrics 文件：`{report_input.metrics_path or "未提供"}`

## 图像处理流程

图像处理步骤已按实验配置顺序执行，具体中间结果见输出图像路径。

## 输出图像路径

{_format_output_images(output_images)}

## 评价指标结果

{metrics_table}

## 论文相关片段

{paper_context}

## 结果分析

根据输出图像和评价指标，可以初步比较处理结果与参考图像之间的差异。

## 结论

本次实验已完成图像处理流程复现，并生成可追溯的实验结果文件。
"""

    output_path.write_text(markdown, encoding="utf-8")
    return str(output_path)
