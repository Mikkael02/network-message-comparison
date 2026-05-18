from datetime import datetime, timezone
from pathlib import Path
import json
import statistics
import time

from benchmarks.external_clients import (
    ExternalGrpcClient,
    ExternalHttpClient,
    ExternalWsClient,
)
from app.experiments.models import (
    ExperimentTransport,
    RequestResponseExperimentConfig,
)


CLIENT_FACTORIES = {
    ExperimentTransport.HTTP: lambda config: ExternalHttpClient(
        base_url=config.http_base_url
    ),
    ExperimentTransport.WS: lambda config: ExternalWsClient(
        url=config.ws_url
    ),
    ExperimentTransport.GRPC: lambda config: ExternalGrpcClient(
        address=config.grpc_address
    ),
}


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize(latencies_ms: list[float]) -> dict:
    return {
        "count": len(latencies_ms),
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "avg_ms": statistics.mean(latencies_ms),
        "median_ms": statistics.median(latencies_ms),
    }


def measure_operation(client, payload: dict, iterations: int) -> list[float]:
    latencies_ms: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = client.send(payload)
        end = time.perf_counter_ns()

        if response["status"] != "success":
            raise RuntimeError(f"Measurement failed with response: {response}")

        latency_ms = (end - start) / 1_000_000
        latencies_ms.append(latency_ms)

    return latencies_ms


def run_transport_measurements(
    transport: ExperimentTransport,
    client,
    config: RequestResponseExperimentConfig,
) -> dict:
    transport_name = transport.value

    set_resource_id = f"{config.set_resource_prefix}_{transport_name}"
    get_resource_id = f"{config.get_resource_prefix}_{transport_name}"

    set_payload = {
        "source": config.source,
        "payload": {
            "operation": "set_value",
            "resource_id": set_resource_id,
            "value": config.set_value,
        },
    }

    initial_set_for_get_payload = {
        "source": config.source,
        "payload": {
            "operation": "set_value",
            "resource_id": get_resource_id,
            "value": config.get_seed_value,
        },
    }

    get_payload = {
        "source": config.source,
        "payload": {
            "operation": "get_value",
            "resource_id": get_resource_id,
        },
    }

    init_response = client.send(initial_set_for_get_payload)
    if init_response["status"] != "success":
        raise RuntimeError(
            f"Failed to prepare GET benchmark for {transport_name}: {init_response}"
        )

    set_latencies = measure_operation(client, set_payload, config.iterations)
    get_latencies = measure_operation(client, get_payload, config.iterations)

    return {
        "transport": transport_name,
        "iterations": config.iterations,
        "set_value": {
            "latencies_ms": set_latencies,
            "summary": summarize(set_latencies),
        },
        "get_value": {
            "latencies_ms": get_latencies,
            "summary": summarize(get_latencies),
        },
    }


def run_request_response_experiment(
    config: RequestResponseExperimentConfig,
) -> dict:
    started_at = now_utc_iso()

    clients = {
        transport: CLIENT_FACTORIES[transport](config)
        for transport in config.transports
    }

    results = {
        "started_at": started_at,
        "iterations": config.iterations,
        "transports": [transport.value for transport in config.transports],
        "measurements": [],
    }

    try:
        for transport, client in clients.items():
            result = run_transport_measurements(transport, client, config)
            results["measurements"].append(result)
    finally:
        for client in clients.values():
            client.close()

    results["finished_at"] = now_utc_iso()
    return results


def save_request_response_experiment_results(
    results: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)