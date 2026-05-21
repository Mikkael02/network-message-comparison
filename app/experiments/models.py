from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ExperimentTransport(str, Enum):
    HTTP = "http"
    WS = "ws"
    GRPC = "grpc"


class ValidationScenario(str, Enum):
    BASELINE_VALID_DICT = "baseline_valid_dict"
    STRUCTURAL_VALIDATION_VALID_SET = "structural_validation_valid_set"
    FULL_VALIDATION_VALID_SET = "full_validation_valid_set"
    STRUCTURAL_VALIDATION_INVALID = "structural_validation_invalid"
    BUSINESS_VALIDATION_INVALID = "business_validation_invalid"

class SerializationOperation(str, Enum):
    SET_VALUE = "set_value"
    GET_VALUE = "get_value"

class RequestResponseExperimentConfig(BaseModel):
    transports: list[ExperimentTransport] = Field(
        default_factory=lambda: [
            ExperimentTransport.HTTP,
            ExperimentTransport.WS,
            ExperimentTransport.GRPC,
        ],
        min_length=1,
    )
    iterations: int = Field(default=50, ge=1, le=5000)

    http_base_url: str = "http://127.0.0.1:8000"
    ws_url: str = "ws://127.0.0.1:8001/ws/process"
    grpc_address: str = "127.0.0.1:50051"

    source: str = "external_benchmark_client"
    set_value: int = Field(default=42, ge=0, le=1000)
    get_seed_value: int = Field(default=77, ge=0, le=1000)

    set_resource_prefix: str = "rr_benchmark_set"
    get_resource_prefix: str = "rr_benchmark_get"

    @field_validator("transports")
    @classmethod
    def validate_unique_transports(
        cls,
        value: list[ExperimentTransport],
    ) -> list[ExperimentTransport]:
        if len(set(value)) != len(value):
            raise ValueError("transports must not contain duplicates")
        return value


class RealtimeFetchExperimentConfig(BaseModel):
    transports: list[ExperimentTransport] = Field(
        default_factory=lambda: [
            ExperimentTransport.HTTP,
            ExperimentTransport.WS,
            ExperimentTransport.GRPC,
        ],
        min_length=1,
    )
    iterations: int = Field(default=50, ge=1, le=5000)

    http_base_url: str = "http://127.0.0.1:8000"
    ws_changes_url: str = "ws://127.0.0.1:8001/ws/changes"
    ws_process_url: str = "ws://127.0.0.1:8001/ws/process"
    grpc_address: str = "127.0.0.1:50051"

    resource_prefix: str = "realtime_benchmark"
    first_value: int = Field(default=10, ge=0, le=1000)
    second_value: int = Field(default=20, ge=0, le=1000)
    third_value: int = Field(default=15, ge=0, le=1000)

    @field_validator("transports")
    @classmethod
    def validate_unique_realtime_transports(
        cls,
        value: list[ExperimentTransport],
    ) -> list[ExperimentTransport]:
        if len(set(value)) != len(value):
            raise ValueError("transports must not contain duplicates")
        return value


class ValidationExperimentConfig(BaseModel):
    scenarios: list[ValidationScenario] = Field(
        default_factory=lambda: [
            ValidationScenario.BASELINE_VALID_DICT,
            ValidationScenario.STRUCTURAL_VALIDATION_VALID_SET,
            ValidationScenario.FULL_VALIDATION_VALID_SET,
            ValidationScenario.STRUCTURAL_VALIDATION_INVALID,
            ValidationScenario.BUSINESS_VALIDATION_INVALID,
        ],
        min_length=1,
    )
    iterations: int = Field(default=5000, ge=1, le=200000)

    source: str = "validation_benchmark_client"
    valid_resource_id: str = "validation_valid_set"
    readonly_resource_id: str = "readonly_validation_target"
    valid_value: int = Field(default=42, ge=0, le=1000)

    @field_validator("scenarios")
    @classmethod
    def validate_unique_scenarios(
        cls,
        value: list[ValidationScenario],
    ) -> list[ValidationScenario]:
        if len(set(value)) != len(value):
            raise ValueError("scenarios must not contain duplicates")
        return value

class SerializationExperimentConfig(BaseModel):
    transports: list[ExperimentTransport] = Field(
        default_factory=lambda: [
            ExperimentTransport.HTTP,
            ExperimentTransport.WS,
            ExperimentTransport.GRPC,
        ],
        min_length=1,
    )
    operations: list[SerializationOperation] = Field(
        default_factory=lambda: [
            SerializationOperation.SET_VALUE,
            SerializationOperation.GET_VALUE,
        ],
        min_length=1,
    )
    iterations: int = Field(default=2000, ge=1, le=100000)

    http_base_url: str = "http://127.0.0.1:8000"
    ws_url: str = "ws://127.0.0.1:8001/ws/process"
    grpc_address: str = "127.0.0.1:50051"

    source: str = "serialization_benchmark_client"
    set_value: int = Field(default=42, ge=0, le=1000)
    get_seed_value: int = Field(default=77, ge=0, le=1000)

    set_resource_prefix: str = "serialization_set"
    get_resource_prefix: str = "serialization_get"

    @field_validator("transports")
    @classmethod
    def validate_unique_serialization_transports(
        cls,
        value: list[ExperimentTransport],
    ) -> list[ExperimentTransport]:
        if len(set(value)) != len(value):
            raise ValueError("transports must not contain duplicates")
        return value

    @field_validator("operations")
    @classmethod
    def validate_unique_serialization_operations(
        cls,
        value: list[SerializationOperation],
    ) -> list[SerializationOperation]:
        if len(set(value)) != len(value):
            raise ValueError("operations must not contain duplicates")
        return value

class SavedExperimentRunMetadata(BaseModel):
    run_id: str
    experiment_name: str
    saved_at: str
    run_label: str | None = None
    file_path: str


class SavedExperimentRunsResponse(BaseModel):
    total_count: int
    runs: list[SavedExperimentRunMetadata]

class SavedExperimentRunDetailResponse(BaseModel):
    metadata: SavedExperimentRunMetadata
    results: dict