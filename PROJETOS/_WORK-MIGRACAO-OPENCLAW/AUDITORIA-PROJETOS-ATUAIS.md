---
doc_id: "AUDITORIA-PROJETOS-ATUAIS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
---

# AUDITORIA-PROJETOS-ATUAIS

## Baseline usado

- baseline oficial desta auditoria: `worktree atual`
- fonte compartilhada de drift corrigida antes do retrofit: `scripts/criar_projeto.py`
- regra desta fotografia: registrar o ponto atual do projeto no estado local real, e nao apenas em commits antigos

## Matriz Consolidada

| Ordem Global | Projeto | Faixa | Baseline | Drift encontrado | Fase / Epico / Issue atuais | Ponto atual | Proxima unidade elegivel |
|---|---|---|---|---|---|---|---|
| G0 | `scripts/criar_projeto.py` | governanca compartilhada | worktree atual | corrigidos `EPIC-EPIC-*`, `SESSION-MAPA` antigo, wrappers congelados em bootstrap e PRD placeholder enganoso | nao_aplicavel | manutencao de gerador | testes automatizados + retrofit concluido |
| G1 | `OC-SMOKE-SKILLS` | canario / framework | worktree atual | intake/PRD tratavam o projeto como scaffold generico, nao como canario do framework; wrappers estavam datados | `F1-FUNDACAO` / `EPIC-F1-01` / `ISSUE-F1-01-001` | execution | executar a issue canario `T1`, depois review e auditoria do proprio canario |
| G2 | `OC-MISSION-CONTROL` | backlog principal | worktree atual | F2 estava parcialmente fora de sincronia com o estado real do repo; `ISSUE-F2-03-001` ja estava satisfeita pelo worktree | `F2-OPENROUTER-E-AGENTES` / `EPIC-F2-02..03` / todas as issues F2 atuais sincronizadas | audit | auditar formalmente `F2-OPENROUTER-E-AGENTES` (`R01`) |
| G3 | `OC-HOST-OPS` | backlog principal | worktree atual | PRD era placeholder de scaffold; wrappers ainda congelavam o projeto na bootstrap F1 | `F1-FUNDACAO` bootstrap aprovado; backlog real a materializar a partir do PRD | planning | rodar `SESSION-PLANEJAR-PROJETO.md` para materializar fases/epicos/issues do host-side real |
| G4 | `QMD` | backlog principal | worktree atual | faltavam wrappers locais; `AUDIT-LOG.md` estava em modo template; arvore issue-first ainda nao foi materializada | PRD pronto; fase F1 ainda nao materializada no filesystem | planning | rodar `SESSION-PLANEJAR-PROJETO.md` para materializar a F1 de memoria + QMD |
| G5 | `OC-TRADING` | backlog principal | worktree atual | PRD era placeholder de scaffold; wrappers ainda congelavam o projeto na bootstrap F1 | `F1-FUNDACAO` bootstrap aprovado; backlog real a materializar a partir do PRD | planning | rodar `SESSION-PLANEJAR-PROJETO.md` para decompor a vertical Trading em fases/epicos/issues reais |

## Observacoes por Projeto

### OC-SMOKE-SKILLS

- este projeto nao e backlog de produto; ele valida o framework atual
- `GUIA-TESTE-SKILLS.md` e a referencia funcional primaria do canario
- a issue bootstrap permanece aberta de proposito como prova controlada de execucao

### OC-MISSION-CONTROL

- a reconciliacao de F2 usou o worktree atual como evidencia
- `ISSUE-F2-02-001` e `ISSUE-F2-03-001` foram sincronizadas com o estado atual da documentacao e tooling
- o proximo passo ficou naturalmente em auditoria de fase

### OC-HOST-OPS

- o intake ja era real; o PRD placeholder foi substituido
- a F1 agora vale apenas como bootstrap historico aprovado
- o backlog real do projeto comeca no planning do PRD atual

### QMD

- intake e PRD atuais seguem como base real do projeto
- wrappers locais foram criados para colocar QMD no mapa operacional
- a arvore issue-first ainda precisa ser materializada no filesystem a partir do PRD

### OC-TRADING

- o intake ja era real; o PRD placeholder foi substituido
- a F1 agora vale apenas como bootstrap historico aprovado
- o backlog real do projeto comeca no planning do PRD atual, com dependencia explicita de `OC-MISSION-CONTROL`
