---
doc_id: "FEATURE-2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-03"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-2"
feature_slug: "DOIS-MODOS-DE-FORNECIMENTO-INTERNO-EMITIDO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de: []
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-2 - dois modos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: []

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: dois modos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`
- **Resultado de negocio esperado**: entregar um recorte executavel do PRD sem depender de backlog monolitico

## 2. Comportamento Esperado

- habilitar dois modos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`
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
| US-2-01 | dois modos de fornecimento: `interno_emitido_com_qr` e `externo_recebido` | 3 | - | todo | `user-stories/US-2-01-DOIS-MODOS-DE-FORNECIMENTO-INTERNO-EMITIDO/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`
