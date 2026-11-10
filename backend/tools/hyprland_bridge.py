"""Controle do Hyprland via hyprctl. Suporta a sintaxe Lua (0.55+) e a antiga. Somente ações em lista branca."""
import json, re, subprocess
from tools.config import cfg

def _ctl(*a):
    try: r = subprocess.run(["hyprctl", *a], capture_output=True, text=True, timeout=5)
    except FileNotFoundError: raise RuntimeError("hyprctl não encontrado (controle de janelas só funciona no Hyprland/Linux)")
    return (r.stdout or r.stderr).strip()
_LUA = {}
def _is_lua():
    if "v" not in _LUA:
        try: m = re.match(r"v?0\.(\d+)", json.loads(_ctl("version", "-j")).get("tag", "")); _LUA["v"] = bool(m and int(m.group(1)) >= 55)
        except Exception: _LUA["v"] = True
    return _LUA["v"]
def _disp(lua, *legacy):
    out = _ctl("dispatch", lua) if _is_lua() else _ctl("dispatch", *legacy)
    if out.lower().startswith("error") or "error:" in out.lower()[:80]: raise RuntimeError(out[:200])
    return out

def workspaces(): return json.loads(_ctl("-j", "workspaces"))
def windows(): return [{"class": c["class"], "title": c["title"], "ws": c["workspace"]["id"]} for c in json.loads(_ctl("-j", "clients"))]
def goto_workspace(id: int): n = int(id); return _disp(f'hl.dsp.focus({{ workspace = "{n}" }})', "workspace", str(n))
def launch(app: str):
    if not app.replace("-", "").replace("_", "").isalnum(): raise ValueError("nome de app inválido")
    return _disp(f'hl.dsp.exec_cmd("{app}")', "exec", app)
def close_active(): return _disp("hl.dsp.window.close()", "killactive")
def move_to_workspace(id: int): n = int(id); return _disp(f'hl.dsp.window.move({{ workspace = "{n}" }})', "movetoworkspace", str(n))

ACTIONS = {f.__name__: f for f in (workspaces, windows, goto_workspace, launch, close_active, move_to_workspace)}
def run(action: str, **kw):
    if not cfg().get("hypr_control"): raise PermissionError('controle do Hyprland desligado (config: "hypr_control": true)')
    if action not in ACTIONS: raise ValueError(f"ação não permitida: {action}")
    if "id" in kw and not 1 <= int(kw["id"]) <= 10: raise ValueError("workspace deve estar entre 1 e 10")
    return ACTIONS[action](**kw)
