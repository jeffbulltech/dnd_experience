from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ADVENTURES_DIR = Path(__file__).resolve().parents[2] / "data" / "adventures"


class AdventureTemplate:
    """Represents a pre-made adventure template."""

    def __init__(self, data: dict[str, Any]):
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.level_range: str = data.get("level_range", "1-20")
        self.setting: str = data.get("setting", "Custom")
        self.seed_content: str = data.get("seed_content", "")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level_range": self.level_range,
            "setting": self.setting,
        }


def list_adventure_templates() -> list[AdventureTemplate]:
    """List all available adventure templates."""
    templates: list[AdventureTemplate] = []

    if not ADVENTURES_DIR.exists():
        return templates

    for file_path in ADVENTURES_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                templates.append(AdventureTemplate(data))
        except (json.JSONDecodeError, KeyError) as e:
            # Skip invalid files
            continue

    return sorted(templates, key=lambda t: t.name)


def get_adventure_template(template_id: str) -> AdventureTemplate | None:
    """Load a specific adventure template by ID."""
    if template_id == "custom":
        return None

    file_path = ADVENTURES_DIR / f"{template_id}.json"
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AdventureTemplate(data)
    except (json.JSONDecodeError, KeyError):
        return None


def get_adventure_seed_content(template_id: str | None) -> str:
    """Get the seed content for an adventure template."""
    if not template_id or template_id == "custom":
        return ""

    template = get_adventure_template(template_id)
    if template:
        return template.seed_content
    return ""
