# Architecture

SentinelTrace uses source-specific parsers that emit `NormalizedEvent` values. `event_service.ingest` deduplicates and persists events, then runs the detection rules against the newly accepted batch. Alerts link back to source events through `alert_events`. FastAPI provides the API and the React client consumes overview and alert responses.
