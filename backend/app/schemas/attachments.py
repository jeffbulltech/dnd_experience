from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignAttachmentRead(BaseModel):
    id: int
    campaign_id: int
    uploader_id: int | None
    original_filename: str
    content_type: str
    file_size: int
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CampaignAttachmentResponse(CampaignAttachmentRead):
    download_url: str | None = None

