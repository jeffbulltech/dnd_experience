from __future__ import annotations

from functools import lru_cache

SPECIES = [
  {
    "id": "human",
    "name": "Human",
    "speed": 30,
    "size": "medium",
    "abilities": {"all": 1},
    "languages": ["Common"],
  },
  {
    "id": "elf",
    "name": "Elf",
    "speed": 30,
    "size": "medium",
    "abilities": {"dexterity": 2},
    "languages": ["Common", "Elvish"],
    "traits": ["Darkvision", "Keen Senses"],
  },
  {
    "id": "dwarf",
    "name": "Dwarf",
    "speed": 25,
    "size": "medium",
    "abilities": {"constitution": 2},
    "languages": ["Common", "Dwarvish"],
    "traits": ["Darkvision", "Dwarven Resilience"],
  },
]

BACKGROUNDS = [
  {
    "id": "acolyte",
    "name": "Acolyte",
    "skills": ["insight", "religion"],
    "languages": 2,
    "feature": "Shelter of the Faithful",
  },
  {
    "id": "soldier",
    "name": "Soldier",
    "skills": ["athletics", "intimidation"],
    "tools": ["gaming_set", "vehicles_land"],
    "feature": "Military Rank",
  },
  {
    "id": "sage",
    "name": "Sage",
    "skills": ["arcana", "history"],
    "languages": 2,
    "feature": "Researcher",
  },
]

CLASSES = [
  {
    "id": "fighter",
    "name": "Fighter",
    "hit_die": 10,
    "primary_abilities": ["strength", "constitution"],
    "saving_throws": ["strength", "constitution"],
    "skill_choices": {
      "count": 2,
      "options": [
        "acrobatics",
        "animal_handling",
        "athletics",
        "history",
        "insight",
        "intimidation",
        "perception",
        "survival",
      ]
    }
  },
  {
    "id": "wizard",
    "name": "Wizard",
    "hit_die": 6,
    "primary_abilities": ["intelligence"],
    "saving_throws": ["intelligence", "wisdom"],
    "spellcasting": {
      "ability": "intelligence"
    },
    "skill_choices": {
      "count": 2,
      "options": [
        "arcana",
        "history",
        "insight",
        "investigation",
        "medicine",
        "religion"
      ]
    }
  },
  {
    "id": "cleric",
    "name": "Cleric",
    "hit_die": 8,
    "primary_abilities": ["wisdom", "charisma"],
    "saving_throws": ["wisdom", "charisma"],
    "spellcasting": {
      "ability": "wisdom"
    },
    "skill_choices": {
      "count": 2,
      "options": [
        "history",
        "insight",
        "medicine",
        "persuasion",
        "religion"
      ]
    }
  },
]

SKILLS = [
  {"id": "acrobatics", "name": "Acrobatics", "ability": "dexterity"},
  {"id": "animal_handling", "name": "Animal Handling", "ability": "wisdom"},
  {"id": "arcana", "name": "Arcana", "ability": "intelligence"},
  {"id": "athletics", "name": "Athletics", "ability": "strength"},
  {"id": "deception", "name": "Deception", "ability": "charisma"},
  {"id": "history", "name": "History", "ability": "intelligence"},
  {"id": "insight", "name": "Insight", "ability": "wisdom"},
  {"id": "intimidation", "name": "Intimidation", "ability": "charisma"},
  {"id": "investigation", "name": "Investigation", "ability": "intelligence"},
  {"id": "medicine", "name": "Medicine", "ability": "wisdom"},
  {"id": "nature", "name": "Nature", "ability": "intelligence"},
  {"id": "perception", "name": "Perception", "ability": "wisdom"},
  {"id": "performance", "name": "Performance", "ability": "charisma"},
  {"id": "persuasion", "name": "Persuasion", "ability": "charisma"},
  {"id": "religion", "name": "Religion", "ability": "intelligence"},
  {"id": "sleight_of_hand", "name": "Sleight of Hand", "ability": "dexterity"},
  {"id": "stealth", "name": "Stealth", "ability": "dexterity"},
  {"id": "survival", "name": "Survival", "ability": "wisdom"},
]

TOOLS = [
  {"id": "gaming_set", "name": "Gaming Set"},
  {"id": "vehicles_land", "name": "Vehicles (Land)"},
  {"id": "thieves_tools", "name": "Thieves' Tools"},
  {"id": "alchemist_supplies", "name": "Alchemist's Supplies"},
]

LANGUAGES = [
  "Common",
  "Dwarvish",
  "Elvish",
  "Giant",
  "Gnomish",
  "Goblin",
  "Halfling",
  "Orc",
  "Draconic",
  "Infernal",
]

EQUIPMENT_PACKS = [
  {
    "id": "dungeoneer_pack",
    "name": "Dungeoneer's Pack",
    "contents": [
      {"item": "Backpack", "quantity": 1},
      {"item": "Crowbar", "quantity": 1},
      {"item": "Hammer", "quantity": 1},
      {"item": "Pitons", "quantity": 10},
      {"item": "Torches", "quantity": 10},
      {"item": "Rations", "quantity": 10},
      {"item": "Waterskin", "quantity": 1},
      {"item": "Hempen Rope (50 ft)", "quantity": 1},
    ]
  },
  {
    "id": "explorer_pack",
    "name": "Explorer's Pack",
    "contents": [
      {"item": "Backpack", "quantity": 1},
      {"item": "Bedroll", "quantity": 1},
      {"item": "Mess Kit", "quantity": 1},
      {"item": "Tinderbox", "quantity": 1},
      {"item": "Torches", "quantity": 10},
      {"item": "Rations", "quantity": 10},
      {"item": "Waterskin", "quantity": 1},
      {"item": "Hempen Rope (50 ft)", "quantity": 1},
    ]
  },
]

ARMOR = [
  {"id": "leather_armor", "name": "Leather Armor", "type": "light", "ac": 11, "cost": {"gp": 10}},
  {"id": "chain_mail", "name": "Chain Mail", "type": "heavy", "ac": 16, "cost": {"gp": 75}},
]

WEAPONS = [
  {"id": "longsword", "name": "Longsword", "damage": "1d8 slashing", "type": "martial"},
  {"id": "shortbow", "name": "Shortbow", "damage": "1d6 piercing", "type": "simple"},
]

CURRENCY_TYPES = ["cp", "sp", "ep", "gp", "pp"]

SPELLS = [
  {
    "id": "fire_bolt",
    "name": "Fire Bolt",
    "level": 0,
    "school": "Evocation",
    "classes": ["wizard", "sorcerer"],
    "casting_time": "1 action",
    "range": "120 feet",
    "components": ["V", "S"],
    "duration": "Instantaneous",
  },
  {
    "id": "cure_wounds",
    "name": "Cure Wounds",
    "level": 1,
    "school": "Evocation",
    "classes": ["cleric", "druid", "bard"],
    "casting_time": "1 action",
    "range": "Touch",
    "components": ["V", "S"],
    "duration": "Instantaneous",
  },
  {
    "id": "shield",
    "name": "Shield",
    "level": 1,
    "school": "Abjuration",
    "classes": ["wizard", "sorcerer"],
    "casting_time": "1 reaction",
    "range": "Self",
    "components": ["V", "S"],
    "duration": "1 round",
  },
]

SPELL_SLOTS_BY_CLASS = {
  "wizard": [
    {"level": 1, "slots": {"1": 2}},
    {"level": 2, "slots": {"1": 3}},
    {"level": 3, "slots": {"1": 4, "2": 2}},
  ],
  "cleric": [
    {"level": 1, "slots": {"1": 2}},
    {"level": 2, "slots": {"1": 3}},
  ],
}


@lru_cache
def get_species() -> list[dict]:
    return SPECIES


@lru_cache
def get_backgrounds() -> list[dict]:
    return BACKGROUNDS


@lru_cache
def get_classes() -> list[dict]:
    return CLASSES


@lru_cache
def get_skills() -> list[dict]:
    return SKILLS


@lru_cache
def get_tools() -> list[dict]:
    return TOOLS


@lru_cache
def get_languages() -> list[str]:
    return LANGUAGES


@lru_cache
def get_equipment_packs() -> list[dict]:
    return EQUIPMENT_PACKS


@lru_cache
def get_armor() -> list[dict]:
    return ARMOR


@lru_cache
def get_weapons() -> list[dict]:
    return WEAPONS


@lru_cache
def get_currency_types() -> list[str]:
    return CURRENCY_TYPES


@lru_cache
def get_spells() -> list[dict]:
    return SPELLS


@lru_cache
def get_spell_slots() -> dict[str, list[dict]]:
    return SPELL_SLOTS_BY_CLASS
