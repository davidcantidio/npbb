---
doc_id: "SESSION-PLANEJAR-PROJETO.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-PLANEJAR-PROJETO - Planejamento de Projeto em Sessao de Chat

## Objetivo

Decompor o PRD aprovado do projeto em backlog estruturado `Feature ->
User Story -> Task`, sem reintroduzir scaffold bootstrap.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`

## Parametros Preenchidos

```text
PROJETO:       ATIVOS-INGRESSOS
PRD_PATH:      PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md
ESCOPO:        projeto completo
PROFUNDIDADE:  completo
TASK_MODE:     required
OBSERVACOES:   decompor em ordem: fundacao do dominio, recebimento e conciliacao de ticketeira, emissao e distribuicao, dashboard de ativos e validacao de QR em etapa posterior
```

## Regra Local Adicional

- use o PRD aprovado como fonte de verdade
- nao reaproveite backlog bootstrap herdado; a arvore `features/` deve nascer da decomposicao real deste PRD
- em caso de conflito, `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md` prevalece
