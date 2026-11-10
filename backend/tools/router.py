"""Atalhos determinísticos para comandos de computador (sem depender do LLM)."""
import re, shutil
W = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
     "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100}
ALIAS = {"navegador": ["firefox", "opera", "chromium", "google-chrome-stable"], "terminal": ["kitty", "alacritty", "foot", "wezterm"],
         "arquivos": ["thunar", "nautilus", "dolphin", "pcmanfm"]}
def num(s):
    s = s.strip()
    if s.isdigit(): return int(s)
    tot, hit = 0, False
    for tok in s.split():
        if tok == "e": continue
        if tok not in W: return None
        tot += W[tok]; hit = True
    return tot if hit else None
def _app(name):
    n = re.sub(r"[^a-z0-9\- ]", "", name.lower()).strip().replace(" ", "")
    return next((c for c in ALIAS.get(n, [n]) if n and shutil.which(c)), None)
def match(text):
    t = text.lower().strip().rstrip(".!?,")
    if m := re.search(r"(?:v[aá]|vai|ir|troque|trocar|mude|mudar)\s+(?:para|pra|pro|de)?\s*(?:o\s+|a\s+)?(?:workspace|[aá]rea de trabalho|desktop)\s+(?:n[uú]mero\s+)?([\w ]+)$", t):
        n = num(m.group(1)); return ("hyprland_control", {"action": "goto_workspace", "id": n}) if n and 1 <= n <= 10 else None
    if m := re.search(r"volume\s+(?:em|para|a|pra)?\s*([\w ]+)$", t):
        n = num(m.group(1)); return ("system_control", {"action": "volume_set", "percent": n}) if n is not None else None
    if re.search(r"espa[cç]o\s+(?:em|no|do|de)\s+disco|disco\s+(?:livre|cheio)", t): return ("system_control", {"action": "disk_summary"})
    if re.search(r"mem[óo]ria\s+(?:livre|ram|dispon[ií]vel)|uso de mem[óo]ria", t): return ("system_control", {"action": "ram_summary"})
    if re.search(r"(?:aumente|suba|aumenta|sobe)\s+(?:o\s+)?volume", t): return ("system_control", {"action": "volume_step", "delta": 10})
    if re.search(r"(?:abaixe|diminua|baixe|reduza)\s+(?:o\s+)?volume", t): return ("system_control", {"action": "volume_step", "delta": -10})
    if re.search(r"(?:silencie|mute|tire)\s+(?:o\s+)?(?:som|[aá]udio)|desligue o som", t): return ("system_control", {"action": "mute_toggle"})
    if m := re.search(r"brilho\s+(?:em|para|a|pra)?\s*([\w ]+)$", t):
        n = num(m.group(1)); return ("system_control", {"action": "brightness_set", "percent": n}) if n is not None else None
    if re.search(r"(?:tire|tira|fa[cç]a|capture|capturar)\s+(?:um\s+|uma\s+)?(?:print|captura|screenshot)", t): return ("system_control", {"action": "screenshot"})
    if re.search(r"(?:feche|fechar)\s+(?:a\s+)?(?:janela|aplicativo)(?:\s+ativa)?$", t): return ("hyprland_control", {"action": "close_active"})
    if re.search(r"(?:quais|liste|mostre|que)\s+.*janelas", t): return ("hyprland_control", {"action": "windows"})
    if m := re.search(r"(?:abra|abrir|inicie|lance|execute)\s+(?:(?:o|a)\s+)?(?:(?:aplicativo|programa)\s+)?([\w\- ]+)$", t):
        app = _app(m.group(1)); return ("hyprland_control", {"action": "launch", "app": app}) if app else None
    return None
