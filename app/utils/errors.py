class AppError(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Create an application error with an optional code."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConfigError(AppError, ValueError):
    """Raised when an experiment configuration is invalid."""


class ExperimentError(AppError, ValueError):
    """Raised when an image experiment cannot be completed."""


class RagError(AppError, ValueError, RuntimeError):
    """Raised when local RAG retrieval fails."""


class AgentError(AppError):
    """Raised when the rule-driven agent fails unexpectedly."""


class ReportError(AppError):
    """Raised when report generation fails."""
