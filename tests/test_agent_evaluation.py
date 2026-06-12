from app.evaluation.cases import AgentEvaluationCase, load_default_evaluation_cases
from app.evaluation.runner import (
    AgentEvaluationResult,
    run_evaluation_case,
    summarize_evaluation_results,
)
from scripts.prepare_demo_data import prepare_demo_data


def _get_case(case_id: str) -> AgentEvaluationCase:
    """Return one default evaluation case by id."""
    return next(
        case for case in load_default_evaluation_cases() if case.case_id == case_id
    )


def test_load_default_evaluation_cases_returns_three_unique_cases() -> None:
    """Check built-in evaluation cases are present and uniquely identified."""
    cases = load_default_evaluation_cases()
    case_ids = [case.case_id for case in cases]

    assert len(cases) >= 3
    assert all(case_ids)
    assert len(case_ids) == len(set(case_ids))


def test_run_evaluation_case_success_passes() -> None:
    """Check the normal success case passes the workflow evaluation."""
    prepare_demo_data()
    result = run_evaluation_case(_get_case("gaussian_blur_success"))

    assert result.passed is True
    assert "retrieve_paper_context" in result.actual_nodes
    assert "extract_experiment_spec" in result.actual_nodes
    assert "run_experiment" in result.actual_nodes
    assert "analyze_metrics" in result.actual_nodes
    assert "generate_report" in result.actual_nodes
    assert result.missing_nodes == []
    assert result.missing_outputs == []


def test_run_evaluation_case_missing_config_returns_error_result() -> None:
    """Check missing config evaluation does not crash the test process."""
    result = run_evaluation_case(_get_case("missing_config_error"))

    assert result.error or result.diagnosis
    assert "diagnose_error" in result.actual_nodes
    assert result.error_type == "config_error"


def test_summarize_evaluation_results_counts_passed_and_failed() -> None:
    """Check evaluation summaries count totals, passes, failures, and pass rate."""
    results = [
        AgentEvaluationResult(
            case_id="pass",
            name="pass",
            passed=True,
            expected_nodes=[],
            actual_nodes=[],
            missing_nodes=[],
            expected_outputs=[],
            missing_outputs=[],
            error=None,
            error_type=None,
            diagnosis=None,
            report_path=None,
        ),
        AgentEvaluationResult(
            case_id="fail",
            name="fail",
            passed=False,
            expected_nodes=[],
            actual_nodes=[],
            missing_nodes=[],
            expected_outputs=[],
            missing_outputs=[],
            error="failed",
            error_type="unknown_error",
            diagnosis=None,
            report_path=None,
        ),
    ]

    summary = summarize_evaluation_results(results)

    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 0.5
