from datetime import datetime

from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    adventure_template_id: str | None = Field(None, description="ID of adventure template, or 'custom' for AI-generated")


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = None
    is_active: bool | None = None


class CampaignRead(CampaignBase):
    id: int
    owner_id: int
    is_active: bool = True
    adventure_template_id: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
