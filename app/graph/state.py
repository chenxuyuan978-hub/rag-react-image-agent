from typing import Any, TypedDict


class GraphAgentState(TypedDict):
    """State passed between LangGraph agent workflow nodes."""

    task: str
    config_path: str
    paper_dir: str
    paper_context: list[str]
    extracted_spec: dict[str, Any] | None
    experiment_result: dict[str, Any] | None
    metrics_analysis: str | None
    report_path: str | None
    final_answer: str | None
    error: str | None
    error_type: str | None
    diagnosis: dict[str, Any] | None
    retry_count: int
    max_retries: int
    failed_node: str | None
    steps: list[dict[str, Any]]
