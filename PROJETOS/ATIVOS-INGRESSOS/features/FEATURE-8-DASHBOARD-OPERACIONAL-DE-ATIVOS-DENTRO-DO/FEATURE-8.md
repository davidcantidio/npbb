---
doc_id: "FEATURE-8"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-03"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-8"
feature_slug: "DASHBOARD-OPERACIONAL-DE-ATIVOS-DENTRO-DO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de: []
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-8 - dashboard operacional de ativos dentro do modulo Dashboard

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: []

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: dashboard operacional de ativos dentro do modulo Dashboard
- **Resultado de negocio esperado**: entregar um recorte executavel do PRD sem depender de backlog monolitico

## 2. Comportamento Esperado

- habilitar dashboard operacional de ativos dentro do modulo dashboard
- produzir uma user story canônica para este comportamento

## 3. Dependencias entre Features

- **depende_de**: []

## 4. Criterios de Aceite

- [ ] a feature possui manifesto canônico
- [ ] existe pelo menos uma user story planejada para o comportamento
- [ ] a implementação pode ser rastreada no banco após sync

## 5. Riscos Especificos

- heurística inicial pode exigir refinamento humano no título ou no recorte

## 6. Estrategia de Implementacao

1. detalhar a user story principal
2. gerar tasks com TDD
3. executar, revisar e auditar a feature

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | read model | o sync deve refletir o artefato |
| Backend | scripts Fabrica | geração e materialização |
| Frontend | nao_aplicavel | fora do core |
| Testes | unitários/contrato | validar CLI e escrita determinística |
| Observabilidade | `sync_runs` | registrar a rodada do sync |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-8-01 | dashboard operacional de ativos dentro do modulo Dashboard | 3 | - | todo | `user-stories/US-8-01-DASHBOARD-OPERACIONAL-DE-ATIVOS-DENTRO-DO/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`
