from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InvestigationCreate(BaseModel):
    title: str
    notes: str = ""
    event_ids: list[str] = Field(default_factory=list)
    alert_ids: list[str] = Field(default_factory=list)


class InvestigationRead(InvestigationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
