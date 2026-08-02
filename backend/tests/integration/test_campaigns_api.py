"""Integration tests for the campaigns API endpoints."""

import pytest


class TestListCampaigns:
    def test_list_empty(self, authenticated_client):
        resp = authenticated_client.get("/api/campaigns")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_owned_campaigns(self, authenticated_client):
        authenticated_client.post("/api/campaigns", json={
            "name": "My Campaign",
            "description": "A test",
        })
        resp = authenticated_client.get("/api/campaigns")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Campaign"

    def test_unauthenticated(self, client):
        resp = client.get("/api/campaigns")
        assert resp.status_code == 401


class TestCreateCampaign:
    def test_create_success(self, authenticated_client):
        resp = authenticated_client.post("/api/campaigns", json={
            "name": "Dragon's Lair",
            "description": "Enter the dragon's domain",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Dragon's Lair"
        assert data["is_active"] is True
        assert "id" in data
        assert "owner_id" in data

    def test_create_minimal(self, authenticated_client):
        resp = authenticated_client.post("/api/campaigns", json={"name": "Quick Game"})
        assert resp.status_code == 201

    def test_create_empty_name(self, authenticated_client):
        resp = authenticated_client.post("/api/campaigns", json={"name": ""})
        assert resp.status_code == 422


class TestGetCampaign:
    def test_get_own_campaign(self, authenticated_client):
        create_resp = authenticated_client.post("/api/campaigns", json={"name": "Test"})
        campaign_id = create_resp.json()["id"]

        resp = authenticated_client.get(f"/api/campaigns/{campaign_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"

    def test_get_nonexistent(self, authenticated_client):
        resp = authenticated_client.get("/api/campaigns/99999")
        assert resp.status_code == 404


class TestUpdateCampaign:
    def test_update_name(self, authenticated_client):
        create_resp = authenticated_client.post("/api/campaigns", json={"name": "Old Name"})
        campaign_id = create_resp.json()["id"]

        resp = authenticated_client.put(f"/api/campaigns/{campaign_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_deactivate_campaign(self, authenticated_client):
        create_resp = authenticated_client.post("/api/campaigns", json={"name": "Active"})
        campaign_id = create_resp.json()["id"]

        resp = authenticated_client.put(f"/api/campaigns/{campaign_id}", json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False


class TestDeleteCampaign:
    def test_delete_success(self, authenticated_client):
        create_resp = authenticated_client.post("/api/campaigns", json={"name": "Delete Me"})
        campaign_id = create_resp.json()["id"]

        resp = authenticated_client.delete(f"/api/campaigns/{campaign_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get(f"/api/campaigns/{campaign_id}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, authenticated_client):
        resp = authenticated_client.delete("/api/campaigns/99999")
        assert resp.status_code == 404
