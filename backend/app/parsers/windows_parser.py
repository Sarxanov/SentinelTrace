from typing import Any

from .base import NormalizedEvent

WINDOWS_TYPES = {
    "4624": "successful_logon", "4625": "failed_logon", "4634": "logoff",
    "4648": "explicit_credential_logon", "4672": "privileged_logon",
    "4688": "process_creation", "4720": "account_created",
    "4728": "global_group_membership_change", "4732": "local_group_membership_change",
    "4740": "account_lockout",
}


def parse_windows(record: dict[str, Any]) -> NormalizedEvent:
    event_id = str(record.get("event_id") or record.get("EventID") or record.get("event", {}).get("id") or "")
    data = record.get("event_data") or record.get("EventData") or record.get("data") or {}
    if not isinstance(data, dict):
        data = {}
    username = data.get("TargetUserName") or data.get("SubjectUserName") or record.get("username")
    hostname = record.get("hostname") or record.get("Computer") or record.get("computer")
    return NormalizedEvent(
        timestamp=record.get("timestamp") or record.get("TimeCreated") or record.get("@timestamp"),
        source="windows",
        event_type=WINDOWS_TYPES.get(event_id, "windows_security_event"),
        event_id=event_id or None,
        hostname=hostname,
        username=username,
        source_ip=data.get("IpAddress") or data.get("SourceNetworkAddress") or record.get("source_ip"),
        message=record.get("message") or f"Windows Security Event {event_id}",
        severity=float(record.get("severity", 0) or 0),
        raw_data=record,
        metadata={"logon_type": data.get("LogonType"), "process_name": data.get("NewProcessName")},
    )
