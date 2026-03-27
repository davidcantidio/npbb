---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-HOST-OPS"
---

# SESSION-MAPA - OC-HOST-OPS

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de OC-HOST-OPS

- `PROJETOS/OC-HOST-OPS/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/OC-HOST-OPS/SESSION-CRIAR-PRD.md`
- `PROJETOS/OC-HOST-OPS/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-HOST-OPS/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/OC-HOST-OPS/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/OC-HOST-OPS/SESSION-AUDITAR-FASE.md`
- `PROJETOS/OC-HOST-OPS/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/OC-HOST-OPS/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- fase bootstrap: `F1-FUNDACAO` reconciliada e aprovada como scaffold base
- ponto atual da fila: planejamento documental do backlog real (`SESSION-PLANEJAR-PROJETO`)
- observacao: nao reutilize wrappers antigos de execucao do scaffold como se fossem o backlog principal do projeto

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- o projeto agora segue PRD real de host-side; wrappers de issue/revisao/auditoria nao devem congelar a fila no bootstrap F1
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
