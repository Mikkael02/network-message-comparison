from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ApplicationProtocol(str, Enum):
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"


class PayloadEncoding(str, Enum):
    JSON = "json"
    PROTOBUF = "protobuf"


class LinkLayer(str, Enum):
    ETHERNET = "ethernet"


class NetworkLayer(str, Enum):
    IPV4 = "ipv4"


class TransportLayer(str, Enum):
    TCP = "tcp"


class AggregationMode(str, Enum):
    PER_MESSAGE = "per_message"
    BATCHED = "batched"
    NAGLE_LIKE = "nagle_like"


class TrafficDirection(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BIDIRECTIONAL = "bidirectional"


class TransmissionAnalysisInput(BaseModel):
    application_protocol: ApplicationProtocol
    payload_encoding: PayloadEncoding

    link_layer: LinkLayer = LinkLayer.ETHERNET
    network_layer: NetworkLayer = NetworkLayer.IPV4
    transport_layer: TransportLayer = TransportLayer.TCP

    payload_size_bytes: int = Field(..., ge=1)
    message_count: int = Field(default=1, ge=1)
    message_frequency_hz: float = Field(default=1.0, gt=0)

    batch_size: int = Field(default=1, ge=1)
    aggregation_mode: AggregationMode = AggregationMode.PER_MESSAGE
    traffic_direction: TrafficDirection = TrafficDirection.REQUEST

    mtu_bytes: int = Field(default=1500, ge=68)
    nagle_enabled: bool = False

    application_header_overhead_bytes: Optional[int] = Field(default=None, ge=0)

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, value: int) -> int:
        if value < 1:
            raise ValueError("batch_size must be at least 1")
        return value

    @field_validator("mtu_bytes")
    @classmethod
    def validate_mtu_bytes(cls, value: int) -> int:
        if value < 68:
            raise ValueError("mtu_bytes must be at least 68 bytes for IPv4")
        return value


class LayerOverheadBreakdown(BaseModel):
    payload_size_bytes: int
    serialized_payload_size_bytes: int
    application_protocol_overhead_bytes: int
    transport_overhead_bytes: int
    network_overhead_bytes: int
    link_overhead_bytes: int
    total_transmitted_bytes: int


class FrameAnalysis(BaseModel):
    mtu_bytes: int
    segment_count: int
    frame_count: int
    bytes_per_frame: list[int]
    unused_payload_space_bytes: int
    fragmentation_occurred: bool


class EfficiencyAnalysis(BaseModel):
    overhead_bytes: int
    overhead_ratio: float
    payload_efficiency_ratio: float
    required_bitrate_bps: float
    required_bitrate_kbps: float
    required_bitrate_mbps: float


class TransmissionAnalysisResult(BaseModel):
    input_summary: TransmissionAnalysisInput
    serialized_payload_size_bytes: int
    total_sequence_payload_bytes: int
    total_sequence_transmitted_bytes: int
    total_messages_after_aggregation: int
    layer_breakdown: LayerOverheadBreakdown
    frame_analysis: FrameAnalysis
    efficiency: EfficiencyAnalysis
    notes: list[str]


class SequencePatternInput(BaseModel):
    application_protocol: ApplicationProtocol
    payload_encoding: PayloadEncoding
    payload_sizes_bytes: list[int] = Field(..., min_length=1)
    message_frequency_hz: float = Field(default=1.0, gt=0)
    aggregation_mode: AggregationMode = AggregationMode.PER_MESSAGE
    batch_size: int = Field(default=1, ge=1)
    mtu_bytes: int = Field(default=1500, ge=68)
    application_header_overhead_bytes: Optional[int] = Field(default=None, ge=0)

    @field_validator("payload_sizes_bytes")
    @classmethod
    def validate_payload_sizes(cls, values: list[int]) -> list[int]:
        if any(v < 1 for v in values):
            raise ValueError("all payload sizes must be greater than 0")
        return values


class AggregatedTransmissionUnit(BaseModel):
    batch_index: int = Field(..., ge=1)
    original_message_count: int = Field(..., ge=1)
    original_payload_bytes_sum: int = Field(..., ge=1)
    aggregated_serialized_payload_size_bytes: int = Field(..., ge=1)
    application_protocol_overhead_bytes: int = Field(..., ge=0)
    total_transmitted_bytes: int = Field(..., ge=1)
    frame_count: int = Field(..., ge=1)


class SequenceTransmissionAnalysisResult(BaseModel):
    input_summary: SequencePatternInput
    original_message_count: int = Field(..., ge=1)
    aggregated_message_count: int = Field(..., ge=1)
    total_original_payload_bytes: int = Field(..., ge=1)
    total_serialized_payload_bytes: int = Field(..., ge=1)
    total_transmitted_bytes: int = Field(..., ge=1)
    total_frame_count: int = Field(..., ge=1)
    overhead_bytes: int = Field(..., ge=0)
    overhead_ratio: float = Field(..., ge=0)
    payload_efficiency_ratio: float = Field(..., gt=0, le=1)
    required_bitrate_bps: float = Field(..., gt=0)
    required_bitrate_kbps: float = Field(..., gt=0)
    required_bitrate_mbps: float = Field(..., gt=0)
    aggregated_units: list[AggregatedTransmissionUnit]
    notes: list[str]