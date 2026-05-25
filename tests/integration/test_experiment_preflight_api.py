from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_request_response_returns_503_when_transport_unavailable(monkeypatch):
    from app.overhead import server as server_module

    def fake_preflight(config):
        raise server_module.HTTPException(
            status_code=503,
            detail="Eksperyment nie może zostać uruchomiony. Niedostępne transporty: grpc: FutureTimeoutError",
        )

    monkeypatch.setattr(
        server_module,
        "_assert_transports_ready_for_request_response",
        fake_preflight,
    )

    response = client.post(
        "/experiments/request-response/run",
        json={
            "transports": ["grpc"],
            "iterations": 5,
            "http_base_url": "http://127.0.0.1:8000",
            "ws_url": "ws://127.0.0.1:8001/ws/process",
            "grpc_address": "127.0.0.1:50051",
            "source": "external_benchmark_client",
            "set_value": 42,
            "get_seed_value": 77,
            "set_resource_prefix": "rr_set",
            "get_resource_prefix": "rr_get",
        },
    )

    assert response.status_code == 503
    assert "Niedostępne transporty" in response.json()["detail"]