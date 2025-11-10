from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Campaign, Encounter, EncounterParticipant
from ..schemas.combat import (
    CombatActionRequest,
    CombatState,
    CombatantState,
    ParticipantCreate,
    ParticipantUpdate,
)

ACTIVE_STATUSES = ("active", "pending")


def process_action(db: Session, payload: CombatActionRequest) -> CombatState:
    """
    Apply a combat action and return the updated encounter state.

    This implementation maintains an encounter log while deferring detailed rules
    resolution to future iterations.
    """
    campaign = db.get(Campaign, payload.campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found.")

    encounter = (
        db.query(Encounter)
        .filter(
            Encounter.campaign_id == payload.campaign_id,
            Encounter.status.in_(ACTIVE_STATUSES),
        )
        .order_by(Encounter.updated_at.desc())
        .first()
    )

    if encounter is None:
        encounter = Encounter(
            campaign_id=payload.campaign_id,
            name=f"Encounter {datetime.utcnow():%Y%m%d%H%M%S}",
            status="active",
            round_number=1,
            extra={"actions": []},
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

    log = encounter.extra or {}
    actions = log.setdefault("actions", [])
    actions.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "actor_id": payload.actor_id,
            "target_id": payload.target_id,
            "action_type": payload.action_type,
            "description": payload.description,
        }
    )
    encounter.extra = log
    encounter.updated_at = datetime.utcnow()

    db.add(encounter)
    db.commit()
    db.refresh(encounter)

    return _build_state(db, encounter)


def get_combat_state(db: Session, campaign_id: int) -> CombatState:
    encounter = (
        db.query(Encounter)
        .filter(Encounter.campaign_id == campaign_id, Encounter.status.in_(ACTIVE_STATUSES))
        .order_by(Encounter.updated_at.desc())
        .first()
    )

    if encounter is None:
        return CombatState(
            campaign_id=campaign_id,
            round_number=0,
            turn_order=[],
            active_combatant_id=None,
            combatants={},
            last_updated=datetime.utcnow(),
        )

    return _build_state(db, encounter)


def add_participant(
    db: Session,
    campaign_id: int,
    payload: ParticipantCreate,
) -> CombatState:
    encounter = _ensure_encounter(db, campaign_id)
    participant = EncounterParticipant(
        encounter_id=encounter.id,
        name=payload.name,
        initiative=payload.initiative,
        hit_points=payload.hit_points,
        max_hit_points=payload.max_hit_points,
        armor_class=payload.armor_class,
        conditions=payload.conditions,
        attributes=payload.attributes or {},
    )
    db.add(participant)
    db.commit()
    return _build_state(db, encounter)


def update_participant(
    db: Session,
    campaign_id: int,
    participant_id: int,
    payload: ParticipantUpdate,
) -> CombatState:
    encounter = _ensure_encounter(db, campaign_id)
    participant = db.get(EncounterParticipant, participant_id)
    if participant is None or participant.encounter_id != encounter.id:
        raise ValueError("Participant not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(participant, key, value)

    db.add(participant)
    db.commit()
    return _build_state(db, encounter)


def remove_participant(db: Session, campaign_id: int, participant_id: int) -> CombatState:
    encounter = _ensure_encounter(db, campaign_id)
    participant = db.get(EncounterParticipant, participant_id)
    if participant is None or participant.encounter_id != encounter.id:
        raise ValueError("Participant not found.")

    db.delete(participant)
    db.commit()
    return _build_state(db, encounter)


def _build_state(db: Session, encounter: Encounter) -> CombatState:
    participants = (
        db.query(EncounterParticipant)
        .filter(EncounterParticipant.encounter_id == encounter.id)
        .order_by(EncounterParticipant.initiative.desc())
        .all()
    )

    combatants: dict[int, CombatantState] = {
        participant.id: CombatantState(
            id=participant.id,
            name=participant.name,
            initiative=participant.initiative,
            hit_points=participant.hit_points,
            max_hit_points=participant.max_hit_points,
            armor_class=participant.armor_class,
            conditions=participant.conditions or [],
        )
        for participant in participants
    }

    turn_order = [participant.id for participant in participants]
    active_combatant_id = turn_order[0] if turn_order else None

    return CombatState(
        campaign_id=encounter.campaign_id,
        round_number=encounter.round_number,
        turn_order=turn_order,
        active_combatant_id=active_combatant_id,
        combatants=combatants,
        last_updated=datetime.utcnow(),
    )


def _ensure_encounter(db: Session, campaign_id: int) -> Encounter:
    encounter = (
        db.query(Encounter)
        .filter(Encounter.campaign_id == campaign_id, Encounter.status.in_(ACTIVE_STATUSES))
        .order_by(Encounter.updated_at.desc())
        .first()
    )

    if encounter is None:
        encounter = Encounter(
            campaign_id=campaign_id,
            name=f"Encounter {datetime.utcnow():%Y%m%d%H%M%S}",
            status="active",
            round_number=1,
            extra={"actions": []},
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

    return encounter
