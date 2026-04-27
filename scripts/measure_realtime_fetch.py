from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
import json
import statistics
import time
from datetime import datetime, timezone

from benchmarks.external_realtime_clients import (
    ExternalRealtimeGrpcClient,
    ExternalRealtimeHttpClient,
    ExternalRealtimeWsClient,
)


RESULTS_DIR = Path("results/raw")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = RESULTS_DIR / "realtime_fetch_external.json"
ITERATIONS = 50


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


def measure_http_operation(client, from_version: int, iterations: int) -> tuple[list[float], list[int]]:
    latencies_ms = []
    event_counts = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = client.get_changes(from_version)
        end = time.perf_counter_ns()

        latencies_ms.append((end - start) / 1_000_000)
        event_counts.append(len(response["events"]))

    return latencies_ms, event_counts


def measure_grpc_operation(client, from_version: int, iterations: int) -> tuple[list[float], list[int]]:
    latencies_ms = []
    event_counts = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = client.get_changes(from_version)
        end = time.perf_counter_ns()

        latencies_ms.append((end - start) / 1_000_000)
        event_counts.append(len(response["events"]))

    return latencies_ms, event_counts


async def measure_ws_operation(client, from_version: int, iterations: int) -> tuple[list[float], list[int]]:
    latencies_ms = []
    event_counts = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = await client.get_changes(from_version)
        end = time.perf_counter_ns()

        latencies_ms.append((end - start) / 1_000_000)
        event_counts.append(len(response["events"]))

    return latencies_ms, event_counts


def build_measurement_block(
    transport: str,
    scenario: str,
    latencies_ms: list[float],
    event_counts: list[int],
) -> dict:
    return {
        "transport": transport,
        "scenario": scenario,
        "latencies_ms": latencies_ms,
        "event_counts": event_counts,
        "summary": summarize(latencies_ms),
        "expected_event_count": event_counts[0] if event_counts else None,
    }


async def main_async() -> None:
    started_at = now_utc_iso()

    http_client = ExternalRealtimeHttpClient()
    ws_client = ExternalRealtimeWsClient()
    grpc_client = ExternalRealtimeGrpcClient()

    results = {
        "started_at": started_at,
        "iterations": ITERATIONS,
        "measurements": [],
    }

    try:
        await ws_client.open()

        # non_empty_fetch
        http_client.reset_and_seed()
        await ws_client.reset_and_seed()
        grpc_client.reset_and_seed()

        http_latencies, http_counts = measure_http_operation(http_client, from_version=0, iterations=ITERATIONS)
        ws_latencies, ws_counts = await measure_ws_operation(ws_client, from_version=0, iterations=ITERATIONS)
        grpc_latencies, grpc_counts = measure_grpc_operation(grpc_client, from_version=0, iterations=ITERATIONS)

        results["measurements"].append(
            build_measurement_block("http", "non_empty_fetch", http_latencies, http_counts)
        )
        results["measurements"].append(
            build_measurement_block("ws", "non_empty_fetch", ws_latencies, ws_counts)
        )
        results["measurements"].append(
            build_measurement_block("grpc", "non_empty_fetch", grpc_latencies, grpc_counts)
        )

        # empty_fetch
        http_client.reset_and_seed()
        await ws_client.reset_and_seed()
        grpc_client.reset_and_seed()

        http_empty_latencies, http_empty_counts = measure_http_operation(http_client, from_version=3, iterations=ITERATIONS)
        ws_empty_latencies, ws_empty_counts = await measure_ws_operation(ws_client, from_version=3, iterations=ITERATIONS)
        grpc_empty_latencies, grpc_empty_counts = measure_grpc_operation(grpc_client, from_version=3, iterations=ITERATIONS)

        results["measurements"].append(
            build_measurement_block("http", "empty_fetch", http_empty_latencies, http_empty_counts)
        )
        results["measurements"].append(
            build_measurement_block("ws", "empty_fetch", ws_empty_latencies, ws_empty_counts)
        )
        results["measurements"].append(
            build_measurement_block("grpc", "empty_fetch", grpc_empty_latencies, grpc_empty_counts)
        )

    finally:
        http_client.close()
        await ws_client.close()
        grpc_client.close()

    results["finished_at"] = now_utc_iso()

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main_async())