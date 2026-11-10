"""Agenda 100% local: eventos em ~/.config/james/calendar/events.json + arquivos .ics."""
import json, re
from datetime import datetime, timedelta
from pathlib import Path
DIR = Path.home() / ".config/james/calendar"; STORE = DIR / "events.json"

def _parse(v):
    v = v.strip().rstrip("Z")
    return datetime.strptime(v, "%Y%m%dT%H%M%S") if "T" in v else datetime.strptime(v, "%Y%m%d")

def _ics():
    out = []
    for f in DIR.glob("*.ics"):
        ev = None
        for ln in f.read_text(errors="replace").splitlines():
            if ln.startswith("BEGIN:VEVENT"): ev = {}
            elif ln.startswith("END:VEVENT") and ev and "start" in ev and "title" in ev: out.append(ev); ev = None
            elif ev is not None:
                if ln.startswith("DTSTART"):
                    try: ev["start"] = _parse(ln.split(":", 1)[1]).isoformat()
                    except Exception: pass
                elif ln.startswith("SUMMARY"): ev["title"] = ln.split(":", 1)[1]
    return out

def _all():
    DIR.mkdir(parents=True, exist_ok=True)
    try: mine = json.loads(STORE.read_text())
    except Exception: mine = []
    return mine + _ics()

def upcoming(days: int = 7):
    t0 = datetime.now().replace(hour=0, minute=0, second=0); t1 = t0 + timedelta(days=int(days))
    return sorted((e for e in _all() if t0 <= datetime.fromisoformat(e["start"]) < t1), key=lambda e: e["start"])

def add(title: str, start: str):
    datetime.fromisoformat(start)  # valida (ex.: 2026-11-05T14:30)
    ev = _all(); mine = [e for e in ev if e not in _ics()]
    mine.append({"title": title, "start": start}); STORE.write_text(json.dumps(mine, ensure_ascii=False)); return "evento criado"

def run(action: str, **kw):
    if action not in ("list", "add"): raise ValueError("ação: list | add")
    return upcoming(**kw) if action == "list" else add(**kw)
