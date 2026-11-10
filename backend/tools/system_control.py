"""Controles do sistema: volume, brilho, área de transferência, print e comandos de lista fechada."""
import shlex, subprocess, time
from pathlib import Path
from tools.config import cfg
SINK = "@DEFAULT_AUDIO_SINK@"
def _run(cmd, inp=None):
    try: r = subprocess.run(cmd, input=inp, capture_output=True, text=True, timeout=20)
    except FileNotFoundError: raise RuntimeError(f'{cmd[0]} não encontrado neste sistema (recurso do Linux/Wayland)')
    if r.returncode: raise RuntimeError((r.stderr or r.stdout).strip()[:200] or f"{cmd[0]} falhou")
    return r.stdout.strip()
def _pct(v, lo): return max(lo, min(100, int(v)))
def volume_get(): return _run(["wpctl", "get-volume", SINK])
def volume_set(percent): p = _pct(percent, 0); _run(["wpctl", "set-volume", SINK, f"{p}%"]); return f"volume em {p}%"
def volume_step(delta): d = int(delta); _run(["wpctl", "set-volume", "-l", "1.0", SINK, f"{abs(d)}%{'+' if d > 0 else '-'}"]); return volume_get()
def disk_summary():
    import shutil as sh; u = sh.disk_usage(Path.home()); return f"{u.free / 2**30:.0f} gigabytes livres de {u.total / 2**30:.0f}, {u.used / u.total * 100:.0f} por cento usado"
def ram_summary():
    import psutil; m = psutil.virtual_memory(); return f"{m.available / 2**30:.1f} gigabytes de memória livres de {m.total / 2**30:.0f}"
def mute_toggle(): _run(["wpctl", "set-mute", SINK, "toggle"]); return "mudo alternado"
def brightness_get(): return _run(["brightnessctl", "-m"])
def brightness_set(percent): p = _pct(percent, 5); _run(["brightnessctl", "set", f"{p}%"]); return f"brilho em {p}%"
def clipboard_set(text): _run(["wl-copy"], text); return "copiado"
def clipboard_get(): return _run(["wl-paste", "-n"])[:2000]
def screenshot():
    d = Path.home() / "Pictures"; d.mkdir(exist_ok=True); p = d / time.strftime("james_%Y%m%d_%H%M%S.png")
    _run(["grim", str(p)]); return str(p)
ACTIONS = {f.__name__: f for f in (volume_get, volume_set, volume_step, disk_summary, ram_summary, mute_toggle, brightness_get, brightness_set, clipboard_set, clipboard_get, screenshot)}
def run(action, **kw):
    if action not in ACTIONS: raise ValueError(f"ação não permitida: {action}")
    return ACTIONS[action](**kw)
def run_command(name, **_):
    cmds = cfg()["commands"]
    if name not in cmds: raise ValueError(f"comando fora da lista: {name}")
    return _run(shlex.split(cmds[name]))[:1500]  # sem shell: argumentos separados
def commands_hint():
    c = cfg()["commands"]; return ("\nComandos de run_command: " + ", ".join(c)) if c else ""
