from dataclasses import dataclass, field
from typing import Any

from ..utils.timestamps import parse_timestamp


@dataclass
class NormalizedEvent:
    timestamp: object
    source: str
    event_type: str
    message: str
    hostname: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    username: str | None = None
    event_id: str | None = None
    severity: float = 0
    raw_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.timestamp = parse_timestamp(self.timestamp)
        self.message = str(self.message or self.event_type)
