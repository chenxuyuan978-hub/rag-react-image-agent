import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.runner import (  # noqa: E402
    run_default_evaluation_cases,
    summarize_evaluation_results,
)
from scripts.prepare_demo_data import prepare_demo_data  # noqa: E402


def main() -> int:
    """Run the default LangGraph Agent evaluation cases and print results."""
    prepare_demo_data()
    results = run_default_evaluation_cases()

    for result in results:
        print(f"case_id: {result.case_id}")
        print(f"name: {result.name}")
        print(f"passed: {result.passed}")
        print(f"missing_nodes: {result.missing_nodes}")
        print(f"missing_outputs: {result.missing_outputs}")
        print(f"error_type: {result.error_type}")
        print(f"report_path: {result.report_path}")
        if result.error:
            print(f"error: {result.error}")
        print()

    summary = summarize_evaluation_results(results)
    print("summary:")
    print(f"total: {summary['total']}")
    print(f"passed: {summary['passed']}")
    print(f"failed: {summary['failed']}")
    print(f"pass_rate: {summary['pass_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
