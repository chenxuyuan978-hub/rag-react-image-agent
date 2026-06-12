from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for the health endpoint."""

    status: str


class ExperimentRunRequest(BaseModel):
    """Request schema for running an experiment from a YAML config."""

    config_path: str


class ExperimentRunResponse(BaseModel):
    """Response schema for an experiment run."""

    run_id: str
    run_dir: str
    experiment_name: str
    output_dir: str
    metrics_path: str | None
    summary_path: str


class ComparisonRunRequest(BaseModel):
    """Request schema for running a comparison experiment from YAML."""

    config_path: str


class ComparisonRunResponse(BaseModel):
    """Response schema for a comparison experiment run."""

    comparison_name: str
    run_id: str
    run_dir: str
    metrics_path: str
    summary_path: str


class AgentRunRequest(BaseModel):
    """Request schema for running the minimal ReAct agent."""

    task: str
    config_path: str
    paper_dir: str = "data/papers"


class AgentRunResponse(BaseModel):
    """Response schema for a ReAct agent run."""

    run_id: str
    run_dir: str
    trace: str
    final_answer: str


class LangGraphAgentRunRequest(BaseModel):
    """Request schema for running the LangGraph agent workflow."""

    task: str
    config_path: str = "examples/demo_config.yaml"
    paper_dir: str = "data/papers"


class LangGraphAgentRunResponse(BaseModel):
    """Response schema for a LangGraph agent workflow run."""

    final_answer: str | None
    report_path: str | None
    error: str | None
    error_type: str | None
    diagnosis: dict[str, Any] | None
    retry_count: int
    metrics_analysis: str | None
    extracted_spec: dict[str, Any] | None
    steps: list[dict[str, Any]]
    langsmith_tracing_enabled: bool
    paper_context_count: int


class ReportResponse(BaseModel):
    """Response schema for reading a Markdown report."""

    report_name: str
    content: str


class RunSummaryResponse(BaseModel):
    """Response schema for one archived run summary."""

    run_id: str
    run_dir: str
    experiment_name: str | None
    created_at: str | None
    has_metrics: bool
    has_summary: bool
    has_report: bool
    metrics_path: str | None
    summary_path: str | None
    report_path: str | None


class RunDetailResponse(BaseModel):
    """Response schema for one archived run detail."""

    run_id: str
    run_dir: str
    summary: dict[str, Any] | None
    metrics: list[dict[str, str]] | None
    report_text: str | None
    trace_text: str | None
    output_images: list[str]
