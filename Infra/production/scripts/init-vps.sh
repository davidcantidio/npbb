#!/usr/bin/env bash
set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_ROOT="${APP_ROOT:-/opt/npbb}"
SSH_PORT="${SSH_PORT:-22}"

APP_DIR="${APP_ROOT}/app"
ENV_DIR="${APP_ROOT}/env"
BACKUP_DIR="${APP_ROOT}/backups/postgres"
BACKUP_ARCHIVE_DIR="${APP_ROOT}/backups/archive"
CERTS_DIR="/etc/letsencrypt"
SSH_DIR="/home/${DEPLOY_USER}/.ssh"
DOCKER_KEYRING="/etc/apt/keyrings/docker.gpg"
DOCKER_LIST="/etc/apt/sources.list.d/docker.list"

log() {
  echo "[init-vps] $*"
}

fail() {
  echo "[init-vps] $*" >&2
  exit 1
}

if [[ "${EUID}" -ne 0 ]]; then
  fail "execute este script como root ou com sudo."
fi

if [[ ! -r /etc/os-release ]]; then
  fail "nao foi possivel identificar o sistema operacional."
fi

source /etc/os-release

if [[ "${ID:-}" != "ubuntu" ]]; then
  fail "este bootstrap foi escrito para Ubuntu 22.04 LTS."
fi

export DEBIAN_FRONTEND=noninteractive

log "instalando dependencias base"
apt-get update
apt-get install -y ca-certificates curl git rsync certbot ufw fail2ban gnupg

install -m 0755 -d /etc/apt/keyrings
if [[ ! -f "${DOCKER_KEYRING}" ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o "${DOCKER_KEYRING}"
fi
chmod a+r "${DOCKER_KEYRING}"

cat > "${DOCKER_LIST}" <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=${DOCKER_KEYRING}] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable
EOF

log "instalando docker engine e plugins"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

if ! id -u "${DEPLOY_USER}" >/dev/null 2>&1; then
  log "criando usuario ${DEPLOY_USER}"
  adduser --disabled-password --gecos "" "${DEPLOY_USER}"
fi

usermod -aG docker "${DEPLOY_USER}"

install -d -m 0755 "${APP_DIR}" "${ENV_DIR}" "${BACKUP_DIR}" "${BACKUP_DIR}/incoming" "${BACKUP_ARCHIVE_DIR}"
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_ROOT}"
install -d -m 0700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "${SSH_DIR}"

log "habilitando servicos de host"
systemctl enable --now docker
systemctl enable --now fail2ban

log "configurando ufw"
ufw allow "${SSH_PORT}/tcp"
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

cat <<EOF
[init-vps] bootstrap concluido
[init-vps] usuario padrao: ${DEPLOY_USER}
[init-vps] raiz da aplicacao: ${APP_ROOT}
[init-vps] proximos passos:
[init-vps] 1. copie sua chave publica para ${SSH_DIR}/authorized_keys
[init-vps] 2. valide acesso SSH por chave com ${DEPLOY_USER}
[init-vps] 3. apos validar o acesso, endureca sshd para desabilitar senha e evitar uso rotineiro de root
EOF
