import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_success():
    r = client.post("/api/auth/login", json={"email": "student@example.com", "password": "password"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data


def test_login_fail():
    r = client.post("/api/auth/login", json={"email": "student@example.com", "password": "wrong"})
    assert r.status_code == 401
