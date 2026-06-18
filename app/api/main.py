import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException

from app.api.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    ComparisonRunRequest,
    ComparisonRunResponse,
    ExperimentRunRequest,
    ExperimentRunResponse,
    HealthResponse,
    LangGraphAgentRunRequest,
    LangGraphAgentRunResponse,
    ReportResponse,
    ReproductionIntakeRequest,
    ReproductionIntakeResponse,
    ReproductionRunSummaryResponse,
    RunDetailResponse,
    RunSummaryResponse,
)
from app.core.run_detail import get_run_detail
from app.core.run_history import get_run_summary, list_runs
from app.core.run_manager import copy_file_to_run, create_run_dir
from app.experiments.comparison_runner import load_comparison_config, run_comparison
from app.experiments.config_schema import load_experiment_config
from app.experiments.experiment_runner import run_experiment
from app.graph.workflow import run_langgraph_agent
from app.react.agent import ReActAgent
from app.reproduction.intake import run_reproduction_intake
from app.reproduction.schemas import ReproductionIntakeInput
from app.utils.errors import AppError, ConfigError
from app.utils.logger import get_logger

logger = get_logger(__name__)
REPRODUCTION_RUNS_DIR = Path("data/reproduction_runs")


app = FastAPI(
    title="RAG ReAct Image Agent API",
    description="FastAPI backend for the local RAG + ReAct image reproduction agent.",
    version="0.1.0",
)


def resolve_report_path(report_name: str) -> Path:
    """Resolve a report path under data/outputs and block path traversal."""
    if not report_name or Path(report_name).is_absolute():
        raise HTTPException(status_code=400, detail="Invalid report path")

    base_dir = Path("data/outputs").resolve()
    report_path = (base_dir / report_name).resolve()

    try:
        report_path.relative_to(base_dir)
    except ValueError as error:
        raise HTTPException(
            status_code=400, detail="Report path is outside data/outputs"
        ) from error

    if not report_path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")

    return report_path


def write_archived_config(config_path: str, run_dir: str) -> str:
    """Copy a config into a run directory with output_dir set to that run directory."""
    source_path = Path(config_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_config = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_config, dict):
        raise ConfigError("Experiment config must be a mapping", "CONFIG_INVALID_ROOT")

    raw_config["output_dir"] = run_dir
    archived_path = Path(run_dir) / "config.yaml"
    archived_path.write_text(
        yaml.safe_dump(raw_config, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return str(archived_path)


def get_langsmith_tracing_status(steps: list[dict[str, Any]]) -> bool:
    """Return whether LangSmith tracing was enabled for a workflow state."""
    langsmith_step = next(
        (step for step in steps if step.get("node") == "configure_langsmith"),
        {},
    )
    return bool(langsmith_step.get("data", {}).get("langsmith_tracing_enabled", False))


def _resolve_reproduction_run_dir(run_id: str) -> Path:
    """Resolve a reproduction run directory and block path traversal."""
    if not run_id or Path(run_id).is_absolute():
        raise HTTPException(status_code=400, detail="Invalid reproduction run_id")

    base_dir = REPRODUCTION_RUNS_DIR.resolve()
    run_dir = (base_dir / run_id).resolve()
    try:
        run_dir.relative_to(base_dir)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail="Reproduction run path is outside data/reproduction_runs",
        ) from error

    if not run_dir.is_dir():
        raise HTTPException(status_code=404, detail="Reproduction run not found")
    return run_dir


def _read_reproduction_summary(run_id: str) -> dict[str, Any]:
    """Read one reproduction run intake summary JSON."""
    run_dir = _resolve_reproduction_run_dir(run_id)
    summary_path = run_dir / "intake_summary.json"
    if not summary_path.is_file():
        raise HTTPException(status_code=404, detail="Intake summary not found")
    return json.loads(summary_path.read_text(encoding="utf-8"))


def _build_reproduction_run_list_item(run_dir: Path) -> ReproductionRunSummaryResponse:
    """Build one reproduction run list response from its summary when available."""
    summary_path = run_dir / "intake_summary.json"
    summary: dict[str, Any] = {}
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

    created_at = datetime.fromtimestamp(run_dir.stat().st_mtime).isoformat(
        timespec="seconds"
    )
    return ReproductionRunSummaryResponse(
        run_id=run_dir.name,
        status=summary.get("status"),
        workspace_dir=summary.get("workspace_dir", str(run_dir)),
        paper_text_chars=summary.get("paper_text_chars"),
        source_file_count=summary.get("source_file_count"),
        created_at=created_at,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API health status."""
    return HealthResponse(status="ok")


@app.post("/api/experiments/run", response_model=ExperimentRunResponse)
def run_experiment_api(request: ExperimentRunRequest) -> ExperimentRunResponse:
    """Run an image processing experiment from an existing YAML config."""
    try:
        config = load_experiment_config(request.config_path)
        run_info = create_run_dir(config.experiment_name)
        copy_file_to_run(request.config_path, run_info.run_dir, "config.yaml")
        result = run_experiment(config, run_dir=run_info.run_dir)
        return ExperimentRunResponse(
            run_id=run_info.run_id,
            run_dir=run_info.run_dir,
            experiment_name=result.experiment_name,
            output_dir=result.output_dir,
            metrics_path=result.metrics_path,
            summary_path=result.summary_path,
        )
    except FileNotFoundError as error:
        logger.error("Experiment API file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except AppError as error:
        logger.error("Experiment API application error: %s", error)
        raise HTTPException(status_code=400, detail=error.message) from error
    except ValueError as error:
        logger.error("Experiment API validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/experiments/compare", response_model=ComparisonRunResponse)
def run_comparison_api(request: ComparisonRunRequest) -> ComparisonRunResponse:
    """Run a multi-method comparison experiment from an existing YAML config."""
    try:
        config = load_comparison_config(request.config_path)
        run_info = create_run_dir(config.comparison_name)
        copy_file_to_run(
            request.config_path, run_info.run_dir, "comparison_config.yaml"
        )
        result = run_comparison(config, run_dir=run_info.run_dir)
        return ComparisonRunResponse(
            comparison_name=str(result["comparison_name"]),
            run_id=run_info.run_id,
            run_dir=run_info.run_dir,
            metrics_path=str(result["metrics_path"]),
            summary_path=str(result["summary_path"]),
        )
    except FileNotFoundError as error:
        logger.error("Comparison API file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except AppError as error:
        logger.error("Comparison API application error: %s", error)
        raise HTTPException(status_code=400, detail=error.message) from error
    except ValueError as error:
        logger.error("Comparison API validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/agent/run", response_model=AgentRunResponse)
def run_agent_api(request: AgentRunRequest) -> AgentRunResponse:
    """Run the minimal ReAct agent and return its trace."""
    try:
        config = load_experiment_config(request.config_path)
        run_info = create_run_dir(config.experiment_name)
        archived_config_path = write_archived_config(
            request.config_path, run_info.run_dir
        )
        trace = ReActAgent().run(
            task=request.task,
            config_path=archived_config_path,
            paper_dir=request.paper_dir,
        )
        trace_path = Path(run_info.run_dir) / "trace.txt"
        trace_text = trace.to_text()
        trace_path.write_text(trace_text, encoding="utf-8")
        return AgentRunResponse(
            run_id=run_info.run_id,
            run_dir=run_info.run_dir,
            trace=trace_text,
            final_answer=trace.final_answer,
        )
    except FileNotFoundError as error:
        logger.error("Agent API file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except AppError as error:
        logger.error("Agent API application error: %s", error)
        raise HTTPException(status_code=400, detail=error.message) from error
    except ValueError as error:
        logger.error("Agent API validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/agent/langgraph/run", response_model=LangGraphAgentRunResponse)
def run_langgraph_agent_api(
    request: LangGraphAgentRunRequest,
) -> LangGraphAgentRunResponse:
    """Run the LangGraph agent workflow and return a frontend-friendly state."""
    try:
        state = run_langgraph_agent(
            task=request.task,
            config_path=request.config_path,
            paper_dir=request.paper_dir,
        )
        steps = state.get("steps", [])
        return LangGraphAgentRunResponse(
            final_answer=state.get("final_answer"),
            report_path=state.get("report_path"),
            error=state.get("error"),
            error_type=state.get("error_type"),
            diagnosis=state.get("diagnosis"),
            retry_count=state.get("retry_count", 0),
            metrics_analysis=state.get("metrics_analysis"),
            extracted_spec=state.get("extracted_spec"),
            steps=steps,
            langsmith_tracing_enabled=get_langsmith_tracing_status(steps),
            paper_context_count=len(state.get("paper_context", [])),
        )
    except Exception as error:
        logger.error("LangGraph agent API error: %s", error)
        return LangGraphAgentRunResponse(
            final_answer="LangGraph workflow failed before returning state.",
            report_path=None,
            error=str(error),
            error_type="unknown_error",
            diagnosis=None,
            retry_count=0,
            metrics_analysis=None,
            extracted_spec=None,
            steps=[],
            langsmith_tracing_enabled=False,
            paper_context_count=0,
        )


@app.post("/api/reproduction/intake", response_model=ReproductionIntakeResponse)
def run_reproduction_intake_api(
    request: ReproductionIntakeRequest,
) -> ReproductionIntakeResponse:
    """Create a real paper and source intake workspace."""
    if not request.paper_path.strip() or not request.source_path.strip():
        raise HTTPException(
            status_code=400,
            detail="paper_path and source_path are required",
        )

    try:
        summary = run_reproduction_intake(
            ReproductionIntakeInput(
                paper_path=request.paper_path,
                source_path=request.source_path,
                base_dir=str(REPRODUCTION_RUNS_DIR),
            )
        )
        return ReproductionIntakeResponse(**asdict(summary))
    except FileNotFoundError as error:
        logger.error("Reproduction intake file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        logger.error("Reproduction intake validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.error("Reproduction intake API error: %s", error)
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get(
    "/api/reproduction/runs",
    response_model=list[ReproductionRunSummaryResponse],
)
def list_reproduction_runs_api() -> list[ReproductionRunSummaryResponse]:
    """List existing reproduction intake runs."""
    base_dir = REPRODUCTION_RUNS_DIR
    if not base_dir.is_dir():
        return []

    run_dirs = [path for path in base_dir.iterdir() if path.is_dir()]
    run_dirs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return [_build_reproduction_run_list_item(run_dir) for run_dir in run_dirs]


@app.get(
    "/api/reproduction/runs/{run_id}",
    response_model=ReproductionIntakeResponse,
)
def get_reproduction_run_api(run_id: str) -> ReproductionIntakeResponse:
    """Return one reproduction intake summary by run_id."""
    summary = _read_reproduction_summary(run_id)
    return ReproductionIntakeResponse(**summary)


@app.get("/api/reports/{report_name:path}", response_model=ReportResponse)
def read_report_api(report_name: str) -> ReportResponse:
    """Read a Markdown report from data/outputs."""
    report_path = resolve_report_path(report_name)
    return ReportResponse(
        report_name=report_name,
        content=report_path.read_text(encoding="utf-8"),
    )


@app.get("/api/runs", response_model=list[RunSummaryResponse])
def list_runs_api() -> list[RunSummaryResponse]:
    """Return summaries for all archived runs."""
    runs = list_runs()
    return [RunSummaryResponse(**asdict(run)) for run in runs]


@app.get("/api/runs/{run_id}", response_model=RunSummaryResponse)
def get_run_summary_api(run_id: str) -> RunSummaryResponse:
    """Return one archived run summary by run_id."""
    try:
        run_summary = get_run_summary(run_id)
        return RunSummaryResponse(**asdict(run_summary))
    except FileNotFoundError as error:
        logger.error("Run summary API file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        logger.error("Run summary API validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/runs/{run_id}/detail", response_model=RunDetailResponse)
def get_run_detail_api(run_id: str) -> RunDetailResponse:
    """Return detailed files and metadata for one archived run."""
    try:
        run_detail = get_run_detail(run_id)
        return RunDetailResponse(**asdict(run_detail))
    except FileNotFoundError as error:
        logger.error("Run detail API file error: %s", error)
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        logger.error("Run detail API validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error
