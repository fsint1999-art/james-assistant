"""Memória e tarefas persistentes (JSON local)."""
import json, time
from pathlib import Path
D = Path.home() / ".local/share/james/data"
def _ld(n):
    try: return json.loads((D / n).read_text())
    except Exception: return []
def _sv(n, v): D.mkdir(parents=True, exist_ok=True); (D / n).write_text(json.dumps(v, ensure_ascii=False))
def _new(): return int(time.time() * 1000)

def mem_list(): return _ld("memory.json")
def mem_add(text):
    m = mem_list(); m.append({"id": _new(), "text": text, "t": time.strftime("%d/%m %H:%M")}); _sv("memory.json", m); return "memorizado"
def mem_del(id): _sv("memory.json", [x for x in mem_list() if x["id"] != int(id)]); return "esquecido"
def memory_block():
    m = mem_list()[-20:]
    return ("\nMemória do usuário:\n" + "\n".join(f"- {x['text']}" for x in m)) if m else ""

def task_list(): return _ld("tasks.json")
def task_add(title): t = task_list(); t.append({"id": _new(), "title": title, "done": False}); _sv("tasks.json", t); return "tarefa criada"
def task_toggle(id): t = task_list(); [x.update(done=not x["done"]) for x in t if x["id"] == int(id)]; _sv("tasks.json", t); return "ok"
def task_del(id): _sv("tasks.json", [x for x in task_list() if x["id"] != int(id)]); return "removida"

def memory(action, **kw):
    return {"add": lambda text: mem_add(text), "list": lambda: mem_list(), "delete": lambda id: mem_del(id)}[action](**kw)
def tasks(action, **kw):
    return {"add": lambda title: task_add(title), "list": lambda: task_list(), "done": lambda id: task_toggle(id)}[action](**kw)
