import json
from concurrent import futures

import grpc
from pydantic import ValidationError

from app.core.models.message import MessageEnvelope
from app.core.services.processor import process_message
from app.core.services.realtime_feed import get_state_changes_since
from app.core.services.state_store import InMemoryStateStore, ResourceNotFoundError
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError
from app.shared.error_codes import ErrorCode
from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)


def _proto_operation_to_domain(operation: int) -> str:
    mapping = {
        message_service_pb2.SET_VALUE: "set_value",
        message_service_pb2.GET_VALUE: "get_value",
    }
    return mapping.get(operation, "invalid_operation")


def _grpc_request_to_domain_data(
    request: message_service_pb2.MessageEnvelope,
) -> dict:
    payload_data = {
        "operation": _proto_operation_to_domain(request.payload.operation),
        "resource_id": request.payload.resource_id,
    }

    if request.payload.HasField("value"):
        payload_data["value"] = request.payload.value

    data = {
        "source": request.source,
        "payload": payload_data,
    }

    if request.message_id:
        data["message_id"] = request.message_id

    if request.timestamp:
        data["timestamp"] = request.timestamp

    return data


def _build_success_reply(result: dict) -> message_service_pb2.ProcessReply:
    if result["operation"] == "set_value":
        return message_service_pb2.ProcessReply(
            success=message_service_pb2.SuccessReply(
                status="success",
                message_id=result["message_id"],
                operation=result["operation"],
                resource_id=result["resource_id"],
                update_result=message_service_pb2.UpdateResult(
                    action=result["result"]["action"],
                    stored_value=result["result"]["stored_value"],
                ),
            )
        )

    if result["operation"] == "get_value":
        return message_service_pb2.ProcessReply(
            success=message_service_pb2.SuccessReply(
                status="success",
                message_id=result["message_id"],
                operation=result["operation"],
                resource_id=result["resource_id"],
                get_result=message_service_pb2.GetResult(
                    action=result["result"]["action"],
                    current_value=result["result"]["current_value"],
                ),
            )
        )

    return message_service_pb2.ProcessReply(
        error=message_service_pb2.ErrorReply(
            status="error",
            code=ErrorCode.STRUCTURAL_VALIDATION_ERROR.value,
            message="Unsupported operation in processing result",
            details_json="",
        )
    )


def _build_error_reply(
    code: ErrorCode,
    message: str,
    details=None,
) -> message_service_pb2.ProcessReply:
    details_json = json.dumps(details) if details is not None else ""

    return message_service_pb2.ProcessReply(
        error=message_service_pb2.ErrorReply(
            status="error",
            code=code.value,
            message=message,
            details_json=details_json,
        )
    )


def _build_state_change_batch(
    batch,
) -> message_service_pb2.StateChangeBatch:
    return message_service_pb2.StateChangeBatch(
        from_version=batch.from_version,
        current_version=batch.current_version,
        events=[
            message_service_pb2.StateChangeEvent(
                version=event.version,
                timestamp=event.timestamp.isoformat(),
                resource_id=event.resource_id,
                value=event.value,
            )
            for event in batch.events
        ],
    )


class MessageServiceServicer(message_service_pb2_grpc.MessageServiceServicer):
    def __init__(self, state_store: InMemoryStateStore) -> None:
        self.state_store = state_store

    def Process(self, request, context):
        try:
            domain_data = _grpc_request_to_domain_data(request)
            message = MessageEnvelope.model_validate(domain_data)

            validate_business_rules(message)
            result = process_message(message, self.state_store)

            return _build_success_reply(result)

        except ValidationError as exc:
            return _build_error_reply(
                code=ErrorCode.STRUCTURAL_VALIDATION_ERROR,
                message="Request validation failed",
                details=exc.errors(),
            )

        except BusinessValidationError as exc:
            return _build_error_reply(
                code=ErrorCode.BUSINESS_VALIDATION_ERROR,
                message=str(exc),
            )

        except ResourceNotFoundError as exc:
            return _build_error_reply(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message=str(exc),
            )

    def StreamChanges(self, request, context):
        try:
            from_version = request.from_version
            batch = get_state_changes_since(self.state_store, from_version)
            yield _build_state_change_batch(batch)

        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return


def create_server(
    state_store: InMemoryStateStore | None = None,
) -> grpc.Server:
    store = state_store or InMemoryStateStore()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(
        MessageServiceServicer(store),
        server,
    )
    return server


def serve(address: str = "127.0.0.1:50051") -> None:
    server = create_server()
    server.add_insecure_port(address)
    server.start()
    print(f"gRPC server running on {address}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()