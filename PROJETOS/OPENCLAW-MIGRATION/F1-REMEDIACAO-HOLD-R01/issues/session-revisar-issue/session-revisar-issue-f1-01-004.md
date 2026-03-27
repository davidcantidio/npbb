---
doc_id: "session-revisar-issue-f1-01-004"
version: "1.6"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
issue_target: "ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA"
derived_from: "PROJETOS/OPENCLAW-MIGRATION/SESSION-REVISAR-ISSUE.md"
---

# SESSION-REVISAR-ISSUE — Revisao Pos-Issue (instancia ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA)

**Alvo:** GOV-FRAMEWORK-MASTER limpeza · **Fase:** F1-REMEDIACAO-HOLD-R01

## Parametros obrigatorios

```
PROJETO:      OPENCLAW-MIGRATION
FASE:         F1-REMEDIACAO-HOLD-R01
ISSUE_ID:     ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA
ISSUE_PATH:   PROJETOS/OPENCLAW-MIGRATION/F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/README.md
BASE_COMMIT:  4014b818e44851fea1b5a604865797b105009171
TARGET_COMMIT: 2f2c033aefa4dc067f23e0df6eceec37e9e14e34
EVIDENCIA:    git show 2f2c033aefa4dc067f23e0df6eceec37e9e14e34; git diff 4014b818e44851fea1b5a604865797b105009171..2f2c033aefa4dc067f23e0df6eceec37e9e14e34 -- PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md AGENTS.md (handoff YAML completo em fef4b2a678211796489199de2f4ce81e8da3e785)
OBSERVACOES:  Revisao round 1 concluida: veredito aprovada; issue promovida a done; EPIC-F1-01 e gate da fase actualizados em commit de cascata.
```

Validacoes obrigatorias do preenchimento:

- `FASE` deve corresponder exatamente ao nome da pasta da fase
- `ISSUE_ID` deve manter o identificador canonico completo com prefixo `ISSUE-`
- `EVIDENCIA` nao pode ser apenas `diff`; precisa apontar o comando, range, PR, log ou artefato exato
- se a revisao mirar um commit unico, preferir `TARGET_COMMIT=<sha>` com `EVIDENCIA=git show <sha>` ou `git diff <sha>^..<sha>`
- se `BASE_COMMIT`, `TARGET_COMMIT` ou `EVIDENCIA` vierem como `auto` ou `nao_informado`, resolva primeiro a secao `## Handoff para Revisao Pos-Issue` do manifesto da issue
- se `BASE_COMMIT` e `TARGET_COMMIT` forem iguais e a evidencia pedida for diff, trate como ambiguidade; use `git show <sha>` ou peca ajuste antes de seguir
- se os parametros explicitamente informados conflitarem com o handoff persistido, apresente `ALERTA - PARAMETROS DIVERGENTES` antes de prosseguir

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa no papel de
agente senior revisor.

Siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia:

- a issue informada (se for pasta, leia `README.md` e os `TASK-*.md` para revisao)
- o handoff de revisao persistido no manifesto da issue, quando existir
- o epico e a fase referenciados pela issue
- `decision_refs`, quando existirem
- apenas os arquivos de codigo citados pela issue e pela evidencia recebida
- `PROJETOS/COMUM/PROMPT-REVISAR-ISSUE.md`

Nao execute descoberta autonoma de fase ou issue.

Antes do Passo 0, valide os parametros recebidos. Se `FASE`, `ISSUE_ID`,
`ISSUE_PATH`, `BASE_COMMIT`, `TARGET_COMMIT` ou `EVIDENCIA` estiverem
malformados, ambiguos ou nao reproduziveis, responda `BLOQUEADO` em vez de
inferir o alvo da revisao.

Se qualquer parametro vier como `auto` ou `nao_informado`, resolva-o a partir
do handoff da issue. Se o handoff estiver ausente, incompleto ou inconsistente,
responda `BLOQUEADO`.

Se houver conflito entre parametros manuais e o handoff persistido, apresente:

```text
ALERTA - PARAMETROS DIVERGENTES
─────────────────────────────────────────
Handoff canonico:
  BASE_COMMIT: <...>
  TARGET_COMMIT: <...>
  EVIDENCIA: <...>
Parametros recebidos:
  BASE_COMMIT: <...>
  TARGET_COMMIT: <...>
  EVIDENCIA: <...>
─────────────────────────────────────────
```

Regra de resolucao: use o handoff canonico como fonte de verdade por padrao.
So mantenha override manual quando ele for mais especifico e reproduzivel que o
handoff; se nao for possivel decidir com seguranca, responda `BLOQUEADO`.

## Pré-condição: Sync do Índice SQLite

Antes do Passo 0, sincronize o índice SQLite derivado de `PROJETOS/`:

1. rode `./bin/sync-openclaw-projects-db.sh`
2. consulte no DB o estado atual da issue: `status`, `task_instruction_mode`,
   tasks abertas, épico, fase e sprint associados
3. compare o resultado com o Markdown canônico; o **Markdown prevalece**
4. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do bloco
   `REVISAO POS-ISSUE`
5. após qualquer gravação em `PROJETOS/` que altere issue, task, épico, fase,
   sprint ou handoff de review, execute novo sync

## Contrato Operacional Pos-PRD

- esta sessao deve rodar no `agente senior`, isto e, no modelo configurado em
  `OPENCLAW_AUDITOR_MODEL`, acessado via OpenRouter; o default esperado e
  `openrouter/anthropic/claude-opus-4.6`
- esta sessao nao introduz confirmacao humana adicional apos o PRD; os
  checkpoints abaixo pertencem ao proprio gate do agente senior
- o resultado operacional do gate deve ser `APROVADO`, `AJUSTAR` ou
  `REPROVADO`
- override humano apos o PRD so e valido quando houver conflito reproduzivel
  entre handoff e evidencia manual, cancelamento declarado ou contexto
  externo novo
- divergencia **SQLite vs Markdown** e telemetria operacional em
  `DRIFT_INDICE`; isso nao substitui a leitura canonica do manifesto da issue
  nem a validacao de alinhamento com o PRD
- inferir o `ROUND` atual a partir do handoff persistido; se o handoff nao
  trouxer round explicito, assuma `ROUND: 1` como primeira revisao da issue
- toda revisao deve explicitar alinhamento com o PRD, a feature de origem e os
  criterios de aceite da issue antes do veredito final
- se a correcao ainda pertencer ao escopo original, o agente senior deve
  preferir adicionar ou ajustar `TASK-N.md` dentro da propria issue em vez de
  abrir novo follow-up local
- quando devolver a mesma issue para `active`, a saida deve anunciar
  explicitamente `TASK_ID: auto` e `ROUND: <N+1>` para o proximo loop local

### Passo 0 - Confirmacao de escopo e evidencia

Registre:

```text
REVISAO POS-ISSUE
─────────────────────────────────────────
Issue:
Status atual:
Objetivo:
task_instruction_mode:
ROUND atual da issue:
Feature/criterios do PRD auditados:
BASE_COMMIT:
TARGET_COMMIT:
Evidencias disponiveis:
Limitacoes da revisao:
Risco de expandir escopo indevidamente:
```

Se nao houver evidencia minima para sustentar a revisao, responda `BLOQUEADO`.

Se a issue original estiver `todo` ou `active` e a evidencia nao provar todos
os criterios de aceitacao e itens de DoD, apresente antes de prosseguir:

```text
ALERTA — REVISAO PREMATURA
─────────────────────────────────────────
Issue original ainda aberta: <todo | active>
Escopo coberto pela evidencia: <commit parcial / worktree parcial / outro>
Lacunas para considerar a issue done:
- <criterio/DoD ainda nao evidenciado>
Risco: abrir issue-local agora pode duplicar o escopo da issue original
```

Quando esse alerta aparecer, trate o caso por padrao como implementacao
parcial: nao abra `issue-local` para escopo ainda pertencente a issue original
e use `correcao_requerida` com `status_resultante_issue: active`, salvo
evidencia suficiente em contrario.

### Passo 1 - Achados preliminares

Registre:

```text
ACHADOS PRELIMINARES
─────────────────────────────────────────
Estado da revisao: <completa | parcial>
Aderencia ao escopo:
Alinhamento com PRD/feature:
Cobertura de testes observada:
Lacunas contra criterios/DoD:

Achados:
| # | Tipo | Severidade | Evidencia | Destino sugerido |
|---|---|---|---|---|
| 1 | bug / test-gap / scope-drift / architecture-drift | high/medium/low | ... | issue-local / new-intake |

Destino sugerido consolidado: <nenhum | issue-local | new-intake>
```

Nao gere arquivo neste passo.

### Passo 2 - Veredito proposto

Registre:

```text
VEREDITO PROPOSTO
─────────────────────────────────────────
veredito: <aprovada | correcao_requerida | cancelled>
status_resultante_issue: <done | active | cancelled>
destino_proposto: <nenhum | issue-local | new-intake>
reabrir issue original: <nao | sim, apos atualizar a mesma issue>
ROUND de retorno: <n-a | N+1>
saida persistida: <sincronizar issue revisada | issue original atualizada + sincronizar issue revisada | nova ISSUE-*/ com README.md + TASK-*.md | nova ISSUE-*.md | nenhum artefato; abrir intake fora desta sessao>
```

Regras deste passo:

- se o veredito for `aprovada`, use `status_resultante_issue: done` e prossiga
  para o Passo 4
- se o veredito for `cancelled`, use `status_resultante_issue: cancelled` e
  prossiga para o Passo 4
- se a revisao estiver marcada como `parcial` e os achados representarem apenas
  escopo ainda nao entregue da issue original, use `correcao_requerida` com
  `status_resultante_issue: active`, `destino_proposto: nenhum` e
  `saida persistida: issue original atualizada + sincronizar issue revisada; retomar execucao da issue original`
- se a correcao ainda estiver dentro do escopo original e puder ser decomposta
  em task, use `correcao_requerida` com `status_resultante_issue: active`,
  `destino_proposto: nenhum` e ajuste a issue original antes da cascata documental
- quando a mesma issue voltar para `active`, use
  `ROUND de retorno: <ROUND atual + 1>` e encerre com proximo passo explicito:
  `SESSION-IMPLEMENTAR-ISSUE.md` com `TASK_ID: auto`
- nao abra `issue-local` para duplicar trabalho que ainda cabe na issue
  original em status `todo`, `active` ou `ready_for_review` quando o escopo
  remanescente ainda pertence a mesma issue
- quando `correcao_requerida` permanecer dentro do escopo original, execute o
  Passo 3 antes de qualquer sincronizacao `ready_for_review -> active`
- se o destino proposto for `new-intake`, nao gere issue local; ainda assim,
  sincronize a issue original no Passo 4 e registre que o proximo passo e
  abrir um intake no fluxo canonico
- se o destino proposto for `issue-local`, use `status_resultante_issue: done`
  para a issue original e prossiga para os Passos 4 e 5

### Passo 3 - Persistencia da correcao na issue original

Execute este passo somente quando o veredito aprovado for
`correcao_requerida`, `status_resultante_issue: active` e
`destino_proposto: nenhum`.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Atualizacoes obrigatorias:

1. manifesto da issue original:
   - registrar no proprio conteudo da issue um resumo objetivo do gap apontado
     pela revisao e o recorte que volta para execucao
   - atualizar `last_updated`
   - se a correcao passar a exigir maior rigor operacional, promover
     `task_instruction_mode: optional -> required`
2. tasks atingidas pelo achado:
   - se o gap reabrir uma task existente, ajustar a task correspondente e mover
     o status dela para `todo` ou `active`
   - reescrever objetivo, arquivos a ler ou tocar, testes ou validacoes e TDD
     quando aplicavel
   - manter tasks concluidas e fora do achado em `done`
3. nova task dentro da mesma issue, quando o gap ainda pertencer ao escopo
   original mas nao couber em task existente:
   - criar a proxima task rastreavel no formato ja usado pela issue
   - issue granularizada: criar o proximo `TASK-N.md` e atualizar a lista
     `## Tasks` no `README.md`
   - issue legada: adicionar a task ou checklist no proprio manifesto; se
     `task_instruction_mode: required`, atualizar tambem `## Instructions por Task`

Regras deste passo:

- issue granularizada: persistir delta no `README.md` e em cada `TASK-N.md`
  tocado; nao basta mudar apenas o status agregado da issue
- issue legada: preservar o arquivo unico atual; nao migrar a issue para pasta
  durante esta sessao
- se nenhuma alteracao precisar ser persistida na issue original apos o
  veredito, responda `BLOQUEADO` e nao siga para o Passo 4
- a branch de mesma issue nunca gera `issue-local`
- conclua este passo antes de qualquer sincronizacao `ready_for_review -> active`
- mantenha `## Handoff para Revisao Pos-Issue` como snapshot historico; esse
  bloco sera sobrescrito apenas no proximo fechamento para `ready_for_review`

### Passo 4 - Sincronizacao do veredito na issue revisada

Execute este passo sempre que o gate do agente senior estiver consolidado e
nao houver motivo para `REPROVADO`.
Se a revisao permanecer na mesma issue, conclua primeiro o Passo 3.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Atualizacoes obrigatorias:

1. manifesto da issue revisada:
   - `ready_for_review -> done` quando a revisao aprovar o fechamento
   - `ready_for_review -> active` quando o escopo original voltar para execucao
   - `ready_for_review -> cancelled` quando a revisao for encerrada sem conclusao valida
2. `EPIC-*.md` pai:
   - atualizar a linha da issue para o novo status
   - se todas as issues estiverem `done` ou `cancelled`, promover o epico a `done`
   - caso contrario, manter ou retornar o epico para `active`
3. manifesto da fase:
   - atualizar a linha do epico para o novo status
   - se todos os epicos estiverem `done`, mover `audit_gate` para `pending`
   - se o epico voltar para `active` e o `audit_gate` estiver `pending`, retornar para `not_ready`
4. `SPRINT-*.md` que contem a issue:
   - atualizar a linha da issue para o novo status
   - se todas as issues da sprint estiverem `done` ou `cancelled`, promover a sprint a `done`
   - caso contrario, manter a sprint em `active`

Regras deste passo:

- a issue original nao deve permanecer em `ready_for_review` apos o veredito final desta sessao
- `ready_for_review` nunca conta como issue encerrada na recalculadora de epico, fase ou sprint
- `ready_for_review -> active` so pode ser gravado depois que o Passo 3
  persistir o delta da mesma issue em `README.md`, `TASK-N.md` ou no manifesto
  legado com suas instructions inline
- se o destino final for `new-intake`, a issue original ainda precisa ser sincronizada antes de encerrar
- se a fase ja estiver com `audit_gate: approved`, qualquer tentativa de reabrir o epico ou a fase deve responder `BLOQUEADO`
- quando o resultado final for `ready_for_review -> active`, encerre a sessao
  com handoff explicito de retomada: `TASK_ID: auto` e `ROUND: <N+1>`

### Passo 5 - Rascunho da issue de correcao

Gere rascunho completo de novo recurso de issue local no mesmo epico e fase,
seguindo `GOV-ISSUE-FIRST.md`.

Regras obrigatorias do rascunho:

- so gerar `issue-local` quando o achado for novo, local e distinto do escopo
  remanescente da issue original; nao use este passo para continuar uma issue
  que voltou para `active`
- se o fix ainda couber no escopo original, ajuste a issue original e suas
  tasks em vez de usar este passo

- usar issue granularizada como padrao: criar pasta
  `ISSUE-F<N>-<NN>-<MMM>-<SLUG>/` com `README.md` e `TASK-*.md` quando houver
  multiplas tasks, tarefas decupadas ou `task_instruction_mode: required`
- usar arquivo unico `ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md` apenas quando a
  correcao for simples, local e de task unica
- se a issue for granularizada, usar `README.md` como manifesto e
  `PROJETOS/COMUM/TEMPLATE-TASK.md` para cada `TASK-N.md`
- manter no manifesto da issue: user story, contexto tecnico, plano TDD,
  criterios, DoD, tasks, arquivos reais e artefato minimo
- criar `doc_id` coerente com o formato escolhido:
  - issue granularizada: `doc_id` do `README.md` igual ao identificador da issue
  - issue legada: `doc_id` no formato `ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md`
- manter `status: todo`
- definir `task_instruction_mode` conforme `SPEC-TASK-INSTRUCTIONS.md`
- usar `required` quando houver risco alto, multi-arquivo, ordem critica,
  regressao delicada ou handoff sensivel
- quando uma task envolver codigo novo ou alteracao com cobertura automatizavel,
  marcar `tdd_aplicavel: true` e preencher `testes_red` + `passos_atomicos`
  na ordem red -> green -> refactor; quando nao envolver TDD, manter
  `tdd_aplicavel: false` ou omitir conforme a spec
- registrar no `Contexto Tecnico`:
  - issue de origem
  - evidencia usada na revisao
  - sintoma observado
  - risco de nao corrigir
- registrar em `Dependencias` a issue de origem alem de intake, PRD, epico e fase

Registre:

```text
RASCUNHO: ISSUE-F<N>-<NN>-<MMM>-<SLUG>/ (pasta) ou ISSUE-F<N>-<NN>-<MMM>-<SLUG>.md (arquivo legado)
─────────────────────────────────────────
<conteudo completo>
─────────────────────────────────────────
Destino: PROJETOS/{{PROJETO}}/{{FASE}}-.../issues/
```

### Passo 6 - Sincronizacao documental minima da nova issue local

Execute somente se a nova issue de correcao for aprovada.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
```

Atualizacoes obrigatorias:

1. `EPIC-*.md` pai:
   - adicionar a nova issue a tabela `Issues do Epico`
   - apontar o campo `Documento` para a pasta `./issues/ISSUE-.../` ou para o
     arquivo legado correspondente
   - se o epico estiver `done`, retornar para `active`
2. manifesto da fase:
   - manter ou retornar o epico para `active`, se necessario
   - se `audit_gate` estiver `pending`, voltar para `not_ready`

Regras deste passo:

- nao reabra a issue original
- nao adicione a nova issue a sprint automaticamente; selecao de sprint continua
  fora desta sessao
- se a fase ja estiver com `audit_gate: approved`, pare com `BLOQUEADO` e
  registre que a correcao deve ser tratada fora da fase fechada

Se qualquer sincronizacao conflitar com o estado atual dos artefatos,
responda `BLOQUEADO` e nao grave nada.
