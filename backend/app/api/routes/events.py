import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...api.dependencies import current_user
from ...config import get_settings
from ...database import get_db
from ...models import Event, User
from ...parsers.json_parser import parse_json_record
from ...parsers.linux_parser import parse_linux
from ...schemas.event import EventRead, IngestResponse, PaginatedEvents
from ...services.event_service import ingest

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=PaginatedEvents)
def list_events(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)], page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), source: str | None = None, event_type: str | None = None, severity: float | None = Query(None, ge=0, le=100), query_text: str | None = Query(None, alias="q", max_length=255), username: str | None = None, source_ip: str | None = None, hostname: str | None = None, event_id: str | None = None, date_from: datetime | None = None, date_to: datetime | None = None):
    query = select(Event)
    count = select(func.count(Event.id))
    for field, value in ((Event.source, source), (Event.event_type, event_type), (Event.severity, severity), (Event.username, username), (Event.source_ip, source_ip), (Event.hostname, hostname), (Event.event_id, event_id)):
        if value is not None:
            query = query.where(field == value); count = count.where(field == value)
    if query_text:
        pattern = f"%{query_text}%"
        clause = Event.message.ilike(pattern)
        query = query.where(clause); count = count.where(clause)
    if date_from:
        query = query.where(Event.timestamp >= date_from); count = count.where(Event.timestamp >= date_from)
    if date_to:
        query = query.where(Event.timestamp <= date_to); count = count.where(Event.timestamp <= date_to)
    total = db.scalar(count) or 0
    items = db.scalars(query.order_by(Event.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)], file: UploadFile = File(...), source: str = Query("json")):
    if source not in {"json", "windows", "suricata", "linux"}:
        raise HTTPException(422, "unsupported source format")
    normalized = []
    errors = []
    size = 0
    pending = b""
    line_no = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > get_settings().max_upload_bytes:
            raise HTTPException(413, "file exceeds configured upload limit")
        pending += chunk
        lines = pending.split(b"\n")
        pending = lines.pop()
        for raw_line in lines:
            line_no += 1
            line = raw_line.decode("utf-8", errors="replace")
            if not line.strip():
                continue
            try:
                if source == "linux":
                    normalized.append(parse_linux(line))
                else:
                    normalized.append(parse_json_record(json.loads(line), source))
            except Exception as exc:
                errors.append(f"line {line_no}: {exc}")
    if pending.strip():
        line_no += 1
        line = pending.decode("utf-8", errors="replace")
        if line.strip():
            try:
                if source == "linux":
                    normalized.append(parse_linux(line))
                else:
                    normalized.append(parse_json_record(json.loads(line), source))
            except Exception as exc:
                errors.append(f"line {line_no}: {exc}")
    result = ingest(db, normalized)
    result["errors"].extend(errors); result["rejected"] += len(errors)
    return result


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: str, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(current_user)]):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "event not found")
    return event
