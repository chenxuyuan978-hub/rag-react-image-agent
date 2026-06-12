from app.llm.config import load_llm_config


def test_load_llm_config_defaults_to_fake(monkeypatch) -> None:
    """Check that missing environment variables load a safe fake config."""
    for name in [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_TEMPERATURE",
        "LLM_TIMEOUT_SECONDS",
    ]:
        monkeypatch.delenv(name, raising=False)

    config = load_llm_config()

    assert config.provider == "fake"
    assert config.model == "fake-local"
    assert config.api_key is None
    assert config.base_url is None
    assert config.temperature == 0.0
    assert config.timeout_seconds == 60


def test_load_llm_config_parses_temperature_and_timeout(monkeypatch) -> None:
    """Check that numeric LLM environment variables are parsed correctly."""
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_MODEL", "fake-test")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.25")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "120")

    config = load_llm_config()

    assert config.provider == "fake"
    assert config.model == "fake-test"
    assert config.temperature == 0.25
    assert config.timeout_seconds == 120


def test_load_llm_config_allows_missing_api_key(monkeypatch) -> None:
    """Check that missing API keys do not break configuration loading."""
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    config = load_llm_config()

    assert config.api_key is None
