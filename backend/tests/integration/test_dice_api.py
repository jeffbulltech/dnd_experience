"""Integration tests for the dice API endpoints."""

import pytest


@pytest.fixture()
def campaign_id(authenticated_client):
    """Create a campaign for dice rolling."""
    resp = authenticated_client.post("/api/campaigns", json={"name": "Dice Game"})
    return resp.json()["id"]


class TestRollDice:
    def test_simple_roll(self, authenticated_client, campaign_id):
        resp = authenticated_client.post("/api/dice/roll", json={
            "expression": "1d20",
            "campaign_id": campaign_id,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert 1 <= data["total"] <= 20
        assert data["expression"] == "1d20"

    def test_roll_with_modifier(self, authenticated_client, campaign_id):
        resp = authenticated_client.post("/api/dice/roll", json={
            "expression": "1d20+5",
            "campaign_id": campaign_id,
        })
        assert resp.status_code == 200
        assert resp.json()["total"] >= 6  # min 1+5

    def test_roll_wrong_campaign(self, authenticated_client):
        resp = authenticated_client.post("/api/dice/roll", json={
            "expression": "1d20",
            "campaign_id": 99999,
        })
        assert resp.status_code == 403

    def test_roll_advantage(self, authenticated_client, campaign_id):
        resp = authenticated_client.post("/api/dice/roll", json={
            "expression": "2d20kh1",
            "campaign_id": campaign_id,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert 1 <= data["total"] <= 20


class TestDiceHistory:
    def test_empty_history(self, authenticated_client, campaign_id):
        resp = authenticated_client.get(f"/api/dice/history?campaign_id={campaign_id}")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_after_rolls(self, authenticated_client, campaign_id):
        for _ in range(3):
            authenticated_client.post("/api/dice/roll", json={
                "expression": "1d6",
                "campaign_id": campaign_id,
            })

        resp = authenticated_client.get(f"/api/dice/history?campaign_id={campaign_id}")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_history_limit(self, authenticated_client, campaign_id):
        for _ in range(5):
            authenticated_client.post("/api/dice/roll", json={
                "expression": "1d6",
                "campaign_id": campaign_id,
            })

        resp = authenticated_client.get(f"/api/dice/history?campaign_id={campaign_id}&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2
