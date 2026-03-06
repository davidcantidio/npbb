---
doc_id: "EPIC-F2-02-ENDPOINT-ANALISE-ETARIA-E-AUTORIZACAO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F2-02 - Endpoint Analise Etaria e Autorizacao

## Objetivo

Expor o endpoint `GET /dashboard/leads/analise-etaria` no router de dashboard, reaproveitando autenticacao JWT, regras de visibilidade por usuario e filtros do dominio existente.

## Resultado de Negocio Mensuravel

Usuarios autenticados passam a acessar a analise etaria diretamente pela API do produto, com um caminho unico e auditavel para alimentar o novo dashboard.

## Definition of Done

- O router `backend/app/routers/dashboard_leads.py` expone a rota nova sob o prefixo `/dashboard`.
- O endpoint exige Bearer token valido e reaproveita as mesmas regras de visibilidade do dashboard atual.
- `evento_id`, `data_inicio` e `data_fim` sao aceitos como query params, e `evento_id` reduz corretamente a lista `por_evento`.
- Respostas sem dados retornam payload valido com lista vazia e consolidado coerente, sem erro 500.

## Issues

### DLE-F2-02-001 - Publicar a rota nova no router de dashboard
Status: todo

**User story**
Como pessoa integradora do frontend, quero um endpoint dedicado para analise etaria a fim de consumir um contrato especifico sem sobrecarregar o relatorio legado.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` para falhar enquanto `GET /dashboard/leads/analise-etaria` nao existir ou nao serializar o novo response model.
2. `Green`: adicionar a rota em `backend/app/routers/dashboard_leads.py`, chamando o servico analitico e retornando `AgeAnalysisResponse`.
3. `Refactor`: manter a logica de agregacao fora do router e padronizar o uso de helpers de erro HTTP ja presentes no modulo.

**Criterios de aceitacao**
- Given um token valido, When o cliente chama `GET /dashboard/leads/analise-etaria`, Then a resposta HTTP e `200` com `version`, `generated_at`, `filters`, `por_evento` e `consolidado`.
- Given a rota nova publicada, When o endpoint legado `/dashboard/leads/relatorio` e chamado, Then ele continua respondendo sem regressao funcional.

### DLE-F2-02-002 - Reaproveitar autenticacao e visibilidade por usuario
Status: todo

**User story**
Como pessoa gestora de seguranca, quero que a nova rota use as mesmas barreiras de autenticacao e escopo do dashboard atual para nao abrir dados de eventos indevidamente.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` para falhar quando a nova rota responder sem autenticacao ou ignorar filtros de visibilidade por tipo de usuario.
2. `Green`: reutilizar `get_current_user`, `get_session` e a logica de `_apply_visibility` de `backend/app/routers/dashboard_leads.py` na rota nova.
3. `Refactor`: consolidar funcoes compartilhadas de filtros de acesso para que relatorio legado e analise etaria mantenham o mesmo comportamento.

**Criterios de aceitacao**
- Given request sem Bearer token, When a rota nova e chamada, Then a resposta e `401`.
- Given um usuario com escopo restrito, When a analise etaria e consultada, Then apenas eventos autorizados entram em `por_evento` e no consolidado.

### DLE-F2-02-003 - Tratar filtros vazios e cenarios sem dados
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero receber respostas vazias mas validas quando nao houver leads para os filtros aplicados para que a interface mostre "sem dados" em vez de erro.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_report_endpoint.py` para falhar quando um filtro sem correspondencia gerar erro 500 ou payload inconsistente.
2. `Green`: ajustar o endpoint e o servico para sempre devolver consolidado valido, `por_evento=[]` quando necessario e filtros ecoados na resposta.
3. `Refactor`: normalizar o tratamento de "sem dados" entre a rota nova e os handlers do dashboard existente.

**Criterios de aceitacao**
- Given um `evento_id` inexistente dentro do escopo do usuario, When o endpoint e chamado, Then a resposta e `200` com `por_evento` vazio e `base_total=0`.
- Given um intervalo de datas sem leads, When a resposta e gerada, Then o payload continua serializavel e sem campos obrigatorios ausentes.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f2/epic-f2-02-endpoint-analise-etaria-e-autorizacao.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
