import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.llm.extractors import extract_experiment_spec  # noqa: E402


def main() -> int:
    """Run a local FakeLLM experiment extraction demo."""
    context = (
        "In the image denoising experiment, we apply Gaussian blur with "
        "kernel size 5. The restored images are evaluated using MSE, PSNR, "
        "and SSIM."
    )
    spec = extract_experiment_spec(context)

    print(f"method: {spec.method}")
    print(f"params: {spec.params}")
    print(f"metrics: {spec.metrics}")
    print(f"raw_response: {spec.raw_response}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
