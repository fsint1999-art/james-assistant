import { useEffect, useState } from "react";
export const api = (u, o) => fetch(u, o).then(r => r.json());
export const post = (u, b = {}) => api(u, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) });
const del = u => api(u, { method: "DELETE" });
export const uploadFile = f => f ? api(`/api/upload?name=${encodeURIComponent(f.name)}`, { method: "POST", body: f }) : Promise.resolve({});

export function Rail({ stream, setStream, mode, setMode }) {
  return (<section className="panel"><h2>STREAMS</h2>
    <div className="seg">{["General", "BrainDump", "Research"].map(s => <button key={s} className={s === stream ? "on2" : ""} onClick={() => setStream(s)}>{s}</button>)}</div>
    <h2 style={{ marginTop: 14 }}>MODOS</h2>
    <div className="seg">{[["voice", "Voz"], ["text", "Texto"], ["auto", "Auto"]].map(([k, l]) => <button key={k} className={k === mode ? "on2" : ""} onClick={() => setMode(k)}>{l}</button>)}</div>
    <small>{{ voice: "Escuta e fala as respostas", text: "Microfone pausado", auto: "Escuta, responde só em texto" }[mode]}</small></section>);
}

export function HQ({ cal, onRun }) {
  const [tasks, setTasks] = useState([]), [u, setU] = useState({ in: 0, out: 0, turns: 0 }), [t, setT] = useState("");
  const load = () => api("/api/tasks").then(setTasks).catch(() => {});
  useEffect(() => { load(); const i = setInterval(() => { load(); api("/api/usage").then(setU).catch(() => {}); }, 3000); return () => clearInterval(i); }, []);
  const add = async () => { if (t.trim()) { await post("/api/tasks", { title: t }); setT(""); load(); } };
  const Q = [["Tarefas pendentes", "liste minhas tarefas pendentes"], ["Agenda de hoje", "o que tenho na agenda hoje?"], ["Clima", "como está o clima?"], ["Resumo do dia", "resuma minha agenda e tarefas de hoje"]];
  return (<div className="grid3">
    <section className="panel"><h2>TAREFAS</h2>
      <div className="input"><input value={t} onChange={e => setT(e.target.value)} onKeyDown={e => e.key === "Enter" && add()} placeholder="Nova tarefa…" /><button onClick={add}>Adicionar</button></div>
      <ul className="tools">{tasks.map(k => <li key={k.id}><label><input type="checkbox" checked={k.done} onChange={() => post(`/api/tasks/${k.id}/toggle`).then(load)} /> <span className={k.done ? "done" : ""}>{k.title}</span></label>
        <button onClick={() => del(`/api/tasks/${k.id}`).then(load)} aria-label="Remover">×</button></li>)}</ul>
      {!tasks.length && <p className="dim">Sem tarefas. Diga “James, anote uma tarefa…”.</p>}</section>
    <section className="panel"><h2>AGENDA · 7 DIAS</h2>
      <ul className="tools">{cal.map((e, i) => <li key={i}><span>{e.title}</span><em>{new Date(e.start).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" })}</em></li>)}</ul>
      {!cal.length && <p className="dim">Nada agendado.</p>}</section>
    <div className="col">
      <section className="panel"><h2>USO DE TOKENS</h2><div className="temp">{((u.in + u.out) / 1000).toFixed(1)}k</div>
        <small>Entrada {u.in} · Saída {u.out}</small><small>Média/turno {u.turns ? Math.round((u.in + u.out) / u.turns) : 0} · custo $0 (local)</small></section>
      <section className="panel"><h2>EXECUÇÃO RÁPIDA</h2>{Q.map(([l, p]) => <button key={l} className="qr" onClick={() => onRun(p)}>{l}</button>)}</section></div>
  </div>);
}

export function Memory() {
  const [m, setM] = useState([]), [t, setT] = useState(""); const load = () => api("/api/memory").then(r => setM(Array.isArray(r) ? r : [])).catch(() => {}); useEffect(() => { load(); const i = setInterval(load, 3000); return () => clearInterval(i); }, []);
  const add = async () => { if (t.trim()) { await post("/api/memory", { text: t }); setT(""); load(); } };
  return (<section className="panel wide"><h2>MEMÓRIA</h2>
    <div className="input"><input value={t} onChange={e => setT(e.target.value)} onKeyDown={e => e.key === "Enter" && add()} placeholder="Algo que o JAMES deve lembrar…" /><button onClick={add}>Memorizar</button></div>
    <ul className="tools">{m.map(x => <li key={x.id}><span>{x.text}</span><em>{x.t}</em><button onClick={() => del(`/api/memory/${x.id}`).then(load)} aria-label="Esquecer">×</button></li>)}</ul>
    {!m.length && <p className="dim">Vazia. Diga “James, lembre que…” ou adicione acima. Tudo fica só neste computador.</p>}</section>);
}

export function Logs({ logs }) {
  const [tab, setTab] = useState("Transcrição"), [q, setQ] = useState(""), [tr, setTr] = useState([]);
  useEffect(() => { api("/api/transcript").then(setTr).catch(() => {}); }, [logs]);
  const rows = tab === "Transcrição" ? tr.map(m => ({ t: m.t, src: m.role === "user" ? "USER" : "JAMES", text: m.content, files: m.files })) : tab === "Ferramentas" ? logs.filter(l => l.src === "TOOL") : logs;
  return (<section className="panel wide"><h2>REGISTROS</h2>
    <div className="input"><div className="seg">{["Transcrição", "Ferramentas", "Logs"].map(k => <button key={k} className={k === tab ? "on2" : ""} onClick={() => setTab(k)}>{k}</button>)}</div>
      <input value={q} onChange={e => setQ(e.target.value)} placeholder="Buscar…" /><button onClick={() => post("/api/clear")}>Limpar conversa</button></div>
    <div className="lines tall">{rows.filter(r => (r.text || "").toLowerCase().includes(q.toLowerCase())).map((l, i) => tab === "Transcrição" ? <div key={i} className={`msg ${l.src}`}><time>{l.t}</time> <b>{l.src}</b><Msg text={l.text} files={l.files} /></div> : <p key={i} className={l.src}><time>{l.t}</time> <b>{l.src}</b> {l.text}</p>)}</div></section>);
}

export function Config() {
  const [mo, setMo] = useState({ installed: [], current: "" }), [msg, setMsg] = useState("");
  const load = () => api("/api/models").then(setMo).catch(() => {}); useEffect(() => { load(); }, []);
  return (<section className="panel wide"><h2>CONFIGURAÇÃO</h2>
    <p>Modelo de IA ativo: <b className="ok">{mo.current || "nenhum"}</b></p>
    {mo.installed.length ? <div className="seg">{mo.installed.map(n => <button key={n} className={n === mo.current ? "on2" : ""} onClick={() => post("/api/model", { name: n }).then(() => { setMsg("Modelo trocado."); load(); })}>{n}</button>)}</div>
      : <p className="bad">Nenhum modelo instalado. No terminal: <code>ollama pull llama3.2</code></p>}
    <h2 style={{ marginTop: 18 }}>ARQUIVOS</h2>
    <label className="btn">Enviar arquivo<input type="file" hidden onChange={e => uploadFile(e.target.files[0]).then(r => setMsg(r.error || `Enviado: ${r.path}`))} /></label>
    <small>Depois peça: “James, leia o arquivo que enviei”. Limite de 20 MB.</small>{msg && <p className="ok">{msg}</p>}</section>);
}

const copyText = async s => { try { await navigator.clipboard.writeText(s); } catch { const a = document.createElement("textarea"); a.value = s; document.body.appendChild(a); a.select(); document.execCommand("copy"); a.remove(); } };
export function Msg({ text, files = [] }) {
  const [ok, setOk] = useState("");
  const copy = async (s, k) => { await copyText(s); setOk(k); setTimeout(() => setOk(""), 1500); };
  const parts = String(text || "").split(/```[\w+-]*\n?([\s\S]*?)```/g);
  return (<div>
    {parts.map((p, i) => i % 2 ? <div className="code" key={i}><button onClick={() => copy(p.trim(), i)}>{ok === i ? "Copiado" : "Copiar código"}</button><pre>{p.trim()}</pre></div> : p.trim() && <p key={i}>{p.trim()}</p>)}
    <div className="msg-actions"><button onClick={() => copy(String(text || ""), "all")}>{ok === "all" ? "Copiado" : "Copiar texto"}</button>
      {files.map(f => <a key={f} className="btn" href={`/api/download?path=${encodeURIComponent(f)}`} download>Baixar {f.split("/").pop()}</a>)}</div></div>);
}
