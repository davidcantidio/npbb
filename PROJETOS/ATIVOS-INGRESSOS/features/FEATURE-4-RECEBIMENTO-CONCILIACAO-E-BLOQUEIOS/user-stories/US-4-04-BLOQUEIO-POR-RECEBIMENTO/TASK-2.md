---
doc_id: "TASK-2.md"
user_story_id: "US-4-04-BLOQUEIO-POR-RECEBIMENTO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/services/ativos_recebimento_bloqueio.py"
  - "backend/app/routers/ativos.py"
tdd_aplicavel: false
---

# TASK-2 - Avaliacao de pipeline: bloquear aumento dependente sem recebimento

## objetivo

No fluxo em que um **pedido de aumento dependente de ticketeira** e avaliado, aplicar a regra: sem recebimento que cubra a necessidade, o item permanece bloqueado com motivo persistido `bloqueado_por_recebimento`. Aumentos **nao** dependentes de ticketeira nao devem ser afetados por esta regra (criterio Given/Then da US).

## precondicoes

- TASK-1 `done`: persistencia do motivo/estado de bloqueio disponivel.
- [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) e [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) implementadas o suficiente para consultar recebido confirmado e tetos/saldo usados na verificacao de “cobertura” *(mesmo que a logica de cobertura final seja refinada em T3, T2 deve integrar leitura consistente com o codigo existente)*.
- Distincao “dependente de ticketeira” vs outros ajustes alinhada com [US-4-05](../US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES/README.md) onde ja existir contrato; caso ainda nao exista, usar flags/tipos definidos na US-4-01/FEATURE-3 modo externo.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false` (router e servico compartilham fluxo de ativos).
- `write_scope`: o ficheiro de servico pode ser renomeado se o projeto padronizar outro nome; manter um unico modulo dono da regra de bloqueio ate T3.

## arquivos_a_ler_ou_tocar

- `backend/app/services/ativos_recebimento_bloqueio.py` *(criar se nao existir — concentrar regra de negocio aqui)*
- `backend/app/routers/ativos.py` *(pontos que criam ou avaliam aumentos / solicitacoes)*
- `backend/app/schemas/ativos.py` *(se a resposta de API deve expor estado de bloqueio para operacao; evitar duplicar US-4-06 se for apenas indicador minimo)*
- Servicos/repositorios entregues por US-4-02/US-4-03 para leitura de recebimento e saldo distribuivel
- [US-4-04 README.md](./README.md) *(criterios de aceitacao)*

## passos_atomicos

1. Localizar o comando ou use case que avalia “fluxo de ajuste” para aumentos (endpoint ou servico chamado por `ativos`).
2. Implementar funcao pura ou servico testavel: dado aumento classificado como dependente de ticketeira e contexto de recebimentos por evento/categoria/modo, decidir se falta cobertura e retornar decisao de bloqueio com motivo canonico.
3. Persistir bloqueio via contrato da T1 quando a decisao for bloquear; nao persistir bloqueio indevido para fluxos excluidos pela US.
4. Integrar chamada ao servico no pipeline existente (ordem: apos validacoes basicas, antes de efeitos que consumam saldo indevidamente).
5. Garantir idempotencia razoavel: reavaliar o mesmo pedido nao deve criar estados inconsistentes.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/ -q -k ativos` *(ajustar padrao quando testes T4 existirem)*
- `cd backend && ruff check app/services/ativos_recebimento_bloqueio.py app/routers/ativos.py`

## resultado_esperado

- Cenario Given/When/Then 1 da US satisfeito: sem recebimento que cubra, item bloqueado com motivo persistido equivalente a `bloqueado_por_recebimento`.
- Cenario “aumento que nao depende de ticketeira” nao recebe este bloqueio.

## testes_ou_validacoes_obrigatorias

- Cobertura manual ou teste automatizado minimo (refinado em T4) para os dois casos acima.

## stop_conditions

- Parar e reportar `BLOQUEADO` se nao existir classificacao confiavel de “dependente de ticketeira” no codigo — escalar alinhamento com US-4-05 / FEATURE-3 antes de heuristica fragil.
- Parar se T1 nao estiver `done`.
