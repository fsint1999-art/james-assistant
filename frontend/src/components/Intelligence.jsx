export default function Intelligence({ steps, busy }) {
  const phase = busy ? "reason" : steps.length ? "respond" : "idle";
  return (
    <section className="panel"><h2>INTELLIGENCE / ACTIVE PROCESS</h2>
      <div className="orr">{["observe", "reason", "respond"].map(p => <span key={p} className={p === phase ? "on" : ""}>{p}</span>)}</div>
      <ul className="tools">{steps.filter(s => s.tool).map((s, i) => <li key={i}><code>{s.tool}</code><em className={s.status}>{s.status}</em></li>)}</ul>
      {!steps.length && !busy && <p className="dim">Aguardando comando.</p>}
    </section>);
}
