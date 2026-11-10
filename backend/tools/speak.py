"""Voz grave offline: Piper (TTS) + sox (baixa o tom). Toca no backend, mesmo com o HUD fechado."""
import shutil, subprocess
from pathlib import Path
from tools.config import cfg
def available():
    t = cfg()["tts"]; return bool(shutil.which("piper") and shutil.which("play") and Path(t["model"]).exists())
def say(text, wait=False):
    if not available(): return False
    t = cfg()["tts"]
    p1 = subprocess.Popen(["piper", "--model", t["model"], "--output-raw"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p2 = subprocess.Popen(["play", "-q", "-t", "raw", "-r", str(t["rate"]), "-e", "signed", "-b", "16", "-c", "1", "-", "pitch", str(t["pitch"]), "tempo", str(t["tempo"]), "bass", "6"],
                          stdin=p1.stdout, stderr=subprocess.DEVNULL)
    p1.stdout.close(); p1.stdin.write(text.encode()); p1.stdin.close()
    if wait: p2.wait()
    return True

def diagnose():
    t = cfg()["tts"]; miss = []
    if not shutil.which("piper"): miss.append("piper (yay -S piper-tts-bin)")
    if not shutil.which("play"): miss.append("sox (sudo pacman -S sox)")
    if not Path(t["model"]).exists(): miss.append(f"arquivo de voz: {t['model']}")
    if miss: return {"ok": False, "detail": "faltando: " + "; ".join(miss)}
    try: r = subprocess.run(["piper", "--model", t["model"], "--output-raw"], input=b"Ao seu dispor, senhor.", capture_output=True, timeout=60)
    except Exception as e: return {"ok": False, "detail": str(e)}
    if r.returncode or not r.stdout: return {"ok": False, "detail": "piper falhou: " + r.stderr.decode(errors="replace")[-300:]}
    say("Ao seu dispor, senhor.")
    return {"ok": True, "detail": "piper gerou áudio e mandou ao sox; se não ouviu nada, verifique a saída de áudio padrão (wpctl status)"}

# ---- Kokoro (alternativa ao Piper) ----
_piper_available, _piper_say, _piper_diag = available, say, diagnose
_K = {"m": None}
def _engine(): return cfg()["tts"].get("engine", "piper")
def _kpaths():
    d = Path(cfg()["tts"].get("kokoro_dir", str(Path.home() / ".local/share/james/kokoro")))
    return d / "kokoro-v1.0.onnx", d / "voices-v1.0.bin"
def _kok_ok():
    try: import kokoro_onnx  # noqa
    except ImportError: return False
    a, b = _kpaths(); return bool(shutil.which("play")) and a.exists() and b.exists()
def _kok_say(text, wait=False):
    import numpy as np
    if _K["m"] is None:
        from kokoro_onnx import Kokoro
        a, b = _kpaths(); _K["m"] = Kokoro(str(a), str(b))
    t = cfg()["tts"]
    s, sr = _K["m"].create(text, voice=t.get("voice", "pm_alex"), speed=float(t.get("speed", 0.95)), lang="pt-br")
    pcm = (np.clip(s, -1, 1) * 32767).astype("<i2").tobytes()
    p = subprocess.Popen(["play", "-q", "-t", "raw", "-r", str(sr), "-e", "signed", "-b", "16", "-c", "1", "-", "pitch", str(t.get("kokoro_pitch", -100))],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p.stdin.write(pcm); p.stdin.close()
    if wait: p.wait()
    return True
def available(): return _kok_ok() if _engine() == "kokoro" else _piper_available()
def say(text, wait=False): return _kok_say(text, wait) if _engine() == "kokoro" else _piper_say(text, wait)
def diagnose():
    if _engine() != "kokoro": return _piper_diag()
    if not _kok_ok(): return {"ok": False, "detail": "falta kokoro-onnx no venv, sox, ou os arquivos em " + str(_kpaths()[0].parent)}
    try: _kok_say("Ao seu dispor, senhor.")
    except Exception as e: return {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    return {"ok": True, "detail": "kokoro gerou e tocou o áudio"}


# ---- v8: envelope do áudio para animar o núcleo com a voz ----
import time as _time
ENV = {}
def _set_env(pcm, sr, stretch):
    import numpy as np
    a = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768; n = max(1, int(sr * .05)); f = a[: len(a) // n * n].reshape(-1, n)
    r = np.sqrt((f ** 2).mean(1)); r = np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1)
    ENV.clear(); ENV.update(t0=_time.time() + .2, dt=.05 * stretch, rms=[round(float(x), 3) for x in r])
def _play(pcm, sr, extra):
    p = subprocess.Popen(["play", "-q", "-t", "raw", "-r", str(sr), "-e", "signed", "-b", "16", "-c", "1", "-", *extra], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p.stdin.write(pcm); p.stdin.close(); return p
def _say_piper_env(text, wait=False):
    t = cfg()["tts"]; pp = (globals().get("_piper") or (lambda: shutil.which("piper")))()
    if not (pp and Path(t["model"]).exists()): return False
    pcm = subprocess.run([pp, "--model", t["model"], "--output-raw"], input=text.encode(), capture_output=True, timeout=60).stdout
    if not pcm: return False
    _set_env(pcm, t["rate"], 1 / float(t["tempo"]))
    p = _play(pcm, t["rate"], ["pitch", str(t["pitch"]), "tempo", str(t["tempo"])])
    if wait: p.wait()
    return True
def _kok_say(text, wait=False):
    import numpy as np
    if _K["m"] is None:
        from kokoro_onnx import Kokoro
        a, b = _kpaths(); _K["m"] = Kokoro(str(a), str(b))
    t = cfg()["tts"]
    s, sr = _K["m"].create(text, voice=t.get("voice", "pm_alex"), speed=float(t.get("speed", .95)), lang="pt-br")
    pcm = (np.clip(s, -1, 1) * 32767).astype("<i2").tobytes(); _set_env(pcm, sr, 1.0)
    p = _play(pcm, sr, ["pitch", str(t.get("kokoro_pitch", -100))])
    if wait: p.wait()
    return True
if "_piper_say" in globals(): _piper_say = _say_piper_env
else: say = _say_piper_env
