from typing import Any


def classify_error(error_message: str) -> str:
    """Classify an error message into a stable workflow error type."""
    message = error_message.lower()

    if any(keyword in message for keyword in ["config", "yaml", "config_path"]):
        return "config_error"
    if any(
        keyword in message
        for keyword in [
            "file not found",
            "not found",
            "does not exist",
            "no such file",
            "path",
            "image file",
        ]
    ):
        return "file_not_found"
    if any(
        keyword in message
        for keyword in ["metrics.csv", "metric", "mse", "psnr", "ssim"]
    ):
        return "metrics_error"
    if any(keyword in message for keyword in ["report", "report.md", "markdown"]):
        return "report_error"
    if any(
        keyword in message
        for keyword in [
            "experiment",
            "operation",
            "image processing",
            "processor",
            "unknown operation",
        ]
    ):
        return "experiment_error"
    return "unknown_error"


def _reason_and_action(error_type: str) -> tuple[str, str, bool]:
    """Return stable diagnosis text and retryability for one error type."""
    if error_type == "config_error":
        return (
            "The experiment configuration is missing, invalid, or cannot be parsed.",
            "Check the YAML config path and required fields before running again.",
            False,
        )
    if error_type == "file_not_found":
        return (
            "A required input, reference, config, or output file is missing.",
            "Verify file paths and regenerate demo data if needed.",
            True,
        )
    if error_type == "experiment_error":
        return (
            "The image processing experiment failed during execution.",
            "Check operation names, parameters, and image compatibility.",
            True,
        )
    if error_type == "metrics_error":
        return (
            "The workflow could not read or compute experiment metrics.",
            "Check metrics.csv and ensure a reference image is configured.",
            True,
        )
    if error_type == "report_error":
        return (
            "The workflow could not generate or read the Markdown report.",
            "Check summary and metrics paths before generating the report again.",
            True,
        )
    return (
        "The workflow failed for an unknown reason.",
        "Inspect the original error message and workflow steps.",
        False,
    )


def build_error_diagnosis(
    error_message: str,
    failed_node: str | None = None,
    retry_count: int = 0,
) -> dict[str, Any]:
    """Build a stable structured diagnosis for a workflow error."""
    error_type = classify_error(error_message)
    possible_reason, suggested_action, retryable = _reason_and_action(error_type)

    return {
        "error_type": error_type,
        "failed_node": failed_node,
        "message": error_message,
        "possible_reason": possible_reason,
        "suggested_action": suggested_action,
        "retryable": retryable,
        "retry_count": retry_count,
    }


def should_retry(
    diagnosis: dict[str, Any],
    retry_count: int,
    max_retries: int,
) -> bool:
    """Return whether the workflow should retry a failed step."""
    return bool(diagnosis.get("retryable")) and retry_count < max_retries
