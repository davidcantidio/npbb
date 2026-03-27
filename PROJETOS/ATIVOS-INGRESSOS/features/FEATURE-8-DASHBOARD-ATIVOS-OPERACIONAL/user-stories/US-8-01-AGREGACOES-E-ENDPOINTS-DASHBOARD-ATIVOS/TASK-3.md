---
doc_id: "TASK-3.md"
user_story_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/services/dashboard_ativos.py"
tdd_aplicavel: false
---

# T3 - Servico de agregacao read-only

## objetivo

Implementar **servico de leitura** (funcoes ou classe) que, dada sessao SQLModel/SQLAlchemy e parametros do schema de query T1, calcula os agregados e devolve instancia do **response model** T1. Garantir comportamento **estavel** quando nao ha linhas: **zeros numericos** e/ou **colecoes vazias** conforme contrato, **sem 500** por `None` inesperado ou divisao por zero. Manter **separacao semantica** entre remanejado e aumento/reducao (PRD 2.6), reutilizando leituras canonicas do dominio quando ja existirem (ex. padroes de FEATURE-4/6).

## precondicoes

- [T2](TASK-2.md) concluida: estrategia DDL ou query-only definida.
- [T1](TASK-1.md) concluida: tipos de entrada/saida fixos.
- Testes de integracao podem usar `TESTING=true` / SQLite conforme `AGENTS.md` — ajustar expectativas se dialecto limitar funcoes SQL (usar ramos documentados como no `dashboard_leads.py`).

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: novo modulo de servico sob `backend/app/services/`.

## arquivos_a_ler_ou_tocar

- `backend/app/schemas/dashboard_ativos.py`
- `backend/app/services/` *(convencoes existentes)*
- `backend/app/routers/dashboard_leads.py` *(padroes de sessao, filtros, visibilidade)*
- Modelos e servicos de ativos/recebimento/distribuicao relevantes em `backend/app/models/`, `backend/app/routers/ativos.py`, `ingressos.py` conforme mapeamento da T2
- **Criar**: `backend/app/services/dashboard_ativos.py` *(nome final pode alinhar ao router na T4)*

## passos_atomicos

1. Implementar funcao principal `build_dashboard_ativos_aggregate(session, query: DashboardAtivosQuery) -> DashboardAtivosResponse` *(ajustar nomes aos tipos T1)*.
2. Aplicar filtros de visibilidade de usuario **apenas na camada de router** (T4) ou receber `Usuario` / escopo ja validado — **nao** duplicar RBAC aqui sem alinhar a T4; se o servico precisar de `usuario`, assinar na T4.
3. Para cada dimensao, executar query/view definida na T2; agregar em memoria apenas se necessario para performance documentada.
4. Preencher todos os campos obrigatorios do response; para dimensoes sem dados, retornar `0` ou `[]` conforme tipo no schema T1.
5. Opcional (manifesto FEATURE-8): preparar hook ou comentario para **cache** futuro — nao implementar Redis sem decisao explicita.

## comandos_permitidos

- `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -c "from app.services.dashboard_ativos import ..."`
- `cd backend && .venv/bin/ruff check app/services/dashboard_ativos.py`

## resultado_esperado

- Servico importavel e testavel que materializa o contrato T1 a partir do banco.
- Nenhum endpoint HTTP nesta task.

## testes_ou_validacoes_obrigatorias

- Chamada manual ou teste unitario minimo (opcional nesta task): evento inexistente ou sem dados retorna estrutura completa sem excecao — pode ser adiado para T5 se a suite T5 cobrir via API.

## stop_conditions

- Parar se queries corretas exigirem mudanca de modelo transacional — escalar para FEATURE de dominio, nao contornar com SQL incorreto.
- Parar se remanejado e ajustes nao puderem ser distinguidos com dados existentes — `BLOQUEADO` com referencia a tabela/campo em falta.
