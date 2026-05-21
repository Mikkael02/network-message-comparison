from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_frontend_root_returns_html():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    assert "Panel badawczy" in response.text
    assert "Model transmisji" in response.text
    assert "Eksperymenty" in response.text
    assert "Środowisko" in response.text
    assert "Historia uruchomień" in response.text

    assert "Model transmisji i narzutu" in response.text
    assert "Status środowiska" in response.text
    assert "Podsumowanie środowiska" in response.text
    assert "Usługi środowiska" in response.text
    assert "Ostatnie zapisane uruchomienia" in response.text
    assert "Szczegóły zapisanego uruchomienia" in response.text

    assert "Procesy środowiska" not in response.text
    assert "Podsumowanie procesów" not in response.text
    assert "Usługi zarządzane" not in response.text

    assert "Available reports" not in response.text
    assert "Top-level insights" not in response.text
    assert "Report viewer" not in response.text


def test_frontend_static_css_is_served():
    response = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_frontend_static_js_is_served():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert (
        "javascript" in response.headers["content-type"]
        or "text/plain" in response.headers["content-type"]
    )