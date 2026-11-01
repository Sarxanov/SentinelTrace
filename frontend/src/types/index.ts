export type Overview = { total_events: number; total_alerts: number; critical_alerts: number; high_alerts: number; sources: Record<string, number> };
export type Alert = { id: string; rule_id: string; title: string; description: string; severity: string; risk_score: number; status: string; reasons: string[]; created_at: string };
