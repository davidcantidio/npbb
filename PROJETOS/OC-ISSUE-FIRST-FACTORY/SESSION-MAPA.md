---
doc_id: "SESSION-MAPA.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OC-ISSUE-FIRST-FACTORY"
---

# SESSION-MAPA - OC-ISSUE-FIRST-FACTORY

> Mapa dos wrappers locais do projeto.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.

## Mapa Canonico

Leia e use como fonte de verdade:

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Wrappers Locais de OC-ISSUE-FIRST-FACTORY

- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-CRIAR-PRD.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-REVISAR-ISSUE.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-AUDITAR-FASE.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-REMEDIAR-HOLD.md`
- `PROJETOS/OC-ISSUE-FIRST-FACTORY/SESSION-REFATORAR-MONOLITO.md`

## Ponto Atual

- estado na arvore: `INTAKE-OC-ISSUE-FIRST-FACTORY.md` e `PRD-OC-ISSUE-FIRST-FACTORY.md`
  ja existem como **drafts versionados**; Markdown e Git sao a fonte ate fechamento
  dos gates
- proxima unidade pratica: **revisar e aprovar** o intake atual via
  `SESSION-CRIAR-INTAKE` (ajustar o draft conforme necessario; nao tratar como
  criacao em branco salvo decisao explicita); em seguida **revisar e aprovar** o
  PRD via `SESSION-CRIAR-PRD` alinhado ao intake aprovado
- observacao: o planning deste projeto so comeca apos o PRD aprovado e nao deve
  absorver a implementacao das tasks dos projetos criados pela capability

## Regra Local Adicional

- os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
- wrappers de issue/revisao/auditoria nao devem congelar a fila em F1/bootstrap; resolva a unidade atual nos artefatos do projeto
- os wrappers locais apontam para os caminhos repo-relative do projeto
- em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
