---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-SMOKE-SKILLS"
---

# SESSION-MAPA - OC-SMOKE-SKILLS

> Mapa dos wrappers locais do projeto-canario.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de OC-SMOKE-SKILLS

- `PROJETOS/OC-SMOKE-SKILLS/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-CRIAR-PRD.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-AUDITAR-FASE.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/OC-SMOKE-SKILLS/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- fase atual: `F1-FUNDACAO`
- ponto atual da fila: execucao controlada da issue canario (`SESSION-IMPLEMENTAR-ISSUE`)
- observacao: este projeto valida o framework atual; nao trate `OC-SMOKE-SKILLS` como backlog de produto

## Regra Local Adicional

- os wrappers locais sao presets finos do canario, nao uma segunda fonte normativa
- execucao, revisao e auditoria devem continuar ancoradas na issue/bootstrap canario enquanto o guia de smoke usar essa prova controlada
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
