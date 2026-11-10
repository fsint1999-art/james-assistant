#!/usr/bin/env python3
"""Aplica o MCP e melhorias de erro ao core_engine.py que você editou à mão. Idempotente."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "core_engine.py"); s = open(p).read()
def rep(a, b, marker):
    global s
    if marker in s: return
    assert a in s, f"trecho não encontrado: {a[:60]}"; s = s.replace(a, b, 1)
rep("screen, umbrel", "screen, umbrel, mcp_bridge", "mcp_bridge")
rep('    "n8n": lambda **a: umbrel.run(**a),', '    "n8n": lambda **a: umbrel.run(**a),\n    "mcp": lambda **a: mcp_bridge.run(**a),', '"mcp": lambda')
rep('    if name == "run_command": return', '    if name == "mcp" and act == "call" and a.get("tool") not in ((cfg().get("mcp") or {}).get("servers", {}).get(a.get("server"), {}).get("readonly", [])): return f"chamar a ferramenta {a.get(\'tool\')} do servidor MCP {a.get(\'server\')}"\n    if name == "run_command": return', 'name == "mcp" and act')
rep("- weather: args {}", '- mcp: args {"action":"servers"} | {"action":"list","server":"<nome>"} | {"action":"call","server":"<nome>","tool":"<ferramenta>","args":{...}}  (servidor MCP do Umbrel)\n- weather: args {}', "- mcp: args")
rep("umbrel.hint())", "umbrel.hint() + mcp_bridge.hint())", "mcp_bridge.hint()")
rep('res = f"ERRO: {e}"; steps[-1]["status"] = "error"', 'res = f"ERRO: {e}"; steps[-1]["status"] = "error"; steps[-1]["result"] = res', 'steps[-1]["result"] = res')
open(p, "w").write(s); print("v10 aplicado em core_engine.py")
