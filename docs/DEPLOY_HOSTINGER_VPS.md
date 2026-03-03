# Deploy Hostinger VPS

Guia oficial para publicar o NPBB em uma VPS Hostinger com `Docker Compose`, `Postgres` local e `Cloudflare` apenas na borda no cutover final.

## 1) Layout esperado na VPS

```bash
/opt/npbb/app                  # clone do repositorio
/opt/npbb/env/.env.production  # variaveis de ambiente
/opt/npbb/backups/postgres     # dumps locais
/opt/npbb/certs                # certificados origin do Cloudflare
```

## 2) Bootstrap inicial da VPS

Com acesso `root`:

```bash
apt-get update
apt-get install -y ca-certificates curl git ufw

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

. /etc/os-release
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
install -o deploy -g deploy -d /opt/npbb/app /opt/npbb/env /opt/npbb/backups/postgres /opt/npbb/certs

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

Recomendado apos o bootstrap:
- adicionar sua chave SSH em `/home/deploy/.ssh/authorized_keys`;
- desabilitar login por senha assim que o acesso por chave estiver funcionando.

## 3) Preparar o repositorio e o env

```bash
sudo -u deploy git clone <repo> /opt/npbb/app
cd /opt/npbb/app
cp Infra/production/.env.example /opt/npbb/env/.env.production
```

Edite `/opt/npbb/env/.env.production`:
- na fase IP, mantenha:
  - `DEPLOY_MODE=ip`
  - `ENABLE_TLS=false`
  - `VITE_API_BASE_URL=http://187.77.51.117/api`
  - `FRONTEND_ORIGIN=http://187.77.51.117`
  - `PUBLIC_APP_BASE_URL=http://187.77.51.117`
  - `PUBLIC_LANDING_BASE_URL=http://187.77.51.117`
  - `PUBLIC_API_DOC_URL=http://187.77.51.117/api/docs`
  - `PASSWORD_RESET_URL=http://187.77.51.117/reset-password`
  - `API_ROOT_PATH=/api`
- configure `POSTGRES_PASSWORD`, `SECRET_KEY`, `PASSWORD_RESET_TOKEN_SECRET`;
- configure `SMTP_*` da Hostinger;
- opcionalmente configure `SMOKE_LOGIN_EMAIL` e `SMOKE_LOGIN_PASSWORD` para smoke autenticado.

## 4) Deploy da stack

No host:

```bash
cd /opt/npbb/app
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
```

O script:
- valida o env;
- faz `docker compose config`;
- builda `api`, `web` e `edge`;
- sobe `postgres`, `api`, `web`, `edge` e `backup`.

## 5) Validacao da fase IP

```bash
cd /opt/npbb/app
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

Checks obrigatorios:
- `http://187.77.51.117/api/health`
- `http://187.77.51.117/api/docs`
- `http://187.77.51.117/`
- `http://187.77.51.117/eventos`
- login e rotas autenticadas, se `SMOKE_LOGIN_*` estiverem preenchidos

## 6) Restore de banco para ensaio ou cutover

Veja o runbook em [RUNBOOK_RESTORE_POSTGRES_VPS.md](/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/docs/RUNBOOK_RESTORE_POSTGRES_VPS.md).

## 7) Cutover final para dominio + Cloudflare

Quando o dominio estiver pronto:

1. Copie o certificado origin do Cloudflare para `/opt/npbb/certs/origin.crt` e `/opt/npbb/certs/origin.key`.
2. Atualize o env:
   - `DEPLOY_MODE=domain`
   - `ENABLE_TLS=true`
   - `APP_DOMAIN=app.seu-dominio.com`
   - `API_DOMAIN=api.seu-dominio.com`
   - `VITE_API_BASE_URL=https://api.seu-dominio.com`
   - `FRONTEND_ORIGIN=https://app.seu-dominio.com`
   - `PUBLIC_APP_BASE_URL=https://app.seu-dominio.com`
   - `PUBLIC_LANDING_BASE_URL=https://app.seu-dominio.com`
   - `PUBLIC_API_DOC_URL=https://api.seu-dominio.com/docs`
   - `PASSWORD_RESET_URL=https://app.seu-dominio.com/reset-password`
   - `API_ROOT_PATH=`
   - `COOKIE_SECURE=true`
3. Refaça o deploy:

```bash
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```

4. No Cloudflare:
   - crie `A` records para `app` e `api` apontando para `187.77.51.117`;
   - marque ambos como `proxied`;
   - SSL/TLS em `Full (strict)`.

## 8) Operacao diaria

Deploy recorrente:

```bash
cd /opt/npbb/app
git pull
./scripts/deploy_vps.sh /opt/npbb/env/.env.production
./scripts/smoke_vps.sh /opt/npbb/env/.env.production
```
