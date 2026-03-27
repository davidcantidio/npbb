---
doc_id: "TASK-5.md"
user_story_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T4"
parallel_safe: false
write_scope:
  - "backend/tests/"
tdd_aplicavel: true
---

# T5 - Testes de API: contrato, dimensoes e ausencia de dados

## objetivo

Adicionar **testes automatizados** que verificam os criterios Given/When/Then da [US](README.md): resposta distingue as **oito dimensoes** sem colapsar remanejado em aumento/reducao; **ausencia de dados** resulta em comportamento documentado (zeros/listas vazias) e **HTTP 200** (ou 4xx apenas quando fora de escopo autenticado, nunca 500 por falta de linhas agregadas). Reutilizar fixtures de cliente autenticado e padroes de `backend/tests/` ja usados para `dashboard` ou `ativos`.

## precondicoes

- [T4](TASK-4.md) concluida: rota registada e chamavel.
- Variaveis `TESTING=true`, `SECRET_KEY`, `PYTHONPATH` conforme [AGENTS.md](../../../../../../AGENTS.md) na raiz do repositorio.

## orquestracao

- `depends_on`: `T4`.
- `parallel_safe`: `false`.
- `write_scope`: novos ou estendidos ficheiros sob `backend/tests/` tocando apenas o dashboard de ativos.

## arquivos_a_ler_ou_tocar

- [README.md](README.md) — criterios de aceitacao
- `backend/tests/` — fixtures (`conftest.py`), testes de routers existentes *(ex.: leads, ativos)*
- `backend/app/routers/dashboard_ativos.py`
- **Criar/estender**: ficheiro dedicado, ex. `backend/tests/test_dashboard_ativos.py` *(nome final alinhado ao repo)*

## testes_red

- **testes_a_escrever_primeiro**:
  - Teste autenticado: GET ao endpoint de agregacao com `evento_id` (seed ou fixture existente) — espera **200** e corpo JSON com presenca das chaves/estruturas das **oito dimensoes** conforme schema T1.
  - Teste com evento **sem dados** de agregacao (ou evento criado vazio para ativos): espera **200**, valores numericos zero ou colecoes vazias, **sem** excecao no servidor.
  - Onde dados de teste permitam: assert que **remanejado** e **aumentado/reduzido** nao sao o mesmo campo nem copia implicita *(ajustar ao shape T1 — ex. tres chaves distintas no payload)*.
- **comando_para_rodar**:
  - `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_dashboard_ativos.py`
  - *(ajustar caminho do modulo se o ficheiro tiver outro nome)*
- **criterio_red**:
  - Os testes falham antes de qualquer correcao pos-T4 se o contrato ou robustez ainda nao estiverem corretos; se passarem sem implementacao da T4, parar e rever escopo.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red) ou corrigir implementacao T3/T4 ate obter red significativo se ja estiver green por acaso.
3. Ajustar servico/router para satisfazer asserts mantendo semantica de dominio.
4. Rodar suite ate green; refatorar testes para clareza (nomes de cenario alinhados ao Given/When/Then).
5. Incluir na suite comando de regressao minimo citado em `comandos_permitidos`.

## comandos_permitidos

- `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_dashboard_ativos.py`
- `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q` *(se integracao exigir suite maior)*
- `cd backend && .venv/bin/ruff check tests/test_dashboard_ativos.py`

## resultado_esperado

- Suite de testes verde em CI local com `TESTING=true`.
- Evidencia objetiva dos criterios de aceitacao da US cobertos por asserts.

## testes_ou_validacoes_obrigatorias

- `pytest` no modulo novo sem falhas.
- Nenhum teste depende de ordem global fragil sem isolamento de dados.

## stop_conditions

- Parar se fixtures nao permitirem criar cenario de **remanejado vs ajustes** distintos — documentar limitacao na task e reduzir assert a presenca estrutural dos campos + smoke de zeros.
- Parar se testes exigirem Postgres e SQLite nao suportar SQL das agregacoes — seguir padrao de `dashboard_leads.py` para dialecto ou marcar testes como `skip` com justificativa e issue.
