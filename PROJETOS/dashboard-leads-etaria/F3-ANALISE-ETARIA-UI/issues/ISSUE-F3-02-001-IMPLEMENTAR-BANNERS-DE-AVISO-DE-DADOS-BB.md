---
doc_id: "ISSUE-F3-02-001-IMPLEMENTAR-BANNERS-DE-AVISO-DE-DADOS-BB.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F3-02-001 - Implementar banners de aviso de dados BB

## User Story

Como engenheiro de frontend do dashboard, quero entregar Implementar banners de aviso de dados BB para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Criar componentes de banner de aviso que indicam a qualidade dos dados de cruzamento
BB. O banner é exibido no topo da página de análise etária e dentro de cards de evento
individual quando relevante.

Thresholds (80% e 20%) devem ser constantes configuráveis no frontend, alinhados com
o backend. Usar mesmos valores definidos no PRD seção 4.4.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [ ] Banner amarelo (⚠️) quando cobertura entre 20% e 80%: "Dados parcialmente disponíveis. Realize o cruzamento completo com a base do Banco."
- [ ] Banner vermelho (🔴) quando cobertura < 20%: "Dados de vínculo BB indisponíveis para este evento — realize o cruzamento com a base de dados do Banco."
- [ ] Sem banner quando cobertura ≥ 80%
- [ ] Banner no topo da página usa cobertura consolidada
- [ ] Texto do banner inclui instrução de ação ao operador
- [ ] Banner é dismissível (X) mas reaparece ao recarregar/mudar filtro
- [ ] Componente `CoverageBanner` genérico e reutilizável

## Definition of Done da Issue

- [ ] Banner amarelo (⚠️) quando cobertura entre 20% e 80%: "Dados parcialmente disponíveis. Realize o cruzamento completo com a base do Banco."
- [ ] Banner vermelho (🔴) quando cobertura < 20%: "Dados de vínculo BB indisponíveis para este evento — realize o cruzamento com a base de dados do Banco."
- [ ] Sem banner quando cobertura ≥ 80%
- [ ] Banner no topo da página usa cobertura consolidada
- [ ] Texto do banner inclui instrução de ação ao operador
- [ ] Banner é dismissível (X) mas reaparece ao recarregar/mudar filtro
- [ ] Componente `CoverageBanner` genérico e reutilizável

## Tarefas Decupadas

- [ ] T1: Criar componente `CoverageBanner.tsx` com props: `coverage`, `threshold_warning`, `threshold_danger`
- [ ] T2: Implementar variante amarela (warning)
- [ ] T3: Implementar variante vermelha (danger)
- [ ] T4: Integrar no topo da página `LeadsAgeAnalysisPage`
- [ ] T5: Integrar em cards de evento individual (na tabela ou detalhe)

## Arquivos Reais Envolvidos

- `frontend/src/components/dashboard/CoverageBanner.tsx`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`

## Artifact Minimo

- `frontend/src/components/dashboard/CoverageBanner.tsx`

## Dependencias

- [Epic](../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE.md)
- [Fase](../F3_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F3-02-COBERTURA-ESTADOS-QUALIDADE]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
