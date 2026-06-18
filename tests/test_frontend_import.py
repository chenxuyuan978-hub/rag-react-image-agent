import importlib.util
from pathlib import Path
from types import ModuleType


def _load_streamlit_module() -> ModuleType:
    """Load the Streamlit frontend module without running the app."""
    app_path = Path("frontend/streamlit_app.py")
    spec = importlib.util.spec_from_file_location("streamlit_app", app_path)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_streamlit_app_can_be_imported() -> None:
    """Check that the Streamlit frontend entry file can be imported."""
    module = _load_streamlit_module()

    assert hasattr(module, "main")
    assert hasattr(module, "run_langgraph_agent_via_api")


def test_run_langgraph_agent_via_api_uses_backend_request(monkeypatch) -> None:
    """Check LangGraph API helper can be tested without a real backend."""
    module = _load_streamlit_module()
    captured_request = {}

    class FakeResponse:
        """Small fake response object for the frontend API helper."""

        def raise_for_status(self) -> None:
            """Simulate a successful HTTP response."""

        def json(self) -> dict:
            """Return stable fake LangGraph Agent response JSON."""
            return {
                "final_answer": "ok",
                "steps": [],
                "error": None,
                "diagnosis": None,
            }

    def fake_post(url: str, json: dict, timeout: int) -> FakeResponse:
        """Capture the outgoing request instead of calling a real backend."""
        captured_request["url"] = url
        captured_request["json"] = json
        captured_request["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(module.requests, "post", fake_post)

    result = module.run_langgraph_agent_via_api(
        task="demo task",
        config_path="examples/demo_config.yaml",
        paper_dir="data/papers",
        api_base_url="http://testserver",
        timeout_seconds=5,
    )

    assert result["final_answer"] == "ok"
    assert captured_request["url"] == "http://testserver/api/agent/langgraph/run"
    assert captured_request["json"]["task"] == "demo task"
    assert captured_request["timeout"] == 5
