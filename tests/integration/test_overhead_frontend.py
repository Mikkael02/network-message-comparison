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


def test_frontend_static_css_is_served():
    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_frontend_static_js_is_served():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"] or "text/plain" in response.headers["content-type"]