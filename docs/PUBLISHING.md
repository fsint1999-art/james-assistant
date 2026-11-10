# Publicar no GitHub pelo terminal

## 0. Antes de tudo (checklist)
```bash
cd ~/Documents/james_assistant
git grep -nIE "token|senha|password|192\.168|SEU_NOME" || true   # revise cada ocorrência
ls ~/.config/james/config.json   # fica FORA do repositório; não copie para dentro
```
Comece com repositório **privado**. Se algum token já foi colado em conversa, log ou arquivo versionado, gere um novo no Umbrel (revogue o antigo).

## 1. Instalar git e GitHub CLI
- **Windows:** `winget install Git.Git GitHub.cli`
- **macOS:** `brew install git gh`
- **Arch:** `sudo pacman -S git github-cli` · **Debian/Ubuntu:** `sudo apt install git gh`

## 2. Identidade e login
```bash
git config --global user.name "Seu Nome"
git config --global user.email "voce@exemplo.com"
gh auth login        # escolha GitHub.com > HTTPS > navegador
```

## 3. Criar o repositório e enviar
```bash
git init -b main
git add .
git status            # confirme: sem .venv, node_modules, dist, config.json, .onnx
git commit -m "JAMES: primeira versão"
gh repo create james-assistant --private --source=. --remote=origin --push
```
Sem o `gh`: crie um repositório vazio em github.com e rode
`git remote add origin https://github.com/SEU_USUARIO/james-assistant.git && git push -u origin main`
(a senha é um *Personal Access Token*; ou use SSH: `ssh-keygen -t ed25519`, cole a chave pública em *Settings → SSH keys*, e use `git@github.com:SEU_USUARIO/james-assistant.git`).

## 4. Tornar público (quando estiver revisado)
```bash
gh repo edit --visibility public --accept-visibility-change-consequences
```

## 5. Atualizações
```bash
git add -A && git commit -m "descrição" && git push
```
