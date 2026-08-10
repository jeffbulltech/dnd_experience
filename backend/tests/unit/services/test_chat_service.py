"""Unit tests for chat_service module."""

import pytest

from app.models import Campaign, ChatMessage
from app.services import chat_service
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.characters import create_test_character
from tests.fixtures.users import create_test_user


class TestChatService:
    """Unit tests for chat_service functions."""

    def test_fetch_chat_history_success(self, db_session):
        """Test successful chat history retrieval."""
        user = create_test_user(db_session)
        # Campaign creation seeds a welcome message from the GM.
        campaign = create_test_campaign(db_session, user.id)

        # Create some chat messages
        msg1 = ChatMessage(
            campaign_id=campaign.id,
            character_id=None,
            role="player",
            content="First message",
            rag_context=[],
            extra={}
        )
        msg2 = ChatMessage(
            campaign_id=campaign.id,
            character_id=None,
            role="gm",
            content="GM response",
            rag_context=[],
            extra={}
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()

        history = chat_service.fetch_chat_history(
            db_session, campaign_id=campaign.id, limit=10
        )

        # Welcome message + the 2 messages created above.
        assert len(history) == 3
        assert history[0].role in ["player", "gm"]
        assert history[1].role in ["player", "gm"]

    def test_fetch_chat_history_with_limit(self, db_session):
        """Test that limit parameter works correctly."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Create 10 messages
        messages = []
        for i in range(10):
            msg = ChatMessage(
                campaign_id=campaign.id,
                character_id=None,
                role="player" if i % 2 == 0 else "gm",
                content=f"Message {i}",
                rag_context=[],
                extra={}
            )
            messages.append(msg)
        db_session.add_all(messages)
        db_session.commit()
        
        # Request only 5
        history = chat_service.fetch_chat_history(
            db_session, campaign_id=campaign.id, limit=5
        )
        
        assert len(history) == 5

    def test_fetch_chat_history_empty(self, db_session):
        """Test fetching history when no messages exist."""
        user = create_test_user(db_session)
        # Build the campaign directly (bypassing campaign_service.create_campaign)
        # so no welcome message is seeded, leaving chat history genuinely empty.
        campaign = Campaign(name="Empty Campaign", owner_id=user.id)
        db_session.add(campaign)
        db_session.commit()

        history = chat_service.fetch_chat_history(
            db_session, campaign_id=campaign.id, limit=10
        )

        assert len(history) == 0

    def test_fetch_chat_history_filters_by_campaign(self, db_session):
        """Test that history is filtered by campaign."""
        user = create_test_user(db_session)
        campaign1 = create_test_campaign(db_session, user.id, name="Camp 1")
        campaign2 = create_test_campaign(db_session, user.id, name="Camp 2")
        
        msg1 = ChatMessage(
            campaign_id=campaign1.id,
            character_id=None,
            role="player",
            content="Camp 1 message",
            rag_context=[],
            extra={}
        )
        msg2 = ChatMessage(
            campaign_id=campaign2.id,
            character_id=None,
            role="player",
            content="Camp 2 message",
            rag_context=[],
            extra={}
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()
        
        camp1_history = chat_service.fetch_chat_history(
            db_session, campaign_id=campaign1.id, limit=10
        )

        # Welcome message + the explicit message created above, both scoped
        # to campaign1 only.
        assert len(camp1_history) == 2
        assert "Camp 1 message" in [msg.content for msg in camp1_history]
        assert "Camp 2 message" not in [msg.content for msg in camp1_history]

    def test_fetch_chat_history_includes_character_id(self, db_session):
        """Test that history includes messages with character_id."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        character = create_test_character(db_session, user.id, campaign.id)
        
        msg1 = ChatMessage(
            campaign_id=campaign.id,
            character_id=None,
            role="player",
            content="No character",
            rag_context=[],
            extra={}
        )
        msg2 = ChatMessage(
            campaign_id=campaign.id,
            character_id=character.id,
            role="player",
            content="With character",
            rag_context=[],
            extra={}
        )
        db_session.add_all([msg1, msg2])
        db_session.commit()
        
        history = chat_service.fetch_chat_history(
            db_session, campaign_id=campaign.id, limit=10
        )

        # Welcome message + the 2 messages created above.
        assert len(history) == 3
        # Both should be included regardless of character_id
        contents = [msg.content for msg in history]
        assert "No character" in contents
        assert "With character" in contents
