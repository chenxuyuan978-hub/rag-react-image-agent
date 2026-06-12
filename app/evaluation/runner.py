from dataclasses import dataclass
from typing import Any

from app.evaluation.cases import AgentEvaluationCase, load_default_evaluation_cases
from app.graph.workflow import run_langgraph_agent


@dataclass
class AgentEvaluationResult:
    """Structured result for one LangGraph Agent evaluation case."""

    case_id: str
    name: str
    passed: bool
    expected_nodes: list[str]
    actual_nodes: list[str]
    missing_nodes: list[str]
    expected_outputs: list[str]
    missing_outputs: list[str]
    error: str | None
    error_type: str | None
    diagnosis: dict[str, Any] | None
    report_path: str | None


def _has_output(state: dict[str, Any], output_name: str) -> bool:
    """Return whether a named state output is present and meaningful."""
    value = state.get(output_name)
    if value is None:
        return False
    if isinstance(value, str) and not value:
        return False
    return not (isinstance(value, list | dict) and not value)


def run_evaluation_case(case: AgentEvaluationCase) -> AgentEvaluationResult:
    """Run one Agent evaluation case and return a structured result."""
    state: dict[str, Any] = {}
    caught_error: str | None = None

    try:
        state = dict(
            run_langgraph_agent(
                task=case.task,
                config_path=case.config_path,
                paper_dir=case.paper_dir,
            )
        )
    except Exception as error:
        caught_error = str(error)

    steps = state.get("steps", [])
    actual_nodes = [
        str(step.get("node"))
        for step in steps
        if isinstance(step, dict) and step.get("node")
    ]
    missing_nodes = [node for node in case.expected_nodes if node not in actual_nodes]
    missing_outputs = [
        output for output in case.expected_outputs if not _has_output(state, output)
    ]

    workflow_error = state.get("error") or caught_error
    error_type = state.get("error_type")
    diagnosis = state.get("diagnosis")
    has_error_signal = bool(workflow_error or diagnosis)
    error_expectation_passed = (
        has_error_signal if case.expect_error else not has_error_signal
    )
    error_type_passed = (
        case.expected_error_type is None or error_type == case.expected_error_type
    )
    passed = (
        not missing_nodes
        and not missing_outputs
        and error_expectation_passed
        and error_type_passed
        and caught_error is None
    )

    return AgentEvaluationResult(
        case_id=case.case_id,
        name=case.name,
        passed=passed,
        expected_nodes=case.expected_nodes,
        actual_nodes=actual_nodes,
        missing_nodes=missing_nodes,
        expected_outputs=case.expected_outputs,
        missing_outputs=missing_outputs,
        error=str(workflow_error) if workflow_error else None,
        error_type=str(error_type) if error_type else None,
        diagnosis=diagnosis if isinstance(diagnosis, dict) else None,
        report_path=str(state.get("report_path")) if state.get("report_path") else None,
    )


def run_default_evaluation_cases() -> list[AgentEvaluationResult]:
    """Run all built-in Agent evaluation cases."""
    return [run_evaluation_case(case) for case in load_default_evaluation_cases()]


def summarize_evaluation_results(
    results: list[AgentEvaluationResult],
) -> dict[str, float | int]:
    """Summarize Agent evaluation results with counts and pass rate."""
    total = len(results)
    passed = sum(1 for result in results if result.passed)
    failed = total - passed
    pass_rate = passed / total if total else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
    }
