import os
from dataclasses import dataclass

TRUE_VALUES = {"true", "1", "yes", "y", "on"}
FALSE_VALUES = {"false", "0", "no", "n", "off", ""}


@dataclass
class LangSmithConfig:
    """Configuration for optional LangSmith tracing."""

    tracing_enabled: bool
    api_key: str | None
    project: str
    endpoint: str | None


def _get_optional_env(name: str) -> str | None:
    """Read an optional environment variable, treating empty strings as missing."""
    value = os.getenv(name)
    if value is None:
        return None

    stripped_value = value.strip()
    return stripped_value or None


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse common boolean environment variable values."""
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return default


def load_langsmith_config() -> LangSmithConfig:
    """Load optional LangSmith tracing configuration from environment variables."""
    api_key = _get_optional_env("LANGSMITH_API_KEY")
    tracing_requested = _parse_bool(os.getenv("LANGSMITH_TRACING"), default=False)

    return LangSmithConfig(
        tracing_enabled=tracing_requested and api_key is not None,
        api_key=api_key,
        project=_get_optional_env("LANGSMITH_PROJECT") or "rag-react-image-agent",
        endpoint=_get_optional_env("LANGSMITH_ENDPOINT"),
    )


def configure_langsmith_environment(config: LangSmithConfig | None = None) -> bool:
    """Configure LangSmith environment variables if tracing is available."""
    resolved_config = config or load_langsmith_config()
    if resolved_config.tracing_enabled and resolved_config.api_key:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = resolved_config.api_key
        os.environ["LANGSMITH_PROJECT"] = resolved_config.project
        if resolved_config.endpoint:
            os.environ["LANGSMITH_ENDPOINT"] = resolved_config.endpoint
        return True

    os.environ["LANGSMITH_TRACING"] = "false"
    return False
