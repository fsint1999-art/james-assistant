"""Integração com o umbrelOS: dispara fluxos do n8n por webhook (lista fechada)."""
import httpx
from tools.config import cfg
def _c(): return cfg()["n8n"]
def up():
    try: return httpx.get(_c()["url"], timeout=1.5).status_code < 500
    except Exception: return False
def hint():
    w = _c()["workflows"]; return ("\nFluxos n8n disponíveis: " + ", ".join(w)) if w else ""
def run(action, name=None, payload=None):
    c = _c()
    if action == "list": return list(c["workflows"])
    if action != "run": raise ValueError("ação: list | run")
    if name not in c["workflows"]: raise ValueError(f"fluxo fora da lista: {name}")
    base = c["url"].rstrip("/") + ("/webhook-test/" if c.get("test") else "/webhook/")
    h = {"X-James-Token": c["token"]} if c.get("token") else {}
    r = httpx.post(base + c["workflows"][name], json=payload or {}, headers=h, timeout=60); r.raise_for_status()
    return r.text[:1500]
