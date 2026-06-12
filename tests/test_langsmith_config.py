import os

from app.observability.langsmith_config import (
    configure_langsmith_environment,
    load_langsmith_config,
)


def test_langsmith_config_defaults_to_disabled(monkeypatch) -> None:
    """Check that LangSmith tracing is disabled without environment variables."""
    for name in [
        "LANGSMITH_TRACING",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        "LANGSMITH_ENDPOINT",
    ]:
        monkeypatch.delenv(name, raising=False)

    config = load_langsmith_config()

    assert config.tracing_enabled is False
    assert config.api_key is None
    assert config.project == "rag-react-image-agent"
    assert config.endpoint is None


def test_langsmith_config_true_without_api_key_configures_disabled(
    monkeypatch,
) -> None:
    """Check that tracing=true without an API key does not enable tracing."""
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)

    config = load_langsmith_config()
    enabled = configure_langsmith_environment(config)

    assert config.tracing_enabled is False
    assert enabled is False
    assert config.project == "rag-react-image-agent"
    assert os.environ["LANGSMITH_TRACING"] == "false"


def test_langsmith_config_true_with_api_key_configures_enabled(monkeypatch) -> None:
    """Check that tracing is enabled when requested with an API key."""
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    monkeypatch.setenv("LANGSMITH_ENDPOINT", "https://example.test")

    config = load_langsmith_config()
    enabled = configure_langsmith_environment(config)

    assert config.tracing_enabled is True
    assert enabled is True
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "test-key"
    assert os.environ["LANGSMITH_PROJECT"] == "test-project"
    assert os.environ["LANGSMITH_ENDPOINT"] == "https://example.test"


def test_langsmith_boolean_parsing(monkeypatch) -> None:
    """Check supported boolean spellings for LANGSMITH_TRACING."""
    for value in ["true", "1", "yes"]:
        monkeypatch.setenv("LANGSMITH_TRACING", value)
        monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
        assert load_langsmith_config().tracing_enabled is True

    for value in ["false", "0", "no"]:
        monkeypatch.setenv("LANGSMITH_TRACING", value)
        monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
        assert load_langsmith_config().tracing_enabled is False
