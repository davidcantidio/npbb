---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-20"
project: "OC-MISSION-CONTROL"
---

# SESSION-MAPA - OC-MISSION-CONTROL

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de OC-MISSION-CONTROL

- `PROJETOS/OC-MISSION-CONTROL/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-CRIAR-PRD.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-AUDITAR-FASE.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/OC-MISSION-CONTROL/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- fase atual: `F2-OPENROUTER-E-AGENTES`
- ponto atual da fila: auditoria formal da fase (`SESSION-AUDITAR-FASE`)
- observacao: o backlog F2 foi reconciliado com o worktree atual; nao reutilize wrappers antigos de F1/bootstrap

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- wrappers de issue/revisao/auditoria devem refletir a fila atual do Mission Control, nao o bootstrap inicial da F1
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
