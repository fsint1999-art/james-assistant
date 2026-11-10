"""Manipulação segura de arquivos: tudo confinado às raízes permitidas."""
import json, shutil, zipfile
from pathlib import Path

CFG = Path.home() / ".config/james/config.json"
def _roots():
    try: return [Path(r).expanduser().resolve() for r in json.loads(CFG.read_text())["allowed_roots"]]
    except Exception: return [Path.home().resolve()]

def _safe(p: str) -> Path:
    path = Path(p).expanduser().resolve()
    if not any(path == r or r in path.parents for r in _roots()):
        raise PermissionError(f"Fora das raízes permitidas: {path}")
    return path

def search(query: str, root: str = "~", limit: int = 20):
    base = _safe(root)
    out = []
    for f in base.rglob(f"*{query}*"):
        out.append(str(f))
        if len(out) >= limit: break
    return out

def read(path: str, max_chars: int = 6000):
    return _safe(path).read_text(errors="replace")[:max_chars]

def list_dir(path: str = "~"):
    return sorted(p.name + ("/" if p.is_dir() else "") for p in _safe(path).iterdir())

def move(src: str, dst: str):
    s, d = _safe(src), _safe(dst)
    if d.exists() and not d.is_dir(): raise FileExistsError(f"destino já existe: {d}")
    shutil.move(str(s), str(d)); return f"{s} -> {d}"

def compress(src: str, dst: str):
    s, d = _safe(src), _safe(dst)
    with zipfile.ZipFile(d, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ([s] if s.is_file() else s.rglob("*")):
            if f.is_file(): z.write(f, f.relative_to(s.parent))
    return str(d)

def _w(path):
    p = _safe(path)
    try:
        if any(x.startswith(".") for x in p.relative_to(Path.home()).parts): raise PermissionError("arquivos ocultos são protegidos")
    except ValueError: pass
    return p
def _bak(p):
    if p.exists(): shutil.copy2(p, str(p) + ".bak")
def write(path: str, content: str):
    p = _w(path); p.parent.mkdir(parents=True, exist_ok=True); _bak(p); p.write_text(content); return f"gravado {p}"
def append(path: str, content: str):
    p = _w(path); _bak(p)
    with open(p, "a") as f: f.write(content)
    return f"texto acrescentado em {p}"
def replace(path: str, old: str, new: str):
    p = _w(path); t = p.read_text(); n = t.count(old)
    if n != 1: raise ValueError(f"trecho encontrado {n}x; preciso de exatamente 1")
    _bak(p); p.write_text(t.replace(old, new)); return f"editado {p}"

ACTIONS = {"search": search, "read": read, "list": list_dir, "move": move, "compress": compress, "write": write, "append": append, "replace": replace}
def run(action: str, **kw):
    if action not in ACTIONS: raise ValueError(f"ação desconhecida: {action}")
    return ACTIONS[action](**kw)
