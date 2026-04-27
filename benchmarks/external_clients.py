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


class ExternalHttpClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def close(self) -> None:
        self.client.close()

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post("/process", json=payload)
        return response.json()


class ExternalWsClient:
    def __init__(self, url: str = "ws://127.0.0.1:8001/ws/process") -> None:
        self.url = url

    def close(self) -> None:
        pass

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        return asyncio.run(self._send_async(payload))

    async def _send_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            return json.loads(response)


class ExternalGrpcClient:
    def __init__(self, address: str = "127.0.0.1:50051") -> None:
        self.channel = grpc.insecure_channel(address)
        grpc.channel_ready_future(self.channel).result(timeout=5)
        self.stub = message_service_pb2_grpc.MessageServiceStub(self.channel)

    def close(self) -> None:
        self.channel.close()

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = self._build_request(payload)
        response = self.stub.Process(request)
        return self._normalize_response(response)

    @staticmethod
    def _build_request(payload: dict[str, Any]) -> message_service_pb2.MessageEnvelope:
        operation_map = {
            "set_value": message_service_pb2.SET_VALUE,
            "get_value": message_service_pb2.GET_VALUE,
        }

        payload_data = payload["payload"]
        message_payload = message_service_pb2.MessagePayload(
            operation=operation_map[payload_data["operation"]],
            resource_id=payload_data["resource_id"],
        )

        if "value" in payload_data:
            message_payload.value = payload_data["value"]

        request = message_service_pb2.MessageEnvelope(
            source=payload["source"],
            payload=message_payload,
        )

        if "message_id" in payload:
            request.message_id = payload["message_id"]

        if "timestamp" in payload:
            request.timestamp = payload["timestamp"]

        return request

    @staticmethod
    def _normalize_response(response: message_service_pb2.ProcessReply) -> dict[str, Any]:
        outcome = response.WhichOneof("outcome")

        if outcome == "success":
            success = response.success
            result_type = success.WhichOneof("result")

            if result_type == "update_result":
                result = {
                    "action": success.update_result.action,
                    "stored_value": success.update_result.stored_value,
                }
            else:
                result = {
                    "action": success.get_result.action,
                    "current_value": success.get_result.current_value,
                }

            return {
                "status": success.status,
                "message_id": success.message_id,
                "operation": success.operation,
                "resource_id": success.resource_id,
                "result": result,
            }

        details = json.loads(response.error.details_json) if response.error.details_json else None

        return {
            "status": response.error.status,
            "error": {
                "code": response.error.code,
                "message": response.error.message,
                "details": details,
            },
        }