import random
import re

from datetime import datetime

from ..schemas.dice import DiceRollRequest, DiceRollResult

ROLL_PATTERN = re.compile(
    r"^(?P<count>\d*)d(?P<sides>\d+)"
    r"(?P<keep>(kh|kl)\d+)?"
    r"(?P<modifier>(\+|-)\d+)?$",
    re.IGNORECASE,
)


def roll_dice(request: DiceRollRequest) -> DiceRollResult:
    match = ROLL_PATTERN.match(request.expression.replace(" ", ""))
    if not match:
        msg = "Invalid dice expression."
        raise ValueError(msg)

    count = int(match.group("count") or 1)
    sides = int(match.group("sides"))
    modifier = int(match.group("modifier") or 0)
    keep_spec = match.group("keep")

    rolls = _roll_multiple(count, sides)

    kept_rolls = rolls
    has_advantage = False
    has_disadvantage = False
    if keep_spec:
        threshold = int(keep_spec[2:])
        if keep_spec.startswith("kh"):
            has_advantage = count == 2 and threshold == 1 and sides == 20
            kept_rolls = sorted(rolls, reverse=True)[:threshold]
        else:
            has_disadvantage = count == 2 and threshold == 1 and sides == 20
            kept_rolls = sorted(rolls)[:threshold]

    total = sum(kept_rolls) + modifier

    is_crit_success = sides == 20 and max(kept_rolls, default=0) == 20
    is_crit_failure = sides == 20 and min(kept_rolls, default=sides) == 1

    detail = {
        "kept_rolls": kept_rolls,
        "modifier": modifier,
        "rolls": rolls,
    }

    return DiceRollResult(
        expression=request.expression,
        total=total,
        individual_rolls=rolls,
        has_advantage=has_advantage,
        has_disadvantage=has_disadvantage,
        is_critical_success=is_crit_success,
        is_critical_failure=is_crit_failure,
        detail=detail,
        timestamp=datetime.utcnow().isoformat(),
    )


def _roll_multiple(count: int, sides: int) -> list[int]:
    if count < 1 or sides < 2:
        msg = "Dice count must be >=1 and sides >=2."
        raise ValueError(msg)
    return [random.randint(1, sides) for _ in range(count)]
