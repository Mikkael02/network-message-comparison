from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.models.message import MessageEnvelope
from app.core.services.processor import process_message
from app.core.services.state_store import (
    InMemoryStateStore,
    ResourceNotFoundError,
)
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError
from app.shared.error_codes import ErrorCode
from app.shared.response_builders import (
    build_error_response,
    build_success_response,
)

app = FastAPI(
    title="Network Message Comparison - WebSocket Transport",
    version="0.1.0",
)

state_store = InMemoryStateStore()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/process")
async def websocket_process_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            raw_data = await websocket.receive_json()

            try:
                message = MessageEnvelope.model_validate(raw_data)
                validate_business_rules(message)
                result = process_message(message, state_store)

                response = build_success_response(result)
                await websocket.send_json(response.model_dump(mode="json"))

            except ValidationError as exc:
                error_response = build_error_response(
                    code=ErrorCode.STRUCTURAL_VALIDATION_ERROR,
                    message="Request validation failed",
                    details=exc.errors(),
                )
                await websocket.send_json(error_response.model_dump(mode="json"))

            except BusinessValidationError as exc:
                error_response = build_error_response(
                    code=ErrorCode.BUSINESS_VALIDATION_ERROR,
                    message=str(exc),
                )
                await websocket.send_json(error_response.model_dump(mode="json"))

            except ResourceNotFoundError as exc:
                error_response = build_error_response(
                    code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=str(exc),
                )
                await websocket.send_json(error_response.model_dump(mode="json"))

    except WebSocketDisconnect:
        pass