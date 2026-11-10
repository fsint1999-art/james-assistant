import { useEffect, useState, useRef } from "react";
import ArcReactor from "./components/ArcReactor.jsx";
import Telemetry from "./components/Telemetry.jsx";
import Intelligence from "./components/Intelligence.jsx";
import TerminalFeed from "./components/TerminalFeed.jsx";
import Services from "./components/Services.jsx";
import Context from "./components/Context.jsx";
import Background from "./components/Background.jsx";
import { Rail, HQ, Memory, Logs, Config, post, uploadFile, Msg } from "./components/Pages.jsx";

const get = u => fetch(u).then(r => r.json());
const MAP = { search_web: "web", file_manager: "files", hyprland_control: "hypr", calendar: "calendar", weather: "weather" };
export default function App() {
  const [m, setM] = useState(null), [logs, setLogs] = useState([]), [steps, setSteps] = useState([]), [sv, setSv] = useState({});
  const [busy, setBusy] = useState(false), [text, setText] = useState(""), [reply, setReply] = useState("Pronto, senhor. Diga “James”.");
  const [clock, setClock] = useState(new Date()), [wx, setWx] = useState(null), [cal, setCal] = useState([]), [v, setV] = useState({ state: "off" });
  const seq = useRef(null), modeRef = useRef("voice"), envRef = useRef(null);
  const [page, setPage] = useState("voz"), [stream, setStreamS] = useState("General"), [mode, setModeS] = useState("voice");
  const setStream = n => { setStreamS(n); post("/api/stream", { name: n }); setSteps([]); setReply("Canal: " + n); };
  const setMode = k => { setModeS(k); modeRef.current = k; post("/api/mode", { mode: k }); };

  useEffect(() => {
    const fast = async () => { try { setM(await get("/api/metrics")); setLogs(await get("/api/logs")); setSv(await get("/api/services")); } catch { setM(null); } };
    const slow = async () => { try { setWx(await get("/api/weather")); setCal(await get("/api/calendar")); } catch {} };
    fast(); slow(); const ids = [setInterval(fast, 2000), setInterval(slow, 300000), setInterval(() => setClock(new Date()), 1000)];
    return () => ids.forEach(clearInterval);
  }, []);

  useEffect(() => {
    const id = setInterval(async () => {
      try {
        const j = await get("/api/voice"); setV(j);
        if (j.env?.rms && j.env.t0 !== envRef.current?.t0) envRef.current = j.env;
        if (seq.current === null) { seq.current = j.seq; return; }
        if (j.seq !== seq.current) { seq.current = j.seq; setReply(j.reply); setSteps(j.steps || []); !j.tts && speak(j.reply); }
      } catch {}
    }, 300);
    return () => clearInterval(id);
  }, []);

  const speak = t => modeRef.current === "voice" && "speechSynthesis" in window && speechSynthesis.speak(Object.assign(new SpeechSynthesisUtterance(t), { lang: "pt-BR", pitch: 0.4, rate: 0.9, voice: speechSynthesis.getVoices().find(x => x.lang.startsWith("pt")) }));
  async function send(t) {
    if (!t.trim() || busy) return;
    setBusy(true); setText(""); setReply("Processando…");
    try {
      const r = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: t }) }).then(r => r.json());
      setReply(r.reply); setSteps(r.steps);
    } catch { setReply("Backend inacessível. Verifique o uvicorn na porta 8000."); }
    setBusy(false);
  }
  const toggleMute = () => post("/api/mute").then(r => setV(x => ({ ...x, muted: r.muted })));
  const level = () => { const e = envRef.current; if (!e) return 0; const i = Math.floor((Date.now() / 1000 - e.t0) / e.dt); return i < 0 || i >= e.rms.length ? 0 : e.rms[i]; };
  const working = busy || v.state === "thinking";
  const rstate = v.muted ? "mute" : working ? "busy" : v.state === "speaking" ? "speak" : v.state === "listening" ? "listen" : "idle";
  const active = new Set([...steps.filter(s => s.tool).map(s => MAP[s.tool]), working && "ollama", v.state === "listening" && "voice"].filter(Boolean));
  const chip = { sleeping: "Diga “James” para ativar", listening: "Ouvindo…", thinking: `Entendi: “${v.heard}”`, paused: "Microfone pausado (modo Texto)", speaking: "Falando…", muted: "Microfone mudo", off: v.error || "Voz desligada" }[v.state];
  return (
    <main className="hud"><Background level={level} state={rstate} />
      <header><h1>J.A.M.E.S.</h1><span className="dim">assistente pessoal · local</span>
        <nav>{[["voz", "Voz"], ["hq", "HQ"], ["memoria", "Memória"], ["logs", "Logs"], ["config", "Config"]].map(([k, l]) => <button key={k} className={page === k ? "on2" : ""} onClick={() => setPage(k)}>{l}</button>)}</nav>
        <time>{clock.toLocaleTimeString("pt-BR")}<small>{clock.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" })}</small></time></header>
      {page !== "voz" ? <section className="page">
        {page === "hq" && <HQ cal={cal} onRun={p => { setPage("voz"); send(p); }} />}{page === "memoria" && <Memory />}{page === "logs" && <Logs logs={logs} />}{page === "config" && <Config />}</section> : <>
      <aside className="left"><Rail stream={stream} setStream={setStream} mode={mode} setMode={setMode} /><Telemetry m={m} /><Context wx={wx} cal={cal} /></aside>
      <section className="center">
        <ArcReactor level={level} state={rstate} />
        <div className="reply" aria-live="polite"><Msg text={reply} files={steps.filter(s => s.file).map(s => s.file)} /></div>
        <div className="seg"><p className={`chip ${v.state}`}>{chip}</p><button aria-pressed={!!v.muted} onClick={toggleMute}>{v.muted ? "Mic: mudo" : "Mic: ligado"}</button></div>
        {steps.some(s => s.status === "pendente") && <div className="seg"><button onClick={() => send("sim")}>Sim</button><button onClick={() => send("não")}>Não</button></div>}
        <div className="input">
          <label className="btn">Anexar<input type="file" hidden onChange={e => uploadFile(e.target.files[0]).then(x => setReply(x.error || "Arquivo recebido: " + x.path))} /></label>
          <input value={text} onChange={e => setText(e.target.value)} onKeyDown={e => e.key === "Enter" && send(text)} placeholder="Ou digite um comando…" />
          <button onClick={() => send(text)} disabled={busy}>Enviar</button>
        </div>
      </section>
      <aside className="right"><Intelligence steps={steps} busy={working} /><Services ok={sv} active={active} /><TerminalFeed logs={logs} /></aside></>}
    </main>);
}
