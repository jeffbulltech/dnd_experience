from __future__ import annotations

from fastapi import APIRouter

from ..services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/species")
def list_species() -> list[dict]:
    return catalog_service.get_species()


@router.get("/backgrounds")
def list_backgrounds() -> list[dict]:
    return catalog_service.get_backgrounds()


@router.get("/classes")
def list_classes() -> list[dict]:
    return catalog_service.get_classes()


@router.get("/skills")
def list_skills() -> list[dict]:
    return catalog_service.get_skills()


@router.get("/tools")
def list_tools() -> list[dict]:
    return catalog_service.get_tools()


@router.get("/armor")
def list_armor() -> list[dict]:
    return catalog_service.get_armor()


@router.get("/weapons")
def list_weapons() -> list[dict]:
    return catalog_service.get_weapons()


@router.get("/equipment-packs")
def list_equipment_packs() -> list[dict]:
    return catalog_service.get_equipment_packs()


@router.get("/currency")
def list_currency_types() -> list[str]:
    return catalog_service.get_currency_types()


@router.get("/languages")
def list_languages() -> list[str]:
    return catalog_service.get_languages()


@router.get("/spells")
def list_spells() -> list[dict]:
    return catalog_service.get_spells()


@router.get("/spell-slots")
def list_spell_slots() -> dict[str, list[dict]]:
    return catalog_service.get_spell_slots()
