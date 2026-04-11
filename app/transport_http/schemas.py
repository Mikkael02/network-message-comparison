from typing import Any, Literal

from pydantic import BaseModel


class ProcessResponse(BaseModel):
    status: Literal["success"] = "success"
    message_id: str
    operation: str
    resource_id: str
    result: dict[str, Any]


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: ErrorDetails