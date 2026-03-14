# Instalar OpenClaw no VPS Hostinger (Ubuntu)

## Seu VPS

| Campo | Valor |
|-------|-------|
| **IP** | `187.77.51.117` |
| **Hostname** | srv1407804.hstgr.cloud |
| **SO** | Ubuntu 24.04 LTS |
| **Estado** | running |

## Instalação via SSH

O MCP Hostinger **não executa comandos via SSH** — ele só gerencia o ciclo de vida do VPS (criar, parar, firewall, etc.). Para instalar o OpenClaw, use SSH manualmente.

### 1. Conectar ao VPS

```bash
ssh root@187.77.51.117
# ou, se usar usuário com sudo:
# ssh seu_usuario@187.77.51.117
```

### 2. Baixar e executar o script

**Opção A — Comando direto (mais rápido):**

```bash
# No VPS, execute:
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g openclaw@latest
openclaw onboard --install-daemon
```

**Opção B — Script local (do repositório npbb):**

```bash
# No seu Mac (a partir da pasta npbb):
scp scripts/install-openclaw-vps.sh root@187.77.51.117:/tmp/

# Conecte e execute:
ssh root@187.77.51.117
chmod +x /tmp/install-openclaw-vps.sh
sudo /tmp/install-openclaw-vps.sh
```

### 3. Iniciar o Gateway

```bash
openclaw gateway --port 18789 --verbose
```

Para manter rodando em background (com systemd, após o onboard):

```bash
# O onboard --install-daemon já configura o serviço
systemctl --user status openclaw  # ou similar, conforme o wizard
```

## Acesso remoto

- **Tailscale**: OpenClaw suporta `gateway.tailscale.mode: serve` ou `funnel` para expor o dashboard.
- **SSH tunnel**: `ssh -L 18789:127.0.0.1:18789 root@187.77.51.117` e acesse localmente.

## Script de pós-instalação (Hostinger)

Foi criado um script de pós-instalação na sua conta Hostinger chamado **"OpenClaw Install"**. Ao criar um **novo** VPS com template Ubuntu, você pode anexar esse script para instalar o OpenClaw automaticamente no primeiro boot.

Para VPS já existentes, use as instruções SSH acima.

## Referências

- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Getting Started](https://docs.openclaw.ai/start/getting-started)
- [Docker (alternativa)](https://docs.openclaw.ai/install/docker)
