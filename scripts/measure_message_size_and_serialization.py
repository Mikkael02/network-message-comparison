from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json
import statistics
import time
from datetime import datetime, timezone

from app.transport_grpc.generated import message_service_pb2


RAW_OUTPUT_PATH = Path("results/raw/message_size_and_serialization.json")
CSV_OUTPUT_PATH = Path("results/processed/message_size_and_serialization_summary.csv")

RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

ITERATIONS = 5000


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize_us(values: list[float]) -> dict:
    return {
        "count": len(values),
        "min_us": min(values),
        "max_us": max(values),
        "avg_us": statistics.mean(values),
        "median_us": statistics.median(values),
    }


def measure_serialization(serializer, obj, iterations: int) -> tuple[bytes, list[float]]:
    timings_us: list[float] = []
    serialized = b""

    for _ in range(iterations):
        start = time.perf_counter_ns()
        serialized = serializer(obj)
        end = time.perf_counter_ns()
        timings_us.append((end - start) / 1_000)

    return serialized, timings_us


def measure_deserialization(deserializer, payload: bytes, iterations: int) -> list[float]:
    timings_us: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        deserializer(payload)
        end = time.perf_counter_ns()
        timings_us.append((end - start) / 1_000)

    return timings_us


def json_serialize(data: dict) -> bytes:
    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def json_deserialize(payload: bytes) -> dict:
    return json.loads(payload.decode("utf-8"))


def build_domain_request(operation: str) -> dict:
    base = {
        "message_id": "11111111-1111-1111-1111-111111111111",
        "timestamp": "2026-04-27T12:00:00Z",
        "source": "measurement_client",
    }

    if operation == "set_value":
        return {
            **base,
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_01",
                "value": 42,
            },
        }

    if operation == "get_value":
        return {
            **base,
            "payload": {
                "operation": "get_value",
                "resource_id": "sensor_01",
            },
        }

    raise ValueError(f"Unsupported operation: {operation}")


def build_domain_success_response(operation: str) -> dict:
    base = {
        "status": "success",
        "message_id": "11111111-1111-1111-1111-111111111111",
        "operation": operation,
        "resource_id": "sensor_01",
    }

    if operation == "set_value":
        return {
            **base,
            "result": {
                "action": "value_updated",
                "stored_value": 42,
            },
        }

    if operation == "get_value":
        return {
            **base,
            "result": {
                "action": "value_returned",
                "current_value": 42,
            },
        }

    raise ValueError(f"Unsupported operation: {operation}")


def build_grpc_request_message(operation: str):
    if operation == "set_value":
        return message_service_pb2.MessageEnvelope(
            message_id="11111111-1111-1111-1111-111111111111",
            timestamp="2026-04-27T12:00:00Z",
            source="measurement_client",
            payload=message_service_pb2.MessagePayload(
                operation=message_service_pb2.SET_VALUE,
                resource_id="sensor_01",
                value=42,
            ),
        )

    if operation == "get_value":
        return message_service_pb2.MessageEnvelope(
            message_id="11111111-1111-1111-1111-111111111111",
            timestamp="2026-04-27T12:00:00Z",
            source="measurement_client",
            payload=message_service_pb2.MessagePayload(
                operation=message_service_pb2.GET_VALUE,
                resource_id="sensor_01",
            ),
        )

    raise ValueError(f"Unsupported operation: {operation}")


def build_grpc_success_response_message(operation: str):
    if operation == "set_value":
        return message_service_pb2.ProcessReply(
            success=message_service_pb2.SuccessReply(
                status="success",
                message_id="11111111-1111-1111-1111-111111111111",
                operation="set_value",
                resource_id="sensor_01",
                update_result=message_service_pb2.UpdateResult(
                    action="value_updated",
                    stored_value=42,
                ),
            )
        )

    if operation == "get_value":
        return message_service_pb2.ProcessReply(
            success=message_service_pb2.SuccessReply(
                status="success",
                message_id="11111111-1111-1111-1111-111111111111",
                operation="get_value",
                resource_id="sensor_01",
                get_result=message_service_pb2.GetResult(
                    action="value_returned",
                    current_value=42,
                ),
            )
        )

    raise ValueError(f"Unsupported operation: {operation}")


def protobuf_request_serialize(message) -> bytes:
    return message.SerializeToString()


def protobuf_request_deserialize(payload: bytes):
    msg = message_service_pb2.MessageEnvelope()
    msg.ParseFromString(payload)
    return msg


def protobuf_response_serialize(message) -> bytes:
    return message.SerializeToString()


def protobuf_response_deserialize(payload: bytes):
    msg = message_service_pb2.ProcessReply()
    msg.ParseFromString(payload)
    return msg


def measure_json_representation(transport: str, operation: str) -> dict:
    request_obj = build_domain_request(operation)
    response_obj = build_domain_success_response(operation)

    request_bytes, request_serialize_us = measure_serialization(
        json_serialize,
        request_obj,
        ITERATIONS,
    )
    response_bytes, response_serialize_us = measure_serialization(
        json_serialize,
        response_obj,
        ITERATIONS,
    )

    request_deserialize_us = measure_deserialization(
        json_deserialize,
        request_bytes,
        ITERATIONS,
    )
    response_deserialize_us = measure_deserialization(
        json_deserialize,
        response_bytes,
        ITERATIONS,
    )

    return {
        "transport": transport,
        "encoding": "json",
        "operation": operation,
        "request_size_bytes": len(request_bytes),
        "response_size_bytes": len(response_bytes),
        "request_serialize_us": request_serialize_us,
        "request_deserialize_us": request_deserialize_us,
        "response_serialize_us": response_serialize_us,
        "response_deserialize_us": response_deserialize_us,
        "request_serialize_summary": summarize_us(request_serialize_us),
        "request_deserialize_summary": summarize_us(request_deserialize_us),
        "response_serialize_summary": summarize_us(response_serialize_us),
        "response_deserialize_summary": summarize_us(response_deserialize_us),
    }


def measure_protobuf_representation(operation: str) -> dict:
    request_msg = build_grpc_request_message(operation)
    response_msg = build_grpc_success_response_message(operation)

    request_bytes, request_serialize_us = measure_serialization(
        protobuf_request_serialize,
        request_msg,
        ITERATIONS,
    )
    response_bytes, response_serialize_us = measure_serialization(
        protobuf_response_serialize,
        response_msg,
        ITERATIONS,
    )

    request_deserialize_us = measure_deserialization(
        protobuf_request_deserialize,
        request_bytes,
        ITERATIONS,
    )
    response_deserialize_us = measure_deserialization(
        protobuf_response_deserialize,
        response_bytes,
        ITERATIONS,
    )

    return {
        "transport": "grpc",
        "encoding": "protobuf",
        "operation": operation,
        "request_size_bytes": len(request_bytes),
        "response_size_bytes": len(response_bytes),
        "request_serialize_us": request_serialize_us,
        "request_deserialize_us": request_deserialize_us,
        "response_serialize_us": response_serialize_us,
        "response_deserialize_us": response_deserialize_us,
        "request_serialize_summary": summarize_us(request_serialize_us),
        "request_deserialize_summary": summarize_us(request_deserialize_us),
        "response_serialize_summary": summarize_us(response_serialize_us),
        "response_deserialize_summary": summarize_us(response_deserialize_us),
    }


def flatten_for_csv(measurements: list[dict]) -> list[dict]:
    rows = []

    for item in measurements:
        rows.append(
            {
                "transport": item["transport"],
                "encoding": item["encoding"],
                "operation": item["operation"],
                "request_size_bytes": item["request_size_bytes"],
                "response_size_bytes": item["response_size_bytes"],
                "request_serialize_avg_us": item["request_serialize_summary"]["avg_us"],
                "request_deserialize_avg_us": item["request_deserialize_summary"]["avg_us"],
                "response_serialize_avg_us": item["response_serialize_summary"]["avg_us"],
                "response_deserialize_avg_us": item["response_deserialize_summary"]["avg_us"],
            }
        )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "transport",
        "encoding",
        "operation",
        "request_size_bytes",
        "response_size_bytes",
        "request_serialize_avg_us",
        "request_deserialize_avg_us",
        "response_serialize_avg_us",
        "response_deserialize_avg_us",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started_at = now_utc_iso()

    measurements = []

    for operation in ["set_value", "get_value"]:
        measurements.append(measure_json_representation("http", operation))
        measurements.append(measure_json_representation("ws", operation))
        measurements.append(measure_protobuf_representation(operation))

    raw_output = {
        "started_at": started_at,
        "iterations": ITERATIONS,
        "scope": "application_message_representation_only",
        "measurements": measurements,
        "finished_at": now_utc_iso(),
    }

    with RAW_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2)

    csv_rows = flatten_for_csv(measurements)
    save_csv(csv_rows, CSV_OUTPUT_PATH)

    print(f"Raw results saved to: {RAW_OUTPUT_PATH}")
    print(f"CSV summary saved to: {CSV_OUTPUT_PATH}")


if __name__ == "__main__":
    main()