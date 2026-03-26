---
doc_id: "TEMPLATE-FEATURE"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "<PROJETO>"
feature_key: "FEATURE-<N>"
feature_slug: "<SLUG-EM-MAIUSCULAS-COM-HIFEN>"
prd_path: "../../PRD-<PROJETO>.md"
intake_path: "../../INTAKE-<PROJETO>.md"
depende_de: []
audit_gate: "not_ready"
---

# FEATURE-<N> - <Nome curto da feature>

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-<N>-<SLUG>/FEATURE-<N>.md`. O PRD descreve problema, objetivo,
> escopo, restricoes e rollout global **sem** listar features nem user stories;
> **este documento** consolida a feature entregavel, dependencias entre features,
> criterios de aceite e impacto por camada. User Stories e Tasks ficam em
> `user-stories/` apos as etapas de decomposicao do pipeline.

## 0. Rastreabilidade

- **Projeto**: `<PROJETO>`
- **PRD**: [PRD-<PROJETO>.md](../../PRD-<PROJETO>.md) *(alinhar ao `prd_path` do frontmatter)*
- **Intake** (se aplicavel): [INTAKE-<PROJETO>.md](../../INTAKE-<PROJETO>.md) *(alinhar ao `intake_path`)*
- **depende_de** (outras features): ver frontmatter `depende_de` e secao 3

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**:
- **Resultado de negocio esperado** (1 a 3 linhas):

## 2. Comportamento Esperado

- O que o usuario ou operador consegue fazer quando a feature estiver pronta:
-

## 3. Dependencias entre Features

> Liste apenas outras **features** do mesmo projeto. Use `feature_key` estavel
> (`FEATURE-1`, `FEATURE-2`, ...) ou caminho relativo ao manifesto da feature.

- **depende_de**: [] *(espelho do frontmatter; manter alinhado)*

## 4. Criterios de Aceite

- [ ] <criterio verificavel 1>
- [ ] <criterio verificavel 2>
- [ ] <criterio verificavel 3>

## 5. Riscos Especificos

-

## 6. Estrategia de Implementacao

1. **Modelagem e migration** (se aplicavel):
2. **API / backend**:
3. **UI / superficie**:
4. **Testes e evidencias**:

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | <tabelas / indices> | <colunas, constraints, migracoes> |
| Backend | <endpoints / jobs> | <contratos, erros, idempotencia> |
| Frontend | <telas / fluxos> | <estados, acessibilidade> |
| Testes | <suites> | <escopo minimo> |
| Observabilidade | <logs / metricas> | <alerts se aplicavel> |

## 8. Estado Operacional

- **status**: `todo` | `active` | `blocked` | `done` *(conforme `GOV-SCRUM.md`)*
- **audit_gate**: `not_ready` | `ready` | *(outros valores conforme `GOV-AUDITORIA-FEATURE.md`)*

## 9. User Stories (rastreabilidade)

> Preencha apos decompor **Feature -> User Stories**. Cada linha deve apontar para
> o `README.md` canonico da US. Limites de tamanho e elegibilidade: `GOV-USER-STORY.md`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-<N>.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-<N>-01-<SLUG>/README.md` |
| US-<N>.2 | <comportamento complementar> | 2 | US-<N>.1 | todo | `user-stories/US-<N>-02-<SLUG>/README.md` |

## 10. Referencias e Anexos

- <diagrama, ADR, spec externa, link para rollout no PRD se relevante>

---

## Checklist de prontidao do manifesto

- [ ] `feature_key` e pasta `FEATURE-<N>-<SLUG>/` alinhados com `GOV-FRAMEWORK-MASTER.md`
- [ ] PRD e intake referenciados com caminhos relativos corretos
- [ ] `depende_de` reflete ordem real entre features
- [ ] Criterios de aceite verificaveis e impacts por camada preenchidos
- [ ] Tabela de User Stories atualizada quando US forem criadas ou renomeadas

> **Frase guia** (alinhada ao framework): Feature organiza, User Story fatia, Task executa, Teste valida.
