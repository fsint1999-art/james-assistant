import os, re, shutil, time, httpx
from collections import deque
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import voice
from core_engine import run_agent
from tools import system_monitor, weather, calendar_tool, umbrel, speak, router, mcp_bridge
from tools.config import cfg

app = FastAPI(title="JAMES")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])
LOG = deque(maxlen=200); HIST = {"General": [], "BrainDump": [], "Research": []}; CUR = {"stream": "General"}
def log(src, text): LOG.append({"t": time.strftime("%H:%M:%S"), "src": src, "text": text})
log("JAMES", "Núcleo iniciado.")

MEM = re.compile(r"^\s*(?:james[, ]*)?(?:por favor[, ]*)?(?:(?:lembre(?:-se)?|memorize|n[ãa]o esque[cç]a)\s*(?:que|de|:)?\s+(.+)|(?:guarde|anote|salve|registre)\s+(?:na mem[óo]ria\s*:?\s*|que\s+)(.+))$", re.I)
PATHRE = re.compile(r"(/(?:home|tmp|mnt)/[^\s'\"<>()\[\]]+)")
def find_files(*texts):
    out = []
    for t in texts:
        for m in PATHRE.findall(t or ""):
            m = m.rstrip(".,;:")
            if m not in out and os.path.isfile(m): out.append(m)
    return out

def handle(text):
    log("USER", text)
    H = HIST[CUR["stream"]]; ans = ce.confirm_answer(text); steps = []
    mm = MEM.search(text) if ans is None else None
    if mm:
        txt = next(g for g in mm.groups() if g).strip(); store.mem_add(txt); log("MEM", txt); reply = "Anotado na memória, senhor."
    elif ans is not None: reply = ans
    elif (call := router.match(text)): reply, steps = ce.direct(*call)
    else: reply, steps = run_agent(text, [{"role": m["role"], "content": m["content"]} for m in H[-10:]])
    files = find_files(reply, *[s.get("result") for s in steps])
    steps = steps + [{"phase": "file", "tool": None, "status": "ok", "file": f} for f in files]
    now = time.strftime("%H:%M:%S"); H.extend([{"role": "user", "content": text, "t": now}, {"role": "assistant", "content": reply, "t": now, "files": files}])
    for s in steps:
        if s["tool"]: log("TOOL", f"{s['tool']} {s['status']}" + (f": {str(s.get('result'))[:150]}" if s["status"] == "error" else ""))
    log("JAMES", reply)
    if ce.PENDING: voice.STATE["awaiting"] = True
    return reply, steps

@app.on_event("startup")
def _start():
    if cfg()["voice"]: voice.start(handle)

class Msg(BaseModel): text: str
@app.post("/api/chat")
def chat(m: Msg):
    reply, steps = handle(m.text)
    if voice.STATE["mode"] == "voice" and speak.available(): speak.say(reply)
    return {"reply": reply, "steps": steps}
@app.get("/api/metrics")
def metrics(): return system_monitor.snapshot()
@app.get("/api/logs")
def logs(): return list(LOG)
@app.get("/api/voice")
def voice_state(): return {**voice.STATE, "env": getattr(speak, "ENV", {})}
@app.get("/api/weather")
def wx(): return weather.current()
@app.get("/api/calendar")
def cal(): return calendar_tool.upcoming(7)
@app.get("/api/services")
def services():
    try: ollama = httpx.get(cfg()["ollama_url"] + "/api/tags", timeout=1).status_code == 200
    except Exception: ollama = False
    return {"ollama": ollama, "web": system_monitor.snapshot()["online"], "calendar": True, "weather": bool(weather._c["d"]), "files": True,
            "hypr": bool(shutil.which("hyprctl") and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")), "voice": voice.STATE["state"] != "off", "umbrel": umbrel.up()}

# ---- v3: modelos, memória, tarefas, upload, streams, modos ----
import json as _j
from pathlib import Path
from fastapi import Request
from tools import store
import core_engine as ce

@app.get("/api/models")
def models(): return {"installed": ce.installed(), "current": ce.resolve_model()}
@app.post("/api/model")
def set_model(b: dict):
    p = Path.home() / ".config/james/config.json"
    try: d = _j.loads(p.read_text())
    except Exception: d = {}
    d["model"] = b["name"]; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(_j.dumps(d)); log("JAMES", f"Modelo: {b['name']}"); return {"ok": True}
@app.get("/api/usage")
def usage(): return ce.USAGE
@app.get("/api/memory")
def mem(): return store.mem_list()
@app.post("/api/memory")
def mem_add(b: dict): store.mem_add(b["text"]); return {"ok": True}
@app.delete("/api/memory/{i}")
def mem_del(i: int): store.mem_del(i); return {"ok": True}
@app.get("/api/tasks")
def tasks(): return store.task_list()
@app.post("/api/tasks")
def task_add(b: dict): store.task_add(b["title"]); return {"ok": True}
@app.post("/api/tasks/{i}/toggle")
def task_toggle(i: int): store.task_toggle(i); return {"ok": True}
@app.delete("/api/tasks/{i}")
def task_del(i: int): store.task_del(i); return {"ok": True}
@app.post("/api/stream")
def set_stream(b: dict):
    if b["name"] in HIST: CUR["stream"] = b["name"]
    return {"ok": True}
@app.get("/api/transcript")
def transcript(): return HIST[CUR["stream"]]
@app.post("/api/clear")
def clear(): HIST[CUR["stream"]].clear(); return {"ok": True}
@app.post("/api/mode")
def set_mode(b: dict): voice.STATE["paused"] = b["mode"] == "text"; voice.STATE["mode"] = b["mode"]; return {"ok": True}
@app.post("/api/upload")
async def upload(req: Request, name: str):
    data = await req.body()
    if len(data) > 20 * 2**20: return {"error": "limite de 20 MB"}
    d = Path.home() / ".local/share/james/uploads"; d.mkdir(parents=True, exist_ok=True)
    p = d / Path(name).name; p.write_bytes(data)
    HIST[CUR["stream"]].append({"role": "user", "content": f"[arquivo enviado: {p}] (use file_manager read para ler)", "t": time.strftime("%H:%M:%S")})
    log("FILE", str(p)); return {"path": str(p)}

@app.get("/api/tts/test")
def tts_test(): return speak.diagnose()

@app.post("/api/mute")
def mute():
    voice.STATE["muted"] = not voice.STATE.get("muted", False)
    log("JAMES", "Microfone mudo" if voice.STATE["muted"] else "Microfone ligado"); return {"muted": voice.STATE["muted"]}

@app.get("/api/mcp")
def mcp_info():
    out = {}
    for n in mcp_bridge._servers():
        try: out[n] = {"ok": True, "tools": mcp_bridge.list_tools(n, 5)}
        except Exception as e: out[n] = {"ok": False, "error": str(e)[:200]}
    return out

from fastapi import HTTPException
from fastapi.responses import FileResponse
@app.get("/api/download")
def download(path: str):
    p = Path(path).expanduser().resolve()
    roots = [Path(r).expanduser().resolve() for r in cfg()["allowed_roots"]]
    if not p.is_file() or not any(r in p.parents for r in roots): raise HTTPException(404, "arquivo indisponível")
    try:
        if any(x.startswith(".") for x in p.relative_to(Path.home()).parts): raise HTTPException(403, "arquivos ocultos são protegidos")
    except ValueError: pass
    return FileResponse(p, filename=p.name)

# HUD compilado servido pelo próprio backend (uma porta, um processo). Deve ficar por último.
from fastapi.staticfiles import StaticFiles
_dist = Path(__file__).resolve().parent.parent / "frontend/dist"
if _dist.exists(): app.mount("/", StaticFiles(directory=_dist, html=True), name="hud")
