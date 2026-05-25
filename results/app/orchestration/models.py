from pydantic import BaseModel, Field


class ServiceStatusCheckConfig(BaseModel):
    http_health_url: str = "http://127.0.0.1:8000/health"
    ws_health_url: str = "http://127.0.0.1:8001/health"
    grpc_address: str = "127.0.0.1:50051"
    timeout_seconds: float = Field(default=2.0, gt=0, le=10)


class SingleServiceStatus(BaseModel):
    service_name: str
    available: bool
    response_time_ms: float | None = None
    detail: str


class EnvironmentServiceStatusResponse(BaseModel):
    checked_at: str
    config: ServiceStatusCheckConfig
    all_available: bool
    services: list[SingleServiceStatus]