from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    timestamp: datetime
    source: str
    hostname: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    event_type: str
    event_id: str | None = None
    severity: float
    message: str
    raw_data: dict[str, Any] = Field(default_factory=dict)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    accepted: int
    rejected: int
    duplicates: int
    alerts_created: int
    errors: list[str] = Field(default_factory=list)


class PaginatedEvents(BaseModel):
    items: list[EventRead]
    total: int
    page: int
    page_size: int
