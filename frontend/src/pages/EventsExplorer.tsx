import { useEffect, useState } from "react";
import { getEvents, type EventItem } from "../services/api";

export function EventsExplorer() {
  const [events, setEvents] = useState<EventItem[]>([]); const [query, setQuery] = useState(""); const [page, setPage] = useState(1); const [total, setTotal] = useState(0);
  useEffect(() => { getEvents(`?page=${page}&page_size=20&q=${encodeURIComponent(query)}`).then(data => { setEvents(data.items); setTotal(data.total); }).catch(() => undefined); }, [page, query]);
  return <section className="panel explorer"><h2>Events explorer</h2><input placeholder="Search event messages" value={query} onChange={event => { setPage(1); setQuery(event.target.value); }} /><div className="table">{events.map(event => <div className="event-row" key={event.id}><time>{new Date(event.timestamp).toLocaleString()}</time><b>{event.event_type}</b><span>{event.username ?? event.source_ip ?? "unattributed"}</span><small>{event.message}</small></div>)}</div><div className="pager"><button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><span>Page {page} · {total} events</span><button disabled={page * 20 >= total} onClick={() => setPage(page + 1)}>Next</button></div></section>;
}
