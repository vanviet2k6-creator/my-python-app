import pytest

from myapp.web import create_app


@pytest.fixture
def client():
    return create_app().test_client()


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
    response = client.post("/api/calculate", json={"operation": operation, "a": a, "b": b})
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
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
    assert response.json["error"]


def test_invalid_json(client):
    response = client.post("/api/calculate", data="{", content_type="application/json")
    assert response.status_code == 400
