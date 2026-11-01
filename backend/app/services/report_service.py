import html
import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Alert, Event
from ..services.event_service import overview


def report(db: Session, fmt: str) -> str:
    data = {"created_at": datetime.now(UTC).isoformat(), "overview": overview(db), "alerts": [{"id": a.id, "title": a.title, "severity": a.severity, "risk_score": a.risk_score, "description": a.description, "reasons": a.reasons} for a in db.scalars(select(Alert).order_by(Alert.created_at.desc())).all()], "limitations": ["Synthetic and imported logs are analyzed only; no remediation is performed."]}
    if fmt == "json": return json.dumps(data, indent=2)
    if fmt == "html":
        return f"<html><body><h1>SentinelTrace report</h1><p>Created {html.escape(data['created_at'])}</p><pre>{html.escape(json.dumps(data, indent=2))}</pre></body></html>"
    lines = ["# SentinelTrace report", f"Created: {data['created_at']}", "", "## Overview", f"`{json.dumps(data['overview'])}`", "", "## Alerts"]
    lines += [f"- **{a['severity']}** {a['title']} (risk {a['risk_score']:.0f}): {a['description']}" for a in data["alerts"]]
    lines += ["", "## Limitations", *[f"- {x}" for x in data["limitations"]]]
    return "\n".join(lines)
