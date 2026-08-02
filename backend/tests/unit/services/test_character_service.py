"""Unit tests for character_service module."""

import pytest

from app.schemas.characters import CharacterCreate, CharacterUpdate
from app.services import character_service
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.characters import create_test_character
from tests.fixtures.users import create_test_user


class TestCharacterService:
    """Unit tests for character_service functions."""

    def test_create_character_success(self, db_session):
        """Test successful character creation."""
        user = create_test_user(db_session)
        payload = CharacterCreate(
            name="Test Hero",
            level=1,
            race="Elf",
            character_class="Wizard",
            background="Sage"
        )
        
        result = character_service.create_character(db_session, payload, user_id=user.id)
        
        assert result.id > 0
        assert result.name == "Test Hero"
        assert result.level == 1
        assert result.race == "Elf"
        assert result.character_class == "Wizard"
        assert result.background == "Sage"
        assert result.user_id == user.id

    def test_create_character_with_campaign(self, db_session):
        """Test character creation linked to a campaign."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        payload = CharacterCreate(
            name="Campaign Hero",
            level=3,
            campaign_id=campaign.id
        )
        
        result = character_service.create_character(db_session, payload, user_id=user.id)
        
        assert result.campaign_id == campaign.id

    def test_create_character_with_ability_scores(self, db_session):
        """Test character creation with ability scores."""
        user = create_test_user(db_session)
        payload = CharacterCreate(
            name="Stats Hero",
            level=1,
            ability_scores={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        )
        
        result = character_service.create_character(db_session, payload, user_id=user.id)
        
        assert result.ability_scores is not None
        assert result.ability_scores["strength"] == 15
        assert result.ability_scores["dexterity"] == 14

    def test_list_characters_by_user(self, db_session):
        """Test listing characters filtered by user."""
        user1 = create_test_user(db_session, username="user1")
        user2 = create_test_user(db_session, username="user2")
        
        char1 = create_test_character(db_session, user1.id, name="User1 Char")
        char2 = create_test_character(db_session, user2.id, name="User2 Char")
        
        user1_chars = character_service.list_characters(
            db_session, user_id=user1.id
        )
        
        assert len(user1_chars) == 1
        assert user1_chars[0].id == char1.id
        assert user1_chars[0].id != char2.id

    def test_list_characters_by_campaign(self, db_session):
        """Test listing characters filtered by campaign."""
        user = create_test_user(db_session)
        campaign1 = create_test_campaign(db_session, user.id, name="Campaign 1")
        campaign2 = create_test_campaign(db_session, user.id, name="Campaign 2")
        
        char1 = create_test_character(db_session, user.id, campaign1.id, name="Camp1 Char")
        char2 = create_test_character(db_session, user.id, campaign2.id, name="Camp2 Char")
        char3 = create_test_character(db_session, user.id, None, name="No Campaign")
        
        campaign1_chars = character_service.list_characters(
            db_session, user_id=user.id, campaign_id=campaign1.id
        )
        
        assert len(campaign1_chars) == 1
        assert campaign1_chars[0].id == char1.id

    def test_list_characters_empty(self, db_session):
        """Test listing characters for user with no characters."""
        user = create_test_user(db_session)
        
        chars = character_service.list_characters(db_session, user_id=user.id)
        
        assert len(chars) == 0

    def test_get_character_success(self, db_session):
        """Test successful character retrieval."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id, name="Get Test")
        
        result = character_service.get_character(db_session, character.id)
        
        assert result is not None
        assert result.id == character.id
        assert result.name == "Get Test"

    def test_get_character_not_found(self, db_session):
        """Test retrieval of non-existent character."""
        result = character_service.get_character(db_session, 99999)
        assert result is None

    def test_update_character_success(self, db_session):
        """Test successful character update."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id, level=1)
        
        update = CharacterUpdate(level=5, background="Archmage")
        
        result = character_service.update_character(
            db_session, character.id, update
        )
        
        assert result.level == 5
        assert result.background == "Archmage"

    def test_update_character_partial(self, db_session):
        """Test that partial updates only change specified fields."""
        user = create_test_user(db_session)
        character = create_test_character(
            db_session, user.id, name="Original", level=1, race="Human"
        )
        
        # Only update level
        update = CharacterUpdate(level=10)
        result = character_service.update_character(
            db_session, character.id, update
        )
        
        assert result.level == 10
        assert result.name == "Original"  # Unchanged
        assert result.race == "Human"  # Unchanged

    def test_update_character_campaign_id(self, db_session):
        """Test updating character's campaign assignment."""
        user = create_test_user(db_session)
        campaign1 = create_test_campaign(db_session, user.id, name="Camp 1")
        campaign2 = create_test_campaign(db_session, user.id, name="Camp 2")
        character = create_test_character(db_session, user.id, campaign1.id)
        
        update = CharacterUpdate(campaign_id=campaign2.id)
        result = character_service.update_character(
            db_session, character.id, update
        )
        
        assert result.campaign_id == campaign2.id

    def test_update_character_not_found(self, db_session):
        """Test updating non-existent character."""
        update = CharacterUpdate(level=5)
        
        with pytest.raises(ValueError, match="Character not found"):
            character_service.update_character(db_session, 99999, update)

    def test_delete_character_success(self, db_session):
        """Test successful character deletion."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        character_id = character.id
        
        character_service.delete_character(db_session, character_id)
        
        # Verify character is deleted
        from app.models import Character
        assert db_session.get(Character, character_id) is None

    def test_delete_character_not_found(self, db_session):
        """Test deleting non-existent character."""
        with pytest.raises(ValueError, match="Character not found"):
            character_service.delete_character(db_session, 99999)
