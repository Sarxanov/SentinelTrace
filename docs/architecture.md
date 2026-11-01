# Architecture

SentinelTrace uses source-specific parsers that emit `NormalizedEvent` values. `event_service.ingest` deduplicates and persists events, then runs enabled persisted detection rules against the newly accepted batch. Alerts link back to source events through `alert_events`.

Alembic owns the schema lifecycle. The authentication layer provisions exactly one first-run administrator, creates later analyst accounts through an administrator, and validates signed bearer or HttpOnly cookie sessions. FastAPI applies trusted-host/security-header middleware and the React client consumes authenticated overview, alert, rules, and Events Explorer responses.
