# Detection rules

Implemented rules include multiple failed logins (`AUTH-001`), successful authentication after failures (`AUTH-002`), lockouts (`WIN-001`), privileged activity (`PRIV-001`), account creation (`WIN-002`), group membership change (`WIN-003`), and high-severity Suricata alerts (`NET-001`). Scores are bounded to 0–100 and explain their base, frequency, and correlation contributions.

Rule metadata is seeded by Alembic and stored in `detection_rules`. Administrators can enable/disable rules and change supported time windows through `PATCH /api/rules/{rule_id}`. Disabled rules are not evaluated during ingestion.
