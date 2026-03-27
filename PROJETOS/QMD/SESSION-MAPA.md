---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "QMD"
---

# SESSION-MAPA - QMD

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de QMD

- `PROJETOS/QMD/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/QMD/SESSION-CRIAR-PRD.md`
- `PROJETOS/QMD/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/QMD/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/QMD/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/QMD/SESSION-AUDITAR-FASE.md`
- `PROJETOS/QMD/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/QMD/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- ponto atual da fila: planejamento documental da F1 (`SESSION-PLANEJAR-PROJETO`)
- observacao: o PRD ja existe, mas a arvore issue-first ainda precisa ser materializada no filesystem
- evidencias atuais do repo: `README.md`, `openclaw-workspace/README.md` e `bin/validate-host.sh`

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- canonicos em `PROJETOS/` prevalecem sobre memoria derivada; conflitos sempre sobem ao PM
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
