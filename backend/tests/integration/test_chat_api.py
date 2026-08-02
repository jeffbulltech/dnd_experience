"""Integration tests for the chat API endpoints."""

import json

import pytest


@pytest.fixture()
def campaign_with_character(authenticated_client):
    """Create a campaign and character for chat testing."""
    camp = authenticated_client.post("/api/campaigns", json={"name": "Chat Test"}).json()
    char = authenticated_client.post("/api/characters", json={
        "name": "Chatty Hero",
        "campaign_id": camp["id"],
    }).json()
    return camp, char


class TestSendMessage:
    def test_send_message(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        camp, char = campaign_with_character
        resp = authenticated_client.post("/api/chat", json={
            "campaign_id": camp["id"],
            "character_id": char["id"],
            "content": "I open the door.",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert data["response"] == "Test GM response"
        assert "metadata" in data
        assert "timestamp" in data

    def test_send_message_wrong_campaign(self, authenticated_client, mock_ollama_client, mock_chroma_db):
        resp = authenticated_client.post("/api/chat", json={
            "campaign_id": 99999,
            "content": "Hello",
        })
        assert resp.status_code == 403

    def test_send_empty_message(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        camp, _ = campaign_with_character
        resp = authenticated_client.post("/api/chat", json={
            "campaign_id": camp["id"],
            "content": "",
        })
        assert resp.status_code == 422


class TestStreamMessage:
    def test_stream_returns_sse(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        """Test that the streaming endpoint returns SSE events."""
        camp, char = campaign_with_character

        # Configure mock to behave like streaming (stream=True returns iterator)
        mock_ollama_client.chat.return_value = iter([
            {"message": {"content": "The door "}, "done": False},
            {"message": {"content": "creaks open."}, "done": False},
            {
                "message": {"content": ""},
                "done": True,
                "model": "mistral",
                "prompt_eval_count": 100,
                "eval_count": 20,
            },
        ])

        resp = authenticated_client.post("/api/chat/stream", json={
            "campaign_id": camp["id"],
            "character_id": char["id"],
            "content": "I open the door.",
        })
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        # Parse SSE events from body
        body = resp.text
        events = [block for block in body.split("\n\n") if block.strip()]
        token_events = [e for e in events if e.startswith("event: token")]
        done_events = [e for e in events if e.startswith("event: done")]

        assert len(token_events) >= 1
        assert len(done_events) == 1

        # Parse the done payload
        done_data_line = done_events[0].split("\n")[1]
        done_payload = json.loads(done_data_line.removeprefix("data: "))
        assert "response" in done_payload
        assert "metadata" in done_payload
        assert "timestamp" in done_payload

    def test_stream_wrong_campaign(self, authenticated_client, mock_ollama_client, mock_chroma_db):
        resp = authenticated_client.post("/api/chat/stream", json={
            "campaign_id": 99999,
            "content": "Hello",
        })
        assert resp.status_code == 403


class TestChatHistory:
    def test_history_initially_empty_or_welcome(self, authenticated_client, campaign_with_character):
        """Campaign creation may produce a welcome message, so history may not be empty."""
        camp, _ = campaign_with_character
        resp = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "has_more" in data
        assert isinstance(data["items"], list)

    def test_history_after_message(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        camp, char = campaign_with_character
        # Count existing history (may include welcome message)
        before_resp = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}&limit=200").json()
        before_count = len(before_resp["items"])

        authenticated_client.post("/api/chat", json={
            "campaign_id": camp["id"],
            "character_id": char["id"],
            "content": "I look around.",
        })

        resp = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}&limit=200")
        assert resp.status_code == 200
        data = resp.json()
        # Should have 2 more entries (player + GM)
        assert len(data["items"]) == before_count + 2
        roles = {entry["role"] for entry in data["items"]}
        assert "player" in roles
        assert "gm" in roles

    def test_history_wrong_campaign(self, authenticated_client):
        resp = authenticated_client.get("/api/chat/history?campaign_id=99999")
        assert resp.status_code == 403

    def test_history_limit(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        camp, char = campaign_with_character
        # Send several messages
        for i in range(3):
            authenticated_client.post("/api/chat", json={
                "campaign_id": camp["id"],
                "character_id": char["id"],
                "content": f"Action {i}",
            })

        resp = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["has_more"] is True
        assert data["next_cursor"] is not None

    def test_cursor_pagination(self, authenticated_client, campaign_with_character, mock_ollama_client, mock_chroma_db):
        camp, char = campaign_with_character
        for i in range(3):
            authenticated_client.post("/api/chat", json={
                "campaign_id": camp["id"],
                "character_id": char["id"],
                "content": f"Action {i}",
            })

        # Get first page
        resp1 = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}&limit=2")
        page1 = resp1.json()
        assert len(page1["items"]) == 2
        cursor = page1["next_cursor"]
        assert cursor is not None

        # Get second page using cursor
        resp2 = authenticated_client.get(f"/api/chat/history?campaign_id={camp['id']}&limit=2&before={cursor}")
        page2 = resp2.json()
        assert len(page2["items"]) >= 1

        # Ensure no overlap between pages
        page1_ids = {item["id"] for item in page1["items"]}
        page2_ids = {item["id"] for item in page2["items"]}
        assert page1_ids.isdisjoint(page2_ids)
