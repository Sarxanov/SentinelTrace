from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Event
from ...services.event_service import overview

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/overview")
def statistics_overview(db: Annotated[Session, Depends(get_db)]):
    return overview(db)


@router.get("/severity")
def severity(db: Annotated[Session, Depends(get_db)]):
    return dict(db.execute(select(Event.severity, func.count(Event.id)).group_by(Event.severity)).all())


@router.get("/timeline")
def timeline(db: Annotated[Session, Depends(get_db)]):
    rows = db.execute(select(func.date(Event.timestamp), func.count(Event.id)).group_by(func.date(Event.timestamp)).order_by(func.date(Event.timestamp))).all()
    return [{"date": date, "count": count} for date, count in rows]
