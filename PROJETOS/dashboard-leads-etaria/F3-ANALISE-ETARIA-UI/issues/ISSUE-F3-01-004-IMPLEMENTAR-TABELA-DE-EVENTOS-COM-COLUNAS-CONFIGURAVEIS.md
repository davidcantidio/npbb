---
doc_id: "ISSUE-F3-01-004-IMPLEMENTAR-TABELA-DE-EVENTOS-COM-COLUNAS-CONFIGURAVEIS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-01-004 - Implementar tabela de eventos com colunas configuráveis

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar tabela de eventos com colunas configuráveis para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar a tabela de eventos que exibe todas as métricas da seção 3.2 do PRD: evento
(nome + local), base, clientes BB (% e volume), não clientes, faixas etárias (18–25,
26–40, fora) e faixa dominante. Suportar ordenação por coluna.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [ ] Tabela exibe todos os campos da seção 3.2 do PRD
- [ ] Colunas de percentual formatadas com 1 casa decimal + símbolo %
- [ ] Ordenação por qualquer coluna numérica (click no header)
- [ ] Indicação visual de coluna ordenada e direção (asc/desc)
- [ ] Scroll horizontal em telas pequenas
- [ ] Células de clientes BB exibem "—" quando cobertura insuficiente (null do backend)
- [ ] Linha de evento é clicável (futuro: navegação para detalhe do evento)

## Definition of Done da Issue

- [ ] Tabela exibe todos os campos da seção 3.2 do PRD
- [ ] Colunas de percentual formatadas com 1 casa decimal + símbolo %
- [ ] Ordenação por qualquer coluna numérica (click no header)
- [ ] Indicação visual de coluna ordenada e direção (asc/desc)
- [ ] Scroll horizontal em telas pequenas
- [ ] Células de clientes BB exibem "—" quando cobertura insuficiente (null do backend)
- [ ] Linha de evento é clicável (futuro: navegação para detalhe do evento)

## Tarefas Decupadas

- [ ] T1: Criar componente `EventsAgeTable.tsx`
- [ ] T2: Definir colunas com formatação (percentual, volume, texto)
- [ ] T3: Implementar ordenação por coluna no header
- [ ] T4: Tratar valores null (cobertura BB insuficiente) com placeholder "—"
- [ ] T5: Implementar scroll horizontal responsivo
- [ ] T6: Estilizar zebra-striping e hover para legibilidade

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/EventsAgeTable.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/EventsAgeTable.tsx`

## Dependencias

- [Issue Dependente](./ISSUE-F3-01-001-CRIAR-TIPOS-TYPESCRIPT-E-HOOK-DE-CONSUMO-DA-API.md)
- [Epic](../EPIC-F3-01-DADOS-E-VISUALIZACOES.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-01-DADOS-E-VISUALIZACOES]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
