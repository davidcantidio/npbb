---
doc_id: "ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs:
  - "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md / secao 5"
  - "auditoria_fluxo_ativacao.md / F1-NAO03, F1-NAO04 e Analise de Complexidade Estrutural"
  - "SPEC-ANTI-MONOLITO.md / thresholds por arquivo"
---

# ISSUE-F1-01-002 - Validar baseline estrutural da F1

## User Story

Como mantenedor do sibling `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`, quero medir os
arquivos estruturais apontados no hold e registrar o risco residual fora do
escopo para que a reauditoria saiba exatamente quais alvos do achado historico
ja sairam da nao conformidade e quais itens nao serao absorvidos silenciosamente.

## Contexto Tecnico

A auditoria original marcou `backend/app/models/models.py` e
`backend/app/routers/ativacao.py` como alvos estruturais da F1 e o estado atual
tambem mostra `backend/app/routers/leads.py` acima do threshold `block`. Esta
issue valida a baseline atual de `models.py` e `ativacao.py`, confirma a
estabilidade da fachada `app.models.models` e registra `leads.py` como risco
explicito fora do sibling, sem abrir refactor novo neste backlog.

## Plano TDD

- Red: medir os arquivos estruturais sem assumir que o retrato da auditoria continua igual
- Green: classificar `models.py` e `ativacao.py` contra o spec vigente e validar a fachada `app.models.models`
- Refactor: registrar `backend/app/routers/leads.py` como risco residual fora do sibling

## Criterios de Aceitacao

- Given `SPEC-ANTI-MONOLITO.md` e os arquivos alvo da F1, When as metricas forem medidas, Then `models.py` e `ativacao.py` recebem classificacao objetiva contra os thresholds atuais
- Given os imports amplos via `app.models.models`, When o repositorio for varrido, Then a estabilidade da fachada fica documentada
- Given `backend/app/routers/leads.py` segue acima do threshold, When a issue for fechada, Then ele aparece explicitamente como risco fora do sibling e nao como trabalho silencioso
- Given `models.py` ou `ativacao.py` voltem a cruzar threshold aplicavel, When isso for encontrado, Then a issue responde `BLOQUEADO`

## Definition of Done da Issue

- [x] `models.py` e `ativacao.py` foram medidos contra `SPEC-ANTI-MONOLITO.md`
- [x] a estabilidade da fachada `app.models.models` foi validada por amostragem do repo
- [x] `backend/app/routers/leads.py` esta registrado como risco residual fora do sibling
- [x] existe baseline estrutural suficiente para a issue de evidencia de threshold

## Tasks Decupadas

- [x] T1: medir os arquivos estruturais alvo da F1 contra o spec vigente
- [x] T2: confirmar a estabilidade da fachada `app.models.models`
- [x] T3: validar metadata critica da fundacao e registrar o risco residual fora do sibling

## Instructions por Task

### T1
- objetivo: medir `models.py`, `ativacao.py` e `leads.py` contra os thresholds do spec para estabelecer a baseline estrutural atual
- precondicoes:
  - leitura previa de `SPEC-ANTI-MONOLITO.md`
  - entendimento claro de que `leads.py` nao sera absorvido neste sibling
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
  - `backend/app/models/models.py`
  - `backend/app/routers/ativacao.py`
  - `backend/app/routers/leads.py`
- passos_atomicos:
  1. ler os thresholds de arquivo em `SPEC-ANTI-MONOLITO.md`
  2. medir o total de linhas de `models.py`, `ativacao.py` e `leads.py`
  3. classificar cada arquivo observado como `ok`, `warn` ou `block`
- comandos_permitidos:
  - `sed -n`
  - `wc -l`
- resultado_esperado: baseline estrutural objetiva dos tres arquivos medida contra o spec
- testes_ou_validacoes_obrigatorias:
  - `wc -l backend/app/models/models.py backend/app/routers/ativacao.py backend/app/routers/leads.py`
- stop_conditions:
  - parar se `models.py` ultrapassar `block`
  - parar se `ativacao.py` ultrapassar `warn`

### T2
- objetivo: confirmar que a fachada `app.models.models` continua sendo ponto estavel de importacao no repo
- precondicoes:
  - T1 concluida
  - baseline estrutural registrada
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py`
  - `backend/app/models/__init__.py`
  - `backend/app/`
  - `backend/tests/`
- passos_atomicos:
  1. localizar imports que dependem de `app.models.models`
  2. verificar se a fachada continua sendo usada de forma ampla no backend e nos testes
  3. registrar por que qualquer refactor futuro de modelos precisara preservar essa superficie
- comandos_permitidos:
  - `rg -n`
  - `sed -n`
- resultado_esperado: estabilidade da fachada `app.models.models` demonstrada por referencias reais do repositorio
- testes_ou_validacoes_obrigatorias:
  - `rg -n "from app.models.models import|app.models.models" backend/app backend/tests`
- stop_conditions:
  - parar se a fachada estiver quebrada ou inconsistente no estado atual do repo
  - parar se a validacao depender de refactor de models fora do sibling

### T3
- objetivo: validar a metadata critica da fundacao e registrar o risco residual fora do sibling
- precondicoes:
  - T1 e T2 concluidas
  - baseline estrutural e de imports consolidada
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_lp_ativacao_schema_contract.py`
  - `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md`
- passos_atomicos:
  1. executar o teste focal de metadata da F1
  2. registrar que `models.py` e `ativacao.py` sao os alvos estruturais remediados e que `leads.py` fica fora do sibling como risco residual
  3. preparar a transicao desta baseline para `ISSUE-F1-02-002`
- comandos_permitidos:
  - `python3 -m pytest`
  - `sed -n`
  - `apply_patch`
- resultado_esperado: baseline estrutural fechada com prova minima de metadata e risco residual explicito
- testes_ou_validacoes_obrigatorias:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_lp_ativacao_schema_contract.py`
- stop_conditions:
  - parar se o teste de metadata falhar
  - parar se a issue passar a exigir refactor de `backend/app/routers/leads.py`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
- `backend/app/models/models.py`
- `backend/app/models/__init__.py`
- `backend/app/routers/ativacao.py`
- `backend/app/routers/leads.py`
- `backend/tests/test_lp_ativacao_schema_contract.py`
- `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`

## Artifact Minimo

- baseline estrutural registrada na propria issue, com quadro `arquivo -> linhas -> threshold -> leitura`

## Baseline Estrutural Registrada

Leitura executada contra `SPEC-ANTI-MONOLITO.md`, usando o threshold de arquivo
`warn > 400` e `block > 600`.

| Arquivo | Linhas | Threshold Aplicavel | Leitura |
|---|---:|---|---|
| `backend/app/models/models.py` | `549` | `warn (> 400)` e abaixo de `block (> 600)` | `warn`; alvo estrutural remediado da F1, fora de `block` |
| `backend/app/routers/ativacao.py` | `394` | abaixo de `warn (> 400)` | `ok`; alvo estrutural remediado da F1, abaixo de `warn` |
| `backend/app/routers/leads.py` | `1649` | `block (> 600)` | `block`; risco residual explicito fora do sibling |

## Estabilidade da Fachada `app.models.models`

- o path estavel consumido pelo repositorio continua sendo `app.models.models`
- `backend/app/models/__init__.py` hoje reexporta apenas simbolos de `lead_batch`
  e nao substitui a superficie historica de `app.models.models`
- a varredura em `backend/app` e `backend/tests` encontrou uso amplo da fachada
  em routers, services, schemas, modules e testes, confirmando dependencia real
  da superficie atual
- qualquer refactor futuro dos modelos precisa preservar `app.models.models`
  como superficie estavel de importacao para evitar regressao transversal fora
  deste sibling

## Evidencia Minima de Metadata e Risco Residual

- validacao focal executada com `PYTHONPATH`, `SECRET_KEY=ci-secret-key` e
  `TESTING=true`: `2 passed in 0.12s` em
  `backend/tests/test_lp_ativacao_schema_contract.py`
- a revision
  `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`
  continua rastreando `conversao_ativacao`, `lead_reconhecimento_token` e
  `ix_conversao_ativacao_ativacao_id_cpf`
- `backend/app/models/models.py` e `backend/app/routers/ativacao.py` ficam
  registrados nesta baseline como alvos estruturais remediados da F1
- `backend/app/routers/leads.py` permanece fora deste sibling como risco
  residual explicito e nao deve ser absorvido silenciosamente nesta issue
- esta baseline fecha o pacote estrutural de `ISSUE-F1-01-002` e prepara a
  transicao para `ISSUE-F1-02-002`, onde a evidencia de threshold segue como
  proxima unidade do sibling

## Dependencias

- [PRD Derivado](../../../PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [Auditoria de Origem](../../../auditoria_fluxo_ativacao.md)
- [Epic](../EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md)
- [Fase](../F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
