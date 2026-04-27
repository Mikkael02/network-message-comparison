from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.models.message import MessageEnvelope
from app.core.models.realtime import StateChangeBatch
from app.core.services.processor import process_message
from app.core.services.realtime_feed import (
    get_state_changes_since,
    seed_demo_state_changes,
)
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
from app.shared.response_models import ErrorResponse, SuccessResponse

app = FastAPI(
    title="Network Message Comparison - HTTP Transport",
    version="0.1.0",
)

state_store = InMemoryStateStore()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    response = build_error_response(
        code=ErrorCode.STRUCTURAL_VALIDATION_ERROR,
        message="Request validation failed",
        details=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(BusinessValidationError)
async def business_validation_exception_handler(
    request: Request,
    exc: BusinessValidationError,
) -> JSONResponse:
    response = build_error_response(
        code=ErrorCode.BUSINESS_VALIDATION_ERROR,
        message=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    response = build_error_response(
        code=ErrorCode.RESOURCE_NOT_FOUND,
        message=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(mode="json"),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/process",
    response_model=SuccessResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
)
def process_endpoint(message: MessageEnvelope) -> SuccessResponse:
    validate_business_rules(message)
    result = process_message(message, state_store)
    return build_success_response(result)


@app.get(
    "/changes",
    response_model=StateChangeBatch,
    responses={
        422: {"model": ErrorResponse},
    },
)
def get_changes_endpoint(
    from_version: int = Query(..., ge=0),
) -> StateChangeBatch:
    return get_state_changes_since(state_store, from_version)


@app.post("/changes/seed", response_model=StateChangeBatch)
def seed_changes_endpoint() -> StateChangeBatch:
    before_version = state_store.get_current_version()
    seed_demo_state_changes(state_store)
    return get_state_changes_since(state_store, before_version)