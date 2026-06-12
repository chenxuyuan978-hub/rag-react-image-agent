import json
from dataclasses import dataclass

from app.llm.config import LLMConfig


@dataclass
class FakeLLMClient:
    """Deterministic local LLM client for tests and offline development."""

    config: LLMConfig | None = None

    def generate(self, prompt: str) -> str:
        """Return a stable fake response without network access."""
        normalized_prompt = prompt.lower()
        keywords = ("gaussian blur", "kernel size", "psnr", "ssim", "mse")
        if any(keyword in normalized_prompt for keyword in keywords):
            return json.dumps(
                {
                    "method": "gaussian_blur",
                    "params": {"kernel_size": 5},
                    "metrics": ["mse", "psnr", "ssim"],
                    "notes": (
                        "Gaussian blur experiment uses kernel size 5 and "
                        "evaluates MSE, PSNR, and SSIM."
                    ),
                },
                ensure_ascii=False,
            )

        return "FakeLLM response: offline deterministic text generation is enabled."
