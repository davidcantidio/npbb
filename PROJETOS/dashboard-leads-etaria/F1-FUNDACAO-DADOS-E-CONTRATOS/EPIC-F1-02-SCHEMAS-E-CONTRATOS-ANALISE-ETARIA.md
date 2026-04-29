---
doc_id: "EPIC-F1-02-SCHEMAS-E-CONTRATOS-ANALISE-ETARIA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F1-02 - Schemas e Contratos Analise Etaria

## Objetivo

Definir os contratos tipados de filtros e resposta da analise etaria, incluindo `AgeAnalysisResponse`, `faixas`, cobertura BB e alinhamento inicial com os tipos usados pelo frontend.

## Resultado de Negocio Mensuravel

Backend e frontend passam a compartilhar um contrato explicito para a nova analise, reduzindo regressao de integracao e deixando o endpoint pronto para documentacao OpenAPI.

## Definition of Done

- Existe um schema de query com `evento_id`, `data_inicio` e `data_fim`, com validacao objetiva de intervalo de datas.
- Existe um response model com `version`, `generated_at`, `filters`, `por_evento` e `consolidado`.
- As faixas etarias modelam `18-25`, `26-40`, `fora_18_40` e `sem_info` conforme o PRD.
- `frontend/src/services/dashboard_leads.ts` possui tipos compativeis com o contrato backend planejado.

## Issues

### DLE-F1-02-001 - Modelar o contrato Pydantic da analise etaria
Status: todo

**User story**
Como pessoa mantenedora da API, quero um contrato Pydantic claro para a analise etaria a fim de expor um payload estavel e validavel.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_report_endpoint.py` para falhar enquanto `backend/app/schemas/dashboard_leads.py` nao aceitar os campos `por_evento`, `consolidado`, `faixas` e `cobertura_bb_pct`.
2. `Green`: criar ou expandir `backend/app/schemas/dashboard_leads.py` com `AgeAnalysisResponse`, `AgeBreakdown`, itens por evento e consolidado.
3. `Refactor`: extrair modelos reutilizaveis de faixa e top eventos para reduzir duplicacao entre resposta por evento e consolidada.

**Criterios de aceitacao**
- Given uma resposta valida do endpoint, When o schema Pydantic a serializa, Then os campos `version`, `generated_at`, `filters`, `por_evento` e `consolidado` existem com os tipos esperados.
- Given `clientes_bb_pct` indisponivel por baixa cobertura, When o schema e instanciado, Then o valor `NULL` e aceito sem quebrar a serializacao.

### DLE-F1-02-002 - Fechar o contrato de filtros e threshold de cobertura
Status: todo

**User story**
Como pessoa que consome o dashboard, quero filtros consistentes e threshold padrao de cobertura para obter respostas previsiveis ao alternar entre visao geral e evento especifico.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` para falhar quando `data_fim < data_inicio` ou quando `evento_id` invalido nao gerar erro de validacao claro.
2. `Green`: modelar o query object no backend com validacao de intervalo e definir o threshold default de cobertura BB em local configuravel do modulo de dashboard.
3. `Refactor`: reaproveitar funcoes de normalizacao e validacao ja existentes em `backend/app/routers/dashboard_leads.py` para evitar contratos concorrentes.

**Criterios de aceitacao**
- Given `data_inicio` maior que `data_fim`, When a query e validada, Then a API rejeita o request com erro objetivo de faixa de datas.
- Given request sem `evento_id`, When a query e aceita, Then o contrato indica explicitamente que a resposta deve conter o consolidado geral e a lista `por_evento`.

### DLE-F1-02-003 - Alinhar tipos de consumo no frontend
Status: todo

**User story**
Como pessoa desenvolvedora do frontend, quero tipos coerentes em `frontend/src/services/dashboard_leads.ts` para consumir a analise etaria sem inferencias manuais em cada componente.

**Plano TDD**
1. `Red`: usar o setup de `frontend/src/test/setup.ts` e o padrao de `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx` para falhar quando o parser de `frontend/src/services/dashboard_leads.ts` nao reconhecer os novos campos da resposta.
2. `Green`: adicionar os tipos da analise etaria em `frontend/src/services/dashboard_leads.ts`, mantendo o contrato atual do relatorio legado.
3. `Refactor`: separar os tipos do relatorio legado e da analise etaria para reduzir acoplamento e facilitar a transicao de `DashboardLeads.tsx`.

**Criterios de aceitacao**
- Given uma resposta JSON com `por_evento` e `consolidado`, When o service do frontend a parseia, Then o objeto retornado possui tipos compativeis com o backend.
- Given o relatorio legado ainda em uso, When os tipos novos sao introduzidos, Then `getDashboardLeadsReport` continua compilando sem quebra de assinatura.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f1/epic-f1-02-schemas-e-contratos-analise-etaria.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
