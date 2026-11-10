"""Cliente MCP mínimo (Streamable HTTP, JSON-RPC) para o servidor MCP do umbrelOS 2.0+ e outros."""
import json, os, time, httpx
from tools.config import cfg

def _servers(): return (cfg().get("mcp") or {}).get("servers", {})
def _srv(name):
    s = _servers().get(name)
    if not s: raise ValueError(f"servidor MCP desconhecido: {name} (configurados: {', '.join(_servers()) or 'nenhum'})")
    tok = s.get("token") or os.environ.get(s.get("token_env", ""), "")
    return {"url": s["url"], "headers": {**({"Authorization": f"Bearer {tok}"} if tok else {}), **s.get("headers", {})}}

def _post(srv, body, sid=None, proto=None, timeout=30):
    h = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json", **srv["headers"]}
    if sid: h["Mcp-Session-Id"] = sid
    if proto: h["MCP-Protocol-Version"] = proto
    r = httpx.post(srv["url"], json=body, headers=h, timeout=timeout); r.raise_for_status(); return r
def _parse(r):
    if not r.content: return None
    if "text/event-stream" in r.headers.get("content-type", ""):
        for ln in r.text.splitlines():
            if ln.startswith("data:"):
                try: j = json.loads(ln[5:].strip())
                except ValueError: continue
                if "result" in j or "error" in j: return j
        return None
    return r.json()
def _rpc(srv, method, params=None, timeout=30):
    r = _post(srv, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "james", "version": "1.0"}}}, timeout=timeout)
    j = _parse(r) or {}
    if "error" in j: raise RuntimeError(str(j["error"])[:300])
    sid, proto = r.headers.get("mcp-session-id"), j.get("result", {}).get("protocolVersion")
    _post(srv, {"jsonrpc": "2.0", "method": "notifications/initialized"}, sid, proto, timeout)
    j = _parse(_post(srv, {"jsonrpc": "2.0", "id": 2, "method": method, "params": params or {}}, sid, proto, timeout))
    if not j: raise RuntimeError("resposta vazia do servidor MCP")
    if "error" in j: raise RuntimeError(str(j["error"])[:300])
    return j["result"]

def list_tools(server, timeout=30):
    res = _rpc(_srv(server), "tools/list", timeout=timeout)
    return [{"name": t["name"], "description": (t.get("description") or "")[:160], "params": list((t.get("inputSchema") or {}).get("properties", {}))} for t in res.get("tools", [])]
def call(server, tool, args=None):
    res = _rpc(_srv(server), "tools/call", {"name": tool, "arguments": args or {}})
    txt = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")[:1500]
    if res.get("isError"): raise RuntimeError(txt or "erro na ferramenta MCP")
    return txt or json.dumps(res.get("structuredContent", {}), ensure_ascii=False)[:1500]
def run(action, server=None, tool=None, args=None, **_):
    if action == "servers": return list(_servers())
    if action == "list": return list_tools(server)
    if action == "call": return call(server, tool, args)
    raise ValueError("ação: servers | list | call")

_H = {"t": 0, "s": ""}
def hint():
    if time.time() - _H["t"] < 300: return _H["s"]
    _H["t"] = time.time(); parts = []
    for n in _servers():
        try: parts.append(f"{n}: " + ", ".join(t["name"] for t in list_tools(n, 3)[:25]))
        except Exception: pass
    _H["s"] = ("\nServidores MCP (ferramentas): " + " | ".join(parts)) if parts else ""; return _H["s"]
