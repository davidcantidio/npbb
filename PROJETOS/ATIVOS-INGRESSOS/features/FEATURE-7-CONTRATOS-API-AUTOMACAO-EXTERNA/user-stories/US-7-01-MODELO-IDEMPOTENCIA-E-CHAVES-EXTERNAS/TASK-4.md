---
doc_id: "TASK-4.md"
user_story_id: "US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md"
tdd_aplicavel: false
---

# T4 - Validacao migrate/revert e notas de integracao para US-7-03

## objetivo

Validar o encadeamento **upgrade / downgrade** das revisoes desta US, confirmar nao-regressao de schema legado (tabelas pre-existentes intactas apos ciclo), e registrar **notas de integracao** no `README.md` desta US para consumo por US-7-03 (camada de aplicacao: idempotencia HTTP, mapeamento `integrator_client_ref`, ligacao a recebimento quando FEATURE-4 estiver disponivel), sem implementar endpoints nesta US.

## precondicoes

- T3 concluida: modelos importaveis e migrations T1–T2 aplicadas em ambiente de teste local.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: false.
- `write_scope`: apenas `README.md` desta US-7-01 — nova subsecao curta (ex.: **Integracao com US-7-03**); nao alterar criterios de aceite de outras USs.

## arquivos_a_ler_ou_tocar

- Revisoes Alembic T1, T2
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL/README.md` *(leitura — contexto de handoff)*
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md`

## passos_atomicos

1. Estado limpo de migracoes: `alembic upgrade head`; confirmar presenca das novas tabelas (inspecao via cliente SQL ou `\dt`).
2. `alembic downgrade -1` repetido ate remover as revisoes desta US (ou `downgrade` para revision anterior a T1), confirmando que tabelas criadas desaparecem.
3. `alembic upgrade head` novamente para restaurar estado final.
4. Lista de verificacao manual: tabelas criticas existentes antes da US (ex.: `evento`, `ingestions`, `sources` conforme ambiente) permanecem acessiveis.
5. Acrescentar ao `README.md` da US-7-01 subsecao **Integracao com US-7-03** com: nomes finais de tabelas; significado de `integrator_client_ref`; semantica de `status`; uso previsto de `metadata_json`; passo futuro de FK para recebimento FEATURE-4 quando US-4-01 estiver mergeada; link para US-7-03.

## comandos_permitidos

- `cd backend && .venv/bin/alembic current`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade <revision_antes_T1>`
- `cd backend && .venv/bin/alembic upgrade head`
- Cliente `psql` ou ferramenta equivalente *(leitura de catalogo)*

## resultado_esperado

Evidencia de ciclo migrate/revert aplicavel; contrato escrito no README da US-7-01 para consumo por US-7-03; Definition of Done da US-7-01 desbloqueado do ponto de vista de validacao de persistencia.

## testes_ou_validacoes_obrigatorias

- Ciclo completo downgrade (ate pre-T1) + upgrade `head` sem erro.
- Nenhuma tabela legada core removida inadvertidamente (checagem por lista de tabelas esperadas).

## stop_conditions

- Parar se `downgrade` falhar por dependencias cruzadas — resolver ordem de revisoes ou `depends_on` Alembic antes de continuar.
