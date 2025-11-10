from __future__ import annotations

import io
import itertools
from datetime import datetime

import pytest

from app.config import get_settings
from app.models import ChatMessage, Character, Encounter, EncounterParticipant, User
from app.schemas.campaigns import CampaignCreate
from app.schemas.characters import CharacterCreate, CharacterUpdate
from app.schemas.character_builder import CharacterDraftCreate, CharacterDraftStepUpdate
from app.schemas.chat import ChatHistoryEntry
from app.schemas.combat import CombatActionRequest, ParticipantCreate, ParticipantUpdate
from app.schemas.dice import DiceRollRequest
from app.schemas.game_state import GameStateUpdate
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from app.services import (
    attachment_service,
    campaign_service,
    character_builder_service,
    character_service,
    combat_engine,
    chat_service,
    dice_service,
    game_state_service,
    inventory_service,
    rag_service,
)
from app.utils.dice_roller import roll_dice


USER_SEQ = itertools.count()


def _create_user(session) -> User:
    suffix = next(USER_SEQ)
    user = User(
        email=f"player{suffix}@example.com",
        username=f"player{suffix}",
        hashed_password="hashed",
        display_name="Player One",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_create_and_get_character(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Shardfall", description="Epic quest"),
        owner_id=user.id,
    )
    payload = CharacterCreate(
        name="Elaria",
        level=1,
        race="Elf",
        character_class="Wizard",
        background="Sage",
        campaign_id=campaign.id,
    )
    created = character_service.create_character(db_session, payload, user_id=user.id)

    assert created.id > 0
    assert created.name == "Elaria"
    assert created.user_id == user.id
    assert created.campaign_id == campaign.id

    retrieved = character_service.get_character(db_session, created.id)
    assert retrieved is not None
    assert retrieved.id == created.id

    updated = character_service.update_character(
        db_session, created.id, CharacterUpdate(level=2, background="Archmage Adept")
    )
    assert updated.level == 2
    assert updated.background == "Archmage Adept"

    all_characters = character_service.list_characters(db_session, user_id=user.id, campaign_id=campaign.id)
    assert len(all_characters) == 1
    assert all_characters[0].id == created.id


def test_create_campaign_and_game_state(db_session):
    user = _create_user(db_session)
    payload = CampaignCreate(name="Lost Mine", description="Starter quest")

    campaign = campaign_service.create_campaign(db_session, payload, owner_id=user.id)
    assert campaign.id > 0
    assert campaign.owner_id == user.id

    campaigns = campaign_service.list_campaigns(db_session, owner_id=user.id)
    assert len(campaigns) == 1
    assert campaigns[0].id == campaign.id

    state = game_state_service.get_game_state(db_session, campaign.id)
    assert state.campaign_id == campaign.id
    assert state.active_quests == []

    updated_state = game_state_service.update_game_state(
        db_session,
        campaign.id,
        GameStateUpdate(location="Phandalin", summary="Heroes defend the town", active_quests=["Secure the mine"]),
        owner_id=user.id,
    )
    assert updated_state.location == "Phandalin"
    assert updated_state.active_quests == ["Secure the mine"]


def test_combat_action_creates_encounter(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Battlefield", description=None),
        owner_id=user.id,
    )

    combat_state = combat_engine.process_action(
        db_session,
        CombatActionRequest(
            campaign_id=campaign.id,
            actor_id=1,
            target_id=None,
            action_type="attack",
            description="Swings a sword at the nearest goblin.",
        ),
    )

    assert combat_state.campaign_id == campaign.id
    assert combat_state.round_number >= 1
    assert isinstance(combat_state.turn_order, list)
    latest_state = combat_engine.get_combat_state(db_session, campaign.id)
    assert latest_state.turn_order == combat_state.turn_order
    # add participant
    combat_engine.add_participant(
        db_session,
        campaign.id,
        ParticipantCreate(
            name="Bandit",
            initiative=12,
            hit_points=11,
            max_hit_points=11,
            armor_class=12,
        ),
    )
    state_with_participant = combat_engine.get_combat_state(db_session, campaign.id)
    bandit = next(
        (combatant for combatant in state_with_participant.combatants.values() if combatant.name == "Bandit"),
        None,
    )
    assert bandit is not None
    assert bandit.initiative == 12

    updated_state = combat_engine.update_participant(
        db_session,
        campaign.id,
        bandit.id,
        ParticipantUpdate(hit_points=5),
    )
    assert updated_state.combatants[bandit.id].hit_points == 5

    final_state = combat_engine.remove_participant(db_session, campaign.id, bandit.id)
    assert bandit.id not in final_state.combatants


def test_inventory_crud(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Arcane Vault", description=None),
        owner_id=user.id,
    )
    character = character_service.create_character(
        db_session,
        CharacterCreate(
            name="Sariel",
            level=3,
            race="Elf",
            character_class="Ranger",
            background="Outlander",
            campaign_id=campaign.id,
        ),
        user_id=user.id,
    )

    created = inventory_service.create_inventory_item(
        db_session,
        InventoryItemCreate(
            character_id=character.id,
            name="Longbow",
            quantity=1,
            weight=2.0,
            description="Well-crafted yew bow",
            properties={"range": "150/600"},
        ),
    )

    assert created.id > 0
    assert created.character_id == character.id

    updated = inventory_service.update_inventory_item(
        db_session,
        created.id,
        InventoryItemUpdate(quantity=2),
    )
    assert updated.quantity == 2

    items = inventory_service.list_inventory_items(db_session, character_id=character.id)
    assert len(items) == 1

    inventory_service.delete_inventory_item(db_session, created.id)
    remaining = inventory_service.list_inventory_items(db_session, character_id=character.id)
    assert remaining == []


def test_dice_roll_history(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Skyspire", description=None),
        owner_id=user.id,
    )
    character = character_service.create_character(
        db_session,
        CharacterCreate(
            name="Liora",
            level=4,
            race="Human",
            character_class="Cleric",
            background="Acolyte",
            campaign_id=campaign.id,
        ),
        user_id=user.id,
    )

    request = DiceRollRequest(
        expression="2d6+3", campaign_id=campaign.id, character_id=character.id, roller_type="player"
    )
    result = roll_dice(request)
    dice_service.record_roll(
        db_session,
        campaign_id=request.campaign_id,
        character_id=request.character_id,
        roller_type=request.roller_type or "player",
        expression=result.expression,
        total=result.total,
        detail=result.detail,
    )

    history = dice_service.list_rolls(
        db_session,
        campaign_id=campaign.id,
        character_id=character.id,
    )
    assert len(history) == 1
    assert history[0].expression == "2d6+3"


def test_campaign_attachment_lifecycle(db_session, tmp_path):
    settings = get_settings()
    original_dir = settings.attachments_dir
    settings.attachments_dir = tmp_path / "attachments"
    settings.attachments_dir.mkdir(parents=True, exist_ok=True)

    try:
        owner = _create_user(db_session)
        campaign = campaign_service.create_campaign(
            db_session,
            CampaignCreate(name="Relic Hunt", description="Recover the ancient relic"),
            owner_id=owner.id,
        )

        upload = attachment_service.AttachmentUpload(
            filename="battlemap.jpg",
            content_type="image/jpeg",
            file=io.BytesIO(b"fake image bytes"),
        )

        created = attachment_service.create_attachment(
            db_session,
            campaign_id=campaign.id,
            uploader_id=owner.id,
            upload=upload,
            description="Session 1 battlemap",
        )

        assert created.original_filename == "battlemap.jpg"
        assert created.file_size == len(b"fake image bytes")

        attachments = attachment_service.list_attachments(
            db_session,
            campaign_id=campaign.id,
            requester_id=owner.id,
        )
        assert len(attachments) == 1
        assert attachments[0].id == created.id

        attachment_record = attachment_service.get_attachment(
            db_session,
            campaign_id=campaign.id,
            attachment_id=created.id,
            requester_id=owner.id,
        )
        file_path = attachment_service.resolve_file_path(attachment_record)
        assert file_path.exists()

        attachment_service.delete_attachment(
            db_session,
            campaign_id=campaign.id,
            attachment_id=created.id,
            requester_id=owner.id,
        )

        assert not file_path.exists()
        remaining = attachment_service.list_attachments(
            db_session,
            campaign_id=campaign.id,
            requester_id=owner.id,
        )
        assert remaining == []
    finally:
        settings.attachments_dir = original_dir


def test_get_combat_state_returns_participants(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Citadel Siege", description=None),
        owner_id=user.id,
    )

    encounter = Encounter(
        campaign_id=campaign.id,
        name="Citadel Siege - Round 1",
        status="active",
        round_number=2,
        metadata={},
    )
    db_session.add(encounter)
    db_session.commit()
    db_session.refresh(encounter)

    participant = EncounterParticipant(
        encounter_id=encounter.id,
        name="Elite Guard",
        initiative=18,
        hit_points=22,
        max_hit_points=22,
        armor_class=17,
        conditions=[],
        attributes={},
    )
    db_session.add(participant)
    db_session.commit()

    state = combat_engine.get_combat_state(db_session, campaign.id)
    assert state.round_number == 2
    assert state.turn_order == [participant.id]
    assert state.combatants[participant.id].name == "Elite Guard"


def test_chat_history(db_session):
    user = _create_user(db_session)
    campaign = campaign_service.create_campaign(
        db_session,
        CampaignCreate(name="Whispering Vault", description=None),
        owner_id=user.id,
    )

    message_player = ChatMessage(
        campaign_id=campaign.id,
        character_id=None,
        role="player",
        content="I open the ancient door.",
        rag_context=[],
        extra={},
    )
    message_gm = ChatMessage(
        campaign_id=campaign.id,
        character_id=None,
        role="gm",
        content="The hinges groan as the chamber is revealed.",
        rag_context=["Door opening rules"],
        extra={"mood": "ominous"},
    )
    db_session.add_all([message_player, message_gm])
    db_session.commit()

    history = chat_service.fetch_chat_history(db_session, campaign_id=campaign.id, limit=10)
    assert len(history) == 2
    assert history[0].role in {"player", "gm"}


def test_chat_summary_generation():
    now = datetime.utcnow()
    entries = [
        ChatHistoryEntry(
            id=idx,
            campaign_id=1,
            character_id=None,
            role="player" if idx % 2 == 0 else "gm",
            content=f"Message {idx}",
            rag_context=[],
            metadata={},
            created_at=now,
        )
        for idx in range(10)
    ]
    summary = rag_service.summarize_chat_history(entries, tail=2, max_points=4)
    assert summary
    assert "Message" in summary


def test_character_draft_flow(db_session):
    user = _create_user(db_session)

    draft = character_builder_service.create_draft(
        db_session,
        user_id=user.id,
        payload=CharacterDraftCreate(name="New Hero", starting_level=1),
    )
    assert draft.id > 0
    assert draft.current_step == "intro"

    drafts = character_builder_service.list_drafts(db_session, user_id=user.id)
    assert len(drafts) == 1

    updated = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="ability_scores",
        update=CharacterDraftStepUpdate(
            payload={
                "method": "standard_array",
                "scores": {
                    "strength": 15,
                    "dexterity": 14,
                    "constitution": 13,
                    "intelligence": 12,
                    "wisdom": 10,
                    "charisma": 8,
                },
            }
        ),
    )
    assert updated.step_data["ability_scores"]["method"] == "standard_array"
    assert updated.step_data["ability_scores"]["modifiers"]["strength"] == 2

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="ability_scores",
            update=CharacterDraftStepUpdate(
                payload={
                    "method": "point_buy",
                    "scores": {
                        "strength": 18,
                        "dexterity": 12,
                        "constitution": 12,
                        "intelligence": 10,
                        "wisdom": 10,
                        "charisma": 10,
                    },
                }
            ),
        )

    origin_update = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="origin",
        update=CharacterDraftStepUpdate(
            payload={
                "species": "elf",
                "background": "acolyte",
                "languages": ["Common", "Elvish"],
            }
        ),
    )
    assert origin_update.step_data["origin"]["species"] == "elf"
    assert origin_update.step_data["origin"]["background"] == "acolyte"

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="origin",
            update=CharacterDraftStepUpdate(
                payload={
                    "species": "invalid",
                    "background": "acolyte",
                }
            ),
        )

    class_update = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="class",
        update=CharacterDraftStepUpdate(
            payload={
                "class": "wizard",
            }
        ),
    )
    assert class_update.step_data["class"]["class"] == "wizard"

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="class",
            update=CharacterDraftStepUpdate(
                payload={
                    "class": "invalid",
                }
            ),
        )

    prof_update = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="proficiencies",
        update=CharacterDraftStepUpdate(
            payload={
                "skills": ["arcana", "investigation"],
                "tools": ["gaming_set"],
                "expertise": ["arcana"],
            }
        ),
    )
    assert "proficiencies" in prof_update.step_data
    assert prof_update.step_data["proficiencies"]["skills"] == ["arcana", "investigation"]

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="proficiencies",
            update=CharacterDraftStepUpdate(
                payload={
                    "skills": ["invalid"],
                }
            ),
        )

    equipment_update = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="equipment",
        update=CharacterDraftStepUpdate(
            payload={
                "weapons": ["longsword"],
                "armor": ["leather_armor"],
                "packs": ["explorer_pack"],
                "currency": {"gp": 10, "sp": 5},
                "custom_items": [
                    {"name": "Lucky Charm", "description": "A token of good fortune."}
                ],
            }
        ),
    )
    assert equipment_update.step_data["equipment"]["weapons"] == ["longsword"]
    assert equipment_update.step_data["equipment"]["currency"]["gp"] == 10

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="equipment",
            update=CharacterDraftStepUpdate(
                payload={
                    "weapons": ["unknown"],
                }
            ),
        )

    spell_update = character_builder_service.update_step(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
        step="spells",
        update=CharacterDraftStepUpdate(
            payload={
                "known": ["fire_bolt"],
                "prepared": [],
                "cantrips": ["fire_bolt"],
            }
        ),
    )
    assert spell_update.step_data["spells"]["known"] == ["fire_bolt"]

    with pytest.raises(ValueError):
        character_builder_service.update_step(
            db_session,
            user_id=user.id,
            draft_id=draft.id,
            step="spells",
            update=CharacterDraftStepUpdate(
                payload={
                    "known": ["unknown_spell"],
                }
            ),
        )

    finalized = character_builder_service.finalize_draft(
        db_session,
        user_id=user.id,
        draft_id=draft.id,
    )
    assert finalized.status == "completed"
    assert finalized.character_id is not None

    character = db_session.get(Character, finalized.character_id)
    assert character is not None
    assert character.character_class == "Wizard"
    assert character.ability_scores["dexterity"]["score"] == 16  # elf bonus applied
    assert character.attributes["proficiency_bonus"] == 2

    fetched = character_builder_service.fetch_draft(db_session, user_id=user.id, draft_id=draft.id)
    assert fetched.id == draft.id

    character_builder_service.delete_draft(db_session, user_id=user.id, draft_id=draft.id)
    drafts_after_delete = character_builder_service.list_drafts(db_session, user_id=user.id)
    assert drafts_after_delete == []

