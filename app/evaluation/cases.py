from dataclasses import dataclass


@dataclass
class AgentEvaluationCase:
    """A single expected-behavior case for the LangGraph Agent workflow."""

    case_id: str
    name: str
    task: str
    config_path: str
    paper_dir: str
    expected_nodes: list[str]
    expected_outputs: list[str]
    expect_error: bool
    expected_error_type: str | None


def load_default_evaluation_cases() -> list[AgentEvaluationCase]:
    """Load the built-in LangGraph Agent workflow evaluation cases."""
    success_nodes = [
        "retrieve_paper_context",
        "extract_experiment_spec",
        "run_experiment",
        "analyze_metrics",
        "generate_report",
    ]

    return [
        AgentEvaluationCase(
            case_id="gaussian_blur_success",
            name="Gaussian blur workflow success",
            task="根据论文中的 Gaussian Blur 去噪实验设置运行实验并生成报告",
            config_path="examples/demo_config.yaml",
            paper_dir="data/papers",
            expected_nodes=success_nodes,
            expected_outputs=["final_answer", "report_path"],
            expect_error=False,
            expected_error_type=None,
        ),
        AgentEvaluationCase(
            case_id="missing_config_error",
            name="Missing config path error handling",
            task="使用不存在的配置文件运行实验",
            config_path="examples/not_exists.yaml",
            paper_dir="data/papers",
            expected_nodes=[
                "retrieve_paper_context",
                "extract_experiment_spec",
                "run_experiment",
                "diagnose_error",
            ],
            expected_outputs=["error", "diagnosis"],
            expect_error=True,
            expected_error_type="config_error",
        ),
        AgentEvaluationCase(
            case_id="empty_paper_dir",
            name="Empty paper directory workflow success",
            task="在没有论文片段的情况下运行基础实验并生成报告",
            config_path="examples/demo_config.yaml",
            paper_dir="tests/not_existing_eval_papers",
            expected_nodes=success_nodes,
            expected_outputs=["final_answer"],
            expect_error=False,
            expected_error_type=None,
        ),
    ]
