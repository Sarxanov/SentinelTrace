from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...api.dependencies import current_user, require_admin
from ...database import get_db
from ...models import DetectionRule, User
from ...schemas.rule import RuleRead, RuleUpdate

router = APIRouter(prefix="/api/rules", tags=["detection rules"])


@router.get("", response_model=list[RuleRead])
def list_rules(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    return db.scalars(select(DetectionRule).order_by(DetectionRule.id)).all()


@router.patch("/{rule_id}", response_model=RuleRead)
def update_rule(rule_id: str, payload: RuleUpdate, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_admin)]):
    rule = db.get(DetectionRule, rule_id)
    if not rule:
        raise HTTPException(404, "detection rule not found")
    if payload.time_window_seconds is not None:
        if not 30 <= payload.time_window_seconds <= 86400:
            raise HTTPException(422, "time window must be between 30 and 86400 seconds")
        rule.time_window_seconds = payload.time_window_seconds
    rule.enabled = payload.enabled
    db.commit()
    db.refresh(rule)
    return rule
