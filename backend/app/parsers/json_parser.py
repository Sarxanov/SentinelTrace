from typing import Any

from .base import NormalizedEvent
from .suricata_parser import parse_suricata
from .windows_parser import parse_windows


def parse_json_record(record: dict[str, Any], source: str) -> NormalizedEvent:
    if source == "windows":
        return parse_windows(record)
    if source == "suricata":
        return parse_suricata(record)
    return NormalizedEvent(
        timestamp=record.get("timestamp") or record.get("@timestamp"),
        source=source,
        event_type=str(record.get("event_type") or record.get("type") or "generic_event"),
        hostname=record.get("hostname") or record.get("host"),
        source_ip=record.get("source_ip") or record.get("src_ip"),
        destination_ip=record.get("destination_ip") or record.get("dest_ip"),
        username=record.get("username") or record.get("user"),
        event_id=str(record.get("event_id")) if record.get("event_id") is not None else None,
        severity=float(record.get("severity", 0) or 0),
        message=record.get("message") or record.get("event_type") or "generic event",
        raw_data=record,
    )
