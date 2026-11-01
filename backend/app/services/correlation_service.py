from collections import defaultdict
from datetime import timedelta

from ..models import Event


def build_timeline(events: list[Event], window_seconds: int = 900) -> list[dict]:
    groups: dict[str, list[Event]] = defaultdict(list)
    for event in events:
        key = event.username or event.source_ip or event.hostname or "unattributed"
        groups[key].append(event)
    timeline = []
    for identity, related in groups.items():
        related.sort(key=lambda event: event.timestamp)
        sequence = []
        previous = None
        for event in related:
            if previous and event.timestamp - previous > timedelta(seconds=window_seconds):
                timeline.append({"identity": identity, "events": sequence})
                sequence = []
            sequence.append({"id": event.id, "timestamp": event.timestamp, "event_type": event.event_type, "message": event.message, "source_ip": event.source_ip, "username": event.username})
            previous = event.timestamp
        if sequence:
            timeline.append({"identity": identity, "events": sequence})
    return sorted(timeline, key=lambda group: group["events"][0]["timestamp"])
