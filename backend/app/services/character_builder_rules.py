from __future__ import annotations

from typing import Any

ABILITY_NAMES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

STANDARD_ARRAY = (15, 14, 13, 12, 10, 8)
POINT_BUY_COSTS = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}
POINT_BUY_TOTAL = 27


class AbilityScoreValidationError(ValueError):
    """Raised when ability score input fails validation."""


def _normalize_scores(raw_scores: Any) -> dict[str, int]:
    if raw_scores is None:
        raise AbilityScoreValidationError("Ability scores payload is required.")

    if isinstance(raw_scores, dict):
        scores = {key.lower(): int(value) for key, value in raw_scores.items()}
        missing = [ability for ability in ABILITY_NAMES if ability not in scores]
        extra = [key for key in scores if key not in ABILITY_NAMES]
        if missing:
            raise AbilityScoreValidationError(f"Missing ability scores: {', '.join(missing)}")
        if extra:
            raise AbilityScoreValidationError(f"Unknown ability score keys: {', '.join(extra)}")
        return scores

    if isinstance(raw_scores, (list, tuple)) and len(raw_scores) == len(ABILITY_NAMES):
        return {name: int(value) for name, value in zip(ABILITY_NAMES, raw_scores, strict=False)}

    raise AbilityScoreValidationError("Ability scores must be provided as a dict or list of six values.")


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


def ability_modifier(score: int) -> int:
    return _ability_mod(score)


def proficiency_bonus(level: int) -> int:
    if level <= 4:
        return 2
    if level <= 8:
        return 3
    if level <= 12:
        return 4
    if level <= 16:
        return 5
    return 6


def apply_species_adjustments(scores: dict[str, int], bonuses: dict[str, int] | None) -> dict[str, int]:
    adjusted = dict(scores)
    if not bonuses:
        return adjusted
    for ability, bonus in bonuses.items():
        if ability == "all":
            for key in adjusted:
                adjusted[key] = adjusted.get(key, 0) + bonus
        else:
            adjusted[ability] = adjusted.get(ability, 0) + bonus
    return adjusted


def validate_and_normalize_ability_scores(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Validate ability score selection and return normalized data with modifiers.

    Expected payload shape:
    {
        "method": "standard_array" | "point_buy" | "manual",
        "scores": {...},
        "point_buy_allow_higher": bool optional
    }
    """
    method = (payload or {}).get("method", "").lower()
    if method not in {"standard_array", "point_buy", "manual"}:
        raise AbilityScoreValidationError("Ability score method must be one of standard_array, point_buy, or manual.")

    raw_scores = (payload or {}).get("scores")
    scores = _normalize_scores(raw_scores)

    values = tuple(scores[ability] for ability in ABILITY_NAMES)

    if method == "standard_array":
        if sorted(values) != sorted(STANDARD_ARRAY):
            raise AbilityScoreValidationError(
                f"Standard array must contain the values {STANDARD_ARRAY} exactly once."
            )
    elif method == "point_buy":
        total_cost = 0
        for value in values:
            if value < 8 or value > 15:
                raise AbilityScoreValidationError("Point buy scores must be between 8 and 15.")
            total_cost += POINT_BUY_COSTS.get(value, 100)
        if total_cost > POINT_BUY_TOTAL:
            raise AbilityScoreValidationError("Point buy total exceeds 27 points.")
    else:  # manual
        for value in values:
            if value < 3 or value > 18:
                raise AbilityScoreValidationError("Manual ability scores must be between 3 and 18.")

    modifiers = {ability: _ability_mod(score) for ability, score in scores.items()}

    return {
        "method": method,
        "scores": scores,
        "modifiers": modifiers,
    }

