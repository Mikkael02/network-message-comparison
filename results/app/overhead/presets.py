from pydantic import BaseModel, Field

from app.overhead.models import (
    ApplicationProtocol,
    TransmissionProfile,
)


class LayerPreset(BaseModel):
    name: str
    header_size_bytes: int = Field(..., ge=0)
    trailer_size_bytes: int = Field(default=0, ge=0)
    minimum_payload_bytes: int = Field(default=0, ge=0)


class ProtocolPreset(BaseModel):
    name: str
    default_header_overhead_bytes: int = Field(..., ge=0)


class TransmissionProfilePreset(BaseModel):
    name: str
    description: str
    mtu_bytes: int = Field(..., ge=68)
    ethernet_header_size_bytes: int = Field(..., ge=0)
    ethernet_trailer_size_bytes: int = Field(..., ge=0)
    ethernet_min_payload_bytes: int = Field(..., ge=0)
    ipv4_header_size_bytes: int = Field(..., ge=0)
    tcp_header_size_bytes: int = Field(..., ge=0)


# =========================
# Legacy exported presets
# =========================

ETHERNET_II_PRESET = LayerPreset(
    name="Ethernet II",
    header_size_bytes=14,
    trailer_size_bytes=4,
    minimum_payload_bytes=46,
)

IPV4_PRESET = LayerPreset(
    name="IPv4",
    header_size_bytes=20,
)

TCP_PRESET = LayerPreset(
    name="TCP",
    header_size_bytes=20,
)

HTTP_PROTOCOL_PRESET = ProtocolPreset(
    name="HTTP/JSON",
    default_header_overhead_bytes=200,
)

WEBSOCKET_PROTOCOL_PRESET = ProtocolPreset(
    name="WebSocket/JSON",
    default_header_overhead_bytes=8,
)

GRPC_PROTOCOL_PRESET = ProtocolPreset(
    name="gRPC/Protobuf",
    default_header_overhead_bytes=5,
)


# =========================
# Current preset collections
# =========================

DEFAULT_LAYER_PRESETS = {
    "ethernet": ETHERNET_II_PRESET,
    "ipv4": IPV4_PRESET,
    "tcp": TCP_PRESET,
}

DEFAULT_PROTOCOL_PRESETS = {
    ApplicationProtocol.HTTP: HTTP_PROTOCOL_PRESET,
    ApplicationProtocol.WEBSOCKET: WEBSOCKET_PROTOCOL_PRESET,
    ApplicationProtocol.GRPC: GRPC_PROTOCOL_PRESET,
}

TRANSMISSION_PROFILE_PRESETS = {
    TransmissionProfile.STANDARD_ETHERNET: TransmissionProfilePreset(
        name="Standard Ethernet/TCP",
        description="Ethernet II + IPv4 + TCP with standard MTU 1500.",
        mtu_bytes=1500,
        ethernet_header_size_bytes=14,
        ethernet_trailer_size_bytes=4,
        ethernet_min_payload_bytes=46,
        ipv4_header_size_bytes=20,
        tcp_header_size_bytes=20,
    ),
    TransmissionProfile.CONSTRAINED_MTU: TransmissionProfilePreset(
        name="Constrained MTU",
        description="Smaller MTU profile useful for showing faster fragmentation growth.",
        mtu_bytes=576,
        ethernet_header_size_bytes=14,
        ethernet_trailer_size_bytes=4,
        ethernet_min_payload_bytes=46,
        ipv4_header_size_bytes=20,
        tcp_header_size_bytes=20,
    ),
    TransmissionProfile.TCP_OPTIONS_HEAVY: TransmissionProfilePreset(
        name="TCP Options Heavy",
        description="Standard MTU with larger IPv4/TCP headers to simulate options-heavy transport.",
        mtu_bytes=1500,
        ethernet_header_size_bytes=14,
        ethernet_trailer_size_bytes=4,
        ethernet_min_payload_bytes=46,
        ipv4_header_size_bytes=24,
        tcp_header_size_bytes=32,
    ),
    TransmissionProfile.JUMBO_FRAME: TransmissionProfilePreset(
        name="Jumbo Frame",
        description="Large MTU profile for showing reduced fragmentation with big payloads.",
        mtu_bytes=9000,
        ethernet_header_size_bytes=14,
        ethernet_trailer_size_bytes=4,
        ethernet_min_payload_bytes=46,
        ipv4_header_size_bytes=20,
        tcp_header_size_bytes=20,
    ),
}


# =========================
# Backward-compatible aliases
# =========================

ETHERNET_PRESET = ETHERNET_II_PRESET

HTTP_PRESET = HTTP_PROTOCOL_PRESET
WEBSOCKET_PRESET = WEBSOCKET_PROTOCOL_PRESET
GRPC_PRESET = GRPC_PROTOCOL_PRESET

HTTP_JSON_PRESET = HTTP_PROTOCOL_PRESET
WEBSOCKET_JSON_PRESET = WEBSOCKET_PROTOCOL_PRESET
GRPC_PROTOBUF_PRESET = GRPC_PROTOCOL_PRESET

HTTP_1_1_PRESET = HTTP_PROTOCOL_PRESET
WEBSOCKET_FRAME_PRESET = WEBSOCKET_PROTOCOL_PRESET
WEBSOCKET_1_0_PRESET = WEBSOCKET_PROTOCOL_PRESET
GRPC_FRAME_PRESET = GRPC_PROTOCOL_PRESET
GRPC_1_0_PRESET = GRPC_PROTOCOL_PRESET


__all__ = [
    "LayerPreset",
    "ProtocolPreset",
    "TransmissionProfilePreset",
    "ETHERNET_II_PRESET",
    "IPV4_PRESET",
    "TCP_PRESET",
    "HTTP_PROTOCOL_PRESET",
    "WEBSOCKET_PROTOCOL_PRESET",
    "GRPC_PROTOCOL_PRESET",
    "ETHERNET_PRESET",
    "HTTP_PRESET",
    "WEBSOCKET_PRESET",
    "GRPC_PRESET",
    "HTTP_JSON_PRESET",
    "WEBSOCKET_JSON_PRESET",
    "GRPC_PROTOBUF_PRESET",
    "HTTP_1_1_PRESET",
    "WEBSOCKET_FRAME_PRESET",
    "WEBSOCKET_1_0_PRESET",
    "GRPC_FRAME_PRESET",
    "GRPC_1_0_PRESET",
    "DEFAULT_LAYER_PRESETS",
    "DEFAULT_PROTOCOL_PRESETS",
    "TRANSMISSION_PROFILE_PRESETS",
]