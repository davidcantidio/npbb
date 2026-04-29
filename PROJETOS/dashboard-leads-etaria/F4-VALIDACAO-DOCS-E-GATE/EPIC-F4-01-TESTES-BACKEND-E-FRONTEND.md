---
doc_id: "EPIC-F4-01-TESTES-BACKEND-E-FRONTEND"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F4-01 - Testes Backend e Frontend

## Objetivo

Garantir cobertura automatizada suficiente para as regras criticas da analise etaria no backend e para os fluxos principais de renderizacao e consumo do endpoint no frontend.

## Resultado de Negocio Mensuravel

A entrega v1.0 ganha regressao automatizada para os criterios de aceite centrais, reduzindo risco de quebra silenciosa em calculos de faixa, cobertura BB e navegacao protegida.

## Definition of Done

- Os testes de backend cobrem faixas etarias, `sem_info`, cobertura BB, filtro por `evento_id` e autenticacao.
- Os testes de frontend cobrem rendering da Home, navegacao para a analise etaria e estados principais da tela.
- Existe pelo menos um cenario de integracao entre service e pagina da analise etaria.
- Nenhuma suite relevante do dashboard atual quebra com a introducao do portfolio.

## Issues

### DLE-F4-01-001 - Ampliar cobertura backend da analise etaria
Status: todo

**User story**
Como pessoa mantenedora do backend, quero testes que provem os calculos de idade e cobertura BB para detectar regressao antes de chegar a producao.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` e `backend/tests/test_dashboard_leads_report_endpoint.py` com cenarios que falhem quando `sem_info`, faixa dominante, Top 3 e cobertura BB forem calculados incorretamente.
2. `Green`: implementar os ajustes no servico e no endpoint ate os cenarios passarem com banco SQLite de teste.
3. `Refactor`: concentrar fixtures de seeds do dashboard em helpers reutilizaveis para evitar duplicacao entre suites.

**Criterios de aceitacao**
- Given um conjunto de leads com idades variadas e valores `NULL`, When os testes rodam, Then as faixas retornadas batem exatamente com os dados sem incluir `sem_info` nos percentuais.
- Given requests autenticadas e nao autenticadas, When os testes do endpoint executam, Then os status `200` e `401` aparecem nos cenarios esperados.

### DLE-F4-01-002 - Cobrir Home do portfolio e pagina da analise no frontend
Status: todo

**User story**
Como pessoa mantenedora do frontend, quero smoke tests do portfolio e da pagina etaria para garantir que rotas protegidas e componentes principais continuam renderizando.

**Plano TDD**
1. `Red`: usar `frontend/src/test/setup.ts`, `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx` e `frontend/src/components/__tests__/ProtectedRoute.test.tsx` para falhar enquanto a Home do dashboard e a pagina etaria nao renderizarem os blocos principais.
2. `Green`: adicionar a cobertura da Home e da pagina etaria, mockando o service do dashboard quando necessario.
3. `Refactor`: extrair builders de resposta mock para compartilhar dados entre testes de service e de pagina.

**Criterios de aceitacao**
- Given usuario autenticado, When a rota `/dashboard` e aberta em teste, Then o card da analise etaria aparece.
- Given resposta da API com erro ou sem dados, When a pagina etaria e renderizada em teste, Then os estados corretos da interface aparecem.

### DLE-F4-01-003 - Validar integracao basica service + pagina
Status: todo

**User story**
Como pessoa revisora da entrega, quero uma prova de que a pagina consome o service certo para evitar que a UI renderize mocks desatualizados.

**Plano TDD**
1. `Red`: usar o padrao de `frontend/src/services/__tests__/leads_import_etl.test.ts` para falhar enquanto a pagina da analise etaria nao chamar o metodo novo de `frontend/src/services/dashboard_leads.ts`.
2. `Green`: amarrar a pagina e o service ao contrato da analise etaria com mocks de resposta tipada.
3. `Refactor`: reduzir acoplamento entre a pagina e detalhes de `fetch`, centralizando a orquestracao no service.

**Criterios de aceitacao**
- Given filtros preenchidos, When a pagina executa a busca em teste, Then o service novo e chamado com os parametros esperados.
- Given resposta bem-sucedida, When a Promise resolve, Then o resumo consolidado e a lista `por_evento` aparecem na tela.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f4/epic-f4-01-testes-backend-e-frontend.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
