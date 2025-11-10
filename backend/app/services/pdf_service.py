from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from pdfrw import PdfReader, PdfWriter, PdfDict  # type: ignore

from ..models import Character, CharacterDraft

FIELD_MAP = {
    "character.name": "CharacterName",
    "player.name": "PlayerName",
    "abilities.strength.score": "STR",
    "abilities.strength.mod": "STRmod",
    "abilities.dexterity.score": "DEX",
    "abilities.dexterity.mod": "DEXmod",
    "abilities.constitution.score": "CON",
    "abilities.constitution.mod": "CONmod",
    "abilities.intelligence.score": "INT",
    "abilities.intelligence.mod": "INTmod",
    "abilities.wisdom.score": "WIS",
    "abilities.wisdom.mod": "WISmod",
    "abilities.charisma.score": "CHA",
    "abilities.charisma.mod": "CHamod",
    "proficiency_bonus": "ProficiencyBonus",
    "attributes.armor_class": "AC",
    "attributes.hit_points.max": "HPMax",
    "attributes.hit_points.current": "HPCurrent",
}


class PDFGenerationError(RuntimeError):
    pass


def _extract_value(data: Mapping[str, Any], key: str) -> Any:
    value: Any = data
    for part in key.split('.'):
        if isinstance(value, Mapping) and part in value:
            value = value[part]
        else:
            return None
    return value


def fill_character_sheet(template_path: Path, output_path: Path, character: Character, draft: CharacterDraft) -> Path:
    if not template_path.exists():
        raise PDFGenerationError(f"Template not found: {template_path}")

    reader = PdfReader(str(template_path))
    if not hasattr(reader, "Root"):
        raise PDFGenerationError("Invalid PDF template")

    data = {
        "character": {
            "name": character.name,
        },
        "player": {
            "name": "",
        },
        "abilities": {ability: {
            "score": character.ability_scores.get(ability, {}).get("score", 0),
            "mod": character.ability_scores.get(ability, {}).get("mod", 0),
        } for ability in character.ability_scores},
        "proficiency_bonus": character.attributes.get("proficiency_bonus"),
        "attributes": character.attributes,
    }

    annotations = []
    for page in reader.pages:
        if page.Annots:
            annotations.extend(page.Annots)

    value_map = {}
    for key, field_name in FIELD_MAP.items():
        value = _extract_value(data, key)
        if value is not None:
            value_map[field_name] = str(value)

    for annotation in annotations:
        if annotation.Subtype != '/Widget' or not annotation.T:
            continue
        field_name = annotation.T[1:-1]
        if field_name in value_map:
            annotation.update(PdfDict(V='{}'.format(value_map[field_name]), AP=''))

    writer = PdfWriter()
    writer.trailer = reader
    writer.write(str(output_path))
    return output_path
