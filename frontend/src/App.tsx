import { useState } from "react";
import { Dashboard } from "./pages/Dashboard";
import { EventsExplorer } from "./pages/EventsExplorer";
import { Login } from "./pages/Login";
import "./styles.css";
export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("sentineltrace_token")));
  if (!authenticated) return <Login onAuthenticated={() => setAuthenticated(true)} />;
  return <><Dashboard /><EventsExplorer /></>;
}
