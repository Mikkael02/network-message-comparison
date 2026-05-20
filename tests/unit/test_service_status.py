from app.orchestration.models import (
    ServiceStatusCheckConfig,
    SingleServiceStatus,
)
from app.orchestration.service_status import (
    check_environment_services,
    check_http_like_service,
)


def test_check_environment_services_aggregates_statuses(monkeypatch):
    from app.orchestration import service_status as service_status_module

    monkeypatch.setattr(
        service_status_module,
        "check_http_like_service",
        lambda service_name, url, timeout_seconds: SingleServiceStatus(
            service_name=service_name,
            available=True,
            response_time_ms=5.0,
            detail="ok",
        ),
    )
    monkeypatch.setattr(
        service_status_module,
        "check_grpc_service",
        lambda service_name, address, timeout_seconds: SingleServiceStatus(
            service_name=service_name,
            available=False,
            response_time_ms=None,
            detail="timeout",
        ),
    )

    result = check_environment_services(ServiceStatusCheckConfig())

    assert result.all_available is False
    assert len(result.services) == 3
    assert result.services[0].service_name == "http_transport"
    assert result.services[1].service_name == "ws_transport"
    assert result.services[2].service_name == "grpc_transport"


def test_check_http_like_service_returns_unavailable_on_exception(monkeypatch):
    from app.orchestration import service_status as service_status_module

    class FailingClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            raise RuntimeError("connection failed")

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(service_status_module.httpx, "Client", FailingClient)

    result = check_http_like_service(
        service_name="http_transport",
        url="http://127.0.0.1:8000/health",
        timeout_seconds=1.0,
    )

    assert result.available is False
    assert "RuntimeError" in result.detail