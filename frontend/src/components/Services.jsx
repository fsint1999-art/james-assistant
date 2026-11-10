const N = [["ollama", "IA local"], ["web", "Web"], ["calendar", "Agenda"], ["weather", "Clima"], ["files", "Arquivos"], ["hypr", "Hyprland"], ["voice", "Voz"], ["umbrel", "Umbrel"]];
export default function Services({ ok = {}, active }) {
  return (
    <section className="panel"><h2>SERVIÇOS EM EXECUÇÃO</h2>
      <svg className="svc" viewBox="0 0 260 220" role="img" aria-label="Serviços do JAMES">
        <circle cx="130" cy="110" r="78" className="orbit" />
        {N.map(([id, label], i) => {
          const a = (i / N.length) * 2 * Math.PI - Math.PI / 2, x = 130 + 78 * Math.cos(a), y = 110 + 78 * Math.sin(a);
          const c = active.has(id) ? "active" : ok[id] ? "ok" : "off";
          return <g key={id} className={`node ${c}`}><line x1="130" y1="110" x2={x} y2={y} /><circle cx={x} cy={y} r="9" />
            <text x={x} y={y + (y > 110 ? 24 : -15)} textAnchor="middle">{label}</text></g>;
        })}
        <circle cx="130" cy="110" r="16" className="hub" /><text x="130" y="115" textAnchor="middle" className="hubt">J</text>
      </svg>
    </section>);
}
