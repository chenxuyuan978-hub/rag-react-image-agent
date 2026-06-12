from dataclasses import dataclass

from app.llm.config import LLMConfig


@dataclass
class FakeLLMClient:
    """Deterministic local LLM client for tests and offline development."""

    config: LLMConfig | None = None

    def generate(self, prompt: str) -> str:
        """Return a stable fake response without network access."""
        normalized_prompt = prompt.lower()
        keywords = ("gaussian blur", "psnr", "ssim", "mse")
        if any(keyword in normalized_prompt for keyword in keywords):
            return (
                "FakeLLM response: Gaussian blur denoising can be evaluated with "
                "MSE, PSNR, and SSIM. A typical experiment setting may use "
                "kernel size 5."
            )

        return "FakeLLM response: offline deterministic text generation is enabled."
