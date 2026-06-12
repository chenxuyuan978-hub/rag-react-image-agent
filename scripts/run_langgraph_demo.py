import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.workflow import run_langgraph_agent  # noqa: E402
from scripts.prepare_demo_data import prepare_demo_data  # noqa: E402


def main() -> int:
    """Run the LangGraph demo workflow and print its execution steps."""
    prepare_demo_data()
    state = run_langgraph_agent(
        task="根据论文中的 Gaussian Blur 去噪实验设置运行实验并生成报告",
        config_path="examples/demo_config.yaml",
        paper_dir="data/papers",
    )

    langsmith_step = next(
        (
            step
            for step in state.get("steps", [])
            if step.get("node") == "configure_langsmith"
        ),
        {},
    )
    tracing_enabled = bool(
        langsmith_step.get("data", {}).get("langsmith_tracing_enabled", False)
    )
    print(f"langsmith_tracing_enabled: {tracing_enabled}")
    if not tracing_enabled:
        print(
            "LangSmith tracing disabled. Set LANGSMITH_TRACING=true and "
            "LANGSMITH_API_KEY to enable it."
        )

    for step in state.get("steps", []):
        print(step)

    print(f"final_answer: {state.get('final_answer')}")
    print(f"report_path: {state.get('report_path')}")
    print(f"error: {state.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
