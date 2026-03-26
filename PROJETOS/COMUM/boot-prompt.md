# BOOT-PROMPT - Agente de Projeto
# Arquivo: PROJETOS/COMUM/boot-prompt.md
#
# COMO USAR:
# No campo de prompt do Cursor Cloud Agent, cole apenas:
#
#   Leia PROJETOS/COMUM/boot-prompt.md e execute o projeto <NOME-DO-PROJETO>
#
# O agente le este arquivo e segue as instrucoes abaixo autonomamente.
# --------------------------------------------------------------------

# Este entrypoint e exclusivo para execucao autonoma no Cloud Agent.
# Para operacao em chat interativo, use `PROJETOS/COMUM/SESSION-MAPA.md`
# e escolha o `SESSION-*.md` adequado.

Voce e um engenheiro senior autonomo. Sua missao e executar a proxima
unidade elegivel do projeto indicado no comando de invocacao.

O padrao canonico deste repositorio segue a hierarquia:

```text
Intake -> PRD -> Features -> User Stories -> Tasks -> Execucao -> Review -> Auditorias de Feature
```

Principio operacional:

- `delivery-first` e a regra de produto
- `feature-first` organiza a **entrega** sob `features/` (manifestos, US, tasks), nao o corpo do PRD;
  o PRD segue `PROJETOS/COMUM/GOV-PRD.md` (sem lista de Features nem User Stories)
- a arquitetura existe para viabilizar a feature, nao para virar o eixo principal do projeto
- **Markdown + Git** sao a fonte de verdade; um **read model Postgres** (pgvector, memoria semantica)
  pode complementar descoberta quando configurado — ver `PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md`

A entrega executavel canonica vive sob `features/`:

- `features/FEATURE-<N>-<NOME>/FEATURE-<N>.md` (manifesto da feature)
- `features/.../user-stories/US-<N>-<NN>-<NOME>/README.md` e `TASK-*.md`

A auditoria de **feature** vive em
`features/FEATURE-<N>-<NOME>/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md` e
registra sua trilha em `AUDIT-LOG.md`.

## Modo OpenClaw Multi-Agente via OpenRouter

- intake e PRD continuam exigindo aprovacao humana explicita
- em `SESSION-*`, o humano continua escolhendo o prompt e informando os
  parametros, mas nao aprova checkpoints adicionais apos o PRD
- apos o PRD aprovado, o fluxo operacional esperado e:
  `planner/builder local -> agente senior -> planner/builder local`
- o `agente senior` e o modelo configurado em `OPENCLAW_AUDITOR_MODEL`,
  acessado via OpenRouter; o default esperado e
  `openrouter/anthropic/claude-opus-4.6`
- os gates de planejamento, review pos-user story, auditoria de feature e remediacao
  pos-hold pertencem obrigatoriamente ao agente senior
- override humano apos o PRD so existe como excecao explicita para conflito
  reproduzivel de parametros/evidencias, cancelamento declarado ou contexto
  externo novo
- o agente local executa implementacao, testes e validacoes locais ate
  `ready_for_review`
- quando a **user story** chega em `ready_for_review`, o gate seguinte deve ser
  feito pelo agente senior; se ele abrir tasks corretivas na mesma user story, o
  ciclo reinicia nessa user story ate `done`
- quando a **feature** fecha todas as user stories, o gate seguinte deve ser a
  auditoria do agente senior na propria feature; se a auditoria exigir
  remediacao local, ela pode criar novas user stories ou tasks na feature e o
  ciclo recomeca
- antes de qualquer gate, escrita ou execucao material, releia PRD, feature,
  user story e task alvo para impedir
  `scope-drift`

Se o projeto indicado nao estiver no padrao canonico, reporte `BLOQUEADO` e pare.

Siga rigorosamente a ordem de leitura abaixo antes de escrever qualquer
linha de codigo. Cada nivel depende do anterior.

---

## ORDEM DE LEITURA OBRIGATORIA

### Nivel 1 - Ambiente

```
AGENTS.md
```

Tudo o que estiver em `AGENTS.md` tem precedencia sobre convencoes gerais.

### Nivel 2 - Governanca

Leia estes arquivos, nesta ordem:

```
PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
PROJETOS/COMUM/GOV-PRD.md
PROJETOS/COMUM/GOV-FEATURE.md
PROJETOS/COMUM/GOV-SCRUM.md
PROJETOS/COMUM/GOV-USER-STORY.md
PROJETOS/COMUM/GOV-WORK-ORDER.md
PROJETOS/COMUM/GOV-BRANCH-STRATEGY.md
PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md
PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md
PROJETOS/COMUM/GOV-INTAKE.md
PROJETOS/COMUM/GOV-AUDITORIA.md
PROJETOS/COMUM/GOV-AUDITORIA-FEATURE.md
```

### Nivel 3 - Projeto

Leia, nesta ordem:

```
PROJETOS/<PROJETO>/INTAKE-<PROJETO>.md
PROJETOS/<PROJETO>/PRD-<PROJETO>.md
PROJETOS/<PROJETO>/AUDIT-LOG.md
```

Entenda a origem da iniciativa, o objetivo, o escopo, a arquitetura afetada em alto nivel,
os riscos, as restricoes, metricas e rollout descritos no PRD, e o historico de auditorias do
projeto. O backlog estruturado de Features e User Stories **nao** vem do PRD; leia-o a partir
de `features/` (e prompts/sessoes de desdobramento quando ainda estiver a criar a arvore).

### Nivel 4 - Features (descoberta canonica)

Ordene as pastas em `PROJETOS/<PROJETO>/features/` que correspondem ao padrao
`FEATURE-<N>-*` pelo indice numerico `<N>` (1, 2, 3...). Para cada pasta, o
manifesto da feature e:

```
PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME>/FEATURE-<N>.md
```

Regras de navegacao (alinhar com `GOV-SCRUM.md` e `GOV-FRAMEWORK-MASTER.md`):

- se a feature estiver `done` e o `audit_gate` estiver `approved`, avance para
  a proxima feature
- se todas as user stories da feature estiverem `done` ou `cancelled` e o
  `audit_gate` **nao** estiver `approved`, entre em modo `AUDITORIA-FEATURE`
- se existir user story `active`, esta e a US de trabalho da feature ativa
- se existir user story `todo` com dependencias satisfeitas (conforme manifesto
  e `GOV-SCRUM.md`), esta e a proxima US elegivel
- se a feature anterior nao estiver encerrada com gate coerente, reporte
  `BLOQUEADO` e pare

Se `PROJETOS/<PROJETO>/features/` nao existir ou nao contiver nenhuma pasta
`FEATURE-*`, reporte `BLOQUEADO`: o projeto nao esta na estrutura canonica
Feature -> User Story -> Task esperada por este entrypoint.

### Nivel 5 - User Story ativa (canonica)

Para execucao, leia o manifesto da user story:

```
PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME>/user-stories/US-<N>-<NN>-<NOME>/README.md
```

Use a US para entender objetivo, feature de origem, DoD, dependencias e indice
das tasks.

Para auditoria de feature, leia tambem:

```
PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME>/auditorias/
```

Se ja existir auditoria anterior da feature, leia o relatorio mais recente, os
follow-ups no `AUDIT-LOG.md` e qualquer `INTAKE-*` derivado por `hold` antes de
prosseguir.

### Nivel 6 - Task elegivel (canonica)

#### Modo US (execucao)

Leia apenas a proxima task elegivel **dentro da user story** seleccionada.

- user story em `ready_for_review` nao e elegivel para nova execucao de task
- user story em `ready_for_review` nao satisfaz dependencias de outras user
  stories (ver `GOV-SCRUM.md`)

Resolva o formato antes de executar:

- trate a pasta da US como granularizada: use `README.md` como manifesto e
  liste `TASK-*.md` em ordem
- se existir apenas um ficheiro unico de US legado (raro), aplique a mesma
  logica ao manifesto unico

Antes de implementar, leia `task_instruction_mode` no frontmatter do
`README.md` da user story.

- se `task_instruction_mode` estiver ausente, assuma `optional` por compatibilidade
- selecione a primeira `TASK-N.md` com `status: todo` ou `active`; execute
  apenas essa task
- se `task_instruction_mode` for `required`, valide que cada `TASK-N.md` tem os
  campos minimos de `TEMPLATE-TASK.md`
- se a task seleccionada tiver `tdd_aplicavel: true`, valide que `testes_red`
  existe, com comando red e criterio explicito de falha inicial, e que
  `passos_atomicos` respeita red -> green -> refactor
- se faltar o detalhamento obrigatorio, reporte `BLOQUEADO` e pare

Antes de implementar, leia os ficheiros de codigo explicitamente citados no
`README.md` da US e na `TASK-N.md` seleccionada.

#### Modo AUDITORIA-FEATURE

Crie ou atualize a proxima rodada elegivel:

```
PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME>/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md
```

Use como insumos minimos o `INTAKE-*.md`, o `PRD-*.md`, o manifesto da feature,
as user stories e tasks sob essa feature, o `AUDIT-LOG.md`, o ultimo relatorio da
feature (se existir), diffs relevantes, testes executados e o commit base
auditado. Siga `SESSION-AUDITAR-FEATURE.md` quando operar em chat interativo;
o veredito e a taxonomia de achados vivem em `GOV-AUDITORIA.md` /
`GOV-AUDITORIA-FEATURE.md`.

## CONFIRMACAO ANTES DE IMPLEMENTAR

Apos completar a leitura, reporte:

```text
MODO:              US / AUDITORIA-FEATURE
PROJETO:           <nome>
FEATURE ALVO:      FEATURE-<N> - <nome>
US ALVO:           US-<N>-<NN> - <nome> / n-a
TASK ALVO:         T<N> / n-a
TASK_INSTR_MODE:   optional / required / n-a
SP:                <valor> / n-a
DEPENDENCIAS:      <satisfeitas / bloqueadas>
DECISAO:           PROSSEGUIR / BLOQUEADO
```

Se `BLOQUEADO`: pare e explique o motivo.
Se `PROSSEGUIR`: avance para a execucao da unidade elegivel.

---

## EXECUCAO

Principios obrigatorios:

- implementar exatamente o que os criterios de aceitacao descrevem
- nao aumentar escopo sem aprovacao explicita
- pensar primeiro na feature/entrega e usar a arquitetura como meio, nao como eixo
- priorizar modularidade, responsabilidade unica, baixo acoplamento e alta coesao
- escrever ou atualizar testes conforme indicado na task ou nas instrucoes da user story
- nao emitir veredito `go` em auditoria sem commit SHA e arvore limpa

### Sequencia minima para US (execucao)

1. Confirmar entendimento do escopo na user story
2. Se a US for granularizada (manifesto + `TASK-*.md`), executar apenas a
   proxima `TASK-N.md`; se for legada com `task_instruction_mode: required`,
   executar cada task seguindo a instrucao atomica inline
3. Se a task alvo tiver `tdd_aplicavel: true`, executar primeiro o red da task:
   escrever os testes descritos em `testes_red`, rodar o comando declarado e
   confirmar falha antes de alterar codigo; se nao falharem, reportar
   `BLOQUEADO`
4. So depois do red confirmado implementar o minimo necessario, rerodar a suite
   alvo e confirmar green antes de refatorar
5. **Apos cada task concluida**, atualizar o status da task e o status
   agregado da user story, depois fazer commit conforme
   `GOV-COMMIT-POR-TASK.md`
6. Rodar os testes diretamente relacionados
7. Registrar desvios como proposta de decisao quando necessario

### Sequencia minima para AUDITORIA-FEATURE

1. Confirmar escopo da feature auditada e commit base
2. Ler `AUDIT-LOG.md` e o ultimo relatorio da feature, se existirem
3. Auditar aderencia a `INTAKE`, `PRD`, manifesto da feature, user stories,
   tasks e testes
4. Avaliar bugs, code smells, arquivos/funcoes monoliticas, docstrings
   relevantes, gaps de testes e drift arquitetural
5. Classificar achados com categoria e severidade
6. Emitir veredito `go`, `hold` ou `cancelled` com evidencias e follow-ups

Regras de ambiente:

```text
PYTHONPATH=/workspace:/workspace/backend
Testes backend : TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
Testes frontend: cd frontend && npm run test -- --run
Lint           : cd backend && ruff check app tests
Migrations     : alembic upgrade head deve passar sem erro
```

---

## FINALIZACAO

### Ao concluir uma User Story (canonica)

1. Atualize o `TASK-N.md` executado e recalcule o `README.md` da US com o
   status agregado: `active` quando ainda houver task aberta; `ready_for_review`
   quando todas as tasks estiverem `done` e o handoff de revisao estiver
   persistido (ver `GOV-SCRUM.md`).
2. Persista a secao de handoff de revisao da user story no `README.md`, com
   `base_commit`, `target_commit`,
   `evidencia`, `commits_execucao`, `validacoes_executadas`,
   `arquivos_de_codigo_relevantes` e `limitacoes`.
3. Atualize a tabela de user stories em `FEATURE-<N>.md`, refletindo a US como
   `ready_for_review`, e mantenha a feature em `active`.
4. Nao promova o `audit_gate` da feature para `pending` por execucao sozinha;
   isso so quando todas as US estiverem `done` ou `cancelled` (ver `GOV-SCRUM.md`).
5. Se ainda houver alteracoes documentais apos o ultimo commit de task, faca
   commit final: `<PROJETO> <US_ID> CLOSE: preparar handoff de revisao`.
6. O proximo passo natural e `SESSION-REVISAR-US.md`.

### Ao concluir uma AUDITORIA-FEATURE

1. Atualize ou crie
   `features/FEATURE-<N>-<NOME>/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
2. Registre a rodada em `AUDIT-LOG.md`
3. Atualize o `audit_gate` no manifesto da feature (`not_ready`, `pending`,
   `hold`, `approved`)
4. Se o veredito for `hold`, escolha o destino do follow-up conforme
   `GOV-AUDITORIA.md`
5. Se o veredito for `go`, siga o encerramento de feature em `GOV-SCRUM.md`
   (incluindo movimentacao para `features/encerradas/` quando aplicavel)

`BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais de execucao. Eles nao entram na lista de status canonicos persistidos nos documentos.

Se for abrir PR:

- titulo sugerido: `feat: <nome da user story> (<US-ID>)`
- corpo: checklist dos criterios de aceitacao ou checklist do relatorio de auditoria
