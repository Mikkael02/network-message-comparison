from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_frontend_root_returns_html():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Transmission Overhead Calculator" in response.text
    assert "Research Dashboard" in response.text
    assert "Transport comparison" in response.text
    assert "Top-level insights" in response.text
    assert "Report viewer" in response.text
    assert "Run request-response experiment" in response.text
    assert "Last request-response experiment summary" in response.text
    assert "Run realtime experiment" in response.text
    assert "Last realtime experiment summary" in response.text
    assert "Run validation experiment" in response.text
    assert "Last validation experiment summary" in response.text
    assert "Run serialization experiment" in response.text
    assert "Last serialization experiment summary" in response.text
    assert "Transmission profile" in response.text
    assert "Advanced transmission settings" in response.text
    assert "Effective transmission settings" in response.text
    assert "Environment status" in response.text
    assert "Environment summary" in response.text
    assert "Environment services" in response.text
    assert "Refresh status" in response.text
    assert "Save result" in response.text
    assert "Run label" in response.text
    assert "Recent saved runs" in response.text
    assert "Recent runs summary" in response.text
    assert "Recent runs table" in response.text
    assert "Saved run details" in response.text
    assert "Saved run detail summary" in response.text
    assert "Saved run detail JSON" in response.text
    assert "Load selected run" in response.text


def test_frontend_static_css_is_served():
    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_frontend_static_js_is_served():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"] or "text/plain" in response.headers["content-type"]