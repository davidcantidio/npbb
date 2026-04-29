---
doc_id: "EPIC-F3-02-PAGINA-ANALISE-ETARIA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F3-02 - Pagina Analise Etaria

## Objetivo

Implementar a pagina `/dashboard/leads/analise-etaria` com filtros, KPIs consolidados, tabela por evento e visualizacao da distribuicao etaria a partir do endpoint novo.

## Resultado de Negocio Mensuravel

Operadores e gestores passam a enxergar em um unico painel a base total, os eventos dominantes e o perfil etario do portfolio sem depender de relatorios externos.

## Definition of Done

- O frontend possui uma funcao de service dedicada para chamar `GET /dashboard/leads/analise-etaria`.
- A pagina apresenta filtros por periodo e evento, usando os componentes ja adotados no dashboard atual.
- O topo da pagina mostra o consolidado geral com `base_total`, clientes BB, faixa dominante, Top 3, media e mediana.
- A lista por evento mostra nome, local, base, cobertura BB e distribuicao etaria em formato de tabela e/ou grafico legivel.

## Issues

### DLE-F3-02-001 - Consumir o endpoint novo no service do frontend
Status: todo

**User story**
Como pessoa desenvolvedora do frontend, quero um client HTTP dedicado para a analise etaria para separar o novo fluxo do relatorio legado.

**Plano TDD**
1. `Red`: usar `frontend/src/test/setup.ts` e o padrao de `frontend/src/services/__tests__/leads_import_etl.test.ts` para falhar quando `frontend/src/services/dashboard_leads.ts` nao conseguir montar a URL e tipar a resposta da analise etaria.
2. `Green`: adicionar um metodo dedicado em `frontend/src/services/dashboard_leads.ts` para chamar `/dashboard/leads/analise-etaria` com Bearer token e query params.
3. `Refactor`: separar helpers de parsing e erro para que o relatorio legado e a analise etaria compartilhem apenas o necessario.

**Criterios de aceitacao**
- Given filtros de `evento_id`, `data_inicio` e `data_fim`, When o service monta a requisicao, Then a query string enviada corresponde aos filtros informados.
- Given erro HTTP do backend, When o service recebe a resposta, Then a excecao propagada continua legivel para exibicao na UI.

### DLE-F3-02-002 - Construir o painel consolidado da analise
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero ver o consolidado geral no topo da pagina para entender rapidamente a fotografia do portfolio antes de entrar no detalhe por evento.

**Plano TDD**
1. `Red`: adaptar a estrutura de `frontend/src/pages/DashboardLeads.tsx` para falhar enquanto a pagina nova nao exibir `base_total`, clientes BB, Top 3, media e mediana usando dados do endpoint etario.
2. `Green`: criar a pagina da analise etaria reaproveitando os componentes de `Card`, `Grid` e `Alert` ja usados em `frontend/src/pages/DashboardLeads.tsx`.
3. `Refactor`: extrair blocos visuais reutilizaveis de KPI e resumo consolidado para manter a pagina enxuta e preparada para dashboards futuros.

**Criterios de aceitacao**
- Given resposta com consolidado preenchido, When a pagina carrega, Then os KPIs principais aparecem antes da lista por evento.
- Given `top_eventos` com tres itens, When o painel consolidado e renderizado, Then o Top 1, Top 2 e Top 3 aparecem na mesma ordem recebida da API.

### DLE-F3-02-003 - Exibir tabela e distribuicao por evento
Status: todo

**User story**
Como pessoa analista de marketing, quero comparar evento a evento a distribuicao etaria e a cobertura BB para identificar rapidamente carteiras fora do padrao.

**Plano TDD**
1. `Red`: usar a base de componentes ja existente em `frontend/src/pages/DashboardLeads.tsx` para falhar enquanto a pagina nao listar todos os eventos retornados em `por_evento`.
2. `Green`: implementar tabela e visualizacao de distribuicao por evento, incluindo nome, cidade, estado, base, cobertura e faixa dominante.
3. `Refactor`: extrair o renderer de barras ou colunas empilhadas para um componente proprio, desacoplando a tela de regras de desenho.

**Criterios de aceitacao**
- Given dois ou mais eventos na resposta, When a pagina renderiza o detalhe, Then existe uma linha ou card para cada item de `por_evento`.
- Given um evento com faixa dominante calculada, When o detalhe e exibido, Then a anotacao textual da faixa dominante aparece junto do respectivo evento.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f3/epic-f3-02-pagina-analise-etaria.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
