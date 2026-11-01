import type { Alert, Overview } from "../types";
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export type EventItem = { id: string; timestamp: string; source: string; event_type: string; severity: number; username?: string; source_ip?: string; message: string };
const authHeaders = (): Record<string, string> => { const token = localStorage.getItem("sentineltrace_token"); return token ? { Authorization: `Bearer ${token}` } : {}; };
async function request(path: string, init?: RequestInit) { const response = await fetch(`${API}${path}`, { ...init, headers: { ...authHeaders(), ...(init?.headers ?? {}) } }); if (!response.ok) throw new Error(response.status === 401 ? "Authentication required" : "Request failed"); return response.json(); }
export async function register(username: string, password: string) { const data = await request("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) }); localStorage.setItem("sentineltrace_token", data.access_token); return data.user; }
export async function login(username: string, password: string) { const data = await request("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) }); localStorage.setItem("sentineltrace_token", data.access_token); return data.user; }
export async function getMe() { return request("/api/auth/me"); }
export async function getOverview(): Promise<Overview> { return request("/api/statistics/overview"); }
export async function getAlerts(): Promise<Alert[]> { return request("/api/alerts"); }
export async function getEvents(params = ""): Promise<{ items: EventItem[]; total: number; page: number; page_size: number }> { return request(`/api/events${params}`); }
