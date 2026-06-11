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
