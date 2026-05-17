from app.overhead.models import ApplicationProtocol
from app.overhead.presets import (
    DEFAULT_LAYER_PRESETS,
    DEFAULT_PROTOCOL_PRESETS,
    ETHERNET_II_PRESET,
    GRPC_PRESET,
    HTTP_1_1_PRESET,
    IPV4_PRESET,
    TCP_PRESET,
    WEBSOCKET_PRESET,
)


def test_default_layer_presets_have_expected_basic_values():
    assert ETHERNET_II_PRESET.header_size_bytes == 14
    assert ETHERNET_II_PRESET.trailer_size_bytes == 4
    assert ETHERNET_II_PRESET.minimum_payload_bytes == 46

    assert IPV4_PRESET.header_size_bytes == 20
    assert TCP_PRESET.header_size_bytes == 20


def test_default_protocol_presets_have_expected_protocol_mapping():
    assert DEFAULT_PROTOCOL_PRESETS[ApplicationProtocol.HTTP] == HTTP_1_1_PRESET
    assert DEFAULT_PROTOCOL_PRESETS[ApplicationProtocol.WEBSOCKET] == WEBSOCKET_PRESET
    assert DEFAULT_PROTOCOL_PRESETS[ApplicationProtocol.GRPC] == GRPC_PRESET


def test_default_protocol_overheads_are_positive():
    assert HTTP_1_1_PRESET.default_header_overhead_bytes > 0
    assert WEBSOCKET_PRESET.default_header_overhead_bytes > 0
    assert GRPC_PRESET.default_header_overhead_bytes > 0


def test_default_layer_presets_dictionary_contains_required_keys():
    assert "ethernet" in DEFAULT_LAYER_PRESETS
    assert "ipv4" in DEFAULT_LAYER_PRESETS
    assert "tcp" in DEFAULT_LAYER_PRESETS