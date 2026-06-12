from app.llm.extractors import ExperimentSpec, extract_experiment_spec


class PlainTextClient:
    """Test client that returns a non-JSON extraction response."""

    def generate(self, prompt: str) -> str:
        """Return a plain-text response with extractable settings."""
        return (
            "The experiment applies Gaussian blur with kernel size 5. "
            "Evaluation metrics include MSE, PSNR, and SSIM."
        )


class UnknownClient:
    """Test client that returns an uninformative response."""

    def generate(self, prompt: str) -> str:
        """Return text without method details."""
        return "No clear experiment setting is available."


def test_extract_experiment_spec_from_gaussian_blur_context() -> None:
    """Check that FakeLLM extracts Gaussian blur settings from paper context."""
    context = (
        "The image denoising experiment uses Gaussian blur with kernel size 5. "
        "We report MSE, PSNR, and SSIM."
    )

    spec = extract_experiment_spec(context)

    assert spec.method == "gaussian_blur"
    assert spec.params["kernel_size"] == 5
    assert set(spec.metrics) == {"mse", "psnr", "ssim"}
    assert spec.raw_response


def test_extract_experiment_spec_handles_empty_context() -> None:
    """Check that empty context does not crash extraction."""
    spec = extract_experiment_spec("", client=UnknownClient())

    assert isinstance(spec, ExperimentSpec)
    assert spec.method == "unknown"
    assert spec.params == {}
    assert spec.metrics == []


def test_extract_experiment_spec_parses_fake_json_response() -> None:
    """Check that FakeLLM JSON responses are parsed correctly."""
    spec = extract_experiment_spec(
        "Gaussian blur kernel size 5 with MSE PSNR SSIM metrics."
    )

    assert spec.method == "gaussian_blur"
    assert spec.params == {"kernel_size": 5}
    assert spec.metrics == ["mse", "psnr", "ssim"]


def test_extract_experiment_spec_falls_back_for_plain_text_response() -> None:
    """Check that non-JSON responses still use fallback extraction."""
    spec = extract_experiment_spec("demo context", client=PlainTextClient())

    assert spec.method == "gaussian_blur"
    assert spec.params["kernel_size"] == 5
    assert spec.metrics == ["mse", "psnr", "ssim"]
