import os
import pytest
from fastapi.testclient import TestClient

from main import app

@pytest.fixture
def auth_headers():
    api_key = "test_api_key_123"
    os.environ["API_KEY"] = api_key
    return {"Authorization": f"Bearer {api_key}"}

def test_responses_unauthorized():
    with TestClient(app) as client:
        response = client.post("/v1/responses", json={"input": "Hello"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated" or response.json()["detail"] == "Invalid or missing API Key"

def test_responses_invalid_token():
    os.environ["API_KEY"] = "test_api_key_123"
    headers = {"Authorization": "Bearer wrong_token"}
    with TestClient(app) as client:
        response = client.post("/v1/responses", json={"input": "Hello"}, headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or missing API Key"

def test_responses_success(auth_headers):
    payload = {
        "model": "test",
        "input": "Hola, cuéntame de ti"
    }
    with TestClient(app) as client:
        response = client.post("/v1/responses", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["object"] == "response"
        assert data["status"] == "completed"
        assert "id" in data
        assert data["id"].startswith("resp_")
        assert len(data["output"]) == 1
        
        msg = data["output"][0]
        assert msg["role"] == "assistant"
        assert msg["type"] == "message"
        assert len(msg["content"]) == 1
        
        content = msg["content"][0]
        assert content["type"] == "output_text"
        assert len(content["text"]) > 0
        assert data["previous_response_id"] is not None

def test_responses_with_previous_session(auth_headers):
    with TestClient(app) as client:
        # First request
        payload1 = {
            "model": "test",
            "input": "Hola, cuéntame de ti"
        }
        response1 = client.post("/v1/responses", json=payload1, headers=auth_headers)
        assert response1.status_code == 200
        session_id = response1.json()["previous_response_id"]
        
        # Second request with follow-up
        payload2 = {
            "model": "test",
            "input": "¿y qué stack usaste ahí?",
            "previous_response_id": session_id
        }
        response2 = client.post("/v1/responses", json=payload2, headers=auth_headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["previous_response_id"] == session_id

def test_responses_streaming_success(auth_headers):
    payload = {
        "model": "test",
        "input": "Hola",
        "stream": True
    }
    with TestClient(app) as client:
        response = client.post("/v1/responses", json=payload, headers=auth_headers)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        decoded_lines = [line.strip() for line in response.iter_lines() if line.strip()]
        
        # Verify event presence and ordering
        assert "event: response.created" in decoded_lines
        assert "event: response.output_item.added" in decoded_lines
        assert "event: response.content_part.added" in decoded_lines
        assert any(line.startswith("event: response.output_text.delta") for line in decoded_lines)
        assert "event: response.output_text.done" in decoded_lines
        assert "event: response.content_part.done" in decoded_lines
        assert "event: response.output_item.done" in decoded_lines
        assert "event: response.completed" in decoded_lines
        assert "data: [DONE]" in decoded_lines

