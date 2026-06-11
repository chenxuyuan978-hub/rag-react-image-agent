import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.react.agent import ReActAgent
from scripts.prepare_demo_data import prepare_demo_data


def ensure_demo_paper() -> Path:
    """Ensure the demo paper used by the ReAct demo exists."""
    paper_path = Path("examples/demo_paper.md")
    if not paper_path.is_file():
        raise FileNotFoundError(f"Demo paper not found: {paper_path}")
    return paper_path


def main() -> int:
    """Run the minimal ReAct demo and print the full trace."""
    prepare_demo_data()
    ensure_demo_paper()

    agent = ReActAgent()
    trace = agent.run(
        task="根据论文中的去噪实验设置，对示例图像做高斯滤波实验，并生成报告。",
        config_path="examples/demo_config.yaml",
        paper_dir="examples",
    )
    print(trace.to_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
