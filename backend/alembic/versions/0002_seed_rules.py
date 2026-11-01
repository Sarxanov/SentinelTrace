"""seed detection rule metadata"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, UTC

revision = "0002_seed_rules"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

RULES = [
    ("AUTH-001", "Multiple failed logins", "Repeated failed authentication for an identity or source.", "medium"),
    ("AUTH-002", "Successful login after failures", "Successful authentication following repeated failures.", "high"),
    ("WIN-001", "Account lockout activity", "A Windows account lockout event.", "medium"),
    ("PRIV-001", "Privileged account activity", "Administrative or privilege-related activity.", "medium"),
    ("WIN-002", "Suspicious account creation", "A new account was created.", "medium"),
    ("WIN-003", "Administrative group membership change", "A security group membership was changed.", "high"),
    ("NET-001", "High-severity Suricata alert", "A high-severity network security alert.", "high"),
]


def upgrade() -> None:
    table = sa.table("detection_rules", sa.column("id", sa.String), sa.column("name", sa.String), sa.column("description", sa.Text), sa.column("severity", sa.String), sa.column("enabled", sa.Boolean), sa.column("time_window_seconds", sa.Integer), sa.column("updated_at", sa.DateTime))
    op.bulk_insert(table, [{"id": rid, "name": name, "description": desc, "severity": severity, "enabled": True, "time_window_seconds": 600, "updated_at": datetime.now(UTC)} for rid, name, desc, severity in RULES])


def downgrade() -> None:
    op.execute("DELETE FROM detection_rules")
