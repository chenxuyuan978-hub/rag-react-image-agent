import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""

    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    temperature: float
    timeout_seconds: int


def _get_optional_env(name: str) -> str | None:
    """Read an optional environment variable, treating empty strings as missing."""
    value = os.getenv(name)
    if value is None:
        return None

    stripped_value = value.strip()
    return stripped_value or None


def _get_float_env(name: str, default: float) -> float:
    """Read a float environment variable with a safe default."""
    value = _get_optional_env(name)
    if value is None:
        return default
    return float(value)


def _get_int_env(name: str, default: int) -> int:
    """Read an integer environment variable with a safe default."""
    value = _get_optional_env(name)
    if value is None:
        return default
    return int(value)


def load_llm_config() -> LLMConfig:
    """Load LLM configuration from environment variables."""
    return LLMConfig(
        provider=_get_optional_env("LLM_PROVIDER") or "fake",
        model=_get_optional_env("LLM_MODEL") or "fake-local",
        api_key=_get_optional_env("LLM_API_KEY"),
        base_url=_get_optional_env("LLM_BASE_URL"),
        temperature=_get_float_env("LLM_TEMPERATURE", 0.0),
        timeout_seconds=_get_int_env("LLM_TIMEOUT_SECONDS", 60),
    )
