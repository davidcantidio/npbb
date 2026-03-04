# Deploy Hostinger VPS

Guia oficial para publicar o NPBB em uma VPS Hostinger com `Docker Compose`, `Postgres` local, frontend estatico servido diretamente pelo `nginx` e TLS com `Certbot` / Let's Encrypt.

Na stack atual, o servico `nginx` cumpre o papel de edge da arquitetura.

## 1) Layout esperado na VPS

```bash
/opt/npbb/app                  # clone do repositorio
/opt/npbb/env/.env.production  # variaveis de ambiente
/opt/npbb/backups/postgres     # dumps locais
/opt/npbb/backups/archive      # copia externa montada no host
/etc/letsencrypt               # certificados do Certbot
```

## 2) Bootstrap inicial da VPS

Use `root` apenas para o bootstrap inicial.

```bash
apt-get update
apt-get install -y git
rm -rf /root/npbb-bootstrap
git clone <repo> /root/npbb-bootstrap
bash /root/npbb-bootstrap/Infra/production/scripts/init-vps.sh
```

Esse bootstrap:
- instala dependencias base de host, Docker e Docker Compose plugin;
- cria `deploy`, adiciona ao grupo `docker` e provisiona diretorios em `/opt/npbb`;
- habilita `ufw` (`22/80/443`) e `fail2ban`.

Passos obrigatorios apos o bootstrap:
- adicionar sua chave SSH em `/home/deploy/.ssh/authorized_keys`;
- validar login com `deploy`;
- desabilitar login por senha assim que o acesso por chave estiver funcionando;
- montar o volume externo de backup em `/opt/npbb/backups/archive`.

Nao use root como fluxo normal de deploy ou operacao.

## 3) Preparar o repositorio e o env

```bash
sudo -u deploy git clone <repo> /opt/npbb/app
cd /opt/npbb/app
cp Infra/production/.env.example /opt/npbb/env/.env.production
mkdir -p /opt/npbb/app/frontend/dist
```

Edite `/opt/npbb/env/.env.production`:

- na fase IP, mantenha:
  - `DEPLOY_MODE=ip`
  - `ENABLE_TLS=false`
  - `VITE_API_BASE_URL=http://SEU_IP/api`
  - `FRONTEND_ORIGIN=http://SEU_IP`
  - `PUBLIC_APP_BASE_URL=http://SEU_IP`
  - `PUBLIC_LANDING_BASE_URL=http://SEU_IP`
  - `PUBLIC_API_DOC_URL=http://SEU_IP/api/docs`
  - `PASSWORD_RESET_URL=http://SEU_IP/reset-password`
  - `API_ROOT_PATH=/api`
- para o dominio final:
  - `DEPLOY_MODE=domain`
  - `ENABLE_TLS=true`
  - `APP_DOMAIN=app.seu-dominio.com`
  - `VITE_API_BASE_URL=https://app.seu-dominio.com/api`
  - `FRONTEND_ORIGIN=https://app.seu-dominio.com`
  - `PUBLIC_APP_BASE_URL=https://app.seu-dominio.com`
  - `PUBLIC_LANDING_BASE_URL=https://app.seu-dominio.com`
  - `PUBLIC_API_DOC_URL=https://app.seu-dominio.com/api/docs`
  - `PASSWORD_RESET_URL=https://app.seu-dominio.com/reset-password`
  - `COOKIE_SECURE=true`
- configure `POSTGRES_PASSWORD`, `SECRET_KEY`, `PASSWORD_RESET_TOKEN_SECRET`;
- configure `SMTP_*` da Hostinger;
- configure `BACKUP_EXTERNAL_HOST_DIR=/opt/npbb/backups/archive`;
- configure `SMOKE_LOGIN_EMAIL` e `SMOKE_LOGIN_PASSWORD` se quiser smoke autenticado.

## 4) Emitir certificado TLS

Depois que o DNS estiver apontando para a VPS:

```bash
certbot certonly --standalone -d app.seu-dominio.com
```

Use os paths gerados pelo Certbot no env:

```bash
TLS_CERT_PATH=/etc/letsencrypt/live/app.seu-dominio.com/fullchain.pem
TLS_KEY_PATH=/etc/letsencrypt/live/app.seu-dominio.com/privkey.pem
CERTS_DIR=/etc/letsencrypt
```

## 5) Deploy manual da stack

No host:

```bash
cd /opt/npbb/app
./scripts/deploy_vps.sh --check-only /opt/npbb/env/.env.production
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
./scripts/check_vps_health.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

O script:
- valida o env e contratos da stack no preflight;
- exige `frontend/dist/index.html` sincronizado no host;
- faz `docker compose config`;
- builda `backend`, `nginx` e `backup`;
- sobe `db`, `backend`, `nginx` e `backup`.

## 6) Deploy automatico via GitHub Actions

Segredos obrigatorios em `Settings -> Secrets and variables -> Actions`:
- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_PORT`
- `VPS_DEPLOY_PATH`

O workflow `.github/workflows/deploy.yml`:
- dispara apenas quando o workflow `CI` conclui com sucesso em `main`;
- faz checkout do `head_sha` aprovado;
- builda `frontend/dist`;
- sincroniza `frontend/dist` para `${VPS_DEPLOY_PATH}/frontend/dist`;
- executa `git checkout --force <sha>` no host, `./scripts/deploy_vps.sh`, `alembic upgrade head`, `./scripts/check_vps_health.sh` e `./scripts/smoke_vps.sh`.

## 7) DNS e Cloudflare

Use Cloudflare apenas como DNS:

1. crie registro `A` para `app` apontando para o IP da VPS;
2. deixe o registro em modo `DNS only`;
3. mantenha o SSL/TLS do Cloudflare desabilitado ou em modo compativel com origem direta, sem proxy.

## 8) Rollback por commit SHA

Rollback manual:

```bash
cd /opt/npbb/app
git fetch origin
git checkout --force <SHA_ANTERIOR>
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
docker compose --env-file /opt/npbb/env/.env.production -f Infra/production/docker-compose.yml exec -T backend alembic upgrade head
./scripts/check_vps_health.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

Rollback via GitHub Actions:
- reexecute o workflow de deploy apontando para um `head_sha` anterior em `main`;
- confirme que o `dist` sincronizado e o checkout remoto correspondem ao mesmo SHA.

## 9) Operacao diaria

```bash
cd /opt/npbb/app
git pull
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
./scripts/check_vps_health.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
./scripts/restore_backup_drill.sh /opt/npbb/env/.env.production
```
