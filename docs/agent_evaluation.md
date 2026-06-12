# Agent Workflow Evaluation

Agent Workflow Evaluation is used to check whether the LangGraph Agent behaves
as expected across stable, repeatable workflow cases.

## Why Agent Evaluation Is Needed

A demo run can prove that the Agent ran once, but it cannot prove that the
workflow is stable over time. Agent Evaluation uses fixed cases to repeatedly
verify that the workflow still follows the expected path after the project
changes.

For an Agent project, the final output alone is not enough. We also need to
check whether the expected nodes were executed, whether important outputs were
generated, and whether failure cases are handled in a structured way.

Agent Evaluation helps answer questions such as:

- Did the Agent retrieve paper context before running the experiment?
- Did it extract an experiment specification?
- Did it run the experiment and analyze metrics?
- Did it generate a report?
- If something failed, did the workflow enter the diagnosis node instead of
  crashing?

## What Is Evaluated

The current evaluation checks:

- Node execution order and node coverage.
- Whether `retrieve_paper_context` was executed.
- Whether `extract_experiment_spec` was executed.
- Whether `run_experiment` was executed.
- Whether `analyze_metrics` was executed.
- Whether `generate_report` was executed.
- Whether error cases enter `diagnose_error`.
- Whether outputs include `final_answer`, `report_path`, `error`, or
  `diagnosis` when expected.
- Whether the workflow is stable without a real LLM API key.
- Whether the workflow is stable without a LangSmith API key.

## Default Evaluation Cases

The default evaluation suite currently contains three cases.

### gaussian_blur_success

This is the normal Gaussian Blur workflow. It verifies that the Agent can
complete paper retrieval, experiment specification extraction, experiment
execution, metric analysis, and Markdown report generation.

Expected nodes:

- `retrieve_paper_context`
- `extract_experiment_spec`
- `run_experiment`
- `analyze_metrics`
- `generate_report`

Expected outputs:

- `final_answer`
- `report_path`

### missing_config_error

This case intentionally uses a missing YAML config path. It verifies that the
Agent does not crash directly. Instead, the workflow should return an `error`
and a structured `diagnosis`.

Expected nodes:

- `retrieve_paper_context`
- `extract_experiment_spec`
- `run_experiment`
- `diagnose_error`

Expected outputs:

- `error`
- `diagnosis`

### empty_paper_dir

This case uses an empty or missing paper directory. It verifies that the Agent
can keep the basic experiment workflow stable even when no paper snippets are
available.

Expected nodes:

- `retrieve_paper_context`
- `extract_experiment_spec`
- `run_experiment`
- `analyze_metrics`
- `generate_report`

Expected outputs:

- `final_answer`

## How To Run

Run the default Agent evaluation suite from the project root:

```bash
python scripts/run_agent_evaluation.py
```

The script prints the result for each case:

- `case_id`
- `name`
- `passed`
- `missing_nodes`
- `missing_outputs`
- `error_type`
- `report_path`

At the end, it prints a summary:

- `total`
- `passed`
- `failed`
- `pass_rate`

## Agent Evaluation vs pytest

`pytest` mainly checks whether functions, modules, boundary conditions, and API
contracts are correct. It is good at verifying small units and deterministic
module behavior.

Agent Evaluation checks whether the complete Agent workflow finishes the task
as intended. It focuses on workflow-level behavior: node execution, output
completeness, and structured error handling.

These two checks are complementary. Agent Evaluation does not replace `pytest`,
and `pytest` does not replace Agent Evaluation. Together, they make the project
more reliable as the Agent becomes more capable.
