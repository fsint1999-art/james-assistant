"""Wake word 'James' 100% offline (Vosk) + ditado de comando em português."""
import json, queue, threading, time
from pathlib import Path
from tools.config import cfg
from tools import speak
STATE = {"state": "off", "heard": "", "reply": "", "steps": [], "seq": 0, "error": None, "tts": False, "mode": "voice", "muted": False}

def _loop(on_command):
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer, SetLogLevel
    SetLogLevel(-1); c = cfg(); SR = 16000; STATE["tts"] = speak.available()
    for k in ("wake_model", "cmd_model"):
        if not Path(c[k]).exists(): raise FileNotFoundError(f"modelo Vosk ausente: {c[k]} (veja o README)")
    wm, cm = Model(c["wake_model"]), Model(c["cmd_model"]); q = queue.Queue()
    wake = KaldiRecognizer(wm, SR, json.dumps(["james", "hey james", "[unk]"]))
    with sd.RawInputStream(samplerate=SR, blocksize=4000, dtype="int16", channels=1, callback=lambda d, f, t, s: q.put(bytes(d))):
        while True:
            if STATE.get("paused") or STATE.get("muted"): STATE["state"] = "muted" if STATE.get("muted") else "paused"; q.get(); continue
            if not STATE.pop("awaiting", False):  # após pergunta de confirmação, escuta direto
                STATE["state"] = "sleeping"; data = q.get()
                j = json.loads(wake.Result() if wake.AcceptWaveform(data) else wake.PartialResult())
                if "james" not in (j.get("text") or j.get("partial", "")): continue
            wake.Reset(); STATE.update(state="listening", heard=""); rec = KaldiRecognizer(cm, SR); text = ""; t0 = time.time()
            while time.time() - t0 < 12 and not text:
                if rec.AcceptWaveform(q.get()): text = json.loads(rec.Result()).get("text", "")
            if text:
                STATE.update(state="thinking", heard=text)
                reply, steps = on_command(text); STATE.update(reply=reply, steps=steps, seq=STATE["seq"] + 1)
                if STATE["tts"] and STATE["mode"] == "voice": STATE["state"] = "speaking"; speak.say(reply, wait=True)
            if STATE.get("awaiting") and not STATE["tts"]: time.sleep(min(8, 1.5 + len(reply) / 14))  # espera a fala terminar
            while not q.empty(): q.get_nowait()
            wake.Reset()

def start(on_command):
    def run():
        try: _loop(on_command)
        except Exception as e: STATE.update(state="off", error=str(e))
    threading.Thread(target=run, daemon=True).start()
