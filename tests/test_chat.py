from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_ai_client

class MockAI:
    async def chat(self, messages, max_tokens, temperature):
        return {"reply": "Hello from mock", "usage": {"promptTokens": 3, "completionTokens": 3, "totalTokens": 6}}


def override_ai():
    return MockAI()


app.dependency_overrides[get_ai_client] = override_ai
client = TestClient(app)


def login_get_token():
    r = client.post("/api/auth/login", json={"email": "student@example.com", "password": "password"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_chat_flow_create_and_reply():
    token = login_get_token()
    r = client.post("/api/chat", headers={"Authorization": f"Bearer {token}"}, json={"message": "Hello world"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"].startswith("Hello")
    assert body["conversationId"]


def test_privacy_redaction_and_history():
    token = login_get_token()
    r1 = client.post("/api/chat", headers={"Authorization": f"Bearer {token}"}, json={"message": "First"})
    cid = r1.json()["conversationId"]

    r2 = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert any(item["id"] == cid for item in r2.json())

    r3 = client.get(f"/api/history/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    assert "id" in r3.json()
