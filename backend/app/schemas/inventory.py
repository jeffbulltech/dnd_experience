from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    character_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=150)
    quantity: int = Field(1, ge=0)
    weight: float | None = Field(None, ge=0)
    description: str | None = None
    properties: dict | None = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    quantity: int | None = Field(None, ge=0)
    weight: float | None = Field(None, ge=0)
    description: str | None = None
    properties: dict | None = None


class InventoryItemRead(InventoryItemBase):
    id: int

    class Config:
        from_attributes = True

