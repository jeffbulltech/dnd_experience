"""Integration tests for the game-state API endpoints."""

import pytest


@pytest.fixture()
def campaign_id(authenticated_client):
    """Create a campaign and return its ID."""
    resp = authenticated_client.post("/api/campaigns", json={"name": "State Test"})
    return resp.json()["id"]


class TestGetGameState:
    def test_get_initial_state(self, authenticated_client, campaign_id):
        resp = authenticated_client.get(f"/api/game-state/{campaign_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["campaign_id"] == campaign_id

    def test_get_wrong_campaign(self, authenticated_client):
        resp = authenticated_client.get("/api/game-state/99999")
        assert resp.status_code == 404


class TestUpdateGameState:
    def test_update_location(self, authenticated_client, campaign_id):
        resp = authenticated_client.put(f"/api/game-state/{campaign_id}", json={
            "location": "The Prancing Pony",
        })
        assert resp.status_code == 200
        assert resp.json()["location"] == "The Prancing Pony"

    def test_update_quests(self, authenticated_client, campaign_id):
        resp = authenticated_client.put(f"/api/game-state/{campaign_id}", json={
            "active_quests": ["Find the ring", "Escape the Shire"],
        })
        assert resp.status_code == 200
        assert len(resp.json()["active_quests"]) == 2

    def test_update_preserves_fields(self, authenticated_client, campaign_id):
        authenticated_client.put(f"/api/game-state/{campaign_id}", json={
            "location": "Rivendell",
            "summary": "Council of Elrond",
        })
        # Update only location
        resp = authenticated_client.put(f"/api/game-state/{campaign_id}", json={
            "location": "Moria",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["location"] == "Moria"
        assert data["summary"] == "Council of Elrond"
