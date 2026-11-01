import type { Alert, Overview } from "../types";
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export async function getOverview(): Promise<Overview> { const response = await fetch(`${API}/api/statistics/overview`); if (!response.ok) throw new Error("Unable to load overview"); return response.json(); }
export async function getAlerts(): Promise<Alert[]> { const response = await fetch(`${API}/api/alerts`); if (!response.ok) throw new Error("Unable to load alerts"); return response.json(); }
