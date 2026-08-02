"""Integration tests for the characters API endpoints."""

import pytest


class TestListCharacters:
    def test_list_empty(self, authenticated_client):
        resp = authenticated_client.get("/api/characters")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_owned_characters(self, authenticated_client):
        authenticated_client.post("/api/characters", json={
            "name": "Aragorn",
            "race": "Human",
            "character_class": "Ranger",
        })
        resp = authenticated_client.get("/api/characters")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["name"] == "Aragorn"

    def test_filter_by_campaign(self, authenticated_client):
        # Create a campaign and a character linked to it
        camp_resp = authenticated_client.post("/api/campaigns", json={"name": "Campaign A"})
        campaign_id = camp_resp.json()["id"]

        authenticated_client.post("/api/characters", json={
            "name": "Linked Hero",
            "campaign_id": campaign_id,
        })
        authenticated_client.post("/api/characters", json={"name": "Unlinked Hero"})

        resp = authenticated_client.get(f"/api/characters?campaign_id={campaign_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Linked Hero"


class TestCreateCharacter:
    def test_create_full(self, authenticated_client):
        resp = authenticated_client.post("/api/characters", json={
            "name": "Gandalf",
            "level": 20,
            "race": "Human",
            "character_class": "Wizard",
            "background": "Sage",
            "ability_scores": {"str": 10, "dex": 14, "con": 12, "int": 20, "wis": 18, "cha": 16},
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Gandalf"
        assert data["level"] == 20
        assert data["ability_scores"]["int"] == 20

    def test_create_minimal(self, authenticated_client):
        resp = authenticated_client.post("/api/characters", json={"name": "Nameless"})
        assert resp.status_code == 201
        assert resp.json()["level"] == 1

    def test_create_empty_name(self, authenticated_client):
        resp = authenticated_client.post("/api/characters", json={"name": ""})
        assert resp.status_code == 422


class TestGetCharacter:
    def test_get_own_character(self, authenticated_client):
        create_resp = authenticated_client.post("/api/characters", json={"name": "Hero"})
        char_id = create_resp.json()["id"]

        resp = authenticated_client.get(f"/api/characters/{char_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Hero"

    def test_get_nonexistent(self, authenticated_client):
        resp = authenticated_client.get("/api/characters/99999")
        assert resp.status_code == 404


class TestUpdateCharacter:
    def test_update_level(self, authenticated_client):
        create_resp = authenticated_client.post("/api/characters", json={"name": "Hero"})
        char_id = create_resp.json()["id"]

        resp = authenticated_client.put(f"/api/characters/{char_id}", json={"level": 5})
        assert resp.status_code == 200
        assert resp.json()["level"] == 5

    def test_update_preserves_other_fields(self, authenticated_client):
        create_resp = authenticated_client.post("/api/characters", json={
            "name": "Hero",
            "race": "Elf",
            "character_class": "Ranger",
        })
        char_id = create_resp.json()["id"]

        resp = authenticated_client.put(f"/api/characters/{char_id}", json={"level": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["level"] == 3
        assert data["race"] == "Elf"
        assert data["character_class"] == "Ranger"


class TestDeleteCharacter:
    def test_delete_success(self, authenticated_client):
        create_resp = authenticated_client.post("/api/characters", json={"name": "Doomed"})
        char_id = create_resp.json()["id"]

        resp = authenticated_client.delete(f"/api/characters/{char_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get(f"/api/characters/{char_id}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, authenticated_client):
        resp = authenticated_client.delete("/api/characters/99999")
        assert resp.status_code == 404
