---
doc_id: "ISSUE-F1-02-002-IMPLEMENTAR-LOGICA-DE-QUERY-DA-ANALISE-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
task_instruction_mode: "optional"
---

# ISSUE-F1-02-002 - Implementar lógica de query da análise etária

## User Story

Como engenheiro de backend do dashboard, quero entregar Implementar lógica de query da análise etária para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar o serviço/use-case que executa a query de análise etária: cálculo de idade a
partir de `data_nascimento`, classificação em faixas, agregação por evento, cálculo de
cobertura BB e geração do consolidado (Top 3, média, mediana, concentração).

Avaliar se o cálculo deve ser feito em SQL (melhor performance) ou em Python (maior
flexibilidade). Para v1.0, priorizar clareza e correção; otimizar em iteração futura
se necessário. O threshold de cobertura BB deve ser configurável (default 80%).

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Idade calculada usando data atual como referência (`date.today()`)
- [x] Faixas: 18–25, 26–40, fora de 18–40 — classificação correta para idades limite (18, 25, 26, 40)
- [x] Leads com `data_nascimento NULL` contabilizados em `sem_info_volume`, excluídos dos percentuais
- [x] Percentuais das faixas somam 100% (sobre base com `data_nascimento NOT NULL`)
- [x] Cobertura BB = % de leads com `is_cliente_bb NOT NULL`
- [x] Quando cobertura < threshold (80% default), `clientes_bb_volume` e `clientes_bb_pct` retornam `null`
- [x] Consolidado: Top 3 por volume, média aritmética, mediana, concentração Top 3
- [x] Filtros `evento_id`, `data_inicio`, `data_fim` aplicados corretamente
- [x] Sem divisão por zero quando base filtrada é vazia

## Definition of Done da Issue

- [x] Idade calculada usando data atual como referência (`date.today()`)
- [x] Faixas: 18–25, 26–40, fora de 18–40 — classificação correta para idades limite (18, 25, 26, 40)
- [x] Leads com `data_nascimento NULL` contabilizados em `sem_info_volume`, excluídos dos percentuais
- [x] Percentuais das faixas somam 100% (sobre base com `data_nascimento NOT NULL`)
- [x] Cobertura BB = % de leads com `is_cliente_bb NOT NULL`
- [x] Quando cobertura < threshold (80% default), `clientes_bb_volume` e `clientes_bb_pct` retornam `null`
- [x] Consolidado: Top 3 por volume, média aritmética, mediana, concentração Top 3
- [x] Filtros `evento_id`, `data_inicio`, `data_fim` aplicados corretamente
- [x] Sem divisão por zero quando base filtrada é vazia

## Tarefas Decupadas

- [x] T1: Criar módulo de serviço `backend/app/services/dashboard_service.py`
- [x] T2: Implementar função de cálculo de idade e classificação em faixa
- [x] T3: Implementar query de agregação por evento com faixas e cobertura BB
- [x] T4: Implementar lógica de consolidado (Top 3, média, mediana, concentração)
- [x] T5: Implementar aplicação de filtros (evento_id, data_inicio, data_fim)
- [x] T6: Tratar edge cases (base vazia, todos sem data_nascimento, cobertura zero)

## Arquivos Reais Envolvidos

- `backend/app/services/dashboard_service.py`
- `backend/tests/`

## Artifact Minimo

- `backend/app/services/dashboard_service.py`

## Dependencias

- [Issue Dependente](./ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md)
- [Issue Dependente](./ISSUE-F1-01-001-ADICIONAR-CAMPOS-IS-CLIENTE-BB-E-IS-CLIENTE-ESTILO-AO-MODELO-LEAD.md)
- [Epic](../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA]]`
- `[[../../../PRD-DASHBOARD-LEADS-ETARIA]]`
