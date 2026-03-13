---
doc_id: "PRD-QR-GEN.md"
version: "0.1"
status: "draft"
intake_kind: "problem"
owner: "PM"
last_updated: "2026-03-13"
origin_intake: "INTAKE-QR-GEN.md"
delivery_surface: "fullstack-module"
business_domain: "landing-pages"
product_type: "platform-capability"
change_type: "correcao-estrutural"
criticality: "alta"
---

# PRD — QR-GEN — Correção de URL Base em QR Codes

## Cabeçalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | problem (remediação controlada) |
| Origem do intake | [INTAKE-QR-GEN.md](./INTAKE.md) |
| Superfície afetada | backend (urls, landing_pages), banco de dados |
| Domínio | landing-pages |
| Criticidade | alta |

---

## 1. Objetivo e Contexto

Este PRD define a correção estrutural para garantir que QR codes gerados pela plataforma NPBB apontem para a URL base correta do ambiente de destino — `app.npbb.com.br` em produção e `localhost` apenas em desenvolvimento local — sem hardcode e sem necessidade de regeração manual após o deploy.

O problema foi identificado no [INTAKE-QR-GEN.md](./INTAKE.md): a URL base é resolvida via variáveis de ambiente, mas quando `PUBLIC_APP_BASE_URL` e `FRONTEND_ORIGIN` não estão configuradas (cenário típico em dev local), o fallback é `http://localhost:5173`. O backend persiste essa URL nas colunas `ativacao.landing_url` e `ativacao.qr_code_url` (data URL do SVG), gerando registros inválidos para produção.

---

## 2. Problema e Evidência Técnica

### 2.1 Causa raiz

O módulo `backend/app/utils/urls.py` implementa `get_public_app_base_url()` com a seguinte ordem de preferência:

1. `PUBLIC_APP_BASE_URL` (variável de ambiente)
2. `FRONTEND_ORIGIN` (primeiro origin)
3. Fallback: `http://localhost:5173`

Em ambiente local sem essas variáveis configuradas, o fallback localhost é usado. O serviço `landing_pages.hydrate_ativacao_public_urls()` chama `build_ativacao_public_urls()` e persiste `landing_url` e `qr_code_url` (SVG codificado) na tabela `ativacao`. O QR code gerado encapsula o link persistido. Registros criados ou atualizados em dev ficam com URL local no banco.

### 2.2 Componentes afetados

- `backend/app/utils/urls.py` — resolução de URL base
- `backend/app/services/landing_pages.py` — `hydrate_ativacao_public_urls`
- Tabela `ativacao` — colunas `landing_url`, `qr_code_url`, `url_promotor`
- Frontend — renderização do QR a partir do link persistido (sem alteração de lógica)

### 2.3 Impacto

- QR codes distribuídos antes do go-live precisarão ser regerados ou os registros no banco corrigidos
- Se registros com URL local chegarem a produção, usuários finais receberão links quebrados ao escanear

---

## 3. Escopo

### 3.1 Dentro

- Garantir que a resolução de URL base em produção use explicitamente `PUBLIC_APP_BASE_URL` ou equivalente documentado
- Documentar e validar a configuração obrigatória de `PUBLIC_APP_BASE_URL` no ambiente de produção
- Levantar o volume de registros `ativacao` com `landing_url` ou `url_promotor` contendo localhost
- Implementar migração ou script de correção para registros existentes com URL incorreta
- Adicionar verificação/safeguard que impeça ou alerte quando `landing_url` for persistida com host local em ambiente de produção (opcional, conforme fase)
- Manter o fluxo de desenvolvimento local funcional (localhost continua válido quando env vars não estiverem configuradas)

### 3.2 Fora

- Suporte a ambientes de staging ou homologação
- Revisão de outros pontos da plataforma onde base URL aparece
- Redesign do módulo de QR code
- Alteração da lógica de renderização do QR no frontend (usa o link já persistido)

---

## 4. Restrições e Riscos

### 4.1 Restrições

- A correção não pode quebrar o fluxo de desenvolvimento local
- Registros já persistidos com URL incorreta devem ser tratados (migração ou limpeza) — não podem ser ignorados silenciosamente
- Produção deve ter `PUBLIC_APP_BASE_URL` configurado antes do go-live

### 4.2 Riscos principais

| Risco | Mitigação |
|---|---|
| QR codes com URL local persistidos chegam ao go-live | Fase de levantamento + migração obrigatória |
| `PUBLIC_APP_BASE_URL` ausente em produção | Documentação explícita + checklist de deploy |
| Regressão em dev local | Testes automatizados com monkeypatch de env vars |
| Migração em massa em tabela grande | Script idempotente, rodada controlada, rollback documentado |

### 4.3 Rollback

- Migração de dados: script reversível que restaura valores anteriores a partir de backup ou snapshot
- Configuração de env: remoção de `PUBLIC_APP_BASE_URL` em produção reativa o fallback (inadequado); rollback = corrigir a variável e reexecutar migração se necessário

---

## 5. Fases Propostas

### F1 — Levantamento e Configuração

**Objetivo:** Confirmar estado atual e garantir configuração de produção.

**Entregas:**
- Script ou query para contar `ativacao` com `landing_url` ou `url_promotor` contendo `localhost` ou `127.0.0.1`
- Documentação explícita em `docs/SETUP.md` e/ou `docs/DEPLOY_*.md` sobre obrigatoriedade de `PUBLIC_APP_BASE_URL` em produção
- Checklist de deploy para `app.npbb.com.br` incluindo verificação dessa variável

**Critério de aceite:**
- Volume de registros incorretos documentado
- PM e DevOps cientes da dependência de configuração

---

### F2 — Migração de Dados e Validação

**Objetivo:** Corrigir registros existentes com URL incorreta.

**Entregas:**
- Script de migração (Alembic data migration ou script standalone) que:
  - Identifica `ativacao` com `landing_url`/`url_promotor` contendo host local
  - Recalcula `landing_url` e `qr_code_url` usando `PUBLIC_APP_BASE_URL` (ou valor configurado para produção)
  - Atualiza os registros
- Script idempotente e com dry-run
- Testes de validação: zero registros com localhost após migração em ambiente de staging/produção

**Critério de aceite:**
- Migração executada com sucesso em ambiente alvo
- Métrica: zero QR codes com URL de localhost persistidos no banco

---

### F3 — Safeguards e Auditoria (Opcional)

**Objetivo:** Reduzir risco de regressão futura.

**Entregas:**
- Guard em `hydrate_ativacao_public_urls` ou no fluxo de persistência que levante erro ou warning quando, em ambiente de produção (detectado por env ou flag), a URL calculada contiver host local
- Teste automatizado cobrindo cenário de produção vs dev

**Critério de aceite:**
- Regressão detectável em CI ou em runtime em produção

---

## 6. Indicadores de Sucesso

- Zero QR codes com URL de localhost persistidos no banco após a correção
- QR codes gerados em produção resolvem corretamente para `app.npbb.com.br`
- Nenhuma regeração manual necessária após go-live para registros já existentes
- Fluxo de desenvolvimento local continua funcional com fallback localhost

---

## 7. Referências

- **Intake de origem:** [INTAKE-QR-GEN.md](./INTAKE.md)
- **Código relevante:**
  - `backend/app/utils/urls.py` — `get_public_app_base_url()`, `build_ativacao_public_urls()`
  - `backend/app/services/landing_pages.py` — `hydrate_ativacao_public_urls()`
  - `backend/app/models/models.py` — modelo `Ativacao` (landing_url, qr_code_url, url_promotor)
- **Governança:** `PROJETOS/COMUM/GOV-INTAKE.md` — gate Intake → PRD
