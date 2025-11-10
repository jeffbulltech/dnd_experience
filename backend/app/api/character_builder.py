from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path as FilePath

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas.character_builder import (
    CharacterDraftCreate,
    CharacterDraftRead,
    CharacterDraftStepUpdate,
    CharacterDraftSummary,
)
from ..services import character_builder_service, pdf_service
from ..services.character_builder_rules import AbilityScoreValidationError
from ..models import Character

router = APIRouter(prefix="/builder", tags=["character-builder"])


@router.get("/drafts", response_model=Sequence[CharacterDraftSummary])
def list_drafts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[CharacterDraftSummary]:
    return character_builder_service.list_drafts(db, user_id=current_user.id)


@router.post("/drafts", response_model=CharacterDraftRead, status_code=status.HTTP_201_CREATED)
def create_draft(
    payload: CharacterDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CharacterDraftRead:
    return character_builder_service.create_draft(db, user_id=current_user.id, payload=payload)


@router.get("/drafts/{draft_id}", response_model=CharacterDraftRead)
def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CharacterDraftRead:
    try:
        return character_builder_service.fetch_draft(db, user_id=current_user.id, draft_id=draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/drafts/{draft_id}/steps/{step}", response_model=CharacterDraftRead)
def update_step(
    draft_id: int,
    step: str = PathParam(..., min_length=1, max_length=50),
    update: CharacterDraftStepUpdate | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CharacterDraftRead:
    try:
        return character_builder_service.update_step(
            db,
            user_id=current_user.id,
            draft_id=draft_id,
            step=step,
            update=update or CharacterDraftStepUpdate(),
        )
    except AbilityScoreValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete(
    "/drafts/{draft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
def delete_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        character_builder_service.delete_draft(db, user_id=current_user.id, draft_id=draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/drafts/{draft_id}/finalize", response_model=CharacterDraftRead)
def finalize_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CharacterDraftRead:
    try:
        return character_builder_service.finalize_draft(db, user_id=current_user.id, draft_id=draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/drafts/{draft_id}/export", response_class=FileResponse)
def export_draft_pdf(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    try:
        draft = character_builder_service.fetch_draft(db, user_id=current_user.id, draft_id=draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if draft.character_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Draft must be finalized before export.")

    settings = get_settings()
    template_path = FilePath(settings.vector_store_path).parents[0] / "templates" / "5E_CharacterSheet_Fillable.pdf"
    output_dir = FilePath(settings.vector_store_path) / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    export_info = draft.step_data.get("export") if isinstance(draft.step_data, dict) else None
    if export_info and FilePath(export_info.get("pdf_path", "")).exists():
        return FileResponse(export_info["pdf_path"], filename=f"character_{draft.character_id}.pdf")

    if not template_path.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF template is not available.")

    character = db.get(Character, draft.character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found.")

    pdf_path = output_dir / f"character_{character.id}.pdf"
    pdf_service.fill_character_sheet(template_path, pdf_path, character, draft)

    draft.step_data = {**draft.step_data, "export": {"pdf_path": str(pdf_path)}}
    db.add(draft)
    db.commit()

    return FileResponse(pdf_path, filename=f"character_{character.id}.pdf")

