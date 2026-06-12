from app.llm.client import get_llm_client
from app.llm.config import LLMConfig
from app.llm.fake_client import FakeLLMClient


def test_get_llm_client_defaults_to_fake(monkeypatch) -> None:
    """Check that the default client is FakeLLMClient."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    client = get_llm_client()

    assert isinstance(client, FakeLLMClient)


def test_fake_llm_client_generate_returns_stable_string() -> None:
    """Check that FakeLLMClient returns deterministic text."""
    client = FakeLLMClient()
    prompt = "Gaussian blur with PSNR SSIM MSE"

    first_response = client.generate(prompt)
    second_response = client.generate(prompt)

    assert isinstance(first_response, str)
    assert first_response == second_response
    assert "Gaussian blur" in first_response
    assert "PSNR" in first_response
    assert "SSIM" in first_response
    assert "MSE" in first_response


def test_get_llm_client_uses_fake_for_unknown_provider() -> None:
    """Check that unknown providers safely fall back to FakeLLMClient."""
    config = LLMConfig(
        provider="unknown",
        model="future-model",
        api_key=None,
        base_url=None,
        temperature=0.0,
        timeout_seconds=60,
    )

    client = get_llm_client(config)

    assert isinstance(client, FakeLLMClient)
    assert isinstance(client.generate("hello"), str)
