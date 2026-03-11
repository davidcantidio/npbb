# PRD — Migração do NPBB para VPS Hostinger

**Repositório:** `davidcantidio/npbb` | **Branch base:** `main`  
**Status:** Proposta  
**Última atualização:** 2026-03-03  
**Owner:** PM

---

## 1. Contexto e Problema

### 1.1 Stack atual

| Camada | Serviço atual | Problema |
|---|---|---|
| Backend (FastAPI) | Render.com (free/starter tier) | Cold starts, latência alta |
| Frontend (React/Vite) | Cloudflare Pages + Wrangler | Build lento, overhead de Workers desnecessário para SPA estática |
| Banco de dados | Supabase (Postgres gerenciado) | Latência de rede extra (hop adicional entre backend e DB), limitações de conexão no free tier |
| DNS/Proxy | Cloudflare | Mantido apenas para DNS; camada de Workers adiciona latência sem benefício real |
| CI/CD | GitHub Actions (`.github/workflows/ci.yml`) | Funcional, mantido |
| Infra como código | `Infra/production/docker-compose.yml` + Nginx templates | Já existe scaffold para VPS — **sinaliza que a migração foi parcialmente planejada** |

### 1.2 Problemas identificados

- **Latência end-to-end elevada:** cada request atravessa Cloudflare CDN → Render → Supabase (região diferente), resultando em 3 hops de rede antes de qualquer resposta.
- **Wrangler é overhead sem benefício:** o projeto não usa Workers, KV, D1 ou nenhum produto de edge da Cloudflare. O `.wrangler/cache` no repositório indica uso residual/legado que pode ser eliminado.
- **Supabase free tier tem limite de conexões simultâneas** e latência variável fora de horário de pico.
- **Render free tier hiberna** instâncias após inatividade — cold start de 30–60s na primeira requisição do dia.
- **O scaffold de VPS já existe** em `Infra/production/` (docker-compose, Nginx com templates TLS, scripts de backup para Postgres) — o projeto foi desenhado para ser executado em VPS, mas nunca migrado.

### 1.3 Objetivo

Consolidar toda a stack em um único VPS na Hostinger, eliminando Render, Supabase e Wrangler. O resultado é uma arquitetura **colocada** (backend + frontend + banco na mesma máquina), com latência previsível, custo fixo e zero cold starts.

---

## 2. Arquitetura Alvo

```
                        Internet
                            │
                    ┌───────▼────────┐
                    │  Cloudflare    │  ← DNS only (sem proxy/Workers)
                    │  (DNS A record)│
                    └───────┬────────┘
                            │ HTTPS :443
                    ┌───────▼────────────────────────────┐
                    │           VPS Hostinger             │
                    │                                     │
                    │  ┌──────────────────────────────┐   │
                    │  │         Nginx                │   │
                    │  │  (TLS termination + reverse  │   │
                    │  │   proxy + static frontend)   │   │
                    │  └──────┬──────────────┬────────┘   │
                    │         │              │             │
                    │  ┌──────▼──────┐  ┌───▼──────────┐ │
                    │  │  Backend    │  │   Frontend   │ │
                    │  │  FastAPI    │  │   dist/      │ │
                    │  │  :8000      │  │   (static)   │ │
                    │  └──────┬──────┘  └──────────────┘ │
                    │         │                           │
                    │  ┌──────▼──────┐                   │
                    │  │  Postgres   │                   │
                    │  │  :5432      │                   │
                    │  └─────────────┘                   │
                    │                                     │
                    │  ┌──────────────────────────────┐   │
                    │  │  Backup container (cron)     │   │
                    │  │  pg_dump → armazenamento ext │   │
                    │  └──────────────────────────────┘   │
                    └─────────────────────────────────────┘
```

### 2.1 Serviços no docker-compose

Todos os serviços sobem via `docker-compose.yml` em `Infra/production/`:

| Serviço | Imagem | Porta interna | Notas |
|---|---|---|---|
| `backend` | `./backend/Dockerfile` | 8000 | variáveis de `.env` |
| `frontend` | build estático servido pelo Nginx | — | `npm run build` no CI |
| `db` | `postgres:16-alpine` | 5432 | volume persistente em `/var/lib/postgresql/data` |
| `nginx` | `./Infra/production/nginx/Dockerfile` | 80, 443 | TLS via Let's Encrypt / Certbot |
| `backup` | `./Infra/production/backup/Dockerfile` | — | cron diário com `pg_dump` |

### 2.2 O que é eliminado

| Serviço | Eliminado por |
|---|---|
| Render.com | Backend roda no VPS via Docker |
| Supabase | Postgres roda localmente no VPS |
| Cloudflare Workers / Wrangler | Frontend é SPA estática servida pelo Nginx |
| `.wrangler/` no repo | Deletado + adicionado ao `.gitignore` |

### 2.3 O que é mantido

- **Cloudflare como DNS** (registro A apontando para IP do VPS) — opcional, mas recomendado para proteção DDoS básica com proxy desabilitado (modo DNS-only).
- **GitHub Actions** para CI (testes + build) — o deploy passa a ser via `ssh + docker-compose pull && up`.
- **Nginx com TLS** — já existe scaffold em `Infra/production/nginx/conf.d/` com templates `api.tls.conf.template` e `app.tls.conf.template`.

---

## 3. Especificação do VPS Hostinger

### 3.1 Plano mínimo recomendado

| Recurso | Mínimo | Recomendado |
|---|---|---|
| vCPU | 2 | 2–4 |
| RAM | 4 GB | 8 GB |
| Disco | 40 GB SSD | 80 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Localização | São Paulo (se disponível) | São Paulo ou Miami |

### 3.2 Software a instalar no VPS

- Docker Engine + Docker Compose v2
- Certbot (Let's Encrypt) para TLS automático
- `fail2ban` para proteção SSH básica
- `ufw` com portas 22, 80, 443 liberadas

---

## 4. Plano de Migração

### Fase 1 — Preparação da Infra (sem downtime)

1. Provisionar VPS no Hostinger com Ubuntu 22.04.
2. Instalar Docker Engine, Docker Compose v2, Certbot, ufw, fail2ban.
3. Configurar usuário não-root com acesso sudo e chave SSH.
4. Completar/auditar `Infra/production/docker-compose.yml`:
   - Confirmar serviços `backend`, `db`, `nginx`, `backup`.
   - Adicionar `healthcheck` em `backend` e `db`.
   - Garantir `restart: unless-stopped` em todos os serviços.
5. Completar templates Nginx em `Infra/production/nginx/conf.d/`:
   - `api.tls.conf.template` — reverse proxy para backend `:8000`.
   - `app.tls.conf.template` — servir `dist/` do frontend.
   - Configurar `render.sh` para substituir variáveis de ambiente nos templates.
6. Criar `Infra/production/.env.example` com todas as variáveis necessárias:
   - `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS`, `DOMAIN`, `CERTBOT_EMAIL`.
7. Criar script `Infra/production/scripts/init-vps.sh` — instalação idempotente de dependências.

### Fase 2 — Migração do banco de dados

1. Fazer dump completo do Supabase:
   ```bash
   pg_dump $SUPABASE_DATABASE_URL -Fc -f npbb_$(date +%Y%m%d).dump
   ```
2. Subir apenas o container `db` no VPS:
   ```bash
   docker-compose up -d db
   ```
3. Restaurar dump no Postgres local:
   ```bash
   pg_restore -d $LOCAL_DATABASE_URL npbb_YYYYMMDD.dump
   ```
4. Executar `alembic upgrade head` contra o banco local para garantir que migrations estão aplicadas.
5. Validar contagens de tabelas críticas (leads, eventos, usuarios) entre Supabase e Postgres local.

### Fase 3 — Deploy do backend

1. Construir imagem do backend e subir no VPS:
   ```bash
   docker-compose up -d backend
   ```
2. Apontar `DATABASE_URL` do backend para o container `db` local (`postgresql://user:pass@db:5432/npbb`).
3. Executar smoke tests via `curl` nos endpoints críticos (`/auth/me`, `/leads`, `/dashboard/leads`).
4. Manter Supabase ativo ainda — não desligar até validação completa.

### Fase 4 — Deploy do frontend e Nginx

1. Executar `npm run build` no CI (GitHub Actions) e copiar `dist/` para o VPS via `scp` ou volume Docker.
2. Emitir certificado TLS com Certbot:
   ```bash
   certbot certonly --nginx -d seudominio.com.br -d www.seudominio.com.br
   ```
3. Subir Nginx com templates TLS preenchidos:
   ```bash
   docker-compose up -d nginx
   ```
4. Testar HTTPS no domínio de produção.

### Fase 5 — Cutover de DNS e limpeza

1. Alterar registro DNS A para o IP do VPS (TTL baixo antes do cutover: 60s).
2. Monitorar logs Nginx e backend por 30 minutos após o cutover.
3. Após estabilização (≥ 24h sem incidentes):
   - Pausar projeto no Render.
   - Pausar projeto no Supabase.
   - Deletar `.wrangler/` do repositório e adicionar ao `.gitignore`.
   - Remover `render.yaml` ou arquivar em `docs/legacy/`.
4. Após 7 dias sem rollback: encerrar contas Render e Supabase.

---

## 5. CI/CD Pós-migração

O pipeline do GitHub Actions deve ser atualizado para:

```yaml
# .github/workflows/deploy.yml (novo job)
deploy:
  needs: [test]
  runs-on: ubuntu-latest
  steps:
    - name: Build frontend
      run: cd frontend && npm ci && npm run build

    - name: Copy frontend dist to VPS
      run: scp -r frontend/dist/ $VPS_USER@$VPS_HOST:/srv/npbb/frontend/dist/

    - name: Deploy via SSH
      run: |
        ssh $VPS_USER@$VPS_HOST "
          cd /srv/npbb/Infra/production &&
          docker-compose pull backend &&
          docker-compose up -d --no-deps backend &&
          docker-compose exec backend alembic upgrade head
        "
```

Segredos a adicionar no GitHub (`Settings → Secrets`): `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`.

---

## 6. Backup e Recuperação

O container `backup` já existe em `Infra/production/backup/`. Deve ser configurado para:

- Executar `pg_dump` diariamente via cron (`Infra/production/backup/crontab`).
- Compactar e enviar dump para armazenamento externo (S3, Backblaze B2 ou volume Hostinger).
- Reter últimos 7 dumps diários + 4 dumps semanais.
- Script `backup.sh` deve registrar sucesso/falha em log acessível via `docker logs backup`.

Critério de recuperação: a partir de um dump, deve ser possível restaurar o sistema completo em ≤ 30 minutos.

---

## 7. Estrutura de Governança do Projeto

### 7.1 Árvore de diretórios obrigatória

```
PROJETOS/
├── COMUM/
│   ├── DECISION-PROTOCOL.md
│   ├── WORK-ORDER-SPEC.md
│   ├── SPRINT-LIMITS.md
│   └── GOV-SCRUM.md
│
├── LEAD-ETL-FUSION/
│   └── ...
│
└── MIGRACAO-VPS-HOSTINGER/
    ├── prd_vps_migration.md
    ├── feito/
    ├── F1-PREPARACAO-INFRA/
    │   ├── EPICS.md
    │   ├── EPIC-F1-01-PROVISIONAMENTO-VPS.md
    │   └── EPIC-F1-02-DOCKER-COMPOSE-E-NGINX.md
    ├── F2-MIGRACAO-BANCO/
    │   ├── EPICS.md
    │   ├── EPIC-F2-01-DUMP-E-RESTORE-SUPABASE.md
    │   └── EPIC-F2-02-VALIDACAO-INTEGRIDADE-DADOS.md
    ├── F3-DEPLOY-BACKEND-FRONTEND/
    │   ├── EPICS.md
    │   ├── EPIC-F3-01-DEPLOY-BACKEND-VPS.md
    │   ├── EPIC-F3-02-DEPLOY-FRONTEND-NGINX.md
    │   └── EPIC-F3-03-TLS-E-DNS-CUTOVER.md
    └── F4-CICD-E-LIMPEZA/
        ├── EPICS.md
        ├── EPIC-F4-01-PIPELINE-DEPLOY-SSH.md
        ├── EPIC-F4-02-BACKUP-AUTOMATIZADO.md
        └── EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md
```

Diretriz operacional: quando uma fase atingir o gate de saída e tiver evidência consolidada, sua pasta deve ser movida para `PROJETOS/MIGRACAO-VPS-HOSTINGER/feito/`.

### 7.2 Gates de saída por fase

| Fase | Gate de saída |
|---|---|
| F1 | `docker-compose up -d` sobe todos os containers saudáveis no VPS; Nginx responde em HTTP |
| F2 | Contagem de registros entre Supabase e Postgres local é idêntica; `alembic upgrade head` sem erros |
| F3 | HTTPS funcionando no domínio de produção; endpoints `/auth/me` e `/leads` respondem em < 500ms |
| F4 | `make ci-quality: PASS`; backup roda e gera arquivo; Render e Supabase pausados; `validation-summary.md` com decisão `promote` |

### 7.3 Épico obrigatório de coerência normativa (F4-03)

Issues obrigatórias:

**ISSUE-F4-03-01 — Validar remoção completa de dependências legadas**
- Given: `.wrangler/`, `render.yaml` ou qualquer referência a `SUPABASE_URL` em arquivos de produção, When: `make eval-integrations` roda, Then: gate falha.

**ISSUE-F4-03-02 — Validar saúde dos containers pós-cutover**
- Given: todos os containers rodando no VPS, When: healthcheck automático roda, Then: `backend`, `db`, `nginx` e `backup` estão `healthy`.

**ISSUE-F4-03-03 — Consolidar evidência de fase**
- Artifact: `artifacts/phase-f4/validation-summary.md` com status de todas as fases, latência medida pós-migração e decisão `promote | hold`.

---

## 8. Critérios de Aceite do PRD

- [ ] VPS provisionado com Docker e Nginx funcionando
- [ ] `docker-compose up -d` sobe todos os serviços sem erro
- [ ] Postgres local contém todos os dados migrados do Supabase (contagem validada por tabela)
- [ ] Frontend acessível via HTTPS no domínio de produção
- [ ] Backend responde em < 300ms para endpoints listados (medido de São Paulo)
- [ ] Certificado TLS válido (Let's Encrypt, renovação automática)
- [ ] Backup diário rodando e gerando arquivo
- [ ] `.wrangler/` removido do repositório
- [ ] `render.yaml` arquivado em `docs/legacy/`
- [ ] Pipeline GitHub Actions fazendo deploy automático em push para `main`
- [ ] Render e Supabase pausados

---

## 9. Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Perda de dados na migração do banco | Baixa | Manter Supabase ativo até ≥ 24h de validação; dump antes de qualquer cutover |
| Downtime durante cutover de DNS | Média | TTL de 60s antes do cutover; rollback em < 5min revertendo registro A |
| Certbot falha ao emitir certificado | Baixa | Testar com `--staging` antes de emitir certificado real |
| Disco do VPS insuficiente para dados + backups | Média | Monitorar uso com `df -h`; configurar alerta em 80% de uso |
| Variáveis de ambiente incorretas no `.env` de produção | Alta | Criar `Infra/production/.env.example` com todos os campos documentados; validar no startup do backend |
| Cold start do backend no container | Baixa | `restart: unless-stopped` + healthcheck garante que container nunca hiberna |
| Wrangler deixou dependências no código frontend | Média | Auditar `package.json` e `vite.config.ts` por referências a `@cloudflare/` antes da Fase 4 |
