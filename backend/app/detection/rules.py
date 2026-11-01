from collections import defaultdict
from datetime import timedelta

from ..models import Event
from .risk_scoring import classify_score, score_alert


def detect(events: list[Event]) -> list[dict]:
    alerts: list[dict] = []
    failed = [e for e in events if e.event_type in {"failed_logon", "failed_ssh_authentication", "invalid_user_attempt", "sudo_auth_failure"}]
    groups: dict[str, list[Event]] = defaultdict(list)
    for event in failed:
        groups[event.username or event.source_ip or "unknown"].append(event)
    for key, items in groups.items():
        items.sort(key=lambda e: e.timestamp)
        window = [e for e in items if items[-1].timestamp - e.timestamp <= timedelta(minutes=10)]
        if len(window) >= 3:
            score, reasons = score_alert(60, len(window))
            alerts.append({"rule_id": "AUTH-001", "title": "Multiple failed logins", "description": f"{len(window)} failures for {key} within 10 minutes.", "severity": classify_score(score), "risk_score": score, "reasons": reasons, "events": window})
    successes = [e for e in events if e.event_type in {"successful_logon", "successful_ssh_authentication"}]
    for success in successes:
        related = [e for e in failed if (success.username and e.username == success.username) or (success.source_ip and e.source_ip == success.source_ip) and e.timestamp <= success.timestamp and success.timestamp - e.timestamp <= timedelta(minutes=15)]
        if len(related) >= 2:
            score, reasons = score_alert(70, len(related), True)
            alerts.append({"rule_id": "AUTH-002", "title": "Successful login after failures", "description": "A successful authentication followed repeated failures.", "severity": classify_score(score), "risk_score": score, "reasons": reasons, "events": related + [success]})
    for event in events:
        rule = None
        if event.event_type == "account_lockout": rule = ("WIN-001", "Account lockout activity", 55)
        elif event.event_type in {"privileged_logon", "sudo_activity"}: rule = ("PRIV-001", "Privileged account activity", 50)
        elif event.event_type == "account_created": rule = ("WIN-002", "Suspicious account creation", 65)
        elif event.event_type in {"global_group_membership_change", "local_group_membership_change"}: rule = ("WIN-003", "Administrative group membership change", 70)
        elif event.event_type == "suricata_alert" and event.severity >= 3: rule = ("NET-001", "High-severity Suricata alert", 80)
        if rule:
            score, reasons = score_alert(rule[2])
            alerts.append({"rule_id": rule[0], "title": rule[1], "description": event.message, "severity": classify_score(score), "risk_score": score, "reasons": reasons, "events": [event]})
    return alerts
