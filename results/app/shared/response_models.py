from typing import Any, Literal

from pydantic import BaseModel

from app.shared.error_codes import ErrorCode


class SuccessResponse(BaseModel):
    status: Literal["success"] = "success"
    message_id: str
    operation: str
    resource_id: str
    result: dict[str, Any]


class ErrorDetails(BaseModel):
    code: ErrorCode
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: ErrorDetails