import pytest
import secrets

from myapp.web import create_app


@pytest.fixture
def client():
    return create_app({"TESTING": True, "SECRET_KEY": secrets.token_hex(32)}).test_client()


def csrf_headers(client):
    return {"X-CSRFToken": client.get("/api/csrf").json["csrf_token"]}


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Máy tính Python" in response.get_data(as_text=True)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 2, 3, 5), ("subtract", 5, 3, 2),
    ("multiply", 4, 3, 12), ("divide", 10, 2, 5),
])
def test_calculations(client, operation, a, b, expected):
    response = client.post("/api/calculate", json={"operation": operation, "a": a, "b": b}, headers=csrf_headers(client))
    assert response.status_code == 200
    assert response.json == {"result": expected}


@pytest.mark.parametrize("payload", [
    [], {"operation": "power", "a": 2, "b": 3},
    {"operation": [], "a": 2, "b": 3},
    {"operation": "add", "a": "2", "b": 3},
    {"operation": "add", "a": True, "b": 3},
    {"operation": "add", "a": 2},
    {"operation": "add", "a": float("inf"), "b": 3},
    {"operation": "multiply", "a": 1e308, "b": 1e308},
    {"operation": "add", "a": 10 ** 400, "b": 3},
    {"operation": "divide", "a": 10, "b": 0},
])
def test_invalid_input(client, payload):
    response = client.post("/api/calculate", json=payload, headers=csrf_headers(client))
    assert response.status_code == 400
    assert response.json["error"]


def test_invalid_json(client):
    response = client.post("/api/calculate", data="{", content_type="application/json", headers=csrf_headers(client))
    assert response.status_code == 400


def test_rejects_missing_csrf(client):
    response = client.post("/api/calculate", json={"operation": "add", "a": 2, "b": 3})
    assert response.status_code == 400
    assert "CSRF" in response.json["error"]


def test_rejects_invalid_csrf(client):
    client.get("/api/csrf")
    response = client.post("/api/calculate", json={"operation": "add", "a": 2, "b": 3}, headers={"X-CSRFToken": "invalid"})
    assert response.status_code == 400


def test_requires_secret_key(monkeypatch):
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="APP_SECRET_KEY"):
        create_app()
