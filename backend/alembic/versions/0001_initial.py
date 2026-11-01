"""initial SentinelTrace schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("hostname", sa.String(255)), sa.Column("source_ip", sa.String(64)),
        sa.Column("destination_ip", sa.String(64)), sa.Column("username", sa.String(255)),
        sa.Column("event_type", sa.String(64), nullable=False), sa.Column("event_id", sa.String(64)),
        sa.Column("severity", sa.Float(), nullable=False, server_default="0"), sa.Column("message", sa.Text(), nullable=False),
        sa.Column("raw_data", sa.JSON(), nullable=False), sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("deduplication_key", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_dedup", "events", ["deduplication_key"], unique=True)
    op.create_index("ix_events_timestamp", "events", ["timestamp"])
    op.create_index("ix_events_source_type", "events", ["source", "event_type"])
    op.create_index("ix_events_source", "events", ["source"]); op.create_index("ix_events_source_ip", "events", ["source_ip"])
    op.create_index("ix_events_username", "events", ["username"]); op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_table("alerts",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("rule_id", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False), sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False), sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_status_severity", "alerts", ["status", "severity"]); op.create_index("ix_alerts_rule_id", "alerts", ["rule_id"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"]); op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_table("alert_events", sa.Column("alert_id", sa.String(36), sa.ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True), sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("investigations",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("event_ids", sa.JSON(), nullable=False), sa.Column("alert_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("users",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)))
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_table("detection_rules",
        sa.Column("id", sa.String(64), primary_key=True), sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False), sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("time_window_seconds", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    for table in ("detection_rules", "users", "investigations", "alert_events", "alerts", "events"):
        op.drop_table(table)
