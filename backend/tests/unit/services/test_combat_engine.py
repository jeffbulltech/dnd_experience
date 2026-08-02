"""Unit tests for combat_engine module."""

import pytest

from app.models import Encounter, EncounterParticipant
from app.schemas.combat import CombatActionRequest, ParticipantCreate, ParticipantUpdate
from app.services import combat_engine
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.users import create_test_user


class TestCombatEngine:
    """Unit tests for combat_engine functions."""

    def test_process_action_creates_encounter(self, db_session):
        """Test that processing an action creates an encounter if none exists."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        action = CombatActionRequest(
            campaign_id=campaign.id,
            actor_id=1,
            target_id=None,
            action_type="attack",
            description="Swing sword"
        )
        
        result = combat_engine.process_action(db_session, action)
        
        assert result.campaign_id == campaign.id
        assert result.round_number == 1
        assert isinstance(result.turn_order, list)
        
        # Verify encounter was created
        encounter = db_session.query(Encounter).filter(
            Encounter.campaign_id == campaign.id,
            Encounter.status.in_(("active", "pending"))
        ).first()
        
        assert encounter is not None
        assert encounter.status == "active"

    def test_process_action_logs_action(self, db_session):
        """Test that actions are logged in encounter metadata."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        action = CombatActionRequest(
            campaign_id=campaign.id,
            actor_id=1,
            target_id=2,
            action_type="attack",
            description="Attack goblin"
        )
        
        combat_engine.process_action(db_session, action)
        
        encounter = db_session.query(Encounter).filter(
            Encounter.campaign_id == campaign.id
        ).first()
        
        assert encounter.extra is not None
        assert "actions" in encounter.extra
        assert len(encounter.extra["actions"]) == 1
        assert encounter.extra["actions"][0]["action_type"] == "attack"
        assert encounter.extra["actions"][0]["description"] == "Attack goblin"

    def test_process_action_campaign_not_found(self, db_session):
        """Test that processing action for non-existent campaign raises error."""
        action = CombatActionRequest(
            campaign_id=99999,
            actor_id=1,
            action_type="attack",
            description="Test"
        )
        
        with pytest.raises(ValueError, match="Campaign not found"):
            combat_engine.process_action(db_session, action)

    def test_get_combat_state_no_encounter(self, db_session):
        """Test getting combat state when no encounter exists."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        state = combat_engine.get_combat_state(db_session, campaign.id)
        
        assert state.campaign_id == campaign.id
        assert state.round_number == 0
        assert state.turn_order == []
        assert state.active_combatant_id is None
        assert state.combatants == {}

    def test_get_combat_state_with_participants(self, db_session):
        """Test getting combat state with participants."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Create encounter and participants
        encounter = Encounter(
            campaign_id=campaign.id,
            name="Test Encounter",
            status="active",
            round_number=1,
            metadata={}
        )
        db_session.add(encounter)
        db_session.flush()
        
        participant1 = EncounterParticipant(
            encounter_id=encounter.id,
            name="Hero",
            initiative=15,
            hit_points=20,
            max_hit_points=20,
            armor_class=16,
            conditions=[],
            attributes={}
        )
        participant2 = EncounterParticipant(
            encounter_id=encounter.id,
            name="Goblin",
            initiative=12,
            hit_points=7,
            max_hit_points=7,
            armor_class=15,
            conditions=[],
            attributes={}
        )
        db_session.add_all([participant1, participant2])
        db_session.commit()
        
        state = combat_engine.get_combat_state(db_session, campaign.id)
        
        assert state.round_number == 1
        assert len(state.combatants) == 2
        assert participant1.id in state.combatants
        assert participant2.id in state.combatants
        # Turn order should be sorted by initiative (descending)
        assert state.turn_order[0] == participant1.id  # Higher initiative first

    def test_add_participant_creates_encounter(self, db_session):
        """Test that adding participant creates encounter if none exists."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        participant = ParticipantCreate(
            name="New Combatant",
            initiative=10,
            hit_points=15,
            max_hit_points=15,
            armor_class=14
        )
        
        result = combat_engine.add_participant(db_session, campaign.id, participant)
        
        assert len(result.combatants) == 1
        combatant = list(result.combatants.values())[0]
        assert combatant.name == "New Combatant"
        assert combatant.initiative == 10

    def test_add_participant_to_existing_encounter(self, db_session):
        """Test adding participant to existing encounter."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Create encounter first
        action = CombatActionRequest(
            campaign_id=campaign.id,
            actor_id=1,
            action_type="attack",
            description="Start combat"
        )
        combat_engine.process_action(db_session, action)
        
        # Add participant
        participant = ParticipantCreate(
            name="Monster",
            initiative=8,
            hit_points=10,
            max_hit_points=10,
            armor_class=12
        )
        
        result = combat_engine.add_participant(db_session, campaign.id, participant)
        
        assert len(result.combatants) == 1

    def test_add_participant_with_conditions(self, db_session):
        """Test adding participant with conditions."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        participant = ParticipantCreate(
            name="Poisoned Hero",
            initiative=10,
            hit_points=15,
            max_hit_points=20,
            armor_class=14,
            conditions=["poisoned"]
        )
        
        result = combat_engine.add_participant(db_session, campaign.id, participant)
        
        combatant = list(result.combatants.values())[0]
        assert "poisoned" in combatant.conditions

    def test_update_participant_success(self, db_session):
        """Test successful participant update."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Add participant
        participant = ParticipantCreate(
            name="Hero",
            initiative=15,
            hit_points=20,
            max_hit_points=20,
            armor_class=16
        )
        state = combat_engine.add_participant(db_session, campaign.id, participant)
        participant_id = list(state.combatants.keys())[0]
        
        # Update participant
        update = ParticipantUpdate(hit_points=15, conditions=["prone"])
        result = combat_engine.update_participant(
            db_session, campaign.id, participant_id, update
        )
        
        assert result.combatants[participant_id].hit_points == 15
        assert "prone" in result.combatants[participant_id].conditions

    def test_update_participant_not_found(self, db_session):
        """Test updating non-existent participant."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        update = ParticipantUpdate(hit_points=10)
        
        with pytest.raises(ValueError, match="Participant not found"):
            combat_engine.update_participant(db_session, campaign.id, 99999, update)

    def test_remove_participant_success(self, db_session):
        """Test successful participant removal."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Add participant
        participant = ParticipantCreate(
            name="To Remove",
            initiative=10,
            hit_points=10,
            max_hit_points=10,
            armor_class=12
        )
        state = combat_engine.add_participant(db_session, campaign.id, participant)
        participant_id = list(state.combatants.keys())[0]
        
        # Remove participant
        result = combat_engine.remove_participant(
            db_session, campaign.id, participant_id
        )
        
        assert participant_id not in result.combatants

    def test_remove_participant_not_found(self, db_session):
        """Test removing non-existent participant."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        with pytest.raises(ValueError, match="Participant not found"):
            combat_engine.remove_participant(db_session, campaign.id, 99999)

    def test_turn_order_sorted_by_initiative(self, db_session):
        """Test that turn order is sorted by initiative (descending)."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Add participants with different initiatives
        p1 = ParticipantCreate(name="Fast", initiative=18, hit_points=10, max_hit_points=10, armor_class=14)
        p2 = ParticipantCreate(name="Medium", initiative=12, hit_points=10, max_hit_points=10, armor_class=14)
        p3 = ParticipantCreate(name="Slow", initiative=8, hit_points=10, max_hit_points=10, armor_class=14)
        
        state1 = combat_engine.add_participant(db_session, campaign.id, p1)
        state2 = combat_engine.add_participant(db_session, campaign.id, p2)
        state3 = combat_engine.add_participant(db_session, campaign.id, p3)
        
        # Final state should have all three, sorted by initiative
        final_state = combat_engine.get_combat_state(db_session, campaign.id)
        
        assert len(final_state.turn_order) == 3
        # First should be highest initiative
        first_id = final_state.turn_order[0]
        assert final_state.combatants[first_id].initiative == 18
