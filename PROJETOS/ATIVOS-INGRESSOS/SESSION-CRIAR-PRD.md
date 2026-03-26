---
doc_id: "SESSION-CRIAR-PRD.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-CRIAR-PRD - Criacao de PRD em Sessao de Chat

## Objetivo

Gerar o PRD do projeto a partir do intake aprovado, mantendo o
enquadramento capability-first do dominio de ativos e ingressos.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`

## Parametros Preenchidos

```text
PROJETO:      ATIVOS-INGRESSOS
INTAKE_PATH:  PROJETOS/ATIVOS-INGRESSOS/INTAKE-ATIVOS-INGRESSOS.md
OBSERVACOES:  manter o PRD no nivel de capacidade; nao listar features; tratar dashboard como superficie e validacao de QR como etapa posterior
```

## Regra Local Adicional

Use o intake aprovado como fonte de verdade e deixe a decomposicao em
features para a etapa posterior do pipeline.
