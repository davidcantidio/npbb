#!/bin/bash
# Script de instalação do OpenClaw em VPS Ubuntu 22.04/24.04
# https://github.com/openclaw/openclaw

set -e

echo "🦞 Instalando OpenClaw no VPS..."

# 1. Instalar Node.js 22 (requisito do OpenClaw)
if ! command -v node &>/dev/null; then
    echo "📦 Instalando Node.js 22..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "⚠️  Node.js $NODE_VERSION detectado. OpenClaw requer Node ≥22."
    echo "   Atualizando para Node.js 22..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ Node.js $(node -v) instalado."

# 2. Instalar OpenClaw globalmente
echo "📦 Instalando OpenClaw..."
sudo npm install -g openclaw@latest

echo "✅ OpenClaw instalado: $(openclaw --version 2>/dev/null || openclaw -v 2>/dev/null || echo 'ok')"

# 3. Rodar onboarding (instala daemon systemd)
echo ""
echo "🚀 Próximo passo: executar o wizard de configuração:"
echo ""
echo "   openclaw onboard --install-daemon"
echo ""
echo "   O wizard vai configurar:"
echo "   - Gateway e workspace"
echo "   - Canais (WhatsApp, Telegram, etc.)"
echo "   - Daemon systemd para manter o serviço rodando"
echo ""
echo "   Depois, inicie o gateway com:"
echo "   openclaw gateway --port 18789 --verbose"
echo ""
echo "   Para acesso remoto, use Tailscale ou SSH tunnel."
echo "   Docs: https://docs.openclaw.ai"
echo ""
