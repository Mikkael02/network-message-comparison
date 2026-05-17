from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_overhead_api_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_overhead_api_presets_returns_layer_and_protocol_presets():
    response = client.get("/presets")

    assert response.status_code == 200

    data = response.json()
    assert "layer_presets" in data
    assert "protocol_presets" in data

    assert "ethernet" in data["layer_presets"]
    assert "ipv4" in data["layer_presets"]
    assert "tcp" in data["layer_presets"]

    assert "http" in data["protocol_presets"]
    assert "websocket" in data["protocol_presets"]
    assert "grpc" in data["protocol_presets"]


def test_analyze_single_returns_valid_result():
    payload = {
        "application_protocol": "http",
        "payload_encoding": "json",
        "payload_size_bytes": 10,
        "message_count": 1,
        "message_frequency_hz": 100.0,
        "mtu_bytes": 1500,
    }

    response = client.post("/analyze/single", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["input_summary"]["application_protocol"] == "http"
    assert data["serialized_payload_size_bytes"] >= 10
    assert data["layer_breakdown"]["total_transmitted_bytes"] > 10
    assert data["frame_analysis"]["frame_count"] >= 1
    assert data["efficiency"]["required_bitrate_kbps"] > 0


def test_analyze_single_detects_fragmentation_for_large_payload():
    payload = {
        "application_protocol": "http",
        "payload_encoding": "json",
        "payload_size_bytes": 5000,
        "message_count": 1,
        "message_frequency_hz": 10.0,
        "mtu_bytes": 1500,
    }

    response = client.post("/analyze/single", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["frame_analysis"]["frame_count"] > 1
    assert data["frame_analysis"]["fragmentation_occurred"] is True


def test_analyze_sequence_returns_valid_result():
    payload = {
        "application_protocol": "http",
        "payload_encoding": "json",
        "payload_sizes_bytes": [10, 10, 10, 10, 10, 10],
        "aggregation_mode": "batched",
        "batch_size": 3,
        "message_frequency_hz": 100.0,
        "mtu_bytes": 1500,
    }

    response = client.post("/analyze/sequence", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["original_message_count"] == 6
    assert data["aggregated_message_count"] == 2
    assert data["total_transmitted_bytes"] > 0
    assert data["total_frame_count"] >= 1
    assert len(data["aggregated_units"]) == 2


def test_analyze_sequence_rejects_invalid_payload_sizes():
    payload = {
        "application_protocol": "http",
        "payload_encoding": "json",
        "payload_sizes_bytes": [10, 0, 10],
        "aggregation_mode": "per_message",
        "batch_size": 1,
        "message_frequency_hz": 100.0,
        "mtu_bytes": 1500,
    }

    response = client.post("/analyze/sequence", json=payload)

    assert response.status_code == 422