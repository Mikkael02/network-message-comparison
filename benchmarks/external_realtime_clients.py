import asyncio
import json
from typing import Any

import grpc
import httpx
import websockets

from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)


def build_set_value_payload(resource_id: str, value: int) -> dict[str, Any]:
    return {
        "source": "realtime_measurement_client",
        "payload": {
            "operation": "set_value",
            "resource_id": resource_id,
            "value": value,
        },
    }


class ExternalRealtimeHttpClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.client = httpx.Client(base_url=base_url, timeout=10.0)

    def close(self) -> None:
        self.client.close()

    def reset_and_seed(self) -> None:
        self.client.post("/changes/seed")

    def set_value(self, resource_id: str, value: int) -> None:
        response = self.client.post("/process", json=build_set_value_payload(resource_id, value))
        data = response.json()
        if data["status"] != "success":
            raise RuntimeError(f"HTTP seed/process failed: {data}")

    def get_changes(self, from_version: int) -> dict[str, Any]:
        response = self.client.get("/changes", params={"from_version": from_version})
        data = response.json()

        if "status" in data and data["status"] == "error":
            raise RuntimeError(f"HTTP realtime request failed: {data}")

        return data


class ExternalRealtimeWsClient:
    def __init__(self, url: str = "ws://127.0.0.1:8001/ws/changes") -> None:
        self.url = url
        self.websocket = None

    async def open(self) -> None:
        self.websocket = await websockets.connect(self.url)

    async def close(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def reset_and_seed(self) -> None:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8001", timeout=10.0) as client:
            await client.post("/ws/changes/seed")

    async def set_value(self, resource_id: str, value: int) -> None:
        async with websockets.connect("ws://127.0.0.1:8001/ws/process") as websocket:
            await websocket.send(json.dumps(build_set_value_payload(resource_id, value)))
            raw_response = await websocket.recv()
            data = json.loads(raw_response)

        if data["status"] != "success":
            raise RuntimeError(f"WS seed/process failed: {data}")

    async def get_changes(self, from_version: int) -> dict[str, Any]:
        await self.websocket.send(json.dumps({"from_version": from_version}))
        raw_response = await self.websocket.recv()
        data = json.loads(raw_response)

        if data["status"] != "success":
            raise RuntimeError(f"WS realtime request failed: {data}")

        return data["batch"]


class ExternalRealtimeGrpcClient:
    def __init__(self, address: str = "127.0.0.1:50051") -> None:
        self.channel = grpc.insecure_channel(address)
        grpc.channel_ready_future(self.channel).result(timeout=5)
        self.stub = message_service_pb2_grpc.MessageServiceStub(self.channel)

    def close(self) -> None:
        self.channel.close()

    def set_value(self, resource_id: str, value: int) -> None:
        response = self.stub.Process(
            message_service_pb2.MessageEnvelope(
                source="realtime_measurement_client",
                payload=message_service_pb2.MessagePayload(
                    operation=message_service_pb2.SET_VALUE,
                    resource_id=resource_id,
                    value=value,
                ),
            )
        )

        if response.WhichOneof("outcome") != "success":
            raise RuntimeError(f"gRPC seed/process failed: {response}")

    def reset_and_seed(self) -> None:
        self.set_value("sensor_01", 10)
        self.set_value("sensor_02", 20)
        self.set_value("sensor_01", 15)

    def get_changes(self, from_version: int) -> dict[str, Any]:
        responses = list(
            self.stub.StreamChanges(
                message_service_pb2.StateChangeRequest(from_version=from_version)
            )
        )

        if len(responses) != 1:
            raise RuntimeError(
                f"Expected exactly one batch in current gRPC streaming setup, got {len(responses)}"
            )

        batch = responses[0]
        return {
            "from_version": batch.from_version,
            "current_version": batch.current_version,
            "events": [
                {
                    "version": event.version,
                    "timestamp": event.timestamp,
                    "resource_id": event.resource_id,
                    "value": event.value,
                }
                for event in batch.events
            ],
        }