#!/usr/bin/env bash
# Instala o JAMES como serviço de usuário: um processo só, sobrevive ao fechar o terminal.
set -e
D="$(cd "$(dirname "$0")" && pwd)"
[[ -x "$D/backend/.venv/bin/python" ]] || { echo "Crie antes o venv: cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt"; exit 1; }
echo "== Compilando o HUD =="; (cd "$D/frontend" && npm install --no-audit --no-fund && npm run build)
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/james.service <<UNIT
[Unit]
Description=JAMES - assistente pessoal local
After=network.target sound.target

[Service]
WorkingDirectory=$D/backend
ExecStart=$D/backend/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8765
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
UNIT
systemctl --user daemon-reload
systemctl --user enable james
systemctl --user import-environment WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE XDG_CURRENT_DESKTOP 2>/dev/null || true
systemctl --user restart james
sleep 2; systemctl --user --no-pager status james | head -5
echo; echo "Pronto: http://127.0.0.1:8765   |   logs: journalctl --user -u james -f"
