---
doc_id: "FEATURE-2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-03"
project: "PIPELINE-SEPARATION"
feature_key: "FEATURE-2"
feature_slug: "PRESERVAR-SEPARACAO-ENTRE-PRD-E-BACKLOG"
prd_path: "../../PRD-PIPELINE-SEPARATION.md"
intake_path: "../../INTAKE-PIPELINE-SEPARATION.md"
depende_de: []
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-2 - preservar separacao entre PRD e backlog executavel

## 0. Rastreabilidade

- **Projeto**: `PIPELINE-SEPARATION`
- **PRD**: [PRD-PIPELINE-SEPARATION.md](../../PRD-PIPELINE-SEPARATION.md)
- **Intake**: [INTAKE-PIPELINE-SEPARATION.md](../../INTAKE-PIPELINE-SEPARATION.md)
- **depende_de**: []
- **Evidencia no PRD**: Escopo/Dentro: preservar separacao entre PRD e backlog executavel
- **Evidencia no PRD**: Rollout: estrategia de deploy: uso interno via CLI
- **Evidencia no PRD**: Riscos globais: risco de produto: recortes ficarem amplos demais

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: preservar separacao entre PRD e backlog executavel
- **Resultado de negocio esperado**: entregar um recorte executavel do PRD sem depender de backlog monolitico

## 2. Comportamento Esperado

- habilitar preservar separacao entre prd e backlog executavel
- produzir uma user story canonica para este comportamento

## 3. Dependencias entre Features

- **depende_de**: []

## 4. Criterios de Aceite

- [ ] a feature possui manifesto canonico
- [ ] existe pelo menos uma user story planejada para o comportamento
- [ ] a implementacao pode ser rastreada no banco apos sync

## 5. Riscos Especificos

- heuristica inicial pode exigir refinamento humano no titulo ou no recorte

## 6. Estrategia de Implementacao

1. detalhar a user story principal
2. gerar tasks com TDD
3. executar, revisar e auditar a feature

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | read model | o sync deve refletir o artefato |
| Backend | scripts Fabrica | geracao e materializacao |
| Frontend | nao_aplicavel | fora do core |
| Testes | unitarios/contrato | validar CLI e escrita deterministica |
| Observabilidade | `sync_runs` | registrar a rodada do sync |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-2-01 | preservar separacao entre PRD e backlog executavel | 3 | - | todo | `user-stories/US-2-01-PRESERVAR-SEPARACAO-ENTRE-PRD-E-BACKLOG/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`
