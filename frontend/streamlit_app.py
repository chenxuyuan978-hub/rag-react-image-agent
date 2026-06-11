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


def show_outputs(
    output_dir: Path, metrics_path: str | None, report_path: str | None
) -> None:
    """Display metrics, output images, and report content in Streamlit."""
    if metrics_path and Path(metrics_path).is_file():
        st.subheader("评价指标结果")
        st.dataframe(pd.read_csv(metrics_path))

    st.subheader("输出图像")
    image_paths = sorted(output_dir.glob("step_*.png"))
    if image_paths:
        for image_path in image_paths:
            st.image(str(image_path), caption=image_path.name)
    else:
        st.info("暂未找到输出图像。")

    st.subheader("Markdown 报告")
    if report_path and Path(report_path).is_file():
        st.markdown(Path(report_path).read_text(encoding="utf-8"))
    else:
        st.info("暂未生成 report.md。")


def main() -> None:
    """Render the Streamlit frontend for the image reproduction agent."""
    st.set_page_config(page_title="RAG + ReAct 图像处理 Agent", layout="wide")
    st.title("基于 RAG + ReAct 的图像处理论文复现实验分析 Agent")

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

    if not st.button("运行"):
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
            st.info("未上传参考图像，当前 MVP 将输入图像作为参考图像用于指标计算。")
        else:
            reference_image_path = save_uploaded_file(reference_image_file, image_dir)

        config_path = create_streamlit_config(
            input_image_path, reference_image_path, output_dir
        )
        load_experiment_config(str(config_path))

        trace = create_agent().run(
            task=task,
            config_path=str(config_path),
            paper_dir=str(paper_dir),
        )

        st.subheader("完整 ReAct Trace")
        st.text(trace.to_text())

        final_observation = trace.steps[-1].observation if trace.steps else {}
        metrics_path = None
        for step in trace.steps:
            if step.action == "RunExperimentTool":
                metrics_path = step.observation.get("metrics_path")
        report_path = final_observation.get("report_path")

        if trace.final_answer.startswith("任务失败"):
            st.error(trace.final_answer)
        else:
            st.success(trace.final_answer)
            show_outputs(output_dir, metrics_path, report_path)
    except Exception as error:
        st.error(f"运行失败：{error}")


if __name__ == "__main__":
    main()
