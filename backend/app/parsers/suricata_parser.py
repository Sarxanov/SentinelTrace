from typing import Any

from .base import NormalizedEvent


def parse_suricata(record: dict[str, Any]) -> NormalizedEvent:
    event_type = str(record.get("event_type") or "unknown")
    alert = record.get("alert") or {}
    severity = float(alert.get("severity", 0) or 0) if event_type == "alert" else 0
    message = alert.get("signature") if event_type == "alert" else f"Suricata {event_type} event"
    metadata = {
        "src_port": record.get("src_port"), "dest_port": record.get("dest_port"),
        "proto": record.get("proto"), "signature_id": alert.get("signature_id"),
        "dns_query": (record.get("dns") or {}).get("rrname"),
        "http_hostname": (record.get("http") or {}).get("hostname"),
        "tls_sni": (record.get("tls") or {}).get("sni"),
    }
    return NormalizedEvent(
        timestamp=record.get("timestamp"), source="suricata", event_type=f"suricata_{event_type}",
        source_ip=record.get("src_ip"), destination_ip=record.get("dest_ip"), message=message,
        event_id=str(alert.get("signature_id")) if alert.get("signature_id") is not None else None,
        severity=severity, raw_data=record, metadata=metadata,
    )
