---
doc_id: "ISSUE-F1-02-004-TESTES-UNITARIOS-DO-ENDPOINT-DE-ANALISE-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-02-004 - Testes unitários do endpoint de análise etária

## User Story

Como engenheiro de backend do dashboard, quero entregar Testes unitários do endpoint de análise etária para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Cobrir o endpoint e o serviço de análise etária com testes unitários que validem
cálculos de faixa, cobertura BB, consolidado e edge cases.

Seguir o padrão de testes do projeto: `TESTING=true` ativa SQLite fallback. Usar
fixtures compartilhadas quando possível.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Teste: faixas etárias calculadas corretamente para idades 17, 18, 25, 26, 40, 41
- [x] Teste: leads sem `data_nascimento` excluídos dos percentuais
- [x] Teste: cobertura BB < 80% retorna `null` para campos BB
- [x] Teste: cobertura BB ≥ 80% retorna valores calculados
- [x] Teste: consolidado com Top 3 correto (volume decrescente)
- [x] Teste: média e mediana calculadas conforme definição do PRD
- [x] Teste: filtro por `evento_id` retorna apenas dados do evento selecionado
- [x] Teste: base vazia retorna resposta válida com zeros
- [x] Teste: endpoint retorna 401 sem autenticação

## Definition of Done da Issue

- [x] Teste: faixas etárias calculadas corretamente para idades 17, 18, 25, 26, 40, 41
- [x] Teste: leads sem `data_nascimento` excluídos dos percentuais
- [x] Teste: cobertura BB < 80% retorna `null` para campos BB
- [x] Teste: cobertura BB ≥ 80% retorna valores calculados
- [x] Teste: consolidado com Top 3 correto (volume decrescente)
- [x] Teste: média e mediana calculadas conforme definição do PRD
- [x] Teste: filtro por `evento_id` retorna apenas dados do evento selecionado
- [x] Teste: base vazia retorna resposta válida com zeros
- [x] Teste: endpoint retorna 401 sem autenticação

## Tarefas Decupadas

- [x] T1: Criar fixtures com leads de diferentes idades, eventos e estados de cruzamento BB
- [x] T2: Testar serviço de cálculo (unit tests puros)
- [x] T3: Testar endpoint via TestClient do FastAPI (integration tests)
- [x] T4: Testar edge cases (sem leads, todos sem data_nascimento, cobertura zero)
- [x] T5: Testar autenticação (401 sem token, 200 com token válido)

## Arquivos Reais Envolvidos

- `backend/tests/`
- `backend/app/routers/dashboard.py`

## Artifact Minimo

- `backend/tests/`

## Dependencias

- [Issue Dependente](./ISSUE-F1-02-003-IMPLEMENTAR-ENDPOINT-GET-API-V1-DASHBOARD-LEADS-ANALISE-ETARIA.md)
- [Epic](../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
