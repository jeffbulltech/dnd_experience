from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Character, CharacterDraft
from ..schemas.character_builder import (
    CharacterDraftCreate,
    CharacterDraftRead,
    CharacterDraftStepUpdate,
    CharacterDraftSummary,
)
from . import character_builder_rules, catalog_service, pdf_service

# TODO: Implement spell selection validation based on class level

VALID_SKILL_IDS = {skill["id"] for skill in catalog_service.get_skills()}
VALID_TOOL_IDS = {tool["id"] for tool in catalog_service.get_tools()}
VALID_WEAPON_IDS = {weapon["id"] for weapon in catalog_service.get_weapons()}
VALID_ARMOR_IDS = {armor["id"] for armor in catalog_service.get_armor()}
VALID_PACK_IDS = {pack["id"] for pack in catalog_service.get_equipment_packs()}
CURRENCY_TYPES = set(catalog_service.get_currency_types())


def _validate_proficiencies(payload: dict | None) -> dict:
    if payload is None:
        raise ValueError("Proficiency selections are required.")

    skills = payload.get("skills") or []
    tools = payload.get("tools") or []
    expertise = payload.get("expertise") or []

    invalid_skills = [skill for skill in skills if skill not in VALID_SKILL_IDS]
    if invalid_skills:
        raise ValueError(f"Unknown skills: {', '.join(invalid_skills)}")

    invalid_tools = [tool for tool in tools if tool not in VALID_TOOL_IDS]
    if invalid_tools:
        raise ValueError(f"Unknown tools: {', '.join(invalid_tools)}")

    invalid_expertise = [skill for skill in expertise if skill not in skills]
    if invalid_expertise:
        raise ValueError("Expertise selections must be chosen from proficient skills.")

    return {
        "skills": skills,
        "tools": tools,
        "expertise": expertise,
    }


def _validate_equipment(payload: dict | None) -> dict:
    if payload is None:
        raise ValueError("Equipment selections are required.")

    weapons = payload.get("weapons") or []
    armor = payload.get("armor") or []
    packs = payload.get("packs") or []
    custom_items = payload.get("custom_items") or []
    currency = payload.get("currency") or {}

    invalid_weapons = [weapon for weapon in weapons if weapon not in VALID_WEAPON_IDS]
    if invalid_weapons:
        raise ValueError(f"Unknown weapons: {', '.join(invalid_weapons)}")

    invalid_armor = [piece for piece in armor if piece not in VALID_ARMOR_IDS]
    if invalid_armor:
        raise ValueError(f"Unknown armor: {', '.join(invalid_armor)}")

    invalid_packs = [pack for pack in packs if pack not in VALID_PACK_IDS]
    if invalid_packs:
        raise ValueError(f"Unknown equipment packs: {', '.join(invalid_packs)}")

    invalid_currency = [coin for coin in currency if coin not in CURRENCY_TYPES]
    if invalid_currency:
        raise ValueError(f"Unknown currency types: {', '.join(invalid_currency)}")

    validated_currency = {coin: int(amount) for coin, amount in currency.items() if int(amount) >= 0}

    return {
        "weapons": weapons,
        "armor": armor,
        "packs": packs,
        "custom_items": custom_items,
        "currency": validated_currency,
    }


def _validate_spells(payload: dict | None, class_id: str | None, level: int) -> dict:
    if payload is None:
        raise ValueError("Spell selections are required.")

    spells_known = payload.get("known") or []
    spells_prepared = payload.get("prepared") or []
    cantrips = payload.get("cantrips") or []

    available_spells = catalog_service.get_spells()
    class_spells = {spell["id"]: spell for spell in available_spells if not class_id or class_id in spell["classes"]}

    invalid_known = [spell_id for spell_id in spells_known if spell_id not in class_spells]
    if invalid_known:
        raise ValueError(f"Unknown or invalid spells: {', '.join(invalid_known)}")

    invalid_prepared = [spell_id for spell_id in spells_prepared if spell_id not in class_spells]
    if invalid_prepared:
        raise ValueError(f"Cannot prepare spells not known to your class: {', '.join(invalid_prepared)}")

    invalid_cantrips = [spell_id for spell_id in cantrips if spell_id not in class_spells]
    if invalid_cantrips:
        raise ValueError(f"Unknown cantrips: {', '.join(invalid_cantrips)}")

    # TODO: enforce known/prepared counts based on class and level
    return {
        "known": spells_known,
        "prepared": spells_prepared,
        "cantrips": cantrips,
    }


def _validate_origin(payload: dict[str, str | list[str]] | None) -> dict[str, str | list[str]]:
    if not payload:
        raise ValueError("Origin selections are required.")

    species_id = payload.get("species")
    background_id = payload.get("background")
    languages = payload.get("languages")

    species_ids = {item["id"] for item in catalog_service.get_species()}
    background_ids = {item["id"] for item in catalog_service.get_backgrounds()}
    language_ids = set(catalog_service.get_languages())

    if species_id and species_id not in species_ids:
        raise ValueError("Unknown species selection.")
    if background_id and background_id not in background_ids:
        raise ValueError("Unknown background selection.")
    if languages:
        invalid_languages = [lang for lang in languages if lang not in language_ids]
        if invalid_languages:
            raise ValueError(f"Unknown languages: {', '.join(invalid_languages)}")

    return {
        "species": species_id,
        "background": background_id,
        "languages": languages or [],
    }


def _validate_class(payload: dict[str, str] | None) -> dict[str, str]:
    if not payload or "class" not in payload:
        raise ValueError("Class selection is required.")

    class_id = payload["class"]
    class_ids = {item["id"] for item in catalog_service.get_classes()}
    if class_id not in class_ids:
        raise ValueError("Unknown class selection.")

    return {"class": class_id}

def list_drafts(db: Session, *, user_id: int) -> Sequence[CharacterDraftSummary]:
    stmt = (
        select(CharacterDraft)
        .where(CharacterDraft.user_id == user_id)
        .order_by(CharacterDraft.updated_at.desc())
    )
    drafts = db.execute(stmt).scalars().all()
    return [
        CharacterDraftSummary.model_validate(draft, from_attributes=True)
        for draft in drafts
    ]


def create_draft(db: Session, *, user_id: int, payload: CharacterDraftCreate) -> CharacterDraftRead:
    draft = CharacterDraft(
        user_id=user_id,
        name=payload.name,
        starting_level=payload.starting_level,
        allow_feats=payload.allow_feats,
        variant_flags=payload.variant_flags or {},
        step_data={},
        status="draft",
        current_step="intro",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return CharacterDraftRead.model_validate(draft, from_attributes=True)

def get_draft(db: Session, *, user_id: int, draft_id: int) -> CharacterDraft:
    draft = db.get(CharacterDraft, draft_id)
    if draft is None or draft.user_id != user_id:
        raise ValueError("Character draft not found.")
    return draft

def fetch_draft(db: Session, *, user_id: int, draft_id: int) -> CharacterDraftRead:
    draft = get_draft(db, user_id=user_id, draft_id=draft_id)
    return CharacterDraftRead.model_validate(draft, from_attributes=True)

def update_step(
    db: Session,
    *,
    user_id: int,
    draft_id: int,
    step: str,
    update: CharacterDraftStepUpdate,
) -> CharacterDraftRead:
    if not step:
        msg = "Step identifier is required."
        raise ValueError(msg)

    draft = get_draft(db, user_id=user_id, draft_id=draft_id)
    step_payload = dict(draft.step_data or {})

    if step == "ability_scores":
        try:
            normalized = character_builder_rules.validate_and_normalize_ability_scores(update.payload or {})
        except character_builder_rules.AbilityScoreValidationError as exc:
            raise ValueError(str(exc)) from exc
        step_payload[step] = normalized
    elif step == "origin":
        step_payload[step] = _validate_origin(update.payload)
    elif step == "class":
        step_payload[step] = _validate_class(update.payload)
    elif step == "proficiencies":
        step_payload[step] = _validate_proficiencies(update.payload)
    elif step == "equipment":
        step_payload[step] = _validate_equipment(update.payload)
    elif step == "spells":
        class_id = draft.step_data.get("class", {}).get("class") if draft.step_data else None
        character_level = draft.starting_level
        step_payload[step] = _validate_spells(update.payload, class_id, character_level)
    else:
        step_payload[step] = update.payload or {}

    draft.step_data = step_payload
    draft.current_step = step
    draft.status = "in_progress" if draft.status == "draft" else draft.status
    if update.mark_complete:
        draft.status = "ready_for_finalize"
    draft.updated_at = datetime.utcnow()
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return CharacterDraftRead.model_validate(draft, from_attributes=True)

def delete_draft(db: Session, *, user_id: int, draft_id: int) -> None:
    draft = get_draft(db, user_id=user_id, draft_id=draft_id)
    db.delete(draft)
    db.commit()

def finalize_draft(db: Session, *, user_id: int, draft_id: int) -> CharacterDraftRead:
    draft = get_draft(db, user_id=user_id, draft_id=draft_id)
    if draft.character_id:
        return CharacterDraftRead.model_validate(draft, from_attributes=True)

    steps = draft.step_data or {}
    ability_step = steps.get("ability_scores")
    origin_step = steps.get("origin")
    class_step = steps.get("class")

    if not ability_step or not origin_step or not class_step:
        raise ValueError("Ability scores, origin, and class must be completed before finalizing.")

    scores = ability_step.get("scores", {})
    species = next((item for item in catalog_service.get_species() if item["id"] == origin_step.get("species")), None)
    background = next((item for item in catalog_service.get_backgrounds() if item["id"] == origin_step.get("background")), None)
    class_info = next((item for item in catalog_service.get_classes() if item["id"] == class_step.get("class")), None)

    if not class_info:
        raise ValueError("Invalid class selection.")

    adjusted_scores = character_builder_rules.apply_species_adjustments(scores, species.get("abilities") if species else None)
    modifiers = {ability: character_builder_rules.ability_modifier(value) for ability, value in adjusted_scores.items()}
    proficiency = character_builder_rules.proficiency_bonus(draft.starting_level)

    skill_defs = catalog_service.get_skills()
    background_skills = set(background.get("skills", [])) if background else set()
    chosen_skills = set((steps.get("proficiencies") or {}).get("skills", []))
    expertise_skills = set((steps.get("proficiencies") or {}).get("expertise", []))
    total_skills = background_skills | chosen_skills

    skills_summary = {}
    passive_perception = 10
    for definition in skill_defs:
        skill_id = definition["id"]
        ability = definition["ability"]
        proficient = skill_id in total_skills
        expertise = skill_id in expertise_skills
        bonus = modifiers.get(ability, 0)
        if proficient:
            bonus += proficiency * (2 if expertise else 1)
        skills_summary[skill_id] = {
            "name": definition["name"],
            "ability": ability,
            "total": bonus,
            "proficient": proficient,
            "expertise": expertise,
        }
        if skill_id == "perception":
            passive_perception = 10 + bonus

    saving_throw_ids = class_info.get("saving_throws", [])
    saving_throws = {
        ability: {
            "total": modifiers.get(ability, 0) + proficiency,
            "proficient": True,
        }
        for ability in saving_throw_ids
    }

    hit_die = class_info.get("hit_die", 8)
    hp_per_level = max(1, hit_die // 2 + 1)
    max_hp = hit_die + modifiers.get("constitution", 0)
    if draft.starting_level > 1:
        max_hp += (draft.starting_level - 1) * (hp_per_level + modifiers.get("constitution", 0))

    equipment_step = steps.get("equipment") or {}
    armor_ids = equipment_step.get("armor", [])
    armor_defs = {armor["id"]: armor for armor in catalog_service.get_armor()}
    if armor_ids:
        primary_armor = armor_defs.get(armor_ids[0], {})
        armor_class = primary_armor.get("ac", 10)
    else:
        armor_class = 10 + modifiers.get("dexterity", 0)

    spells_step = steps.get("spells") or {}
    spell_slots_map = catalog_service.get_spell_slots().get(class_step.get("class"), [])
    available_slots = next((entry.get("slots", {}) for entry in reversed(spell_slots_map) if entry.get("level", 0) <= draft.starting_level), {})

    languages = set(origin_step.get("languages", []))
    if species:
        languages.update(species.get("languages", []))

    character = Character(
        user_id=user_id,
        name=draft.name or "Unnamed Adventurer",
        level=draft.starting_level,
        race=species.get("name") if species else None,
        character_class=class_info.get("name"),
        background=background.get("name") if background else None,
        ability_scores={ability: {"score": score, "mod": modifiers.get(ability, 0)} for ability, score in adjusted_scores.items()},
        skills=skills_summary,
        attributes={
            "proficiency_bonus": proficiency,
            "saving_throws": saving_throws,
            "armor_class": armor_class,
            "hit_points": {"max": max_hp, "current": max_hp, "temp": 0},
            "passive_perception": passive_perception,
            "spell_slots": available_slots,
            "spells": spells_step,
            "equipment": equipment_step,
            "languages": sorted(languages),
        },
        notes=None,
    )
    db.add(character)
    db.commit()
    db.refresh(character)

    draft.character_id = character.id
    draft.status = "completed"
    draft.current_step = "finalized"
    db.add(draft)
    db.commit()
    db.refresh(draft)

    settings = get_settings()
    template_path = Path(settings.vector_store_path).parents[0] / "templates" / "5E_CharacterSheet_Fillable.pdf"
    output_dir = settings.vector_store_path / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    if template_path.exists():
        pdf_path = output_dir / f"character_{character.id}.pdf"
        pdf_service.fill_character_sheet(template_path, pdf_path, character, draft)
        draft.step_data = {**draft.step_data, "export": {"pdf_path": str(pdf_path)}}
        db.add(draft)
        db.commit()
        db.refresh(draft)

    return CharacterDraftRead.model_validate(draft, from_attributes=True)

