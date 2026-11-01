import { useEffect, useState } from "react";
import { Activity, ShieldAlert, Server, TriangleAlert } from "lucide-react";
import { StatCard } from "../components/StatCard";
import { getAlerts, getOverview } from "../services/api";
import type { Alert, Overview } from "../types";

export function Dashboard() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([getOverview(), getAlerts()]).then(([o, a]) => { setOverview(o); setAlerts(a); }).catch((e) => setError(e.message)); }, []);
  if (error) return <div className="error">{error}. Start the FastAPI backend on port 8000.</div>;
  if (!overview) return <div className="loading">Loading telemetry…</div>;
  return <main>
    <header><div><p className="eyebrow">SENTINELTRACE / SECURITY OPERATIONS</p><h1>Overview</h1></div><div className="status"><span /> API ONLINE</div></header>
    <section className="stats"><StatCard label="Total events" value={overview.total_events}/><StatCard label="Total alerts" value={overview.total_alerts} tone="amber"/><StatCard label="Critical alerts" value={overview.critical_alerts} tone="red"/><StatCard label="High severity" value={overview.high_alerts} tone="orange"/></section>
    <section className="grid"><div className="panel"><h2><Activity size={18}/> Event sources</h2>{Object.entries(overview.sources).map(([source, count]) => <div className="bar-row" key={source}><span>{source}</span><b>{count}</b><div className="bar"><i style={{width: `${Math.min(100, count / Math.max(1, overview.total_events) * 100)}%`}} /></div></div>)}</div>
    <div className="panel"><h2><ShieldAlert size={18}/> Recent detections</h2>{alerts.slice(0, 6).map(alert => <div className="alert" key={alert.id}><span className={`dot ${alert.severity}`}/><div><b>{alert.title}</b><small>{alert.description}</small></div><strong>{alert.risk_score.toFixed(0)}</strong></div>)}{alerts.length === 0 && <p className="muted">No detections yet. Ingest a dataset to begin analysis.</p>}</div></section>
    <section className="notice"><Server size={20}/><div><b>Defensive analysis environment</b><p>SentinelTrace analyzes imported telemetry and never executes remediation actions against monitored hosts.</p></div><TriangleAlert size={20}/></section>
  </main>;
}
