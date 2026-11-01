from app.parsers.linux_parser import parse_linux
from app.parsers.suricata_parser import parse_suricata
from app.parsers.windows_parser import parse_windows


def test_windows_parser():
    event = parse_windows({"timestamp": "2025-01-01T00:00:00Z", "event_id": 4625, "event_data": {"TargetUserName": "alice", "IpAddress": "10.0.0.2"}})
    assert event.event_type == "failed_logon" and event.username == "alice"


def test_linux_parser():
    event = parse_linux("Jan 01 10:00:00 host sshd[1]: Failed password for alice from 10.0.0.2 port 22 ssh2", 2025)
    assert event.event_type == "failed_ssh_authentication" and event.source_ip == "10.0.0.2"


def test_suricata_parser():
    event = parse_suricata({"timestamp": "2025-01-01T00:00:00Z", "event_type": "alert", "src_ip": "1.1.1.1", "alert": {"signature": "Test", "severity": 3, "signature_id": 1}})
    assert event.event_type == "suricata_alert" and event.severity == 3
