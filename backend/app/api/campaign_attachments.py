from __future__ import annotations

from collections.abc import Sequence

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path as PathParam,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas.attachments import CampaignAttachmentRead, CampaignAttachmentResponse
from ..services import attachment_service

router = APIRouter(prefix="/campaigns/{campaign_id}/attachments", tags=["campaign-attachments"])


@router.get("", response_model=Sequence[CampaignAttachmentResponse])
def list_campaign_attachments(
    request: Request,
    campaign_id: int = PathParam(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[CampaignAttachmentResponse]:
    try:
        attachments = attachment_service.list_attachments(
            db,
            campaign_id=campaign_id,
            requester_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [_add_download_url(request, campaign_id, attachment) for attachment in attachments]


@router.post("", response_model=CampaignAttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_campaign_attachment(
    request: Request,
    campaign_id: int = PathParam(..., gt=0),
    description: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CampaignAttachmentResponse:
    attachment_upload = attachment_service.AttachmentUpload(
        filename=file.filename or "",
        content_type=file.content_type,
        file=file.file,
    )
    try:
        record = attachment_service.create_attachment(
            db,
            campaign_id=campaign_id,
            uploader_id=current_user.id,
            upload=attachment_upload,
            description=description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _add_download_url(request, campaign_id, record)


@router.get(
    "/{attachment_id}/download",
    name="download_campaign_attachment",
)
def download_campaign_attachment(
    campaign_id: int = PathParam(..., gt=0),
    attachment_id: int = PathParam(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    try:
        attachment = attachment_service.get_attachment(
            db,
            campaign_id=campaign_id,
            attachment_id=attachment_id,
            requester_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    file_path = attachment_service.resolve_file_path(attachment)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment content is missing.")

    return FileResponse(
        file_path,
        media_type=attachment.content_type,
        filename=attachment.original_filename,
    )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_campaign_attachment(
    campaign_id: int = PathParam(..., gt=0),
    attachment_id: int = PathParam(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        attachment_service.delete_attachment(
            db,
            campaign_id=campaign_id,
            attachment_id=attachment_id,
            requester_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _add_download_url(
    request: Request | None,
    campaign_id: int,
    attachment: CampaignAttachmentRead,
) -> CampaignAttachmentResponse:
    if request is None:
        return attachment

    download_url = request.url_for(
        "download_campaign_attachment",
        campaign_id=campaign_id,
        attachment_id=attachment.id,
    )
    data = attachment.model_dump()
    data["download_url"] = str(download_url)
    return CampaignAttachmentResponse.model_validate(data)

