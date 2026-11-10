#!/usr/bin/env bash
# JAMES - auditoria e preparação do Arch Linux
G=$'\e[32m'; Y=$'\e[33m'; X=$'\e[31m'; N=$'\e[0m'; crit=0
ok(){ echo "${G}[OK]${N} $*"; }; warn(){ echo "${Y}[AVISO]${N} $*"; }; bad(){ echo "${X}[FALTA]${N} $*"; crit=1; }
echo "== 1. Dependências =="
for p in python nodejs npm jq curl git hyprland; do pacman -Qq $p &>/dev/null && ok $p || { [[ $p == hyprland ]] && warn "$p (não instalado via pacman)" || bad "$p -> sudo pacman -S $p"; }; done
pacman -Qq pipewire &>/dev/null || pacman -Qq pulseaudio &>/dev/null && ok "áudio (pipewire/pulseaudio)" || bad "pipewire -> sudo pacman -S pipewire pipewire-pulse"
pacman -Qq alsa-lib &>/dev/null && ok alsa-lib || warn "alsa-lib ausente"
for p in grim wl-clipboard brightnessctl wireplumber ydotool sox; do pacman -Qq $p &>/dev/null && ok $p || warn "$p ausente (opcional)"; done
command -v yay &>/dev/null && ok yay || warn "yay ausente (opcional)"
echo "== 2. Caminhos e permissões =="
mkdir -p ~/.config/james ~/.local/share/james/logs && ok "diretórios criados"
[[ -f ~/.config/james/config.json ]] || echo '{"model":"llama3","ollama_url":"http://localhost:11434","allowed_roots":["'$HOME'"],"lat":-23.55,"lon":-46.63,"voice":true}' > ~/.config/james/config.json
chmod +x "$0"; command -v hyprctl &>/dev/null && hyprctl version &>/dev/null && ok "hyprctl responde" || warn "hyprctl indisponível (rode dentro do Hyprland)"
echo "== 3. Hardware e modelos =="
lspci 2>/dev/null | grep -Ei 'vga|3d' | while read -r l; do echo "  GPU: $l"; done
command -v nvidia-smi &>/dev/null && ok "NVIDIA/CUDA: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)"
[[ -e /dev/kfd ]] && ok "AMD ROCm (/dev/kfd)"
echo "  RAM: $(free -h | awk '/Mem/{print $2" total, "$7" livre"}')"
command -v ollama &>/dev/null && { ok "ollama: $(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')"; } || bad "ollama -> sudo pacman -S ollama (ou ollama-cuda / ollama-rocm)"
pacman -Qq portaudio &>/dev/null && ok portaudio || bad "portaudio -> sudo pacman -S portaudio (microfone)"
for m in vosk-model-small-en-us-0.15 vosk-model-small-pt-0.3; do [[ -d ~/.local/share/james/models/$m ]] && ok "modelo $m" || warn "modelo $m ausente (veja README)"; done
command -v piper &>/dev/null && ok piper || warn "piper ausente (voz grave offline; veja README)"
echo "== 4. Diagnóstico =="
[[ $crit == 0 ]] && echo "${G}Ambiente pronto.${N}" || echo "${X}Há dependências críticas faltando.${N}"
exit $crit
