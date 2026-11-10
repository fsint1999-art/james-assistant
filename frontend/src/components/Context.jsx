const fmt = iso => { const d = new Date(iso); return d.toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit" }) + (iso.includes("T") && !iso.endsWith("T00:00:00") ? " " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : ""); };
export default function Context({ wx, cal }) {
  return (<>
    <section className="panel"><h2>CLIMA</h2>
      {!wx || wx.error ? <p className="dim">{wx?.error || "Carregando…"}</p> : <>
        <div className="temp">{Math.round(wx.temp)}°<span>{wx.desc}</span></div>
        <small>Vento {wx.wind} km/h · Umidade {wx.humidity}%</small>
        <small>Hoje {Math.round(wx.days[0].min)}–{Math.round(wx.days[0].max)}° · chuva {wx.days[0].rain}% | Amanhã {Math.round(wx.days[1].min)}–{Math.round(wx.days[1].max)}° · {wx.days[1].rain}%</small></>}
    </section>
    <section className="panel"><h2>AGENDA · 7 DIAS</h2>
      {cal.length ? <ul className="tools">{cal.slice(0, 5).map((e, i) => <li key={i}><span>{e.title}</span><em>{fmt(e.start)}</em></li>)}</ul>
        : <p className="dim">Nada agendado. Diga “James, marque dentista amanhã às 10h”.</p>}
    </section></>);
}
