from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_post_chat_endpoint_new_session(client):
    payload = {
        "message": "Hola, ¿cuál es el estado de mi trámite?",
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["history"]) == 2
    assert data["history"][0]["role"] == "user"
    assert data["history"][1]["role"] == "assistant"


def test_post_chat_endpoint_existing_session(client):
    session_id = "test-session-42"
    payload1 = {
        "message": "Primer mensaje",
        "session_id": session_id,
    }
    res1 = client.post("/chat", json=payload1)
    assert res1.status_code == 200
    assert res1.json()["session_id"] == session_id

    payload2 = {
        "message": "Segundo mensaje",
        "session_id": session_id,
    }
    res2 = client.post("/chat", json=payload2)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["session_id"] == session_id
    assert len(data2["history"]) == 4  # 2 messages from request 1 + 2 from request 2

