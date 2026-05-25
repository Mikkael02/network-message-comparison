import asyncio
from datetime import datetime, timezone
from pathlib import Path
import json
import statistics
import time

from benchmarks.external_realtime_clients import (
    ExternalRealtimeGrpcClient,
    ExternalRealtimeHttpClient,
    ExternalRealtimeWsClient,
)
from app.experiments.models import (
    ExperimentTransport,
    RealtimeFetchExperimentConfig,
)


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


def measure_sync_fetch(get_changes_func, from_version: int, iterations: int) -> tuple[list[float], list[int]]:
    latencies_ms: list[float] = []
    event_counts: list[int] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = get_changes_func(from_version)
        end = time.perf_counter_ns()

        latencies_ms.append((end - start) / 1_000_000)
        event_counts.append(len(response["events"]))

    return latencies_ms, event_counts


async def measure_async_fetch(get_changes_func, from_version: int, iterations: int) -> tuple[list[float], list[int]]:
    latencies_ms: list[float] = []
    event_counts: list[int] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        response = await get_changes_func(from_version)
        end = time.perf_counter_ns()

        latencies_ms.append((end - start) / 1_000_000)
        event_counts.append(len(response["events"]))

    return latencies_ms, event_counts


def _seed_three_changes_sync(client, transport_name: str, config: RealtimeFetchExperimentConfig) -> None:
    resource_a = f"{config.resource_prefix}_{transport_name}_a"
    resource_b = f"{config.resource_prefix}_{transport_name}_b"

    client.set_value(resource_a, config.first_value)
    client.set_value(resource_b, config.second_value)
    client.set_value(resource_a, config.third_value)


async def _seed_three_changes_async(client, transport_name: str, config: RealtimeFetchExperimentConfig) -> None:
    resource_a = f"{config.resource_prefix}_{transport_name}_a"
    resource_b = f"{config.resource_prefix}_{transport_name}_b"

    await client.set_value(resource_a, config.first_value)
    await client.set_value(resource_b, config.second_value)
    await client.set_value(resource_a, config.third_value)


def _run_http_realtime_measurements(config: RealtimeFetchExperimentConfig) -> list[dict]:
    client = ExternalRealtimeHttpClient(base_url=config.http_base_url)

    try:
        baseline_version = client.get_changes(0)["current_version"]
        _seed_three_changes_sync(client, "http", config)

        non_empty_latencies, non_empty_counts = measure_sync_fetch(
            client.get_changes,
            from_version=baseline_version,
            iterations=config.iterations,
        )

        current_version_after_seed = client.get_changes(0)["current_version"]

        empty_latencies, empty_counts = measure_sync_fetch(
            client.get_changes,
            from_version=current_version_after_seed,
            iterations=config.iterations,
        )

        return [
            build_measurement_block("http", "non_empty_fetch", non_empty_latencies, non_empty_counts),
            build_measurement_block("http", "empty_fetch", empty_latencies, empty_counts),
        ]
    finally:
        client.close()


async def _run_ws_realtime_measurements_async(config: RealtimeFetchExperimentConfig) -> list[dict]:
    client = ExternalRealtimeWsClient(
        url=config.ws_changes_url,
        process_url=config.ws_process_url,
    )

    try:
        await client.open()

        baseline_version = (await client.get_changes(0))["current_version"]
        await _seed_three_changes_async(client, "ws", config)

        non_empty_latencies, non_empty_counts = await measure_async_fetch(
            client.get_changes,
            from_version=baseline_version,
            iterations=config.iterations,
        )

        current_version_after_seed = (await client.get_changes(0))["current_version"]

        empty_latencies, empty_counts = await measure_async_fetch(
            client.get_changes,
            from_version=current_version_after_seed,
            iterations=config.iterations,
        )

        return [
            build_measurement_block("ws", "non_empty_fetch", non_empty_latencies, non_empty_counts),
            build_measurement_block("ws", "empty_fetch", empty_latencies, empty_counts),
        ]
    finally:
        await client.close()


def _run_grpc_realtime_measurements(config: RealtimeFetchExperimentConfig) -> list[dict]:
    client = ExternalRealtimeGrpcClient(address=config.grpc_address)

    try:
        baseline_version = client.get_changes(0)["current_version"]
        _seed_three_changes_sync(client, "grpc", config)

        non_empty_latencies, non_empty_counts = measure_sync_fetch(
            client.get_changes,
            from_version=baseline_version,
            iterations=config.iterations,
        )

        current_version_after_seed = client.get_changes(0)["current_version"]

        empty_latencies, empty_counts = measure_sync_fetch(
            client.get_changes,
            from_version=current_version_after_seed,
            iterations=config.iterations,
        )

        return [
            build_measurement_block("grpc", "non_empty_fetch", non_empty_latencies, non_empty_counts),
            build_measurement_block("grpc", "empty_fetch", empty_latencies, empty_counts),
        ]
    finally:
        client.close()


def run_realtime_fetch_experiment(
    config: RealtimeFetchExperimentConfig,
) -> dict:
    started_at = now_utc_iso()

    results = {
        "started_at": started_at,
        "iterations": config.iterations,
        "transports": [transport.value for transport in config.transports],
        "measurements": [],
    }

    for transport in config.transports:
        if transport == ExperimentTransport.HTTP:
            results["measurements"].extend(_run_http_realtime_measurements(config))
        elif transport == ExperimentTransport.WS:
            results["measurements"].extend(asyncio.run(_run_ws_realtime_measurements_async(config)))
        elif transport == ExperimentTransport.GRPC:
            results["measurements"].extend(_run_grpc_realtime_measurements(config))

    results["finished_at"] = now_utc_iso()
    return results


def save_realtime_fetch_experiment_results(
    results: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)