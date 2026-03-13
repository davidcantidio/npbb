---
doc_id: "ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs:
  - "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md / secoes 2, 3, 4 e 5"
  - "auditoria_fluxo_ativacao.md / F1-NAO01 a F1-NAO08"
  - "AUDIT-LOG.md / Resolucoes de Follow-ups em 2026-03-13"
---

# ISSUE-F1-01-001 - Classificar PRD vs repo no fluxo publico

## User Story

Como mantenedor do sibling `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`, quero
comparar o PRD derivado e a auditoria do hold com o estado atual do fluxo
publico para saber exatamente o que ja foi absorvido pelo repositorio e o que
ainda precisa de evidencia ou tratamento residual.

## Contexto Tecnico

O hold da F1 nasceu de um retrato do repositorio em `2026-03-13`, mas o estado
atual ja mostra `submit_url=/leads`, `LandingSubmitResponse` com
`lead_reconhecido` e cobertura focal relevante no backend e frontend. Esta
issue nao implementa contrato novo; ela classifica os achados originais como
`implementado`, `nao_aplicavel` ou `residual` para evitar backlog inflado e
preparar as issues de evidencia do sibling.

## Plano TDD

- Red: ler intake, PRD, auditoria, F1 original e superficies reais sem assumir que o retrato do hold continua igual
- Green: classificar cada achado original do fluxo publico contra o estado atual do repo
- Refactor: consolidar a matriz PRD vs repo em formato suficiente para handoff e reauditoria

## Criterios de Aceitacao

- Given o intake, o PRD, o `AUDIT-LOG.md`, a auditoria de origem e os arquivos reais do fluxo publico, When a comparacao for executada, Then cada achado original relevante recebe classificacao explicita de `implementado`, `nao_aplicavel` ou `residual`
- Given as superficies `landing_pages.py`, `landing_page_submission.py`, `leads.py`, `landing_public.py`, `EventLandingPage.tsx` e testes correlatos, When forem lidas em conjunto, Then fica explicito se o contrato canônico atual corresponde ao fluxo efetivamente usado
- Given qualquer drift material fora do PRD derivado, When ele for encontrado, Then a issue responde `BLOQUEADO` antes de ampliar escopo ou reinterpretar a remediacao
- Given a issue concluida, When um leitor futuro consultar a matriz, Then ele entende por que o sibling parte do estado atual do repositorio e nao do retrato historico do hold

## Definition of Done da Issue

- [ ] intake, PRD, `AUDIT-LOG.md`, auditoria e F1 original foram lidos
- [ ] achados originais do fluxo publico estao classificados contra o estado atual
- [ ] existe matriz rastreavel `achado -> estado atual -> evidencia -> proximo destino`
- [ ] qualquer drift material fora do PRD derivado foi tratado como `BLOQUEADO`

## Tasks Decupadas

- [ ] T1: ler as fontes normativas e as superficies reais do fluxo publico
- [ ] T2: classificar os achados originais do hold contra o estado atual do repositorio
- [ ] T3: registrar a matriz PRD vs repo para as issues seguintes

## Instructions por Task

### T1
- objetivo: formar a baseline documental e tecnica do fluxo publico antes de classificar qualquer achado
- precondicoes:
  - entendimento claro de que o sibling e baseado no estado atual do repositorio
  - proibicao de reabrir backlog funcional sem drift material comprovado
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
  - `PROJETOS/LP/PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
  - `PROJETOS/LP/AUDIT-LOG.md`
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `PROJETOS/LP/F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md`
  - `backend/app/services/landing_pages.py`
  - `backend/app/services/landing_page_submission.py`
  - `backend/app/routers/leads.py`
  - `backend/app/routers/landing_public.py`
  - `frontend/src/pages/EventLandingPage.tsx`
- passos_atomicos:
  1. ler o intake, o PRD derivado, o `AUDIT-LOG.md` e a auditoria `auditoria_fluxo_ativacao.md`
  2. revisar a F1 original para preservar o contexto do gate `hold`
  3. revisar as superficies reais do backend e frontend do fluxo publico listadas nesta issue
- comandos_permitidos:
  - `sed -n`
  - `rg -n`
- resultado_esperado: baseline documental e tecnica suficiente para classificar os achados do hold
- testes_ou_validacoes_obrigatorias:
  - `rg -n "submit_url|lead_reconhecido|token_reconhecimento|conversao_registrada|bloqueado_cpf_duplicado|/landing/ativacoes/.*/submit|/leads" backend frontend`
- stop_conditions:
  - parar se o PRD derivado exigir alterar o fluxo publico alem do que o repositorio atual mostra
  - parar se o estado atual do repo divergir do audit log de forma que exija novo intake

### T2
- objetivo: classificar os achados originais do hold contra o estado atual do repositorio
- precondicoes:
  - T1 concluida
  - baseline documental e tecnica formada
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `backend/app/services/landing_pages.py`
  - `backend/app/services/landing_page_submission.py`
  - `backend/app/routers/leads.py`
  - `backend/app/routers/landing_public.py`
  - `frontend/src/pages/EventLandingPage.tsx`
  - `backend/tests/test_leads_public_create_endpoint.py`
  - `backend/tests/test_landing_public_endpoints.py`
  - `frontend/src/services/__tests__/landing_public.test.ts`
  - `frontend/src/pages/__tests__/EventLandingPage.test.tsx`
- passos_atomicos:
  1. listar os achados `F1-NAO01` a `F1-NAO08` que afetam o fluxo publico e a cobertura do contrato
  2. para cada achado, classificar o estado atual como `implementado`, `nao_aplicavel` ou `residual`
  3. se surgir drift material fora do PRD derivado, marcar a issue como `BLOQUEADO` antes de ampliar o escopo
- comandos_permitidos:
  - `sed -n`
  - `rg -n`
  - `python3 -m pytest`
  - `npm --prefix frontend test -- --run`
- resultado_esperado: classificacao objetiva dos achados do hold contra o estado atual do repositorio
- testes_ou_validacoes_obrigatorias:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py`
  - `npm --prefix frontend test -- --run src/services/__tests__/landing_public.test.ts src/pages/__tests__/EventLandingPage.test.tsx`
- stop_conditions:
  - parar se qualquer teste focal falhar
  - parar se a classificacao depender de reinterpretar o gate da F1 original

### T3
- objetivo: transformar a comparacao em matriz rastreavel para as proximas issues do sibling
- precondicoes:
  - T2 concluida
  - classificacao dos achados original definida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md`
- passos_atomicos:
  1. registrar na propria issue uma matriz com `achado`, `fonte`, `estado atual`, `evidencia` e `destino`
  2. destacar quais itens viram `evidencia para reauditoria` e quais permanecem `risco residual`
  3. explicitar que a matriz orienta `ISSUE-F1-02-001` e `ISSUE-F1-02-002`
- comandos_permitidos:
  - `apply_patch`
  - `rg -n`
- resultado_esperado: issue pronta para servir de baseline rastreavel das proximas etapas
- testes_ou_validacoes_obrigatorias:
  - `rg -n "implementado|nao_aplicavel|residual|BLOQUEADO" PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md`
- stop_conditions:
  - parar se a matriz exigir criar artefato fora do backlog aprovado
  - parar se a evidencia final depender de alterar codigo funcional do fluxo publico

## Arquivos Reais Envolvidos

- `PROJETOS/LP/INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
- `PROJETOS/LP/PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`
- `PROJETOS/LP/AUDIT-LOG.md`
- `PROJETOS/LP/auditoria_fluxo_ativacao.md`
- `PROJETOS/LP/F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md`
- `backend/app/services/landing_pages.py`
- `backend/app/services/landing_page_submission.py`
- `backend/app/routers/leads.py`
- `backend/app/routers/landing_public.py`
- `frontend/src/pages/EventLandingPage.tsx`
- `backend/tests/test_leads_public_create_endpoint.py`
- `backend/tests/test_landing_public_endpoints.py`
- `frontend/src/services/__tests__/landing_public.test.ts`
- `frontend/src/pages/__tests__/EventLandingPage.test.tsx`

## Artifact Minimo

- matriz rastreavel `achado -> estado atual -> evidencia -> destino` registrada na propria issue

## Dependencias

- [Intake Derivado](../../../INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [PRD Derivado](../../../PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md)
- [Audit Log](../../../AUDIT-LOG.md)
- [Auditoria de Origem](../../../auditoria_fluxo_ativacao.md)
- [F1 Original](../../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [Epic](../EPIC-F1-01-BASELINE-DO-ESTADO-ATUAL.md)
- [Fase](../F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)

