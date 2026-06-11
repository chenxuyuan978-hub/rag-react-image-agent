import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.run_detail import get_run_detail
from app.core.run_history import list_runs
from app.core.run_manager import copy_file_to_run, create_run_dir
from app.experiments.comparison_runner import (
    load_comparison_config,
    run_comparison,
)
from app.experiments.config_schema import load_experiment_config
from app.react.agent import ReActAgent
from app.react.tools import (
    AnalyzeMetricsTool,
    GenerateReportTool,
    RagRetrieveTool,
    RunExperimentTool,
)


def save_uploaded_file(uploaded_file: Any, target_dir: Path) -> Path:
    """Save a Streamlit uploaded file into a target directory."""
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(uploaded_file.name).name
    output_path = target_dir / safe_name
    output_path.write_bytes(uploaded_file.getvalue())
    return output_path


def create_streamlit_config(
    input_image: Path,
    reference_image: Path,
    output_dir: Path,
) -> Path:
    """Create a temporary YAML config for the Streamlit experiment run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = output_dir / "streamlit_config.yaml"
    config = {
        "experiment_name": "streamlit_react_experiment",
        "input_image": input_image.as_posix(),
        "reference_image": reference_image.as_posix(),
        "operations": [
            {"name": "gaussian_blur", "params": {"kernel_size": 5}},
            {"name": "sharpen", "params": {}},
        ],
        "metrics": ["mse", "psnr", "ssim"],
        "output_dir": output_dir.as_posix(),
    }
    config_path.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return config_path


def create_agent() -> ReActAgent:
    """Create the MVP ReAct agent with existing tool implementations."""
    return ReActAgent(
        rag_tool=RagRetrieveTool(),
        experiment_tool=RunExperimentTool(),
        metrics_tool=AnalyzeMetricsTool(),
        report_tool=GenerateReportTool(),
    )


def show_image_paths(image_paths: list[str]) -> None:
    """Display image paths and preview images when files exist."""
    if not image_paths:
        st.info("暂无输出图像。")
        return

    for image_path in image_paths:
        path = Path(image_path)
        if path.is_file():
            st.image(str(path), caption=str(path))
        else:
            st.warning(f"图像文件不存在：{image_path}")


def show_agent_outputs(
    output_dir: Path,
    metrics_path: str | None,
    report_path: str | None,
) -> None:
    """Display single-agent metrics, output images, and report content."""
    st.subheader("评价指标结果")
    if metrics_path and Path(metrics_path).is_file():
        st.dataframe(pd.read_csv(metrics_path), use_container_width=True)
    else:
        st.info("暂未找到 metrics.csv。")

    st.subheader("输出图像")
    show_image_paths([str(path) for path in sorted(output_dir.glob("step_*.png"))])

    st.subheader("Markdown 报告")
    if report_path and Path(report_path).is_file():
        st.markdown(Path(report_path).read_text(encoding="utf-8"))
    else:
        st.info("暂未生成 report.md。")


def render_single_agent_tab() -> None:
    """Render the original single ReAct agent experiment workflow."""
    st.header("单次 Agent 实验")

    paper_file = st.file_uploader("上传论文文件（txt/md）", type=["txt", "md"])
    input_image_file = st.file_uploader(
        "上传输入图像（png/jpg/jpeg/bmp）",
        type=["png", "jpg", "jpeg", "bmp"],
    )
    reference_image_file = st.file_uploader(
        "上传参考图像（可选，png/jpg/jpeg/bmp）",
        type=["png", "jpg", "jpeg", "bmp"],
    )
    task = st.text_area(
        "任务描述",
        value="根据论文中的去噪实验设置，对示例图像做高斯滤波实验，并生成报告。",
    )

    if not st.button("运行 Agent 实验"):
        return

    if paper_file is None or input_image_file is None:
        st.error("请至少上传论文文件和输入图像。")
        return

    try:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        paper_dir = Path("data/papers")
        image_dir = Path("data/images")
        output_dir = Path("data/outputs") / f"streamlit_{run_id}"

        save_uploaded_file(paper_file, paper_dir)
        input_image_path = save_uploaded_file(input_image_file, image_dir)
        if reference_image_file is None:
            reference_image_path = input_image_path
            st.info("未上传参考图像，当前将输入图像作为参考图像用于指标计算。")
        else:
            reference_image_path = save_uploaded_file(reference_image_file, image_dir)

        config_path = create_streamlit_config(
            input_image_path,
            reference_image_path,
            output_dir,
        )
        load_experiment_config(str(config_path))

        trace = create_agent().run(
            task=task,
            config_path=str(config_path),
            paper_dir=str(paper_dir),
        )

        st.subheader("完整 ReAct Trace")
        st.text(trace.to_text())

        metrics_path = None
        for step in trace.steps:
            if step.action == "RunExperimentTool":
                metrics_path = step.observation.get("metrics_path")

        final_observation = trace.steps[-1].observation if trace.steps else {}
        report_path = final_observation.get("report_path")

        has_failed_step = any(
            not step.observation.get("success", False) for step in trace.steps
        )
        if has_failed_step:
            st.error(trace.final_answer)
        else:
            st.success(trace.final_answer)
            show_agent_outputs(output_dir, metrics_path, report_path)
    except Exception as error:
        st.error(f"运行失败：{error}")


def render_history_tab() -> None:
    """Render archived run history and selected run details."""
    st.header("历史实验")

    try:
        runs = list_runs()
    except Exception as error:
        st.error(f"读取历史实验失败：{error}")
        return

    if not runs:
        st.info("暂无历史实验。")
        return

    history_df = pd.DataFrame(
        [
            {
                "run_id": run.run_id,
                "experiment_name": run.experiment_name,
                "created_at": run.created_at,
                "has_metrics": run.has_metrics,
                "has_report": run.has_report,
            }
            for run in runs
        ]
    )
    st.dataframe(history_df, use_container_width=True)

    selected_run_id = st.selectbox(
        "选择 run_id 查看详情",
        options=[run.run_id for run in runs],
    )
    if not selected_run_id:
        return

    try:
        detail = get_run_detail(selected_run_id)
    except FileNotFoundError:
        st.error("该历史实验目录不存在。")
        return
    except Exception as error:
        st.error(f"读取实验详情失败：{error}")
        return

    st.subheader("Summary")
    if detail.summary:
        st.json(detail.summary)
    else:
        st.info("未找到 summary.json。")

    st.subheader("Metrics")
    if detail.metrics:
        st.dataframe(pd.DataFrame(detail.metrics), use_container_width=True)
    else:
        st.info("未找到 metrics.csv。")

    st.subheader("Report")
    if detail.report_text:
        st.markdown(detail.report_text)
    else:
        st.info("未找到 report.md。")

    st.subheader("输出图像")
    show_image_paths(detail.output_images)

    if detail.trace_text:
        with st.expander("Trace"):
            st.text(detail.trace_text)


def _resolve_comparison_config_path(uploaded_file: Any, input_path: str) -> str:
    """Resolve a comparison config path from upload or text input."""
    if uploaded_file is not None:
        saved_path = save_uploaded_file(uploaded_file, Path("data/outputs/configs"))
        return str(saved_path)
    return input_path


def render_comparison_tab() -> None:
    """Render multi-method comparison experiment controls and outputs."""
    st.header("多算法对比实验")

    config_path = st.text_input(
        "配置文件路径",
        value="examples/comparison_config.yaml",
    )
    uploaded_config = st.file_uploader(
        "或上传对比实验 YAML 配置",
        type=["yaml", "yml"],
    )

    if not st.button("运行对比实验"):
        return

    try:
        resolved_config_path = _resolve_comparison_config_path(
            uploaded_config,
            config_path,
        )
        config = load_comparison_config(resolved_config_path)
        run_info = create_run_dir(config.comparison_name)
        copy_file_to_run(
            resolved_config_path,
            run_info.run_dir,
            "comparison_config.yaml",
        )
        result = run_comparison(config, run_dir=run_info.run_dir)

        st.success(f"对比实验已完成：{run_info.run_id}")
        st.write(f"输出目录：`{result['output_dir']}`")

        metrics_path = Path(str(result["metrics_path"]))
        st.subheader("comparison_metrics.csv")
        if metrics_path.is_file():
            st.dataframe(pd.read_csv(metrics_path), use_container_width=True)
        else:
            st.warning("未找到 comparison_metrics.csv。")

        st.subheader("指标对比图表")
        chart_paths = [str(path) for path in result.get("chart_paths", [])]
        show_image_paths(chart_paths)

        st.subheader("输出图像")
        output_images = result.get("output_images", {})
        if isinstance(output_images, dict):
            image_paths = [str(path) for path in output_images.values()]
        else:
            image_paths = []
        show_image_paths(image_paths)
    except FileNotFoundError as error:
        st.error(f"文件不存在：{error}")
    except Exception as error:
        st.error(f"对比实验运行失败：{error}")


def render_project_info_tab() -> None:
    """Render a concise project overview."""
    st.header("项目说明")
    st.markdown(
        """
本项目是一个基于 RAG + ReAct 的图像处理论文复现实验分析 Agent。

当前前端支持：

- 上传论文和图像，运行单次规则驱动 ReAct 实验；
- 查看 `data/runs` 下的历史实验列表；
- 查看单次 run 的 summary、metrics、report、trace 和输出图像；
- 使用 YAML 配置运行多算法对比实验；
- 展示 MSE、PSNR、SSIM 的对比图表。
"""
    )


def main() -> None:
    """Render the Streamlit frontend for the image reproduction agent."""
    st.set_page_config(page_title="RAG + ReAct 图像处理 Agent", layout="wide")
    st.title("基于 RAG + ReAct 的图像处理论文复现实验分析 Agent")

    agent_tab, history_tab, comparison_tab, info_tab = st.tabs(
        ["单次 Agent 实验", "历史实验", "多算法对比实验", "项目说明"]
    )

    with agent_tab:
        render_single_agent_tab()
    with history_tab:
        render_history_tab()
    with comparison_tab:
        render_comparison_tab()
    with info_tab:
        render_project_info_tab()


if __name__ == "__main__":
    main()
