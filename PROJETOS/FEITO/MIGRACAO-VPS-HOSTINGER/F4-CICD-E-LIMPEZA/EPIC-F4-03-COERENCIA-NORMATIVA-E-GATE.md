---
doc_id: "EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F4-03 - Coerencia Normativa e Gate

## Objetivo

Fechar a migracao com gates automatizados de limpeza de legado, saude pos-cutover e decisao formal `promote | hold`.

## Resultado de Negocio Mensuravel

A retirada de Render, Supabase e Wrangler deixa de ser implicita e passa a ser comprovada por evidencias objetivas e auditaveis.

## Definition of Done

- existe `Makefile` na raiz com `eval-integrations` e `ci-quality`
- `make eval-integrations` falha com residuos legados fora de `docs/legacy`
- ha check automatizado de `backend`, `db`, `nginx`, `backup` saudaveis e rotas HTTPS acessiveis
- `artifacts/phase-f4/validation-summary.md` consolida F1-F4, backup, saude e decisao final

## Issues

### ISSUE-F4-03-01 - Bloquear dependencias legadas em gates automatizados
Status: todo

**User story**
Como pessoa responsavel pela coerencia da migracao, quero um gate que falhe na presenca de dependencias legadas para impedir promocao com residuos de Render, Supabase ou Wrangler.

**Plano TDD**
1. `Red`: em `scripts/check_repo_hygiene.sh`, `scripts/check_architecture_guards.sh`, novo `scripts/check_migration_legacy.sh`, `.gitignore`, `render.yaml` e `docs/DEPLOY_RENDER_CLOUDFLARE.md` para falhar se `.wrangler/` continuar rastreado, `render.yaml` permanecer fora de `docs/legacy/` ou houver referencias de producao a `SUPABASE_`, `pages.dev` ou `onrender.com`.
2. `Green`: criar `Makefile`, remover `.wrangler/`, arquivar `render.yaml` e a documentacao de deploy legado sob `docs/legacy/`.
3. `Refactor`: centralizar padroes proibidos e excecoes em um unico script de validacao.

**Criterios de aceitacao**
- Given `.wrangler/` rastreado ou `render.yaml` na raiz, When `make eval-integrations` roda, Then o gate falha.
- Given referencias a Supabase, Pages ou Render em arquivos de producao, When o gate roda, Then falha, exceto se o arquivo estiver em `docs/legacy/`.

### ISSUE-F4-03-02 - Validar saude dos containers e smoke HTTPS
Status: todo

**User story**
Como pessoa que valida o ambiente final, quero healthcheck automatizado dos containers e smoke HTTPS para garantir que o cutover ficou saudavel.

**Plano TDD**
1. `Red`: em `scripts/smoke_vps.sh`, novo `scripts/check_vps_health.sh` e `docs/DEPLOY_HOSTINGER_VPS.md` para falhar sem checagem de `backend`, `db`, `nginx` e `backup`.
2. `Green`: implementar leitura de `docker compose ps`, verificacao de `healthy`, smoke de `https://<dominio>/`, `https://<dominio>/eventos`, `https://<dominio>/api/health` e coleta de latencia por `curl -w`.
3. `Refactor`: reaproveitar env e reduzir duplicacao entre smoke funcional e health estrutural.

**Criterios de aceitacao**
- Given stack pos-cutover, When o healthcheck roda, Then os quatro servicos canonicos estao `healthy`.
- Given endpoints obrigatorios, When o smoke HTTPS roda, Then todas as rotas criticas retornam `200` e a latencia coletada e gravada no artefato de fase.

### ISSUE-F4-03-03 - Consolidar summary unico da fase
Status: todo

**User story**
Como pessoa que aprova o encerramento da migracao, quero um summary unico com status dos epicos e gates para decidir `promote | hold` sem julgamento informal.

**Plano TDD**
1. `Red`: em novo `scripts/render_phase_validation_summary.py` e nos artefatos `artifacts/phase-f4/*.md` para falhar sem resumo consolidado.
2. `Green`: gerar `artifacts/phase-f4/validation-summary.md` com status dos epicos F1-F4, resultado de `make eval-integrations`, resultado de `make ci-quality`, ultima evidencia de deploy, ultima evidencia de backup e restore, saude dos containers e decisao final.
3. `Refactor`: padronizar os insumos em `artifacts/phase-f4/evidence/*.json` para evitar montagem manual e manter o gate auditavel.

**Criterios de aceitacao**
- Given todas as evidencias disponiveis, When o summary e renderizado, Then a decisao e `promote` apenas se todos os gates estiverem verdes.
- Given qualquer evidencia ausente ou falha, When o summary e renderizado, Then a decisao e `hold` com blockers explicitos.

## Artifact Minimo do Epico

- `artifacts/phase-f4/validation-summary.md`

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
