---
doc_id: "TASK-1.md"
user_story_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/"
  - "backend/tests/"
tdd_aplicavel: true
---

# T1 - API read-only: serie temporal / agregacao por data (dashboard ativos)

## objetivo

Expor contrato read-only (novo endpoint ou extensao dos endpoints da [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md)) que devolve **pontos ao longo do tempo** para um evento (e filtros ja acordados na US-8-01), com granularidade **diaria** como minimo v1 (parametros `from`/`to` ou equivalente alinhado ao padrao do dashboard de leads). As series devem ser **coerentes** com as oito dimensoes operacionais (sem misturar semantica de remanejado com ajustes — PRD 2.6), de modo que o frontend possa plotar acompanhamento por data sem divergir dos totais agregados.

## precondicoes

- [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md) entregue ou contrato base acordado em branch partilhado (esta task **estende** esse contrato, nao redefine dimensoes).
- [US-8-03](../US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS/README.md) `done` antes do **fecho** da US-8-04; durante implementacao, alinhar shapes com o consumo previsto nos widgets.
- `DATABASE_URL` valido para testes de integracao se a suite usar Postgres; ou `TESTING=true` / `PYTEST_CURRENT_TEST` para SQLite conforme `AGENTS.md` na raiz do repositorio.

## orquestracao

- `depends_on`: `[]` (primeira task da US).
- `parallel_safe`: false.
- `write_scope`: routers, servicos ou schemas de agregacao sob `backend/app/` e testes sob `backend/tests/` tocando apenas o modulo do dashboard de ativos / agregacoes.

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US
- [US-8-01](../US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md)
- [FEATURE-8.md](../../FEATURE-8.md) (secs. 2, 4, 6–7)
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) — 2.3–2.4, 2.6
- Padrao de consumo leads: `frontend/src/config/dashboardManifest.ts`, `frontend/src/components/dashboard/` *(leitura para alinhar parametros de tempo)*
- `backend/tests/` — espelhar convencao de testes de API existentes no repo

## testes_red

- **testes_a_escrever_primeiro**:
  - Teste de API (cliente autenticado fixture do repo) que chama o endpoint de serie temporal com `evento_id` e janela `[from, to]` e espera status 200 e corpo com lista de pontos temporais por dimensao (ou estrutura documentada no schema).
  - Caso limite: janela sem dados retorna lista vazia ou zeros estaveis, sem 500.
- **comando_para_rodar**:
  - A partir da raiz do repo: `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/<modulo>::<test_serie_temporal>`
  - *(ajustar `<modulo>` apos criar o ficheiro de teste; alinhar a `AGENTS.md` se o projeto usar outro PYTHONPATH)*
- **criterio_red**:
  - Os testes acima falham antes da implementacao do endpoint; se passarem sem codigo novo, parar e rever escopo.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Implementar query ou view read-only que agrega por **dia** (bucket UTC ou timezone do evento — documentar escolha no OpenAPI/doc interna) para cada dimensao necessaria ao grafico v1.
4. Expor rota FastAPI com RBAC alinhado aos endpoints da US-8-01; documentar parametros e schema de resposta.
5. Garantir que soma dos pontos na janela e compativel com o endpoint agregado “snapshot” da US-8-01 (teste de coerencia ou comentario de risco + issue se performance impedir assert estrito).
6. Rodar testes ate green; refatorar mantendo suite verde.

## comandos_permitidos

- `cd backend && PYTHONPATH=... SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `cd backend && .venv/bin/ruff check` *(apenas ficheiros tocados)*
- Leitura: `rg`, `git diff`

## resultado_esperado

Endpoint(s) documentado(s) devolvendo serie temporal utilizavel pelo frontend, com testes de API cobrindo sucesso e janela vazia, alinhado ao primeiro criterio Given/When/Then da US-8-04.

## testes_ou_validacoes_obrigatorias

- Suite `pytest` relevante verde com `TESTING=true` (ou ambiente acordado).
- OpenAPI gerado inclui o novo contrato ou doc interna equivalente referenciada no router.

## stop_conditions

- Parar se US-8-01 ainda nao existir no codigo — implementar primeiro a US-8-01 ou acoplar explicitamente a branch que a contem.
- Parar se for necessario alterar semantica de dominio (FEATURE-4/6) em vez de leitura agregada — fora do escopo; escalar PM.
