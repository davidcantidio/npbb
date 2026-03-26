---
doc_id: "SESSION-MAPA.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
---

# SESSION-MAPA - ATIVOS-INGRESSOS

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de ATIVOS-INGRESSOS

- `PROJETOS/ATIVOS-INGRESSOS/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-CRIAR-PRD.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-REVISAR-US.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/ATIVOS-INGRESSOS/SESSION-REFATORAR-MONOLITO.md`

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- a decomposicao do projeto em `features/` so deve ocorrer apos aprovacao do PRD
- wrappers de user story, revisao e auditoria nao devem inventar backlog; use a fila documental real do projeto quando ela existir
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
