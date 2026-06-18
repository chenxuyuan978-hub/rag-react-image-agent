from pathlib import Path

from fastapi.testclient import TestClient

import app.api.main as api_main

client = TestClient(api_main.app)


def _create_reproduction_inputs(tmp_path: Path) -> tuple[Path, Path]:
    """Create a small paper and source directory for API tests."""
    paper_path = tmp_path / "paper.txt"
    paper_path.write_text("Demo paper\nGaussian blur\nPSNR", encoding="utf-8")

    source_dir = tmp_path / "source_repo"
    source_dir.mkdir()
    (source_dir / "README.md").write_text("# demo repo", encoding="utf-8")
    (source_dir / "main.py").write_text("print('hello')", encoding="utf-8")
    return paper_path, source_dir


def test_reproduction_intake_api_creates_task(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Check the reproduction intake API creates an isolated workspace."""
    monkeypatch.setattr(api_main, "REPRODUCTION_RUNS_DIR", tmp_path / "runs")
    paper_path, source_dir = _create_reproduction_inputs(tmp_path)

    response = client.post(
        "/api/reproduction/intake",
        json={"paper_path": str(paper_path), "source_path": str(source_dir)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"].startswith("repro_")
    assert Path(payload["workspace_dir"]).is_dir()
    assert Path(payload["paper_text_path"]).is_file()
    assert payload["paper_text_chars"] > 0
    assert payload["paper_text_lines"] == 3
    assert payload["source_file_count"] == 2
    assert payload["source_top_level_items"] == ["README.md", "main.py"]
    assert payload["status"] == "completed"
    assert payload["errors"] == []


def test_reproduction_runs_api_lists_tasks(tmp_path: Path, monkeypatch) -> None:
    """Check reproduction runs can be listed after creating a task."""
    monkeypatch.setattr(api_main, "REPRODUCTION_RUNS_DIR", tmp_path / "runs")
    paper_path, source_dir = _create_reproduction_inputs(tmp_path)
    created = client.post(
        "/api/reproduction/intake",
        json={"paper_path": str(paper_path), "source_path": str(source_dir)},
    ).json()

    response = client.get("/api/reproduction/runs")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["run_id"] == created["run_id"]
    assert payload[0]["status"] == "completed"
    assert payload[0]["paper_text_chars"] > 0
    assert payload[0]["source_file_count"] == 2


def test_reproduction_run_api_reads_summary(tmp_path: Path, monkeypatch) -> None:
    """Check one reproduction run summary can be read by run_id."""
    monkeypatch.setattr(api_main, "REPRODUCTION_RUNS_DIR", tmp_path / "runs")
    paper_path, source_dir = _create_reproduction_inputs(tmp_path)
    created = client.post(
        "/api/reproduction/intake",
        json={"paper_path": str(paper_path), "source_path": str(source_dir)},
    ).json()

    response = client.get(f"/api/reproduction/runs/{created['run_id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == created["run_id"]
    assert payload["workspace_dir"] == created["workspace_dir"]
    assert payload["source_file_count"] == 2


def test_reproduction_run_api_returns_404_for_missing_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Check missing reproduction run ids return 404."""
    monkeypatch.setattr(api_main, "REPRODUCTION_RUNS_DIR", tmp_path / "runs")

    response = client.get("/api/reproduction/runs/not_exists")

    assert response.status_code == 404
