from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    severity: str
    enabled: bool
    time_window_seconds: int
    updated_at: datetime


class RuleUpdate(BaseModel):
    enabled: bool
    time_window_seconds: int | None = None
