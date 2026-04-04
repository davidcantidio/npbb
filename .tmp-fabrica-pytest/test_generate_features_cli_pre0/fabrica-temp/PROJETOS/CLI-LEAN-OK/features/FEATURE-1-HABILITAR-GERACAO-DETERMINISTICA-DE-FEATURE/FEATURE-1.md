---
doc_id: "FEATURE-1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-03"
project: "CLI-LEAN-OK"
feature_key: "FEATURE-1"
feature_slug: "HABILITAR-GERACAO-DETERMINISTICA-DE-FEATURE"
prd_path: "../../PRD-CLI-LEAN-OK.md"
intake_path: "../../INTAKE-CLI-LEAN-OK.md"
depende_de: []
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-1 - habilitar geracao deterministica de feature

## 0. Rastreabilidade

- **Projeto**: `CLI-LEAN-OK`
- **PRD**: [PRD-CLI-LEAN-OK.md](../../PRD-CLI-LEAN-OK.md)
- **Intake**: [INTAKE-CLI-LEAN-OK.md](../../INTAKE-CLI-LEAN-OK.md)
- **depende_de**: []
- **Evidencia no PRD**: Escopo/Dentro: habilitar geracao deterministica de feature
- **Evidencia no PRD**: Rollout: estrategia de deploy: uso interno via CLI
- **Evidencia no PRD**: Riscos globais: risco de produto: recortes ficarem amplos demais

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: habilitar geracao deterministica de feature
- **Resultado de negocio esperado**: entregar um recorte executavel do PRD sem depender de backlog monolitico

## 2. Comportamento Esperado

- habilitar habilitar geracao deterministica de feature
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
| US-1-01 | habilitar geracao deterministica de feature | 3 | - | todo | `user-stories/US-1-01-HABILITAR-GERACAO-DETERMINISTICA-DE-FEATURE-FLUXO/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`
