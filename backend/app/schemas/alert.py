from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    rule_id: str
    title: str
    description: str
    severity: str
    risk_score: float
    status: str
    reasons: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AlertUpdate(BaseModel):
    status: str
