import json
import re
from dataclasses import dataclass
from typing import Any

from app.llm.client import LLMClient, get_llm_client

"""
extractors.py 负责前后两端：
构造 prompt + 解析 response

LLMClient 负责中间：
把 prompt 发给模型并拿回 response
"""

METHOD_ALIASES = {
    "gaussian_blur": "gaussian_blur",
    "gaussian blur": "gaussian_blur",
    "median_blur": "median_blur",
    "median blur": "median_blur",
    "sharpen": "sharpen",
    "sharpening": "sharpen",
    "edge_detect": "edge_detect",
    "edge detect": "edge_detect",
    "edge detection": "edge_detect",
    "histogram_equalization": "histogram_equalization",
    "histogram equalization": "histogram_equalization",
}

SUPPORTED_METRICS = ("mse", "psnr", "ssim")


@dataclass
class ExperimentSpec:
    """LLM-extracted experiment configuration from paper context."""

    method: str
    params: dict[str, Any]
    metrics: list[str]
    raw_response: str


def _build_extraction_prompt(context: str) -> str:
    """Build a prompt for extracting image experiment settings."""
    return f"""Extract an image processing experiment configuration from context.

Return JSON only with this schema:
{{
  "method": "gaussian_blur | median_blur | sharpen | edge_detect | histogram_equalization",
  "params": {{"kernel_size": 5}},
  "metrics": ["mse", "psnr", "ssim"]
}}

Context:
{context}
"""


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse a JSON object from an LLM response if possible."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    return parsed if isinstance(parsed, dict) else None


def _normalize_method(value: Any, fallback_text: str) -> str:
    """Normalize a method name to the project's internal operation name."""
    candidates = []
    if isinstance(value, str):
        candidates.append(value)
    candidates.append(fallback_text)

    for candidate in candidates:
        normalized = candidate.replace("-", " ").replace("_", " ").lower()
        for alias, method_name in METHOD_ALIASES.items():
            if alias in normalized or alias.replace("_", " ") in normalized:
                return method_name

    return "unknown"


def _parse_params(value: Any, fallback_text: str) -> dict[str, Any]:
    """Parse experiment parameters from JSON data or fallback text."""
    params = value if isinstance(value, dict) else {}
    parsed_params: dict[str, Any] = dict(params)

    if "kernel_size" not in parsed_params:
        match = re.search(r"kernel\s*size\s*[:=]?\s*(\d+)", fallback_text, re.I)
        if match:
            parsed_params["kernel_size"] = int(match.group(1))

    if "kernel_size" in parsed_params:
        try:
            parsed_params["kernel_size"] = int(parsed_params["kernel_size"])
        except (TypeError, ValueError):
            parsed_params.pop("kernel_size", None)

    return parsed_params


def _parse_metrics(value: Any, fallback_text: str) -> list[str]:
    """Parse and normalize metric names from JSON data or fallback text."""
    metrics: list[str] = []
    if isinstance(value, list):
        metrics.extend(str(item).lower() for item in value if isinstance(item, str))

    fallback_lower = fallback_text.lower()
    for metric_name in SUPPORTED_METRICS:
        if metric_name in fallback_lower:
            metrics.append(metric_name)

    ordered_metrics: list[str] = []
    for metric_name in metrics:
        normalized = metric_name.strip().lower()
        if normalized in SUPPORTED_METRICS and normalized not in ordered_metrics:
            ordered_metrics.append(normalized)

    return ordered_metrics


def _spec_from_response(response: str) -> ExperimentSpec:
    """Parse an ExperimentSpec from an LLM response."""
    parsed = _extract_json_object(response) or {}

    return ExperimentSpec(
        method=_normalize_method(parsed.get("method"), response),
        params=_parse_params(parsed.get("params"), response),
        metrics=_parse_metrics(parsed.get("metrics"), response),
        raw_response=response,
    )


def extract_experiment_spec(
    context: str,
    client: LLMClient | None = None,
) -> ExperimentSpec:
    """Extract an experiment specification from paper context."""
    llm_client = client or get_llm_client()
    prompt = _build_extraction_prompt(context)
    response = llm_client.generate(prompt)
    return _spec_from_response(response)
