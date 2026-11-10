#!/usr/bin/env python3
"""Aplica v8 nos arquivos que você editou à mão (core_engine.py, speak.py). Idempotente."""
import os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
p = os.path.join(B, "core_engine.py"); s = open(p).read()
if '["result"]' not in s:
    a = 'steps[-1]["status"] = "ok"'; assert a in s, "core_engine.py: trecho do passo não encontrado"
    s = s.replace(a, 'steps[-1]["status"] = "ok"; steps[-1]["result"] = str(res)[:400]', 1)
if "def direct(" not in s:
    s += '''

def direct(name, args):
    """Executa uma chamada de ferramenta já decidida (atalhos de voz), respeitando a confirmação."""
    steps = [{"phase": "observe", "tool": name, "args": args, "status": "running"}]
    d = needs_confirm(name, args)
    if d:
        PENDING.update(name=name, args=args, t=time.time()); steps[0]["status"] = "pendente"
        return f"Com sua licença, senhor, posso {d}? Responda sim ou não.", steps
    try: res = TOOLS[name](**args); steps[0].update(status="ok", result=str(res)[:400])
    except Exception as e: steps[0]["status"] = "error"; return f"Não foi possível, senhor: {e}", steps
    if isinstance(res, list): res = ", ".join(sorted({str(x.get("class", x)) if isinstance(x, dict) else str(x) for x in res})) or "nenhuma"
    return "Feito, senhor." + ("" if str(res).strip().lower() in ("", "ok") else f" {str(res)[:200]}"), steps
'''
open(p, "w").write(s)
p = os.path.join(B, "tools", "speak.py"); s = open(p).read()
if "_set_env" not in s:
    s += '''

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
'''
    open(p, "w").write(s)
print("v8 aplicado em core_engine.py e speak.py")
