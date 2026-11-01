import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Event
from ...parsers.json_parser import parse_json_record
from ...parsers.linux_parser import parse_linux
from ...schemas.event import EventRead, IngestResponse, PaginatedEvents
from ...services.event_service import ingest

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=PaginatedEvents)
def list_events(db: Annotated[Session, Depends(get_db)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), source: str | None = None, event_type: str | None = None, severity: float | None = None):
    query = select(Event)
    count = select(func.count(Event.id))
    for field, value in ((Event.source, source), (Event.event_type, event_type), (Event.severity, severity)):
        if value is not None:
            query = query.where(field == value); count = count.where(field == value)
    total = db.scalar(count) or 0
    items = db.scalars(query.order_by(Event.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(db: Annotated[Session, Depends(get_db)], file: UploadFile = File(...), source: str = Query("json")):
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024: raise HTTPException(413, "file exceeds 10 MiB limit")
    normalized = []
    errors = []
    for line_no, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
        if not line.strip(): continue
        try:
            if source == "linux": normalized.append(parse_linux(line))
            else: normalized.append(parse_json_record(json.loads(line), source))
        except Exception as exc:
            errors.append(f"line {line_no}: {exc}")
    result = ingest(db, normalized)
    result["errors"].extend(errors); result["rejected"] += len(errors)
    return result


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: str, db: Annotated[Session, Depends(get_db)]):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "event not found")
    return event
