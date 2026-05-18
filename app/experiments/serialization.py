import asyncio
from datetime import datetime, timezone
from pathlib import Path
import json
import statistics
import time
from typing import Any

import grpc
import httpx
import websockets

from app.experiments.models import (
    ExperimentTransport,
    SerializationExperimentConfig,
    SerializationOperation,
)
from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize(timings_us: list[float]) -> dict:
    return {
        "count": len(timings_us),
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "avg_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
    }


def build_json_request(
    config: SerializationExperimentConfig,
    operation: SerializationOperation,
    transport: ExperimentTransport,
) -> dict[str, Any]:
    if operation == SerializationOperation.SET_VALUE:
        resource_id = f"{config.set_resource_prefix}_{transport.value}"
        payload = {
            "operation": "set_value",
            "resource_id": resource_id,
            "value": config.set_value,
        }
    else:
        resource_id = f"{config.get_resource_prefix}_{transport.value}"
        payload = {
            "operation": "get_value",
            "resource_id": resource_id,
        }

    return {
        "source": config.source,
        "payload": payload,
    }


def build_grpc_request(
    config: SerializationExperimentConfig,
    operation: SerializationOperation,
    transport: ExperimentTransport,
) -> message_service_pb2.MessageEnvelope:
    if operation == SerializationOperation.SET_VALUE:
        resource_id = f"{config.set_resource_prefix}_{transport.value}"
        payload = message_service_pb2.MessagePayload(
            operation=message_service_pb2.SET_VALUE,
            resource_id=resource_id,
            value=config.set_value,
        )
    else:
        resource_id = f"{config.get_resource_prefix}_{transport.value}"
        payload = message_service_pb2.MessagePayload(
            operation=message_service_pb2.GET_VALUE,
            resource_id=resource_id,
        )

    return message_service_pb2.MessageEnvelope(
        source=config.source,
        payload=payload,
    )


def serialize_json_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def deserialize_json_payload(payload_bytes: bytes) -> dict[str, Any]:
    return json.loads(payload_bytes.decode("utf-8"))


def measure_json_serialization(payload: dict[str, Any], iterations: int) -> tuple[int, list[float], list[float]]:
    serialize_timings_us: list[float] = []
    deserialize_timings_us: list[float] = []

    serialized = serialize_json_payload(payload)
    size_bytes = len(serialized)

    for _ in range(iterations):
        start = time.perf_counter_ns()
        serialized = serialize_json_payload(payload)
        end = time.perf_counter_ns()
        serialize_timings_us.append((end - start) / 1_000)

    for _ in range(iterations):
        start = time.perf_counter_ns()
        deserialize_json_payload(serialized)
        end = time.perf_counter_ns()
        deserialize_timings_us.append((end - start) / 1_000)

    return size_bytes, serialize_timings_us, deserialize_timings_us


def measure_protobuf_serialization(message_obj, iterations: int) -> tuple[int, list[float], list[float]]:
    serialize_timings_us: list[float] = []
    deserialize_timings_us: list[float] = []

    serialized = message_obj.SerializeToString()
    size_bytes = len(serialized)
    message_type = type(message_obj)

    for _ in range(iterations):
        start = time.perf_counter_ns()
        serialized = message_obj.SerializeToString()
        end = time.perf_counter_ns()
        serialize_timings_us.append((end - start) / 1_000)

    for _ in range(iterations):
        cloned = message_type()
        start = time.perf_counter_ns()
        cloned.ParseFromString(serialized)
        end = time.perf_counter_ns()
        deserialize_timings_us.append((end - start) / 1_000)

    return size_bytes, serialize_timings_us, deserialize_timings_us


def prepare_http_response(
    config: SerializationExperimentConfig,
    operation: SerializationOperation,
) -> dict[str, Any]:
    request_payload = build_json_request(config, operation, ExperimentTransport.HTTP)

    with httpx.Client(base_url=config.http_base_url, timeout=10.0) as client:
        if operation == SerializationOperation.GET_VALUE:
            seed_payload = {
                "source": config.source,
                "payload": {
                    "operation": "set_value",
                    "resource_id": f"{config.get_resource_prefix}_{ExperimentTransport.HTTP.value}",
                    "value": config.get_seed_value,
                },
            }
            client.post("/process", json=seed_payload)

        response = client.post("/process", json=request_payload)
        response.raise_for_status()
        return response.json()


async def prepare_ws_response_async(
    config: SerializationExperimentConfig,
    operation: SerializationOperation,
) -> dict[str, Any]:
    request_payload = build_json_request(config, operation, ExperimentTransport.WS)

    if operation == SerializationOperation.GET_VALUE:
        seed_payload = {
            "source": config.source,
            "payload": {
                "operation": "set_value",
                "resource_id": f"{config.get_resource_prefix}_{ExperimentTransport.WS.value}",
                "value": config.get_seed_value,
            },
        }

        async with websockets.connect(config.ws_url) as websocket:
            await websocket.send(json.dumps(seed_payload))
            await websocket.recv()

    async with websockets.connect(config.ws_url) as websocket:
        await websocket.send(json.dumps(request_payload))
        raw_response = await websocket.recv()
        return json.loads(raw_response)


def prepare_grpc_response(
    config: SerializationExperimentConfig,
    operation: SerializationOperation,
):
    channel = grpc.insecure_channel(config.grpc_address)
    grpc.channel_ready_future(channel).result(timeout=5)

    try:
        stub = message_service_pb2_grpc.MessageServiceStub(channel)

        if operation == SerializationOperation.GET_VALUE:
            seed_request = message_service_pb2.MessageEnvelope(
                source=config.source,
                payload=message_service_pb2.MessagePayload(
                    operation=message_service_pb2.SET_VALUE,
                    resource_id=f"{config.get_resource_prefix}_{ExperimentTransport.GRPC.value}",
                    value=config.get_seed_value,
                ),
            )
            stub.Process(seed_request)

        request_obj = build_grpc_request(config, operation, ExperimentTransport.GRPC)
        response_obj = stub.Process(request_obj)
        return response_obj
    finally:
        channel.close()


def run_single_measurement(
    transport: ExperimentTransport,
    operation: SerializationOperation,
    config: SerializationExperimentConfig,
) -> dict:
    if transport in {ExperimentTransport.HTTP, ExperimentTransport.WS}:
        request_payload = build_json_request(config, operation, transport)

        if transport == ExperimentTransport.HTTP:
            response_payload = prepare_http_response(config, operation)
        else:
            response_payload = asyncio.run(prepare_ws_response_async(config, operation))

        request_size_bytes, request_serialize_us, request_deserialize_us = measure_json_serialization(
            request_payload,
            config.iterations,
        )
        response_size_bytes, response_serialize_us, response_deserialize_us = measure_json_serialization(
            response_payload,
            config.iterations,
        )

        encoding = "json"
    else:
        request_obj = build_grpc_request(config, operation, transport)
        response_obj = prepare_grpc_response(config, operation)

        request_size_bytes, request_serialize_us, request_deserialize_us = measure_protobuf_serialization(
            request_obj,
            config.iterations,
        )
        response_size_bytes, response_serialize_us, response_deserialize_us = measure_protobuf_serialization(
            response_obj,
            config.iterations,
        )

        encoding = "protobuf"

    return {
        "transport": transport.value,
        "operation": operation.value,
        "encoding": encoding,
        "request_size_bytes": request_size_bytes,
        "response_size_bytes": response_size_bytes,
        "request_serialize_us": request_serialize_us,
        "request_deserialize_us": request_deserialize_us,
        "response_serialize_us": response_serialize_us,
        "response_deserialize_us": response_deserialize_us,
        "request_serialize_summary": summarize(request_serialize_us),
        "request_deserialize_summary": summarize(request_deserialize_us),
        "response_serialize_summary": summarize(response_serialize_us),
        "response_deserialize_summary": summarize(response_deserialize_us),
    }


def run_serialization_experiment(
    config: SerializationExperimentConfig,
) -> dict:
    started_at = now_utc_iso()

    results = {
        "started_at": started_at,
        "iterations": config.iterations,
        "transports": [transport.value for transport in config.transports],
        "operations": [operation.value for operation in config.operations],
        "measurements": [],
    }

    for transport in config.transports:
        for operation in config.operations:
            results["measurements"].append(
                run_single_measurement(transport, operation, config)
            )

    results["finished_at"] = now_utc_iso()
    return results


def save_serialization_experiment_results(
    results: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)