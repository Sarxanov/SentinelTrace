from datetime import UTC, datetime


def parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, (int, float)):
        result = datetime.fromtimestamp(value, tz=UTC)
    elif isinstance(value, str):
        text = value.strip().replace("Z", "+00:00")
        result = datetime.fromisoformat(text)
    else:
        raise ValueError("timestamp is required and must be ISO-8601 or epoch seconds")
    if result.tzinfo is None:
        result = result.replace(tzinfo=UTC)
    return result.astimezone(UTC)
