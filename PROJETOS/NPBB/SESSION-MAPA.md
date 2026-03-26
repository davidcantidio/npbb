---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "NPBB"
---

# SESSION-MAPA - NPBB

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de NPBB

- `PROJETOS/NPBB/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/NPBB/SESSION-CRIAR-PRD.md`
- `PROJETOS/NPBB/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/NPBB/SESSION-IMPLEMENTAR-US.md`
- `PROJETOS/NPBB/SESSION-REVISAR-US.md`
- `PROJETOS/NPBB/SESSION-AUDITAR-FEATURE.md`
- `PROJETOS/NPBB/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/NPBB/SESSION-REFATORAR-MONOLITO.md`

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- wrappers de user story/revisao/auditoria nao devem congelar a fila na bootstrap; resolva a unidade atual nos artefatos do projeto
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
