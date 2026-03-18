---
doc_id: "TEMPLATE-PRD"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
project: "<PROJETO>"
intake_kind: "<copiar_do_intake>"
source_mode: "<copiar_do_intake>"
origin_project: "<copiar_do_intake_ou_nao_aplicavel>"
origin_phase: "<copiar_do_intake_ou_nao_aplicavel>"
origin_audit_id: "<copiar_do_intake_ou_nao_aplicavel>"
origin_report_path: "<copiar_do_intake_ou_nao_aplicavel>"
product_type: "<copiar_do_intake>"
delivery_surface: "<copiar_do_intake>"
business_domain: "<copiar_do_intake>"
criticality: "<copiar_do_intake>"
data_sensitivity: "<copiar_do_intake>"
integrations: []
change_type: "<copiar_do_intake>"
audit_rigor: "<copiar_do_intake>"
---

# PRD - <PROJETO>

> Preencha todos os campos. Mantenha a estrutura de governança existente.
> O principio do framework e `delivery-first`; no planejamento, isso se materializa
> como `feature-first`.
> O eixo principal deste PRD sao as **Features** (comportamentos entregaveis).
> A arquitetura (banco/backend/frontend) aparece como impacto de cada feature,
> nao como organizacao principal.
> Copie do intake as taxonomias e os campos de rastreabilidade do frontmatter,
> ajustando apenas quando houver motivo documentado.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-<PROJETO>.md](./INTAKE-<PROJETO>.md)
- **Versão do intake**: X.X
- **Data de criação**: YYYY-MM-DD
- **PRD derivado** (se aplicável): [PRD-<PROJETO>-<SLUG>.md](./PRD-<PROJETO>-<SLUG>.md)

## 1. Resumo Executivo

- **Nome do projeto**:
- **Tese em 1 frase**:
- **Valor esperado em 3 linhas**:

## 2. Problema ou Oportunidade

- **Problema atual**:
- **Evidência do problema**:
- **Custo de não agir**:
- **Por que agora**:

## 3. Público e Operadores

- **Usuário principal**:
- **Usuário secundário**:
- **Operador interno**:
- **Quem aprova ou patrocina**:

## 4. Jobs to be Done

- **Job principal**:
- **Jobs secundários**:
- **Tarefa atual que será substituída**:

## 5. Escopo

### Dentro

-

### Fora

-

## 6. Resultado de Negócio e Métricas

- **Objetivo principal**:
- **Métricas leading**:
- **Métricas lagging**:
- **Critério mínimo para considerar sucesso**:

## 7. Restrições e Guardrails

- **Restrições técnicas**:
- **Restrições operacionais**:
- **Restrições legais ou compliance**:
- **Restrições de prazo**:
- **Restrições de design ou marca**:

## 8. Dependências e Integrações

- **Sistemas internos impactados**:
- **Sistemas externos impactados**:
- **Dados de entrada necessários**:
- **Dados de saída esperados**:

## 9. Arquitetura Geral do Projeto

> Visão geral de impacto arquitetural (detalhes por feature na seção Features)

- **Backend**:
- **Frontend**:
- **Banco/migrações**:
- **Observabilidade**:
- **Autorização/autenticação**:
- **Rollout**:

## 10. Riscos Globais

- **Risco de produto**:
- **Risco técnico**:
- **Risco operacional**:
- **Risco de dados**:
- **Risco de adoção**:

## 11. Não-Objetivos

-

---

# 12. Features do Projeto

> **Este é o eixo principal do planejamento**. Cada feature representa um comportamento
> entregável e demonstrável. Arquitetura (banco/backend/frontend) aparece como impacto
> de cada feature, não como organização principal.
>
> Regra: Se uma feature não pode ser demonstrada como algo utilizável, ela está
> no nível errado de planejamento.
>
> Use IDs estaveis (`Feature 1`, `Feature 2`, ...) e reutilize exatamente esses
> IDs nas secoes de Fases e Epicos.

## Feature 1: <Nome da Feature>

### Objetivo de Negócio

<Descrição do problema que esta feature resolve>

### Comportamento Esperado

<O que o usuário consegue fazer quando esta feature estiver pronta>

### Critérios de Aceite

- [ ] <Critério verificável 1>
- [ ] <Critério verificável 2>
- [ ] <Critério verificável 3>

### Dependências com Outras Features

- <Feature X>: <tipo de dependência>

### Riscos Específicos

-

### Fases de Implementação

1. **Modelagem e Migration**: <descrição>
2. **API**: <descrição>
3. **UI**: <descrição>
4. **Testes**: <descrição>

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | <tabelas> | <colunas, constraints> |
| Backend | <endpoints> | <métodos, contratos> |
| Frontend | <telas> | <componentes, estados> |
| Testes | <suítes> | <escopo> |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | <ação atômica> | 2 | - |
| T2 | <ação atômica> | 3 | T1 |
| T3 | <ação atômica> | 2 | T2 |

---

## Feature 2: <Nome da Feature>

> Repita a mesma estrutura da Feature 1

---

## Feature N: <Nome da Feature>

> Repita a mesma estrutura

---

# 13. Estrutura de Fases

> Mantida a estrutura existente do framework. As features são alocadas nas fases
> conforme dependências e prioridade. Nao organize fases por camada tecnica.

## Fase 1: <Nome da Fase 1>

- **Objetivo**:
- **Features incluídas**:
  - Feature 1
  - Feature 2
- **Gate de saída**:
- **Critérios de aceite**:

### Épicos da Fase 1

| Épico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F1-01 | Feature 1 | todo | 8 |
| EPIC-F1-02 | Feature 2 | todo | 5 |

## Fase 2: <Nome da Fase 2>

- **Objetivo**:
- **Features incluídas**:
- **Gate de saída**:
- **Critérios de aceite**:

---

# 14. Épicos

> Cada épico agrupa issues que implementam uma ou mais features. O campo
> "Feature de Origem" rastreia qual comportamento está sendo entregue.
> Cada linha de issue deve repetir explicitamente a mesma feature usada no PRD.

## Épico: <Nome do Épico>

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**:
- **Resultado de Negócio Mensurável**:
- **Contexto Arquitetural**:
- **Definition of Done**:
  - [ ]

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F1-01-001 | <nome> | 3 | todo | Feature 1 |
| ISSUE-F1-01-002 | <nome> | 5 | todo | Feature 1 |

---

# 15. Dependências Externas

| Dependência | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| <sistema> | API | <projeto> | <impacto> | pending |

---

# 16. Rollout e Comunicação

- **Estratégia de deploy**:
- **Comunicação de mudanças**:
- **Treinamento necessário**:
- **Suporte pós-launch**:

---

# 17. Revisões e Auditorias

- **Auditorias planejadas**: <fases>
- **Critérios de auditoria**: <referência a GOV-AUDITORIA.md>
- **Threshold anti-monolito**: <referência a SPEC-ANTI-MONOLITO.md>

---

# 18. Checklist de Prontidão

- [ ] Intake referenciado e versao confirmada
- [ ] Features definidas com critérios de aceite verificáveis
- [ ] Cada feature com impacts por camada preenchidos
- [ ] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
- [ ] Épicos criados e vinculados a features
- [ ] Fases definidas com gates de saída
- [ ] Dependências externas mapeadas
- [ ] Riscos identificados e mitigacoes planejadas
- [ ] Rollout planejado

---

# 19. Anexos e Referências

- <Link para diagrama>
- <Link para documentação técnica>
- <Link para protótipo>

---

> **Frase Guia**: "Feature organiza, Task executa, Teste valida"
