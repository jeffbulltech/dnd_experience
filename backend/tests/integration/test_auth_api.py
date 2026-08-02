"""Integration tests for the auth API endpoints."""

import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "strongpass123",
            "display_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["display_name"] == "New User"
        assert "id" in data

    def test_register_duplicate_username(self, client, test_user):
        resp = client.post("/api/auth/register", json={
            "email": "other@example.com",
            "username": "testuser",
            "password": "strongpass123",
            "display_name": "Other User",
        })
        assert resp.status_code == 400

    def test_register_duplicate_email(self, client, test_user):
        resp = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "username": "otheruser",
            "password": "strongpass123",
            "display_name": "Other User",
        })
        assert resp.status_code == 400

    def test_register_missing_fields(self, client):
        resp = client.post("/api/auth/register", json={"username": "incomplete"})
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, test_user):
        resp = client.post("/api/auth/token", data={
            "username": "testuser",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        resp = client.post("/api/auth/token", data={
            "username": "testuser",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/token", data={
            "username": "noone",
            "password": "pass",
        })
        assert resp.status_code == 401


class TestMe:
    def test_get_current_user(self, authenticated_client):
        resp = authenticated_client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_invalid_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"})
        assert resp.status_code == 401
