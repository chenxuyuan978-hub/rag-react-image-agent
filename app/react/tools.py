import csv
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from app.experiments.config_schema import load_experiment_config
from app.experiments.experiment_runner import run_experiment
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents
from app.rag.retriever import TfidfRetriever
from app.reports.report_generator import ReportInput, generate_markdown_report
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Tool(Protocol):
    """Protocol for a callable ReAct tool."""

    name: str
    description: str

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Run the tool with dictionary input and return dictionary output."""


class RagRetrieveTool:
    """Tool that retrieves paper chunks with local TF-IDF RAG."""

    name = "rag_retrieve"
    description = "Retrieve relevant txt/md paper chunks from a local directory."

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Load documents, build a TF-IDF index, and return retrieval results."""
        try:
            query = str(tool_input.get("query", ""))
            paper_dir = str(tool_input.get("paper_dir", "data/papers"))
            top_k = int(tool_input.get("top_k", 5))

            documents = load_documents(paper_dir)
            chunks = chunk_documents(documents)
            if not chunks:
                raise ValueError(f"No txt/md documents found in: {paper_dir}")

            retriever = TfidfRetriever()
            retriever.build_index(chunks)
            results = retriever.retrieve(query=query, top_k=top_k)

            return {
                "success": True,
                "results": [asdict(result) for result in results],
            }
        except Exception as error:
            logger.error("%s failed: %s", self.name, error)
            return {"success": False, "error": str(error)}


class RunExperimentTool:
    """Tool that loads an experiment config and runs the experiment."""

    name = "run_experiment"
    description = "Run a configured local image processing experiment."

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Load a YAML experiment config and execute it."""
        try:
            config_path = str(tool_input.get("config_path", ""))
            config = load_experiment_config(config_path)
            result = run_experiment(config)

            return {
                "success": True,
                "experiment_name": result.experiment_name,
                "output_dir": result.output_dir,
                "metrics_path": result.metrics_path,
                "summary_path": result.summary_path,
            }
        except Exception as error:
            logger.error("%s failed: %s", self.name, error)
            return {"success": False, "error": str(error)}


class AnalyzeMetricsTool:
    """Tool that reads metrics.csv and produces a simple text analysis."""

    name = "analyze_metrics"
    description = "Analyze MSE, PSNR, and SSIM values from a metrics CSV file."

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Read metrics.csv and return a short rule-based analysis."""
        try:
            metrics_path = Path(str(tool_input.get("metrics_path", "")))
            if not metrics_path.is_file():
                raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

            with metrics_path.open("r", newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            metric_values = {
                row.get("metric", "").lower(): row.get("value", "") for row in rows
            }
            parts = ["指标分析：MSE 越低越好，PSNR 越高越好，SSIM 越接近 1 越好。"]
            for metric_name in ["mse", "psnr", "ssim"]:
                if metric_name in metric_values:
                    parts.append(
                        f"{metric_name.upper()} = {metric_values[metric_name]}"
                    )

            return {"success": True, "analysis": " ".join(parts)}
        except Exception as error:
            logger.error("%s failed: %s", self.name, error)
            return {"success": False, "error": str(error)}


class GenerateReportTool:
    """Tool that generates a Markdown report from experiment outputs."""

    name = "generate_report"
    description = "Generate a Markdown reproduction report."

    def run(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Generate a Markdown report and return its path."""
        try:
            paper_context = tool_input.get("paper_context")
            if paper_context is not None and not isinstance(paper_context, list):
                raise ValueError("paper_context must be a list or empty")

            report_path = generate_markdown_report(
                ReportInput(
                    summary_path=str(tool_input.get("summary_path", "")),
                    metrics_path=tool_input.get("metrics_path"),
                    paper_context=paper_context,
                    output_path=str(tool_input.get("output_path", "")),
                )
            )

            return {"success": True, "report_path": report_path}
        except Exception as error:
            logger.error("%s failed: %s", self.name, error)
            return {"success": False, "error": str(error)}
