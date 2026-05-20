from datetime import datetime, timezone
import time

import grpc
import httpx

from app.orchestration.models import (
    EnvironmentServiceStatusResponse,
    ServiceStatusCheckConfig,
    SingleServiceStatus,
)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_http_like_service(
    service_name: str,
    url: str,
    timeout_seconds: float,
) -> SingleServiceStatus:
    try:
        start = time.perf_counter_ns()

        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.get(url)

        end = time.perf_counter_ns()
        response_time_ms = (end - start) / 1_000_000

        if response.status_code != 200:
            return SingleServiceStatus(
                service_name=service_name,
                available=False,
                response_time_ms=response_time_ms,
                detail=f"Unexpected HTTP status: {response.status_code}",
            )

        data = response.json()
        if data.get("status") != "ok":
            return SingleServiceStatus(
                service_name=service_name,
                available=False,
                response_time_ms=response_time_ms,
                detail=f"Unexpected health payload: {data}",
            )

        return SingleServiceStatus(
            service_name=service_name,
            available=True,
            response_time_ms=response_time_ms,
            detail="Health check returned status=ok",
        )

    except Exception as exc:
        return SingleServiceStatus(
            service_name=service_name,
            available=False,
            response_time_ms=None,
            detail=f"{type(exc).__name__}: {exc}",
        )


def check_grpc_service(
    service_name: str,
    address: str,
    timeout_seconds: float,
) -> SingleServiceStatus:
    channel = None

    try:
        start = time.perf_counter_ns()
        channel = grpc.insecure_channel(address)
        grpc.channel_ready_future(channel).result(timeout=timeout_seconds)
        end = time.perf_counter_ns()

        response_time_ms = (end - start) / 1_000_000

        return SingleServiceStatus(
            service_name=service_name,
            available=True,
            response_time_ms=response_time_ms,
            detail="gRPC channel is ready",
        )

    except Exception as exc:
        return SingleServiceStatus(
            service_name=service_name,
            available=False,
            response_time_ms=None,
            detail=f"{type(exc).__name__}: {exc}",
        )

    finally:
        if channel is not None:
            channel.close()


def check_environment_services(
    config: ServiceStatusCheckConfig,
) -> EnvironmentServiceStatusResponse:
    services = [
        check_http_like_service(
            service_name="http_transport",
            url=config.http_health_url,
            timeout_seconds=config.timeout_seconds,
        ),
        check_http_like_service(
            service_name="ws_transport",
            url=config.ws_health_url,
            timeout_seconds=config.timeout_seconds,
        ),
        check_grpc_service(
            service_name="grpc_transport",
            address=config.grpc_address,
            timeout_seconds=config.timeout_seconds,
        ),
    ]

    return EnvironmentServiceStatusResponse(
        checked_at=now_utc_iso(),
        config=config,
        all_available=all(service.available for service in services),
        services=services,
    )