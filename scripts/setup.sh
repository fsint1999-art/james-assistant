#!/usr/bin/env bash
# Linux e macOS: cria o venv, instala dependências e compila o HUD.
set -e
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Instale Python 3.10+"; exit 1; }
command -v node >/dev/null || { echo "Instale Node.js 18+"; exit 1; }
python3 -m venv backend/.venv
backend/.venv/bin/pip install -U pip
backend/.venv/bin/pip install -r backend/requirements.txt
(cd frontend && npm install --no-audit --no-fund && npm run build)
mkdir -p ~/.config/james
[ -f ~/.config/james/config.json ] || cp config.example.json ~/.config/james/config.json
echo "Pronto. Edite ~/.config/james/config.json e rode: scripts/run.sh  ->  http://127.0.0.1:8765"
