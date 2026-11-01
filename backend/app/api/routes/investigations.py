from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Event, Investigation, User
from ...api.dependencies import current_user
from ...services.correlation_service import build_timeline
from ...schemas.investigation import InvestigationCreate, InvestigationRead

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.get("", response_model=list[InvestigationRead])
def list_investigations(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    return db.scalars(select(Investigation).order_by(Investigation.created_at.desc())).all()


@router.post("", response_model=InvestigationRead, status_code=201)
def create_investigation(payload: InvestigationCreate, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    item = Investigation(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item


@router.get("/{investigation_id}", response_model=InvestigationRead)
def get_investigation(investigation_id: str, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    item = db.get(Investigation, investigation_id)
    if not item: raise HTTPException(404, "investigation not found")
    return item


@router.get("/{investigation_id}/timeline")
def investigation_timeline(investigation_id: str, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    item = db.get(Investigation, investigation_id)
    if not item:
        raise HTTPException(404, "investigation not found")
    events = db.scalars(select(Event).where(Event.id.in_(item.event_ids)).order_by(Event.timestamp)).all() if item.event_ids else []
    return {"investigation_id": item.id, "title": item.title, "status": item.status, "timeline": build_timeline(events)}
