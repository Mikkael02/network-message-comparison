from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.models.message import MessageEnvelope
from app.core.services.processor import process_message
from app.core.services.state_store import (
    InMemoryStateStore,
    ResourceNotFoundError,
)
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError
from app.transport_http.schemas import ErrorResponse, ProcessResponse

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
    response = ErrorResponse(
        error={
            "code": "STRUCTURAL_VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(),
    )


@app.exception_handler(BusinessValidationError)
async def business_validation_exception_handler(
    request: Request,
    exc: BusinessValidationError,
) -> JSONResponse:
    response = ErrorResponse(
        error={
            "code": "BUSINESS_VALIDATION_ERROR",
            "message": str(exc),
            "details": None,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(),
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    response = ErrorResponse(
        error={
            "code": "RESOURCE_NOT_FOUND",
            "message": str(exc),
            "details": None,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/process",
    response_model=ProcessResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    status_code=status.HTTP_200_OK,
)
def process_endpoint(message: MessageEnvelope) -> ProcessResponse:
    validate_business_rules(message)
    result = process_message(message, state_store)
    return ProcessResponse(**result)