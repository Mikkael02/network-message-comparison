from pydantic import BaseModel, Field

from app.overhead.models import ApplicationProtocol


class LayerPreset(BaseModel):
    name: str
    header_size_bytes: int = Field(..., ge=0)
    trailer_size_bytes: int = Field(default=0, ge=0)
    minimum_payload_bytes: int = Field(default=0, ge=0)
    notes: str = ""


class ProtocolPreset(BaseModel):
    application_protocol: ApplicationProtocol
    default_header_overhead_bytes: int = Field(..., ge=0)
    notes: str = ""


ETHERNET_II_PRESET = LayerPreset(
    name="Ethernet II",
    header_size_bytes=14,
    trailer_size_bytes=4,
    minimum_payload_bytes=46,
    notes="Basic Ethernet II frame model with 14-byte header and 4-byte FCS.",
)

IPV4_PRESET = LayerPreset(
    name="IPv4",
    header_size_bytes=20,
    trailer_size_bytes=0,
    minimum_payload_bytes=0,
    notes="Minimum IPv4 header size without options.",
)

TCP_PRESET = LayerPreset(
    name="TCP",
    header_size_bytes=20,
    trailer_size_bytes=0,
    minimum_payload_bytes=0,
    notes="Minimum TCP header size without options.",
)

HTTP_1_1_PRESET = ProtocolPreset(
    application_protocol=ApplicationProtocol.HTTP,
    default_header_overhead_bytes=200,
    notes=(
        "Simplified HTTP/1.1 overhead model. "
        "Represents request/response line and typical headers."
    ),
)

WEBSOCKET_PRESET = ProtocolPreset(
    application_protocol=ApplicationProtocol.WEBSOCKET,
    default_header_overhead_bytes=6,
    notes=(
        "Simplified WebSocket frame overhead model for small payloads. "
        "Does not include opening handshake."
    ),
)

GRPC_PRESET = ProtocolPreset(
    application_protocol=ApplicationProtocol.GRPC,
    default_header_overhead_bytes=45,
    notes=(
        "Simplified gRPC-over-HTTP/2 overhead model, including gRPC message prefix "
        "and approximate protocol framing."
    ),
)

DEFAULT_PROTOCOL_PRESETS = {
    ApplicationProtocol.HTTP: HTTP_1_1_PRESET,
    ApplicationProtocol.WEBSOCKET: WEBSOCKET_PRESET,
    ApplicationProtocol.GRPC: GRPC_PRESET,
}

DEFAULT_LAYER_PRESETS = {
    "ethernet": ETHERNET_II_PRESET,
    "ipv4": IPV4_PRESET,
    "tcp": TCP_PRESET,
}