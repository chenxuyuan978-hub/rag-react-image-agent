from typing import Protocol

from app.llm.config import LLMConfig, load_llm_config
from app.llm.fake_client import FakeLLMClient


class LLMClient(Protocol):
    """Protocol for text generation clients."""

    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""


def get_llm_client(config: LLMConfig | None = None) -> LLMClient:
    """Return an LLM client for the configured provider."""
    resolved_config = config or load_llm_config()
    provider = resolved_config.provider.strip().lower()

    if provider == "fake":
        return FakeLLMClient(config=resolved_config)

    return FakeLLMClient(config=resolved_config)
