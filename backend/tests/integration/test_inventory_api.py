"""Integration tests for the inventory API endpoints."""

import pytest


@pytest.fixture()
def character_id(authenticated_client):
    """Create a character and return its ID."""
    resp = authenticated_client.post("/api/characters", json={"name": "Inventory Hero"})
    return resp.json()["id"]


class TestListInventory:
    def test_list_empty(self, authenticated_client, character_id):
        resp = authenticated_client.get(f"/api/inventory?character_id={character_id}")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_items(self, authenticated_client, character_id):
        authenticated_client.post("/api/inventory", json={
            "character_id": character_id,
            "name": "Longsword",
            "quantity": 1,
            "weight": 3.0,
        })
        resp = authenticated_client.get(f"/api/inventory?character_id={character_id}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["name"] == "Longsword"


class TestCreateInventoryItem:
    def test_create_full(self, authenticated_client, character_id):
        resp = authenticated_client.post("/api/inventory", json={
            "character_id": character_id,
            "name": "Healing Potion",
            "quantity": 3,
            "weight": 0.5,
            "description": "Restores 2d4+2 HP",
            "properties": {"rarity": "common"},
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Healing Potion"
        assert data["quantity"] == 3
        assert data["properties"]["rarity"] == "common"

    def test_create_minimal(self, authenticated_client, character_id):
        resp = authenticated_client.post("/api/inventory", json={
            "character_id": character_id,
            "name": "Gold Coin",
        })
        assert resp.status_code == 201
        assert resp.json()["quantity"] == 1

    def test_create_wrong_character(self, authenticated_client):
        resp = authenticated_client.post("/api/inventory", json={
            "character_id": 99999,
            "name": "Stolen Goods",
        })
        assert resp.status_code == 403


class TestUpdateInventoryItem:
    def test_update_quantity(self, authenticated_client, character_id):
        create_resp = authenticated_client.post("/api/inventory", json={
            "character_id": character_id,
            "name": "Arrows",
            "quantity": 20,
        })
        item_id = create_resp.json()["id"]

        resp = authenticated_client.put(f"/api/inventory/{item_id}", json={"quantity": 15})
        assert resp.status_code == 200
        assert resp.json()["quantity"] == 15

    def test_update_nonexistent(self, authenticated_client):
        resp = authenticated_client.put("/api/inventory/99999", json={"quantity": 1})
        assert resp.status_code == 404


class TestDeleteInventoryItem:
    def test_delete_success(self, authenticated_client, character_id):
        create_resp = authenticated_client.post("/api/inventory", json={
            "character_id": character_id,
            "name": "Trash",
        })
        item_id = create_resp.json()["id"]

        resp = authenticated_client.delete(f"/api/inventory/{item_id}")
        assert resp.status_code == 204

    def test_delete_nonexistent(self, authenticated_client):
        resp = authenticated_client.delete("/api/inventory/99999")
        assert resp.status_code == 404
