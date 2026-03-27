---
doc_id: "TASK-2.md"
user_story_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/services/"
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/"
tdd_aplicavel: true
---

# T2 - Servico de dominio e API de registo de remanejamento

## objetivo

Implementar servico de dominio e endpoint(s) FastAPI para **executar remanejamento valido** segundo regras do dominio (incl. saldo/disponibilidade herdadas de FEATURE-4/US-6-01 quando aplicavel), persistir a trilha na estrutura da T1 e expor leitura coerente do estado **remanejado** (ou leitura equivalente acordada no modelo). Incluir **bloqueio com erro 4xx claro** quando a **politica de motivo obrigatorio** estiver ativa (config/env/feature flag ou campo de configuracao por evento explicitado no codigo — sem inventar regra fora do PRD/intake) e o operador nao enviar motivo valido.

## precondicoes

- TASK-1 `done`: migracao aplicada e modelos de remanejamento importaveis.
- US-6-01 `done`: fluxo de alocacao/distribuicao base disponivel para integrar validacoes.
- Padrao de autenticacao (`get_current_user`) e RBAC revisados para operador interno.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: `false`.
- `write_scope`: novo ou alterado servico sob `backend/app/services/`, `backend/app/routers/ingressos.py`, schemas em `backend/app/schemas/` (ex.: extensao ou `schemas/remanejamento.py` se o gate fixar nome).

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- `backend/app/core/auth.py`
- `backend/app/utils/http_errors.py`
- `backend/app/db/database.py`
- `backend/app/schemas/ingressos.py` *(ou novo modulo de schema)*
- Modelos e servicos entregues por US-6-01 e FEATURE-4 *(disponivel / bloqueios)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API ou servico: remanejamento valido persiste registro com origem, destino, quantidade, instante e ator.
  - Teste: quando politica de motivo obrigatorio esta **ligada** no teste (fixture/mock de config), POST sem motivo retorna 422 ou 400 com codigo de erro estavel.
  - Teste: remanejamento invalido (ex.: quantidade inconsistente ou regra de dominio) retorna 4xx sem persistir linha de auditoria.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q -k remanej` *(ajustar marcador/nome quando implementado)*
- criterio_red:
  - Os testes novos falham antes da implementacao; se passarem sem codigo de producao, parar e revisar a task.

## passos_atomicos

1. Escrever os testes listados em `testes_red` e confirmar falha inicial.
2. Implementar servico com transacao unica: validar entrada, aplicar politica de motivo, atualizar alocacoes conforme US-6-01 e inserir registro de auditoria na tabela da T1.
3. Expor endpoint POST (prefixo coerente com `/ingressos` ou sub-recurso `/ativos/...` alinhado ao router existente) com dependencia de sessao e usuario corrente.
4. Mapear erros de dominio para HTTP com `raise_http_error` ou padrao do projeto.
5. Garantir que resposta ou cabecalho permita correlacao com o registro de auditoria criado.
6. Rodar testes ate ficarem green; refatorar mantendo green.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q`
- `cd backend && .venv/bin/ruff check app/routers/ingressos.py app/services/ app/schemas/`

## resultado_esperado

API autenticada que registra remanejamento auditavel e aplica bloqueio por falta de motivo quando a politica exige, cumprindo os dois primeiros criterios Given/When/Then da US.

## testes_ou_validacoes_obrigatorias

- Suite de testes da task em green.
- Smoke manual via `/docs`: caso feliz e caso motivo obrigatorio ausente.

## stop_conditions

- Parar se a politica de motivo nao puder ser expressa de forma verificavel (config explicita) — escalar a PM antes de codificar default implicito.
- Parar se T1 exigir alteracao de schema que quebre revisao ja aplicada em outros ambientes — coordenar nova revisao em T1, nao “patch” silencioso aqui.
