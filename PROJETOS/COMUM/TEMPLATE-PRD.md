---
doc_id: "TEMPLATE-PRD"
version: "3.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
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
> O principio do framework e **delivery-first**; a decomposicao em comportamentos entregaveis
> ocorre **apos** este PRD, na etapa explicita `PRD -> Features` (ver `GOV-PRD.md`,
> `PROMPT-PRD-PARA-FEATURES.md`, `SESSION-DECOMPOR-PRD-EM-FEATURES.md`).
> Este documento cobre **produto, escopo, restricoes, riscos, metricas, arquitetura geral e rollout** —
> **sem** catalogo de Features nem listas de User Stories.
> Estrutura obrigatoria do v3.0:
> `Especificacao Funcional` = fonte autoritativa do "o que/por que";
> `Plano Tecnico` = derivado revisavel do "como".
> Se houver conflito, **Especificacao Funcional prevalece**.
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

## 2. Especificacao Funcional

> Nesta secao, descreva **o que** precisa ser entregue e **por que** isso
> importa. Nao use stack, framework, endpoint, esquema fisico ou ferramenta
> como eixo da especificacao.

### 2.1 Problema ou Oportunidade

- **Problema atual**:
- **Evidência do problema**:
- **Custo de não agir**:
- **Por que agora**:

### 2.2 Publico e Operadores

- **Usuário principal**:
- **Usuário secundário**:
- **Operador interno**:
- **Quem aprova ou patrocina**:

### 2.3 Jobs to be Done

- **Job principal**:
- **Jobs secundários**:
- **Tarefa atual que será substituída**:

### 2.4 Escopo

### Dentro

-

### Fora

-

### 2.5 Resultado de Negocio e Metricas

- **Objetivo principal**:
- **Métricas leading**:
- **Métricas lagging**:
- **Critério mínimo para considerar sucesso**:

### 2.6 Restricoes e Guardrails

- **Restrições técnicas**:
- **Restrições operacionais**:
- **Restrições legais ou compliance**:
- **Restrições de prazo**:
- **Restrições de design ou marca**:

### 2.7 Dependencias e Integracoes

- **Sistemas internos impactados**:
- **Sistemas externos impactados**:
- **Dados de entrada necessários**:
- **Dados de saída esperados**:

## 3. Hipoteses Congeladas

- **Lacunas resolvidas na clarificacao**:
- **Hipoteses congeladas**:
- **Dependencias externas pendentes**:
- **Riscos de interpretacao**:

## 4. Plano Tecnico

> Esta secao descreve **como** a especificacao sera viabilizada. Se qualquer
> item daqui entrar em conflito com a `Especificacao Funcional`, o `Plano
> Tecnico` deve ser revisto.

### 4.1 Arquitetura Geral do Projeto

> Visao unificada de impacto arquitetural em nivel de projeto. Detalhamento por entregavel
> fica nos manifestos `FEATURE-*.md` apos a etapa `PRD -> Features`.

- **Backend**:
- **Frontend**:
- **Banco/migrações**:
- **Observabilidade**:
- **Autorização/autenticação**:
- **Rollout** (visao de alto nivel; expandir na secao Rollout e Comunicacao):

### 4.2 Decisoes Tecnicas e Contratos Relevantes

- **Contratos de API / integrações**:
- **Persistencia / migracoes**:
- **Observabilidade e operacao**:
- **Trade-offs tecnicos assumidos**:

## 5. Riscos Globais

- **Risco de produto**:
- **Risco técnico**:
- **Risco operacional**:
- **Risco de dados**:
- **Risco de adoção**:

## 6. Nao-Objetivos

-

---

> **Pos-PRD (nao faz parte deste arquivo):** backlog estruturado de features, user stories e tasks
> segue `GOV-FEATURE.md`, `GOV-USER-STORY.md`, `GOV-SCRUM.md` e os prompts/sessoes de decomposicao.

## 7. Dependencias Externas

| Dependência | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| <sistema> | API | <projeto> | <impacto> | pending |

---

## 8. Rollout e Comunicacao

- **Estratégia de deploy**:
- **Comunicação de mudanças**:
- **Treinamento necessário**:
- **Suporte pós-launch**:

---

## 9. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto** (expectativa, nao backlog de features/US neste PRD):
- **Critérios de auditoria**: <referência a GOV-AUDITORIA.md>
- **Threshold anti-monolito**: <referência a SPEC-ANTI-MONOLITO.md>

---

## 10. Checklist de Prontidao

- [ ] Intake referenciado e versao confirmada
- [ ] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
- [ ] `Especificacao Funcional` e `Plano Tecnico` estao separados com precedencia explicita
- [ ] `Hipoteses Congeladas` esta preenchido com lacunas resolvidas, hipoteses aceitas, dependencias pendentes e riscos de interpretacao
- [ ] Arquitetura geral e rollout descritos **sem** catalogo de Features nem tabelas de User Stories neste PRD
- [ ] Dependencias externas mapeadas
- [ ] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

---

## 11. Anexos e Referencias

- <Link para diagrama>
- <Link para documentação técnica>
- <Link para protótipo>

---

> **Frase Guia (pipeline):** PRD direciona; Feature organiza; User Story fatia; Task executa; Teste valida.
