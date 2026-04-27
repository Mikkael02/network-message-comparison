from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import statistics
import time
from datetime import datetime, timezone

from benchmarks.external_clients import (
    ExternalGrpcClient,
    ExternalHttpClient,
    ExternalWsClient,
)


RESULTS_DIR = Path("results/raw")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ITERATIONS = 50


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def summarize(latencies_ms: list[float]) -> dict:
    return {
        "count": len(latencies_ms),
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "avg_ms": statistics.mean(latencies_ms),
        "median_ms": statistics.median(latencies_ms),
    }


def run_transport_measurements(transport_name: str, client) -> dict:
    set_resource_id = f"{transport_name}_benchmark_set"
    get_resource_id = f"{transport_name}_benchmark_get"

    set_payload = {
        "source": "external_benchmark_client",
        "payload": {
            "operation": "set_value",
            "resource_id": set_resource_id,
            "value": 42,
        },
    }

    initial_set_for_get_payload = {
        "source": "external_benchmark_client",
        "payload": {
            "operation": "set_value",
            "resource_id": get_resource_id,
            "value": 77,
        },
    }

    get_payload = {
        "source": "external_benchmark_client",
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

    set_latencies = measure_operation(client, set_payload, ITERATIONS)
    get_latencies = measure_operation(client, get_payload, ITERATIONS)

    return {
        "transport": transport_name,
        "iterations": ITERATIONS,
        "set_value": {
            "latencies_ms": set_latencies,
            "summary": summarize(set_latencies),
        },
        "get_value": {
            "latencies_ms": get_latencies,
            "summary": summarize(get_latencies),
        },
    }


def main() -> None:
    started_at = now_utc_iso()

    clients = {
        "http": ExternalHttpClient(),
        "ws": ExternalWsClient(),
        "grpc": ExternalGrpcClient(),
    }

    results = {
        "started_at": started_at,
        "iterations": ITERATIONS,
        "measurements": [],
    }

    try:
        for transport_name, client in clients.items():
            print(f"Measuring transport: {transport_name}")
            result = run_transport_measurements(transport_name, client)
            results["measurements"].append(result)

    finally:
        for client in clients.values():
            client.close()

    finished_at = now_utc_iso()
    results["finished_at"] = finished_at

    output_path = RESULTS_DIR / "request_response_external.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()