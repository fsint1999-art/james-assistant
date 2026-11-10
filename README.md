# JAMES — assistente pessoal local

Assistente de IA que roda na sua máquina: modelo via **Ollama**, ativação por voz ("James") offline com **Vosk**, HUD web com núcleo animado, memória, tarefas, agenda, clima, busca web e automações via **n8n** e **MCP (umbrelOS)**. Toda ação que altera algo pede confirmação ("sim/não").

## Suporte por sistema
| Recurso | Linux (Arch/Hyprland) | macOS | Windows |
|---|---|---|---|
| HUD, chat, memória, tarefas, agenda, clima, busca, n8n, MCP | sim | previsto* | previsto* |
| Voz "James" (Vosk) e fala (Piper/Kokoro) | sim | previsto* | previsto* |
| Controle de janelas, volume, brilho, print, área de transferência | sim (Hyprland, wpctl, grim, wl-clipboard) | não | não |
| Serviço em segundo plano | systemd (`install_service.sh`) | manual | manual |

\* Não testado fora do Linux. Os recursos específicos do Linux devolvem um erro claro nos outros sistemas.

## Instalação rápida
Requisitos: Python 3.10+, Node.js 18+, [Ollama](https://ollama.com) com um modelo (`ollama pull llama3.1`).
- **Linux/macOS:** `./scripts/setup.sh` e depois `./scripts/run.sh`
- **Windows (PowerShell):** `.\scripts\setup.ps1` e depois `.\scripts\run.ps1`

Abra http://127.0.0.1:8765. Passo a passo por sistema: [docs/INSTALL.md](docs/INSTALL.md).

## Configuração
Arquivo `~/.config/james/config.json` (Windows: `C:\Users\VOCÊ\.config\james\config.json`); veja `config.example.json`. **Nunca versione esse arquivo: ele guarda tokens.**

## Umbrel (MCP e n8n)
- **MCP (umbrelOS 2.0+):** em *Configurações → Agentes de IA (MCP) → Conectar um agente → Qualquer outro agente*, copie o endereço (`http://SEU_UMBREL/mcp`) e o token (mostrado uma vez) para `mcp.servers.umbrel`. Chamar ferramentas MCP pede confirmação, exceto as listadas em `readonly`.
- **n8n:** crie um fluxo com nó Webhook (POST) e registre em `n8n.workflows`.

## Segurança
Arquivos só dentro de `allowed_roots` (ocultos protegidos, `.bak` antes de editar); comandos só da lista `commands`; Hyprland e controle de tela vêm desligados; o servidor escuta apenas em 127.0.0.1. Modelos de IA podem errar: leia a pergunta de confirmação antes de dizer "sim".

## Licenças de terceiros
Modelos Vosk, vozes Piper/Kokoro e o Ollama têm licenças próprias e **não** estão neste repositório.

Licença do código: MIT.
