from pathlib import Path

from app.react.tools import (
    AnalyzeMetricsTool,
    GenerateReportTool,
    RagRetrieveTool,
    RunExperimentTool,
    Tool,
)
from app.react.trace import ReActStep, ReActTrace


class ReActAgent:
    """A minimal rule-driven ReAct agent for the MVP workflow."""

    def __init__(
        self,
        rag_tool: Tool | None = None,
        experiment_tool: Tool | None = None,
        metrics_tool: Tool | None = None,
        report_tool: Tool | None = None,
    ) -> None:
        """Initialize the agent with tool instances."""
        self.rag_tool = rag_tool or RagRetrieveTool()
        self.experiment_tool = experiment_tool or RunExperimentTool()
        self.metrics_tool = metrics_tool or AnalyzeMetricsTool()
        self.report_tool = report_tool or GenerateReportTool()

    def _record_step(
        self,
        trace: ReActTrace,
        thought: str,
        action: str,
        action_input: dict,
        observation: dict,
    ) -> bool:
        """Append a step and return whether it succeeded."""
        trace.steps.append(
            ReActStep(
                thought=thought,
                action=action,
                action_input=action_input,
                observation=observation,
            )
        )
        if not observation.get("success", False):
            trace.final_answer = f"任务失败：{observation.get('error', '未知错误')}"
            return False
        return True

    def run(
        self,
        task: str,
        config_path: str,
        paper_dir: str = "data/papers",
    ) -> ReActTrace:
        """Run the fixed MVP ReAct workflow and return a trace."""
        trace = ReActTrace()

        rag_input = {
            "query": task or "Gaussian blur PSNR SSIM kernel size",
            "paper_dir": paper_dir,
            "top_k": 5,
        }
        rag_observation = self.rag_tool.run(rag_input)
        if not self._record_step(
            trace,
            "我需要先从论文资料中检索实验设置。",
            "RagRetrieveTool",
            rag_input,
            rag_observation,
        ):
            return trace

        paper_context = [
            result.get("text", "")
            for result in rag_observation.get("results", [])
            if result.get("text")
        ]

        experiment_input = {"config_path": config_path}
        experiment_observation = self.experiment_tool.run(experiment_input)
        if not self._record_step(
            trace,
            "我需要根据实验配置运行图像处理实验。",
            "RunExperimentTool",
            experiment_input,
            experiment_observation,
        ):
            return trace

        metrics_path = experiment_observation.get("metrics_path")
        metrics_input = {"metrics_path": metrics_path}
        metrics_observation = self.metrics_tool.run(metrics_input)
        if not self._record_step(
            trace,
            "我需要分析实验指标。",
            "AnalyzeMetricsTool",
            metrics_input,
            metrics_observation,
        ):
            return trace

        summary_path = str(experiment_observation.get("summary_path", ""))
        output_dir = Path(str(experiment_observation.get("output_dir", ".")))
        report_input = {
            "summary_path": summary_path,
            "metrics_path": metrics_path,
            "paper_context": paper_context,
            "output_path": str(output_dir / "report.md"),
        }
        report_observation = self.report_tool.run(report_input)
        if not self._record_step(
            trace,
            "我需要生成复现实验报告。",
            "GenerateReportTool",
            report_input,
            report_observation,
        ):
            return trace

        trace.final_answer = f"报告已生成：{report_observation.get('report_path')}"
        return trace
