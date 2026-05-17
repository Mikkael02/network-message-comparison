from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_reports_available_endpoint_returns_report_list():
    response = client.get("/reports/available")

    assert response.status_code == 200
    data = response.json()

    assert "reports" in data
    assert isinstance(data["reports"], list)
    assert any(report["key"] == "request-response" for report in data["reports"])


def test_request_response_report_endpoint_returns_json_when_file_exists():
    response = client.get("/reports/request-response")

    if response.status_code == 404:
        assert response.json()["detail"] == "Report file not found"
    else:
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_interpretation_report_endpoint_returns_text_wrapper_when_file_exists():
    response = client.get("/reports/interpretation")

    if response.status_code == 404:
        assert response.json()["detail"] == "Report file not found"
    else:
        assert response.status_code == 200
        assert "content" in response.json()


def test_unknown_report_key_returns_404():
    response = client.get("/reports/not-existing-report")

    assert response.status_code == 404
    assert response.json()["detail"] == "Report key not found"