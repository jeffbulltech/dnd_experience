from pydantic import BaseModel, Field, field_validator


class DiceRollRequest(BaseModel):
    expression: str = Field(..., description="Dice expression, e.g. '2d20kh1+5'")
    campaign_id: int | None = Field(None, ge=1)
    character_id: int | None = Field(None, ge=1)
    roller_type: str | None = None

    @field_validator("expression")
    @classmethod
    def validate_expression(cls, value: str) -> str:
        if not value or "d" not in value:
            msg = "Dice expression must include at least one 'd'."
            raise ValueError(msg)
        return value

    @field_validator("roller_type")
    @classmethod
    def validate_roller_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"player", "gm", "system"}
        if value not in allowed:
            msg = f"roller_type must be one of {allowed}"
            raise ValueError(msg)
        return value


class DiceRollResult(BaseModel):
    expression: str
    total: int
    individual_rolls: list[int]
    has_advantage: bool = False
    has_disadvantage: bool = False
    is_critical_success: bool = False
    is_critical_failure: bool = False
    detail: dict | None = None
    timestamp: str | None = None


class DiceRollLog(BaseModel):
    id: int
    campaign_id: int | None = None
    character_id: int | None = None
    roller_type: str
    expression: str
    total: int
    detail: dict | None = None
    metadata: dict | None = None
    created_at: str

    class Config:
        from_attributes = True
