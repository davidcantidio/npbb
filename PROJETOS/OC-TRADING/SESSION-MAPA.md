---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-TRADING"
---

# SESSION-MAPA - OC-TRADING

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de OC-TRADING

- `PROJETOS/OC-TRADING/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/OC-TRADING/SESSION-CRIAR-PRD.md`
- `PROJETOS/OC-TRADING/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-TRADING/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/OC-TRADING/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/OC-TRADING/SESSION-AUDITAR-FASE.md`
- `PROJETOS/OC-TRADING/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/OC-TRADING/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- fase bootstrap: `F1-FUNDACAO` reconciliada e aprovada como scaffold base
- ponto atual da fila: planejamento documental da vertical Trading (`SESSION-PLANEJAR-PROJETO`)
- observacao: nao reutilize a issue bootstrap como se ela fosse o backlog principal da vertical

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- o projeto agora segue PRD real de Trading; wrappers de issue/revisao/auditoria nao devem congelar a fila no bootstrap F1
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
