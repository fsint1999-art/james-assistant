const Bar = ({ label, v, extra }) => (
  <div className="row"><div className="rl"><span>{label}</span><b>{v == null ? "N/A" : `${v.toFixed(1)}%`}</b></div>
    <div className="bar"><i style={{ width: `${v || 0}%`, background: v > 85 ? "var(--alert)" : "var(--cyan)" }} /></div>{extra && <small>{extra}</small>}</div>);
export default function Telemetry({ m }) {
  if (!m) return <section className="panel"><h2>SYSTEM / TELEMETRY</h2><p className="dim">Sem conexão com o backend.</p></section>;
  const g = m.gpu;
  return (
    <section className="panel"><h2>SYSTEM / TELEMETRY</h2>
      <Bar label={`CPU · ${m.cores} núcleos`} v={m.cpu} extra={m.cpu_temp != null ? `${m.cpu_temp.toFixed(0)} °C` : "temp. indisponível"} />
      <Bar label={`RAM · ${m.ram_gb.toFixed(0)} GB`} v={m.ram} />
      <Bar label="GPU" v={g?.load} extra={g ? `VRAM ${g.vram_used.toFixed(1)}/${g.vram_total.toFixed(1)} GB${g.temp ? ` · ${g.temp} °C` : ""}` : "GPU não detectada"} />
      <Bar label="DISCO /" v={m.disk} extra={`${m.disk_free_gb.toFixed(0)} GB livres`} />
      <div className="kv"><span>REDE</span><b className={m.online ? "ok" : "bad"}>{m.online ? "ONLINE" : "OFFLINE"}</b></div>
    </section>);
}
