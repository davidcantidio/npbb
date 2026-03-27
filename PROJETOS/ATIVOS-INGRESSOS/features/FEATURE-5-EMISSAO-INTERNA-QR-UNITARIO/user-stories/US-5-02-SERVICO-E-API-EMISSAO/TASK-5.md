---
doc_id: "TASK-5.md"
user_story_id: "US-5-02-SERVICO-E-API-EMISSAO"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T4"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/services/"
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: false
---

# TASK-5 - Auditoria, logs e correlacao sem payload sensivel

## objetivo

Garantir **trilhas de auditoria** e logging estruturado nas operacoes de emissao de forma que eventos possam ser **correlacionados** (ex. `correlation_id` ja presente em erros de authz) **sem** persistir ou logar em claro o **payload completo do QR** nem dados pessoais quando a politica interna exigir mascaramento. Cobrir cenarios de sucesso e falha de negocio.

## precondicoes

- TASK-4 (`T4`) `done`.
- [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) `done`.

## orquestracao

- `depends_on`: `T4`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; se o projeto usar modulo central de auditoria, referencia-lo em `arquivos_a_ler_ou_tocar` na implementacao.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- Servico de emissao (TASK-1) e pontos de idempotencia (TASK-4)
- Padroes de logging do projeto *(grep `logging` / structlog em `backend/app`)*
- Registros de auditoria existentes *(se houver tabela ou servico dedicado)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. LGPD / retencao — contexto apenas)*

## passos_atomicos

1. Mapear onde sucesso e falha de emissao sao tratados (router + servico).
2. Registrar evento de auditoria minimo: acao, `evento_id`/escopo, identificador da emissao (quando existir), `correlation_id`, usuario ator, timestamp — **sem** corpo de QR integral.
3. Ajustar logs de aplicacao para mascarar email/telefone/QR conforme politica (ex. ultimos 4 caracteres, hash truncado).
4. Adicionar testes ou asserts: onde viavel, `caplog` ou inspecao de registro de auditoria fake em SQLite para garantir que strings sensiveis conhecidas **nao** aparecem em mensagens de log em cenarios de teste.
5. Documentar no comentario da task ou docstring do modulo o que e considerado sensivel para esta feature.

## comandos_permitidos

- `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py tests/test_emissao_interna_unitario_service.py -q`
- `cd backend && ruff check app/routers/ingressos.py app/services/`

## resultado_esperado

- Consulta a trilhas (ou logs estruturados em ambiente de teste) permite correlacionar emissoes com `correlation_id`.
- Criterio **Given** sucesso ou falha / **Then** correlacao **sem** payload sensivel integral em claro atendido.

## testes_ou_validacoes_obrigatorias

- Pytest verde apos asserts de log/auditoria adicionados.
- Checklist manual: uma emissao feliz e uma falha (403 ou validacao) geram registros utilizaveis para suporte sem vazamento obvio.

## stop_conditions

- Parar se nao existir mecanismo de auditoria persistida e o projeto exigir apenas logs: limitar escopo a logs mascarados e registrar a limitacao em `limitacoes` do handoff da US.
- Parar e reportar `BLOQUEADO` se politica de mascaramento nao estiver definida (quais campos mascarar) — pedir uma linha no README da US ou decisao do PM.
