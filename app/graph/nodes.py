import csv
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.experiments.config_schema import load_experiment_config
from app.experiments.experiment_runner import run_experiment
from app.graph.error_handling import build_error_diagnosis
from app.graph.state import GraphAgentState
from app.llm.extractors import extract_experiment_spec
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents
from app.rag.retriever import TfidfRetriever
from app.reports.report_generator import ReportInput, generate_markdown_report


def _append_step(
    state: GraphAgentState,
    node: str,
    status: str,
    detail: str,
    data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return steps with one new node execution record appended."""
    steps = list(state.get("steps", []))
    steps.append(
        {
            "node": node,
            "status": status,
            "detail": detail,
            "data": data or {},
        }
    )
    return steps


def _clear_error_fields() -> dict[str, Any]:
    """Return state updates that clear the current workflow error."""
    return {"error": None, "error_type": None, "failed_node": None}


def retrieve_paper_context_node(state: GraphAgentState) -> dict[str, Any]:
    """Retrieve paper context snippets with the existing local RAG modules."""
    node = "retrieve_paper_context"
    try:
        documents = load_documents(state.get("paper_dir", "data/papers"))
        if not documents:
            return {
                "paper_context": [],
                "steps": _append_step(
                    state,
                    node,
                    "ok",
                    "No txt/md documents found; continuing with empty context.",
                ),
            }

        chunks = chunk_documents(documents)
        retriever = TfidfRetriever()
        retriever.build_index(chunks)
        query = state.get("task") or "Gaussian blur PSNR SSIM kernel size"
        results = retriever.retrieve(query=query, top_k=5)
        paper_context = [result.text for result in results]

        return {
            "paper_context": paper_context,
            "steps": _append_step(
                state,
                node,
                "ok",
                f"Retrieved {len(paper_context)} paper context chunks.",
                {"sources": [result.source for result in results]},
            ),
        }
    except Exception as error:
        return {
            "paper_context": [],
            "error": str(error),
            "failed_node": node,
            "steps": _append_step(state, node, "error", str(error)),
        }


def extract_experiment_spec_node(state: GraphAgentState) -> dict[str, Any]:
    """Extract an experiment specification from retrieved paper context."""
    node = "extract_experiment_spec"
    try:
        context = "\n\n".join(state.get("paper_context", []))
        spec = extract_experiment_spec(context)
        extracted_spec = {
            "method": spec.method,
            "params": spec.params,
            "metrics": spec.metrics,
            "raw_response": spec.raw_response,
        }

        return {
            "extracted_spec": extracted_spec,
            "steps": _append_step(
                state,
                node,
                "ok",
                f"Extracted method: {spec.method}.",
                {"method": spec.method, "metrics": spec.metrics},
            ),
        }
    except Exception as error:
        return {
            "extracted_spec": None,
            "error": str(error),
            "failed_node": node,
            "steps": _append_step(state, node, "error", str(error)),
        }


def run_experiment_node(state: GraphAgentState) -> dict[str, Any]:
    """Run the configured image processing experiment."""
    node = "run_experiment"
    try:
        config = load_experiment_config(state["config_path"])
        result = run_experiment(config)
        experiment_result = asdict(result)

        return {
            "experiment_result": experiment_result,
            **_clear_error_fields(),
            "steps": _append_step(
                state,
                node,
                "ok",
                f"Experiment completed: {result.experiment_name}.",
                {
                    "metrics_path": result.metrics_path,
                    "summary_path": result.summary_path,
                },
            ),
        }
    except Exception as error:
        return {
            "experiment_result": None,
            "error": str(error),
            "failed_node": node,
            "steps": _append_step(state, node, "error", str(error)),
        }


def analyze_metrics_node(state: GraphAgentState) -> dict[str, Any]:
    """Analyze experiment metrics from metrics.csv."""
    node = "analyze_metrics"
    try:
        experiment_result = state.get("experiment_result") or {}
        metrics_path = experiment_result.get("metrics_path")
        if not metrics_path or not Path(str(metrics_path)).is_file():
            analysis = "No metrics.csv was generated for this experiment."
            return {
                "metrics_analysis": analysis,
                **_clear_error_fields(),
                "steps": _append_step(state, node, "ok", analysis),
            }

        with Path(str(metrics_path)).open("r", newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        metric_values = ", ".join(
            f"{row.get('metric', '').upper()}={row.get('value', '')}" for row in rows
        )
        analysis = (
            "MSE 越低越好，PSNR 越高越好，SSIM 越接近 1 越好。"
            f" 当前指标：{metric_values}"
        )
        return {
            "metrics_analysis": analysis,
            **_clear_error_fields(),
            "steps": _append_step(
                state,
                node,
                "ok",
                "Metrics analyzed.",
                {"rows": rows},
            ),
        }
    except Exception as error:
        return {
            "metrics_analysis": None,
            "error": str(error),
            "failed_node": node,
            "steps": _append_step(state, node, "error", str(error)),
        }


def generate_report_node(state: GraphAgentState) -> dict[str, Any]:
    """Generate a Markdown report from experiment outputs and paper context."""
    node = "generate_report"
    try:
        experiment_result = state.get("experiment_result") or {}
        summary_path = str(experiment_result.get("summary_path", ""))
        metrics_path = experiment_result.get("metrics_path")
        output_dir = Path(str(experiment_result.get("output_dir", ".")))
        report_path = generate_markdown_report(
            ReportInput(
                summary_path=summary_path,
                metrics_path=str(metrics_path) if metrics_path else None,
                paper_context=state.get("paper_context", []),
                output_path=str(output_dir / "report.md"),
            )
        )
        final_answer = f"LangGraph report generated: {report_path}"

        return {
            "report_path": report_path,
            "final_answer": final_answer,
            **_clear_error_fields(),
            "steps": _append_step(
                state,
                node,
                "ok",
                "Report generated.",
                {"report_path": report_path},
            ),
        }
    except Exception as error:
        return {
            "report_path": None,
            "final_answer": f"LangGraph workflow failed: {error}",
            "error": str(error),
            "failed_node": node,
            "steps": _append_step(state, node, "error", str(error)),
        }


def diagnose_error_node(state: GraphAgentState) -> dict[str, Any]:
    """Diagnose the current workflow error and store structured details."""
    node = "diagnose_error"
    error_message = state.get("error") or "Unknown workflow error"
    failed_node = state.get("failed_node")
    diagnosis = build_error_diagnosis(
        error_message=error_message,
        failed_node=failed_node,
        retry_count=state.get("retry_count", 0),
    )

    steps = list(state.get("steps", []))
    steps.append(
        {
            "node": node,
            "status": "completed",
            "diagnosis": diagnosis,
        }
    )

    return {
        "diagnosis": diagnosis,
        "error_type": diagnosis["error_type"],
        "final_answer": f"LangGraph workflow failed: {error_message}",
        "steps": steps,
    }


def retry_failed_step_node(state: GraphAgentState) -> dict[str, Any]:
    """Record one retry attempt and prepare the workflow to retry the failed step."""
    node = "retry_failed_step"
    retry_count = state.get("retry_count", 0) + 1

    return {
        "retry_count": retry_count,
        **_clear_error_fields(),
        "steps": _append_step(
            state,
            node,
            "retrying",
            f"Retrying failed workflow step, attempt {retry_count}.",
            {"retry_count": retry_count},
        ),
    }
