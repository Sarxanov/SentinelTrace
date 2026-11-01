import re
from datetime import UTC, datetime

from .base import NormalizedEvent

AUTH_RE = re.compile(r"^(?P<stamp>\w{3}\s+\d+\s+\d\d:\d\d:\d\d)\s+(?P<host>\S+)\s+(?P<message>.*)$")
USER_RE = re.compile(r"(?:for (?:invalid user )?|user=)(?P<user>[\w.@+-]+)")
IP_RE = re.compile(r"(?:from\s+|rhost=)(?P<ip>\d{1,3}(?:\.\d{1,3}){3})")


def parse_linux(line: str, year: int | None = None) -> NormalizedEvent:
    match = AUTH_RE.match(line.strip())
    if not match:
        raise ValueError("unrecognized Linux authentication log format")
    year = year or datetime.now(UTC).year
    stamp = datetime.strptime(f"{year} {match.group('stamp')}", "%Y %b %d %H:%M:%S").replace(tzinfo=UTC)
    message = match.group("message")
    lower = message.lower()
    if "authentication failure" in lower or "failed password" in lower:
        event_type = "sudo_auth_failure" if "sudo" in lower else "failed_ssh_authentication"
        severity = 35
    elif "accepted " in lower:
        event_type, severity = "successful_ssh_authentication", 10
    elif "invalid user" in lower:
        event_type, severity = "invalid_user_attempt", 40
    elif "session opened" in lower:
        event_type, severity = "session_opened", 5
    elif "session closed" in lower:
        event_type, severity = "session_closed", 5
    elif "sudo" in lower:
        event_type, severity = "sudo_activity", 15
    else:
        event_type, severity = "linux_authentication_event", 0
    user_match = USER_RE.search(message)
    ip_match = IP_RE.search(message)
    return NormalizedEvent(
        timestamp=stamp, source="linux", event_type=event_type, username=user_match.group("user") if user_match else None,
        source_ip=ip_match.group("ip") if ip_match else None, hostname=match.group("host"),
        message=message, severity=severity, raw_data={"line": line},
    )
