import logging

import pytest
from fastapi import HTTPException

from app.api.main import run_experiment_api
from app.api.schemas import ExperimentRunRequest
from app.react.tools import RagRetrieveTool
from app.utils.errors import (
    AgentError,
    AppError,
    ConfigError,
    ExperimentError,
    RagError,
    ReportError,
)
from app.utils.logger import get_logger


def test_get_logger_does_not_add_duplicate_handlers() -> None:
    """Check that repeated get_logger calls do not duplicate handlers."""
    logger_name = "tests.error_handling.logger"
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()

    first_logger = get_logger(logger_name)
    first_count = len(first_logger.handlers)
    second_logger = get_logger(logger_name)

    assert first_logger is second_logger
    assert len(second_logger.handlers) == first_count


def test_custom_errors_can_be_created() -> None:
    """Check that project custom errors keep message and code."""
    errors = [
        AppError("app failed", "APP_ERROR"),
        ConfigError("config failed", "CONFIG_ERROR"),
        ExperimentError("experiment failed", "EXPERIMENT_ERROR"),
        RagError("rag failed", "RAG_ERROR"),
        AgentError("agent failed", "AGENT_ERROR"),
        ReportError("report failed", "REPORT_ERROR"),
    ]

    for error in errors:
        assert str(error)
        assert error.message
        assert error.error_code is not None


def test_api_error_returns_clear_http_exception() -> None:
    """Check that API errors are converted to clear HTTPException details."""
    with pytest.raises(HTTPException) as error:
        run_experiment_api(ExperimentRunRequest(config_path="missing_config.yaml"))

    assert error.value.status_code == 404
    assert "missing_config.yaml" in str(error.value.detail)


def test_tool_layer_returns_success_false_on_error() -> None:
    """Check that tool errors return success=false instead of crashing."""
    result = RagRetrieveTool().run(
        {"query": "Gaussian blur", "paper_dir": "missing_papers", "top_k": 1}
    )

    assert result["success"] is False
    assert "error" in result
