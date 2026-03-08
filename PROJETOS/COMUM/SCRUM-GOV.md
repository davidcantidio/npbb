---
doc_id: "SCRUM-GOV.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# SCRUM-GOV

## Cadeia de Trabalho

`Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias`

## Unidade Operacional Canonica

- `issue` e a menor unidade documental completa para execucao
- `task` e o menor item executavel dentro da issue
- `instruction` e a menor unidade atomica de execucao dentro da task
- `EPIC-*.md` funciona como manifesto do epico e indice das issues
- `SPRINT-*.md` existe apenas para selecao e consolidacao de status
- `auditorias/RELATORIO-AUDITORIA-*.md` e a unidade documental da auditoria de fase
- criterios de aceitacao, DoD, tasks e instructions por task vivem na issue
- projetos ativos devem seguir exclusivamente o padrao `issue-first`

## Definition of Done por Tipo

### Intake

- arquivo `INTAKE-<PROJETO>.md` existe
- `intake_kind` e `source_mode` estao preenchidos
- problema, publico, fluxo principal, restricoes e nao-objetivos estao claros
- riscos, dependencias, lacunas conhecidas e rastreabilidade foram declarados
- checklist de prontidao para PRD esta concluido ou documenta o bloqueio restante
- quando `intake_kind` for `problem`, `refactor` ou `audit-remediation`, o bloco especifico de problema/refatoracao esta preenchido

### Fase

- arquivo de fase preenchido com objetivo, gate, escopo, indice de epicos e estado do gate de auditoria
- todos os epicos da fase possuem documento proprio
- todos os epicos usam indice de issues em `issues/`
- status da fase deriva do estado dos epicos combinado ao gate de auditoria
- fase `done` possui auditoria `go` registrada e so entao pode ser movida para `feito/`

### Epico

- objetivo tecnico mensuravel definido
- resultado de negocio verificavel definido
- contexto arquitetural e dependencias documentados
- Definition of Done especifica evidencia consolidada
- arquivo referencia todas as issues do escopo por tabela navegavel
- status deriva do estado das issues filhas

### Issue

- documento proprio com frontmatter padronizado
- `task_instruction_mode` definido como `optional` ou `required` em novas issues
- user story explicita
- plano TDD definido em `Red`, `Green`, `Refactor`
- criterios de aceitacao no formato `Given/When/Then`
- Definition of Done explicita
- tasks decupadas e artefato minimo declarados
- quando `task_instruction_mode = required`, existe um bloco `Instructions por Task` completo e consistente com cada task listada
- arquivos reais impactados ou testados declarados

### Sprint

- respeita limites de capacidade de `SPRINT-LIMITS.md`
- nao substitui fase, epico ou issue como fonte de verdade
- referencia `issues/ISSUE-*.md` por ID e documento
- status da sprint deriva do estado das issues selecionadas

### Auditoria

- relatorio em `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md` existe
- escopo auditado, commit base e fontes de evidencia estao declarados
- veredito `go`, `hold` ou `cancelled` esta registrado com justificativa
- a auditoria avaliou bugs, regressoes provaveis, code smells, monolitos, docstrings relevantes e cobertura de testes
- `AUDIT-LOG.md` foi atualizado com a rodada
- follow-ups materiais estao convertidos em `issue-local` ou `new-intake` quando o veredito e `hold`
- somente auditoria com arvore limpa e commit SHA pode fechar fase

## Regras de Status

Status canonicos persistidos:

- `todo`
- `active`
- `done`
- `cancelled`

Regra derivada:

- `todo`: nenhum filho iniciado
- `active`: existe filho `active` ou `done`, mas nem todos estao `done`
- `done`: todos os filhos estao `done` e o DoD do pai foi fechado
- `cancelled`: cancelamento explicito com justificativa

`BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais de execucao e nao devem ser persistidos como status principal de fase, epico, issue ou sprint.

## Regras de Task Instructions

- `instruction` nao e documento independente; vive inline na issue
- `task_instruction_mode: required` e obrigatorio para:
  - migrations ou mudancas com persistencia/rollback sensivel
  - ordem de execucao critica
  - alteracao multi-camada ou multi-arquivo com dependencia forte
  - remediacao originada de auditoria `hold`
  - handoff planejado para outra IA ou sessao
- quando `task_instruction_mode: required`, toda task precisa de bloco proprio em `## Instructions por Task`
- issue marcada como `required` sem instructions completas nao e elegivel para execucao
- para compatibilidade de rollout, issue sem `task_instruction_mode` pode ser tratada como `optional` ate ser revisada

## Regras de Auditoria

Vereditos aceitos:

- `go`
- `hold`
- `cancelled`

Estados de gate da fase:

- `not_ready`: fase ainda possui desenvolvimento pendente
- `pending`: todos os epicos estao `done`, aguardando auditoria formal
- `hold`: ultima auditoria rejeitou o gate e abriu follow-ups
- `approved`: ultima auditoria aprovou o gate com veredito `go`

Regras:

- auditoria formal padrao acontece por fase
- auditorias por epico ou issue sao excecao guiada por risco, nao o fluxo padrao
- `hold` e `go` sao vereditos de auditoria, nao status canonicos de backlog
- auditoria com worktree sujo deve ser marcada como `provisional` e nao aprova gate
- achados devem ser classificados por categoria e severidade
- `hold` so bloqueia por achados materiais; smells menores e docstrings faltantes sem risco claro nao travam fase
- follow-up estrutural ou sistemico deve abrir novo `INTAKE-*` com rastreabilidade para a auditoria de origem

## Regras de Arquivamento de Fase

- cada projeto ativo em `PROJETOS/` deve manter uma pasta `feito/` na raiz
- cada projeto ativo deve manter `AUDIT-LOG.md` na raiz
- cada projeto ativo deve manter um intake principal `INTAKE-<PROJETO>.md` na raiz
- intakes adicionais de remediacao podem coexistir na raiz com sufixo proprio
- cada fase ativa deve manter uma pasta `auditorias/`
- quando uma fase atingir `done`, sua pasta inteira deve ser movida para `<projeto>/feito/F*-.../`
- a movimentacao so pode ocorrer apos validacao do gate com auditoria `go` e consolidacao da evidencia
- links internos e automacoes dependentes do caminho devem ser atualizados no mesmo change set
