# Instalação por sistema

## Linux (Arch + Hyprland, o ambiente do autor)
```bash
sudo pacman -S python nodejs npm git portaudio sox grim wl-clipboard brightnessctl wireplumber ollama
sudo systemctl enable --now ollama && ollama pull llama3.1
git clone https://github.com/SEU_USUARIO/james-assistant.git && cd james-assistant
./scripts/setup.sh
```
Voz: baixe `vosk-model-small-en-us-0.15` e `vosk-model-small-pt-0.3` (alphacephei.com/vosk/models) para `~/.local/share/james/models/`. Fala (opcional): `backend/.venv/bin/pip install piper-tts` e uma voz `pt_BR` em `~/.local/share/james/voices/`.
Segundo plano: `./install_service.sh`. Hyprland: veja o README (`exec-once ... import-environment`). Debian/Ubuntu: troque `pacman -S` por `apt install python3-venv nodejs npm git libportaudio2 sox`.

## macOS
```bash
brew install python node git ollama portaudio sox
brew services start ollama && ollama pull llama3.1
git clone https://github.com/SEU_USUARIO/james-assistant.git && cd james-assistant
./scripts/setup.sh && ./scripts/run.sh
```
Permita o microfone ao Terminal em *Ajustes → Privacidade*. Controle do sistema (Hyprland etc.) não existe no macOS.

## Windows 10/11 (PowerShell)
```powershell
winget install Python.Python.3.12 OpenJS.NodeJS.LTS Git.Git Ollama.Ollama
# reabra o PowerShell
ollama pull llama3.1
git clone https://github.com/SEU_USUARIO/james-assistant.git; cd james-assistant
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1; .\scripts\run.ps1
```
Modelos de voz em `C:\Users\VOCÊ\.local\share\james\models\`. A fala usa a voz do navegador.

## Teste
`http://127.0.0.1:8765/api/services` deve listar os serviços; no HUD, digite "que horas são".
