export default function StateBadge({ state }) {
  const cls = state ? `state-badge ${state}` : 'state-badge UNKNOWN'
  return <span className={cls}>{state || 'UNKNOWN'}</span>
}
