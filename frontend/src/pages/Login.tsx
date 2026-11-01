import { useState } from "react";
import type { FormEvent } from "react";
import { login, register } from "../services/api";

export function Login({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [username, setUsername] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [first, setFirst] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); setError(""); try { if (first) await register(username, password); else await login(username, password); onAuthenticated(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Authentication failed"); } }
  return <main className="auth"><p className="eyebrow">SENTINELTRACE / LOCAL ANALYST ACCESS</p><h1>{first ? "Create administrator" : "Sign in"}</h1><p className="muted">{first ? "The first account is provisioned as the local administrator." : "Use your local SentinelTrace analyst account."}</p><form onSubmit={submit}><input required minLength={1} placeholder="Username" value={username} onChange={event => setUsername(event.target.value)} /><input required minLength={12} type="password" placeholder="Password (12+ characters)" value={password} onChange={event => setPassword(event.target.value)} /><button type="submit">{first ? "Create account" : "Sign in"}</button></form>{error && <p className="error">{error}</p>}<button className="link" onClick={() => setFirst(!first)}>{first ? "Existing account? Sign in" : "First run? Create administrator"}</button></main>;
}
