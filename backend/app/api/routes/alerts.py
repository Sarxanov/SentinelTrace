from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Alert
from ...schemas.alert import AlertRead, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Alert).order_by(Alert.created_at.desc())).all()


@router.get("/statistics")
def alert_statistics(db: Annotated[Session, Depends(get_db)]):
    return dict(db.execute(select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)).all())


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: str, db: Annotated[Session, Depends(get_db)]):
    alert = db.get(Alert, alert_id)
    if not alert: raise HTTPException(404, "alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(alert_id: str, update: AlertUpdate, db: Annotated[Session, Depends(get_db)]):
    if update.status not in {"open", "acknowledged", "resolved"}: raise HTTPException(422, "invalid alert status")
    alert = db.get(Alert, alert_id)
    if not alert: raise HTTPException(404, "alert not found")
    alert.status = update.status; db.commit(); db.refresh(alert)
    return alert
