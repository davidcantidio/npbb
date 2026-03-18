---
doc_id: "ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs:
  - "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md / secao 4"
  - "auditoria_fluxo_ativacao.md / F1-NAO01, F1-NAO02, F1-NAO05, F1-NAO06 e F1-NAO07"
  - "ISSUE-F1-01-001 / matriz de baseline do fluxo publico"
---

# ISSUE-F1-02-001 - Consolidar evidencia de contrato e paridade

## User Story

Como mantenedor do sibling `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`, quero
consolidar evidencia executavel do contrato publico atual e da paridade do
wrapper legado para que uma nova auditoria possa validar o fluxo por fatos,
nao pelo retrato historico do hold.

## Contexto Tecnico

O estado atual do repositorio ja mostra `POST /leads` como endpoint canônico,
`submit_url=/leads`, `LandingSubmitResponse` com os campos esperados e testes
focais relevantes no backend e no frontend. Esta issue transforma esse estado
em pacote objetivo de evidencia, usando os comandos exatos aprovados para
backend e frontend, e fecha uma matriz de paridade request/response suficiente
para reauditoria.

## Plano TDD

- Red: rodar a evidencia focal sem assumir que o contrato publico continua aderente
- Green: consolidar os resultados backend e frontend sobre `/leads`, wrapper e `lead_reconhecido`
- Refactor: registrar a matriz final de paridade request/response para leitura de auditoria

## Criterios de Aceitacao

- Given a suite backend focal, When o comando exato aprovado for executado, Then existe evidencia objetiva do contrato canônico e da paridade do wrapper legado
- Given a suite frontend focal, When o comando exato aprovado for executado, Then existe evidencia objetiva de que o caminho principal usa `/leads` e consome o contrato atual
- Given a issue fechada, When um auditor futuro consultar a trilha, Then a matriz de request/response explica a paridade entre `/leads` e `/landing/ativacoes/{id}/submit`
- Given qualquer regressao em `/leads`, wrapper, `submit_url` ou `lead_reconhecido`, When ela surgir, Then a issue responde `BLOQUEADO`

## Definition of Done da Issue

- [x] evidencia backend do contrato canônico e do wrapper legado consolidada
- [x] evidencia frontend do submit via `/leads` consolidada
- [x] matriz de paridade request/response registrada
- [x] regressao em contrato ou paridade tratada como `BLOQUEADO`

## Tasks Decupadas

- [x] T1: consolidar a evidencia backend do contrato canônico e do wrapper legado
- [x] T2: consolidar a evidencia frontend do submit via `/leads`
- [x] T3: fechar a matriz de paridade request/response para a reauditoria

## Instructions por Task

### T1
- objetivo: produzir evidencia backend repetivel do contrato canônico e da compatibilidade do wrapper legado
- precondicoes:
  - baseline de `ISSUE-F1-01-001` concluida
  - nenhum ajuste funcional novo planejado para o fluxo publico
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_leads_public_create_endpoint.py`
  - `backend/tests/test_landing_public_endpoints.py`
  - `backend/app/routers/leads.py`
  - `backend/app/routers/landing_public.py`
  - `backend/app/services/landing_page_submission.py`
- passos_atomicos:
  1. executar o comando backend aprovado sem alterar os arquivos de teste
  2. registrar os cenarios cobertos relevantes para `/leads`, wrapper, `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado` e `token_reconhecimento`
  3. destacar qualquer falha ou desvio como bloqueio objetivo da issue
- comandos_permitidos:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py`
- resultado_esperado: evidencia backend do contrato atual e da paridade do wrapper consolidada sem ambiguidade
- testes_ou_validacoes_obrigatorias:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py`
- stop_conditions:
  - parar se qualquer teste falhar
  - parar se a evidencia backend exigir alterar o contrato publico nesta issue

### T2
- objetivo: produzir evidencia frontend repetivel de que o caminho principal usa `/leads` e consome o contrato atual
- precondicoes:
  - T1 concluida
  - evidencia backend consolidada
- arquivos_a_ler_ou_tocar:
  - `frontend/src/services/__tests__/landing_public.test.ts`
  - `frontend/src/pages/__tests__/EventLandingPage.test.tsx`
  - `frontend/src/services/landing_public.ts`
  - `frontend/src/pages/EventLandingPage.tsx`
- passos_atomicos:
  1. executar o comando frontend aprovado sem alterar os testes
  2. registrar os cenarios cobertos relevantes para `submit_url=/leads`, `lead_reconhecido` e bloqueio por duplicidade
  3. destacar qualquer falha ou divergencia como bloqueio objetivo da issue
- comandos_permitidos:
  - `npm --prefix frontend test -- --run src/services/__tests__/landing_public.test.ts src/pages/__tests__/EventLandingPage.test.tsx`
- resultado_esperado: evidencia frontend do submit canônico e do consumo do contrato atual consolidada
- testes_ou_validacoes_obrigatorias:
  - `npm --prefix frontend test -- --run src/services/__tests__/landing_public.test.ts src/pages/__tests__/EventLandingPage.test.tsx`
- stop_conditions:
  - parar se qualquer teste falhar
  - parar se o frontend focal depender de alterar componentes fora do escopo do sibling

### T3
- objetivo: transformar os resultados de backend e frontend em matriz objetiva de paridade request/response
- precondicoes:
  - T1 e T2 concluidas
  - evidencia backend e frontend registradas
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-001-CONSOLIDAR-EVIDENCIA-DE-CONTRATO-E-PARIDADE.md`
  - `backend/tests/test_leads_public_create_endpoint.py`
  - `backend/tests/test_landing_public_endpoints.py`
  - `frontend/src/services/__tests__/landing_public.test.ts`
  - `frontend/src/pages/__tests__/EventLandingPage.test.tsx`
- passos_atomicos:
  1. registrar uma matriz curta com `request surface`, `response keys`, `evidencia backend` e `evidencia frontend`
  2. destacar na matriz a equivalencia entre `/leads` e `/landing/ativacoes/{id}/submit`
  3. apontar explicitamente quais achados da auditoria original foram cobertos por esta evidencia
- comandos_permitidos:
  - `apply_patch`
  - `rg -n`
- resultado_esperado: matriz de paridade pronta para consumo por auditoria independente
- testes_ou_validacoes_obrigatorias:
  - `rg -n "lead_reconhecido|conversao_registrada|bloqueado_cpf_duplicado|token_reconhecimento|submit_url" backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py frontend/src/services/__tests__/landing_public.test.ts frontend/src/pages/__tests__/EventLandingPage.test.tsx`
- stop_conditions:
  - parar se a paridade request/response nao puder ser demonstrada com os testes focais atuais
  - parar se a issue passar a exigir criacao de suite nova fora do backlog aprovado

## Arquivos Reais Envolvidos

- `backend/tests/test_leads_public_create_endpoint.py`
- `backend/tests/test_landing_public_endpoints.py`
- `backend/app/routers/leads.py`
- `backend/app/routers/landing_public.py`
- `backend/app/services/landing_page_submission.py`
- `frontend/src/services/__tests__/landing_public.test.ts`
- `frontend/src/pages/__tests__/EventLandingPage.test.tsx`
- `frontend/src/services/landing_public.ts`
- `frontend/src/pages/EventLandingPage.tsx`

## Artifact Minimo

- evidencia consolidada na propria issue, com matriz `surface -> response -> prova backend -> prova frontend`

## Evidencia Consolidada

### Resultado dos Comandos Aprovados

| Task | Comando | Resultado objetivo |
|---|---|---|
| T1 | `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py` | `45 passed in 4.00s` |
| T2 | `npm --prefix frontend test -- --run src/services/__tests__/landing_public.test.ts src/pages/__tests__/EventLandingPage.test.tsx` | `32 passed in 12.27s` |
| T3 | `rg -n "lead_reconhecido|conversao_registrada|bloqueado_cpf_duplicado|token_reconhecimento|submit_url" backend/tests/test_leads_public_create_endpoint.py backend/tests/test_landing_public_endpoints.py frontend/src/services/__tests__/landing_public.test.ts frontend/src/pages/__tests__/EventLandingPage.test.tsx` | referencias objetivas localizadas para `submit_url`, `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado` e `token_reconhecimento` |

### Leitura Objetiva por Task

#### T1 - Backend

- `POST /leads` registra conversao com `lead_reconhecido=true`, `conversao_registrada=true`, `bloqueado_cpf_duplicado=false` e `token_reconhecimento` presente.
- duplicidade em ativacao unica preserva reconhecimento e token, mas retorna `conversao_registrada=false` e `bloqueado_cpf_duplicado=true`.
- `GET /ativacoes/{id}/landing` devolve `formulario.submit_url="/leads"`.
- `POST /landing/ativacoes/{id}/submit` preserva a mesma superficie de resposta do endpoint canônico, incluindo `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado` e `token_reconhecimento`.

#### T2 - Frontend

- fixtures e asserts do frontend usam `submit_url="/leads"` como caminho principal.
- o servico consome `lead_reconhecido` e `token_reconhecimento` no contrato atual.
- a pagina cobre submit normal, fluxo reconhecido e bloqueio por duplicidade sem depender do endpoint legado como caminho principal.

### Matriz de Paridade Request/Response

| Request surface | Response keys | Evidencia backend | Evidencia frontend |
|---|---|---|---|
| `POST /leads` | `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado`, `token_reconhecimento` | `backend/tests/test_leads_public_create_endpoint.py:147-152`, `:206-212` | `frontend/src/services/__tests__/landing_public.test.ts:224-260`, `frontend/src/pages/__tests__/EventLandingPage.test.tsx:258-260`, `:621-623` |
| `GET landing` por evento/ativacao | `submit_url="/leads"` | `backend/tests/test_landing_public_endpoints.py:219` | `frontend/src/services/__tests__/landing_public.test.ts:60`, `frontend/src/pages/__tests__/EventLandingPage.test.tsx:89`, `:183` |
| `POST /landing/ativacoes/{id}/submit` | mesma superficie do canônico | `backend/tests/test_landing_public_endpoints.py:433-448`, `:553-566` | o frontend consome o contrato unificado e valida o mesmo conjunto de chaves no caminho principal via `submitLandingForm` |
| duplicidade em ativacao unica | `lead_reconhecido=true`, `conversao_registrada=false`, `bloqueado_cpf_duplicado=true`, `token_reconhecimento` presente | `backend/tests/test_leads_public_create_endpoint.py:206-212`, `backend/tests/test_landing_public_endpoints.py:560-566` | `frontend/src/pages/__tests__/EventLandingPage.test.tsx:621-623` |

### Equivalencia entre Endpoint Canonico e Wrapper Legado

`POST /leads` e `POST /landing/ativacoes/{id}/submit` estao cobertos por testes backend focais que exigem a mesma superficie de resposta para submit bem-sucedido e para bloqueio por duplicidade. Para a reauditoria, a leitura objetiva e: o caminho principal do produto usa `/leads`, enquanto o wrapper legado permanece apenas como adaptador compativel, sem drift de request/response demonstrado pela suite focal atual.

### Achados da Auditoria Original Cobertos

| Achado | Cobertura objetiva nesta issue |
|---|---|
| `F1-NAO01` | contrato de submit com `lead_reconhecido` demonstrado no backend e consumido no frontend |
| `F1-NAO02` | `submit_url="/leads"` demonstrado no payload de landing e no fluxo principal do frontend |
| `F1-NAO05` | contrato canônico e wrapper cobertos por testes focais com request/response consistente |
| `F1-NAO06` | bloqueio por duplicidade em ativacao unica demonstrado com `conversao_registrada=false` e `bloqueado_cpf_duplicado=true` |
| `F1-NAO07` | paridade entre caminho principal e wrapper legado demonstrada por evidencia backend e consumo frontend do contrato atual |

### Condicao de Bloqueio

Nenhum bloqueio foi observado nesta execucao. Se qualquer regressao futura surgir em `/leads`, no wrapper legado, em `submit_url` ou em `lead_reconhecido`, a issue deve ser tratada como `BLOQUEADO` e nao como ajuste silencioso desta trilha documental.

## Dependencias

- [Issue de Baseline](./ISSUE-F1-01-001-CLASSIFICAR-PRD-VS-REPO-NO-FLUXO-PUBLICO.md)
- [Auditoria de Origem](../../../auditoria_fluxo_ativacao.md)
- [Epic](../EPIC-F1-02-EVIDENCIA-OBJETIVA-PARA-REAUDITORIA.md)
- [Fase](../F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
