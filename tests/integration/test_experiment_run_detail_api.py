from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_saved_run_detail_endpoint_returns_run(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "metadata": {
            "run_id": "validation_20260101_demo",
            "experiment_name": "validation",
            "saved_at": "2026-01-01T00:00:00+00:00",
            "run_label": "demo",
            "file_path": "results/runs/validation/demo.json",
        },
        "results": {
            "iterations": 10,
            "measurements": [],
        },
    }

    monkeypatch.setattr(
        server_module,
        "read_saved_run",
        lambda run_id: fake_result,
    )

    response = client.get("/experiment-runs/validation_20260101_demo")

    assert response.status_code == 200
    data = response.json()

    assert data["metadata"]["experiment_name"] == "validation"
    assert data["results"]["iterations"] == 10


def test_saved_run_detail_endpoint_returns_404_for_missing_run(monkeypatch):
    from app.overhead import server as server_module

    def fake_reader(run_id):
        raise FileNotFoundError(f"Saved run not found: {run_id}")

    monkeypatch.setattr(server_module, "read_saved_run", fake_reader)

    response = client.get("/experiment-runs/missing_run")

    assert response.status_code == 404
    assert "Saved run not found" in response.json()["detail"]