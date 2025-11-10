from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Campaign, CampaignAttachment, Character
from ..schemas.attachments import CampaignAttachmentRead


@dataclass
class AttachmentUpload:
    filename: str
    content_type: str | None
    file: BinaryIO


def list_attachments(db: Session, *, campaign_id: int, requester_id: int) -> list[CampaignAttachmentRead]:
    _require_campaign_access(db, campaign_id=campaign_id, user_id=requester_id)

    stmt = (
        select(CampaignAttachment)
        .where(CampaignAttachment.campaign_id == campaign_id)
        .order_by(CampaignAttachment.created_at.desc())
    )
    attachments = db.execute(stmt).scalars().all()
    return [CampaignAttachmentRead.model_validate(record, from_attributes=True) for record in attachments]


def create_attachment(
    db: Session,
    *,
    campaign_id: int,
    uploader_id: int,
    upload: AttachmentUpload,
    description: str | None = None,
) -> CampaignAttachmentRead:
    campaign = _require_campaign_access(db, campaign_id=campaign_id, user_id=uploader_id)

    if not upload.filename:
        raise ValueError("Uploaded file must include a filename.")

    settings = get_settings()
    base_dir = settings.attachments_dir
    campaign_dir = base_dir / str(campaign.id)
    campaign_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(upload.filename).name
    extension = Path(upload.filename).suffix
    stored_filename = f"{uuid4().hex}{extension}"
    storage_path = Path(str(campaign.id)) / stored_filename
    destination = base_dir / storage_path

    upload.file.seek(0)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    file_size = destination.stat().st_size
    if file_size == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("Uploaded file is empty.")

    attachment = CampaignAttachment(
        campaign_id=campaign.id,
        uploader_id=uploader_id,
        original_filename=original_name,
        stored_filename=stored_filename,
        storage_path=str(storage_path),
        content_type=upload.content_type or "application/octet-stream",
        file_size=file_size,
        description=description,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return CampaignAttachmentRead.model_validate(attachment, from_attributes=True)


def get_attachment(
    db: Session,
    *,
    campaign_id: int,
    attachment_id: int,
    requester_id: int,
) -> CampaignAttachment:
    _require_campaign_access(db, campaign_id=campaign_id, user_id=requester_id)

    attachment = db.get(CampaignAttachment, attachment_id)
    if attachment is None or attachment.campaign_id != campaign_id:
        raise ValueError("Attachment not found.")
    return attachment


def delete_attachment(
    db: Session,
    *,
    campaign_id: int,
    attachment_id: int,
    requester_id: int,
) -> None:
    attachment = get_attachment(
        db,
        campaign_id=campaign_id,
        attachment_id=attachment_id,
        requester_id=requester_id,
    )

    settings = get_settings()
    file_path = settings.attachments_dir / Path(attachment.storage_path)
    db.delete(attachment)
    db.commit()

    if file_path.exists():
        file_path.unlink()


def resolve_file_path(attachment: CampaignAttachment) -> Path:
    settings = get_settings()
    return settings.attachments_dir / Path(attachment.storage_path)


def _require_campaign_access(db: Session, *, campaign_id: int, user_id: int) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found.")
    if campaign.owner_id == user_id:
        return campaign

    stmt = (
        select(Character.id)
        .where(Character.campaign_id == campaign_id, Character.user_id == user_id)
        .limit(1)
    )
    participant = db.execute(stmt).scalar_one_or_none()
    if participant is None:
        raise ValueError("Campaign not found.")
    return campaign

