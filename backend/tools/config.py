import json
from pathlib import Path
M = Path.home() / ".local/share/james/models"
DEF = {"model": "llama3", "ollama_url": "http://localhost:11434", "allowed_roots": [str(Path.home())],
       "lat": -23.55, "lon": -46.63, "voice": True, "mcp": {"servers": {}}, "hypr_control": False,
       "n8n": {"url": "http://umbrel.local:5678", "token": "", "test": False, "workflows": {}},
       "tts": {"model": str(Path.home() / ".local/share/james/voices/pt_BR-faber-medium.onnx"), "rate": 22050, "pitch": -200, "tempo": 0.92}, "vision_model": "", "screen_control": False,
       "commands": {"espaco_disco": "df -h /", "uptime": "uptime", "memoria": "free -h"},
       "wake_model": str(M / "vosk-model-small-en-us-0.15"), "cmd_model": str(M / "vosk-model-small-pt-0.3")}
def cfg():
    d = dict(DEF)
    try: d.update(json.loads((Path.home() / ".config/james/config.json").read_text()))
    except Exception: pass
    return d
