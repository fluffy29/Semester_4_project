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


def login_get_token(email="student@example.com"):
    r = client.post("/api/auth/login", json={"email": email, "password": "password"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_admin_list_requires_role():
    token = login_get_token()
    r = client.get("/api/admin/conversations", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

    # admin token
    admin_token = login_get_token("admin@example.com")
    r2 = client.get("/api/admin/conversations", headers={"Authorization": f"Bearer {admin_token}"})
    assert r2.status_code == 200
