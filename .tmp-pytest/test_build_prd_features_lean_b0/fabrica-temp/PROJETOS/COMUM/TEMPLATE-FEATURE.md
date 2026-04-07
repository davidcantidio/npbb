---
doc_id: "TEMPLATE-FEATURE"
version: "1.3"
status: "active"
owner: "PM"
last_updated: "2026-04-03"
project: "<PROJETO>"
feature_key: "FEATURE-<N>"
feature_slug: "<SLUG-EM-MAIUSCULAS-COM-HIFEN>"
prd_path: "../../PRD-<PROJETO>.md"
intake_path: "../../INTAKE-<PROJETO>.md"
# agent_id: opcional; metadata opaca quando a feature vier da trilha lean
depende_de: []
audit_gate: "not_ready"
---

# FEATURE-<N> - <Nome curto da feature>

## 0. Rastreabilidade

- **Projeto**: `<PROJETO>`
- **PRD**: [PRD-<PROJETO>.md](../../PRD-<PROJETO>.md)
- **Intake**: [INTAKE-<PROJETO>.md](../../INTAKE-<PROJETO>.md)
- **depende_de**: []

### Evidencia no PRD

> Este manifesto Markdown continua sendo o alvo canonico quando a feature
> existir. Propostas estruturadas upstream devem convergir para este shape.

- **Secao / ancora**: `<secao-do-prd>` - **Sintese**: `<parafrase-curta>`
- **Secao / ancora**: `<secao-do-prd>` - **Sintese**: `<parafrase-curta>`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: `<problema-objetivo>`
- **Resultado de negocio esperado**: `<1-a-3-linhas>`

## 2. Comportamento Esperado

- `<comportamento-1>`
- `<comportamento-2>`

## 3. Dependencias entre Features

- **depende_de**: []

## 4. Criterios de Aceite

- [ ] <criterio verificavel 1>
- [ ] <criterio verificavel 2>
- [ ] <criterio verificavel 3>

## 5. Riscos Especificos

- <risco 1>

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | <impacto-ou-nao_aplicavel> | <detalhamento-curto> |
| Backend | <impacto-ou-nao_aplicavel> | <detalhamento-curto> |
| Frontend | <impacto-ou-nao_aplicavel> | <detalhamento-curto> |
| Testes | <impacto-minimo-esperado> | <detalhamento-curto> |
| Observabilidade | <impacto-ou-nao_aplicavel> | <detalhamento-curto> |

> Na trilha lean, `layer_impacts` chega estruturado por camada no shape
> `{impact, detail}`; o manifesto final apenas espelha esse shape na tabela acima.

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-<N>.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-<N>-01-<SLUG>/README.md` |
| US-<N>.2 | <comportamento complementar> | 2 | US-<N>.1 | todo | `user-stories/US-<N>-02-<SLUG>/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`

---

## Checklist de prontidao do manifesto

- [ ] `feature_key`, `feature_slug` e pasta `FEATURE-<N>-<SLUG>/` estao coerentes
- [ ] PRD e intake estao referenciados com caminhos relativos corretos
- [ ] Evidencia no PRD esta preenchida com `secao / ancora` + `sintese`
- [ ] `depende_de` reflete a ordem real entre features
- [ ] Criterios de aceite e impactos por camada estao preenchidos
- [ ] Tabela de User Stories so e atualizada apos a etapa `Feature -> User Stories`

> Frase guia: Feature organiza, User Story fatia, Task executa, Teste valida.
