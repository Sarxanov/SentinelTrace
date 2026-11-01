import hashlib
import json
from datetime import UTC, datetime
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..detection.rules import detect
from ..models import Alert, AlertEvent, Event
from ..parsers.base import NormalizedEvent


def _dedup(event: NormalizedEvent) -> str:
    payload = json.dumps({"timestamp": event.timestamp.isoformat(), "source": event.source, "type": event.event_type, "message": event.message, "raw": event.raw_data}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def ingest(db: Session, normalized: Iterable[NormalizedEvent]) -> dict:
    accepted = duplicates = 0
    errors: list[str] = []
    inserted: list[Event] = []
    for item in normalized:
        try:
            key = _dedup(item)
            if db.scalar(select(Event).where(Event.deduplication_key == key)):
                duplicates += 1
                continue
            event = Event(timestamp=item.timestamp, source=item.source, hostname=item.hostname, source_ip=item.source_ip, destination_ip=item.destination_ip, username=item.username, event_type=item.event_type, event_id=item.event_id, severity=item.severity, message=item.message, raw_data=item.raw_data, metadata_json=item.metadata, deduplication_key=key)
            db.add(event)
            inserted.append(event)
            accepted += 1
        except Exception as exc:
            errors.append(str(exc))
    db.flush()
    generated = 0
    for result in detect(inserted):
        alert = Alert(rule_id=result["rule_id"], title=result["title"], description=result["description"], severity=result["severity"], risk_score=result["risk_score"], reasons=result["reasons"])
        db.add(alert)
        db.flush()
        for event in result["events"]:
            db.add(AlertEvent(alert_id=alert.id, event_id=event.id))
        generated += 1
    db.commit()
    return {"accepted": accepted, "rejected": len(errors), "duplicates": duplicates, "alerts_created": generated, "errors": errors}


def overview(db: Session) -> dict:
    return {
        "total_events": db.scalar(select(func.count(Event.id))) or 0,
        "total_alerts": db.scalar(select(func.count(Alert.id))) or 0,
        "critical_alerts": db.scalar(select(func.count(Alert.id)).where(Alert.severity == "critical")) or 0,
        "high_alerts": db.scalar(select(func.count(Alert.id)).where(Alert.severity == "high")) or 0,
        "sources": dict(db.execute(select(Event.source, func.count(Event.id)).group_by(Event.source)).all()),
    }
