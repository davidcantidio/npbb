---
doc_id: "TASK-1.md"
user_story_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/schemas/dashboard_ativos.py"
tdd_aplicavel: false
---

# T1 - Contrato Pydantic e alinhamento ao padrao dashboard de leads

## objetivo

Definir o **contrato de API read-only** do dashboard de ativos: schemas Pydantic de **query** (filtros) e **response** (agregados) espelhando o estilo de [`backend/app/schemas/dashboard_leads.py`](../../../../../../backend/app/schemas/dashboard_leads.py) e permitindo consumo coerente com [`frontend/src/config/dashboardManifest.ts`](../../../../../../frontend/src/config/dashboardManifest.ts) e componentes sob `frontend/src/components/dashboard/`. A resposta deve expor, de forma **explicita e separada**, as oito dimensoes: **planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido, problemas**, sem campos ambiguos que misturem **remanejado** com **aumento/reducao** (PRD 2.6).

## precondicoes

- Leitura do [README.md](README.md) desta US e de [FEATURE-8.md](../../FEATURE-8.md) (secs. 2, 6–7).
- Dominio base das FEATURE-2, FEATURE-4 e FEATURE-6 disponivel no codigo para **consulta** ao nomear campos (sem implementar queries nesta task).
- PRD secs. 2.4–2.6 lidas para vocabulario de negocio.

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter (apenas novo modulo de schemas; sem router nem servico).

## arquivos_a_ler_ou_tocar

- `backend/app/schemas/dashboard_leads.py`
- `backend/app/routers/dashboard_leads.py` *(parametros e shape de resposta de referencia)*
- `frontend/src/config/dashboardManifest.ts` *(leitura — alinhar nomes opcionais de filtro)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` — 2.4–2.6
- **Criar/alterar**: `backend/app/schemas/dashboard_ativos.py`

## passos_atomicos

1. Listar no docstring ou comentario curto do modulo o mapeamento **campo JSON -> significado de negocio** para cada uma das oito dimensoes (uma subestrutura ou campos de topo estaveis).
2. Definir modelo de **query** com `evento_id` obrigatorio ou opcional alinhado ao leads (ex.: `evento_id` + filtros opcionais); incluir **diretoria_id** ou equivalente como **opcional v1** se o modelo de dados ja expuser diretoria por evento (PRD: agregacao por evento e diretoria). Se o modelo ainda nao suportar filtro por diretoria nas agregacoes, documentar no schema como `Optional` com descricao OpenAPI e **nao** inventar semantica nova.
3. Definir modelo de **response** com `generated_at` (ou padrao leads), eco de **filters** aplicados e bloco de **KPIs/agregados** com as oito chaves separadas (tipos numericos ou estruturas aninhadas acordadas — ex. totais por dimensao).
4. Garantir valores default ou campos opcionais que permitam resposta completa com **zeros** quando nao houver dados (contrato estavel antes da implementacao SQL).
5. Revisar nomes e tipos para compatibilidade com geracao OpenAPI automatica do FastAPI.

## comandos_permitidos

- `cd backend && .venv/bin/ruff check app/schemas/dashboard_ativos.py` *(apos criar ficheiro)*
- Leitura: `rg`, `git diff`

## resultado_esperado

- Ficheiro `backend/app/schemas/dashboard_ativos.py` com modelos importaveis pelo router/servico nas tasks seguintes.
- Contrato documentado (Field descriptions) suficiente para implementacao T3/T4 sem reinterpretar PRD.

## testes_ou_validacoes_obrigatorias

- Modulo importa sem erro: `python -c "from app.schemas.dashboard_ativos import ..."` com `PYTHONPATH` conforme `AGENTS.md`.
- Nenhum endpoint novo e obrigatorio nesta task.

## stop_conditions

- Parar e escalar PM se PRD/US exigirem dimensoes ou filtros nao listados na US sem ADR ou adendo.
- Parar se for necessario alterar tabelas de dominio (FEATURE-2/4/6) para **definir** o contrato — fora do escopo desta task (apenas refletir o que ja existe ou placeholders opcionais documentados).
