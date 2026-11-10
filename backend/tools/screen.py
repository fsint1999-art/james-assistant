"""Camada de tela: ver (modelo de visão local) e agir (ydotool, desligado por padrão)."""
import base64, subprocess, tempfile, httpx
from pathlib import Path
from tools.config import cfg
KEYS = {"enter": "28:1 28:0", "tab": "15:1 15:0", "esc": "1:1 1:0"}
def look(question="Descreva o que está na tela."):
    c = cfg(); vm = c.get("vision_model")
    if not vm: raise RuntimeError('defina "vision_model" no config (ex.: qwen2.5vl) e rode ollama pull')
    f = tempfile.mktemp(suffix=".png"); subprocess.run(["grim", f], check=True, timeout=10)
    img = base64.b64encode(Path(f).read_bytes()).decode(); Path(f).unlink()
    r = httpx.post(c["ollama_url"] + "/api/chat", timeout=300, json={"model": vm, "stream": False, "messages": [{"role": "user", "content": question, "images": [img]}]})
    r.raise_for_status(); return r.json()["message"]["content"][:1500]
def _yd(*a):
    if not cfg().get("screen_control"): raise PermissionError('controle de tela desligado (config: "screen_control": true)')
    subprocess.run(["ydotool", *a], check=True, timeout=10); return "ok"
def type_text(text): return _yd("type", text)
def key(code): return _yd("key", *KEYS.get(code, code).split())
def click(x, y): _yd("mousemove", "-a", "-x", str(int(x)), "-y", str(int(y))); return _yd("click", "0xC0")
ACTIONS = {"look": look, "type_text": type_text, "key": key, "click": click}
def run(action, **kw):
    if action not in ACTIONS: raise ValueError(f"ação não permitida: {action}")
    return ACTIONS[action](**kw)
