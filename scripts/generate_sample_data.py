from pathlib import Path
import json


def main() -> None:
    target = Path(__file__).parents[1] / "datasets" / "generated"
    target.mkdir(exist_ok=True)
    records = [{"timestamp": "2025-01-15T10:%02d:00Z" % minute, "event_id": 4625, "event_data": {"TargetUserName": "student", "IpAddress": "192.0.2.10"}} for minute in range(5)]
    (target / "windows.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} reproducible synthetic records to {target}")


if __name__ == "__main__":
    main()
