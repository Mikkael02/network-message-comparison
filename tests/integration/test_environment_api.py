from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_environment_default_config_endpoint_returns_defaults():
    response = client.get("/environment/services/default-config")

    assert response.status_code == 200
    data = response.json()

    assert data["http_health_url"] == "http://127.0.0.1:8000/health"
    assert data["ws_health_url"] == "http://127.0.0.1:8001/health"
    assert data["grpc_address"] == "127.0.0.1:50051"
    assert data["timeout_seconds"] == 2.0


def test_environment_status_get_endpoint_uses_checker(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "checked_at": "2026-01-01T00:00:00+00:00",
        "config": {
            "http_health_url": "http://127.0.0.1:8000/health",
            "ws_health_url": "http://127.0.0.1:8001/health",
            "grpc_address": "127.0.0.1:50051",
            "timeout_seconds": 2.0,
        },
        "all_available": True,
        "services": [
            {
                "service_name": "http_transport",
                "available": True,
                "response_time_ms": 4.2,
                "detail": "Health check returned status=ok",
            },
            {
                "service_name": "ws_transport",
                "available": True,
                "response_time_ms": 5.1,
                "detail": "Health check returned status=ok",
            },
            {
                "service_name": "grpc_transport",
                "available": True,
                "response_time_ms": 3.7,
                "detail": "gRPC channel is ready",
            },
        ],
    }

    monkeypatch.setattr(server_module, "check_environment_services", lambda config: fake_result)

    response = client.get("/environment/services/status")

    assert response.status_code == 200
    data = response.json()

    assert data["all_available"] is True
    assert len(data["services"]) == 3


def test_environment_status_post_endpoint_uses_checker(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "checked_at": "2026-01-01T00:00:00+00:00",
        "config": {
            "http_health_url": "http://127.0.0.1:9000/health",
            "ws_health_url": "http://127.0.0.1:9001/health",
            "grpc_address": "127.0.0.1:55000",
            "timeout_seconds": 1.5,
        },
        "all_available": False,
        "services": [
            {
                "service_name": "http_transport",
                "available": False,
                "response_time_ms": None,
                "detail": "ConnectError: failed",
            },
            {
                "service_name": "ws_transport",
                "available": False,
                "response_time_ms": None,
                "detail": "ConnectError: failed",
            },
            {
                "service_name": "grpc_transport",
                "available": False,
                "response_time_ms": None,
                "detail": "FutureTimeoutError:",
            },
        ],
    }

    monkeypatch.setattr(server_module, "check_environment_services", lambda config: fake_result)

    payload = {
        "http_health_url": "http://127.0.0.1:9000/health",
        "ws_health_url": "http://127.0.0.1:9001/health",
        "grpc_address": "127.0.0.1:55000",
        "timeout_seconds": 1.5,
    }

    response = client.post("/environment/services/status", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["all_available"] is False
    assert data["config"]["grpc_address"] == "127.0.0.1:55000"