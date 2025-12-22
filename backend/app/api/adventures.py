from typing import Sequence

from fastapi import APIRouter

from ..services import adventure_service

router = APIRouter(prefix="/adventures", tags=["adventures"])


@router.get("")
def list_adventures() -> Sequence[dict]:
    """List all available adventure templates."""
    templates = adventure_service.list_adventure_templates()
    return [template.to_dict() for template in templates]
