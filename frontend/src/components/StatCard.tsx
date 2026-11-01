export function StatCard({ label, value, tone = "" }: { label: string; value: number; tone?: string }) {
  return <div className={`card ${tone}`}><span>{label}</span><strong>{value.toLocaleString()}</strong></div>;
}
