---
doc_id: "SESSION-REVISAR-US.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SESSION-REVISAR-US - Revisao Pos-User Story em Sessao de Chat

## Parametros obrigatorios

```
PROJETO:      <nome do projeto>
FEATURE_ID:   <FEATURE-<N>>
US_ID:        <US-<N>-<NN> ou identificador canonico da user story no projeto>
US_PATH:      <caminho completo: arquivo `.md` da US ou pasta US-*/ com README.md>
BASE_COMMIT:  <sha base anterior ao diff, "worktree", "auto" ou "nao_informado">
TARGET_COMMIT:<sha revisado, "HEAD", "worktree", "auto" ou "nao_informado">
EVIDENCIA:    <referencia reproduzivel: "git show <sha>", "git diff <base>..<target>", PR, logs, testes, links, "auto" ou "nao_informado">
OBSERVACOES:  <restricoes adicionais ou "nenhuma">
REVIEW_MODE:  <"auto" | "padrao" | "revisao_criterio_emergente">
```

Validacoes obrigatorias do preenchimento:

- `US_ID` deve manter o identificador canonico usado no backlog da feature
- `EVIDENCIA` nao pode ser apenas `diff`; precisa apontar o comando, range, PR, log ou artefato exato
- se a revisao mirar um commit unico, preferir `TARGET_COMMIT=<sha>` com `EVIDENCIA=git show <sha>` ou `git diff <sha>^..<sha>`
- se `BASE_COMMIT`, `TARGET_COMMIT` ou `EVIDENCIA` vierem como `auto` ou `nao_informado`, resolva primeiro a secao `## Handoff para Revisao Pos-User Story` do manifesto da user story
- se `BASE_COMMIT` e `TARGET_COMMIT` forem iguais e a evidencia pedida for diff, trate como ambiguidade; use `git show <sha>` ou peca ajuste antes de seguir
- se os parametros explicitamente informados conflitarem com o handoff persistido, apresente `ALERTA - PARAMETROS DIVERGENTES` antes de prosseguir

Limites e elegibilidade da user story em revisao: `PROJETOS/COMUM/GOV-USER-STORY.md` (tamanho, `task_instruction_mode`, criterios de execucao).

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa no papel de
agente senior revisor.

## Passo -1 (obrigatorio — no maximo tres comandos antes de ler manifestos)

Antes de abrir `README.md` da user story, `TASK-*.md`, a feature referenciada ou
ficheiros citados pela evidencia:

1. executar o preflight canonico: `./bin/ensure-fabrica-projects-index-runtime.sh`
   na raiz do repositorio (opcional `--json`);
2. se o exit code for diferente de `0` **e** a revisao exigir `sync_runs`,
   comparacao DB real ou outro runtime operacional: responda `BLOQUEADO`, copie
   o motivo para a saida e **nao** elabore plano extenso nem leia artefactos de
   escopo (ver `PROJETOS/COMUM/SPEC-RUNTIME-POSTGRES-MATRIX.md`);
3. so apos (1) passar ou (2) nao se aplicar, prossiga com `boot-prompt` e
   **leitura minima** conforme `PROJETOS/COMUM/SPEC-LEITURA-MINIMA-EVIDENCIA.md`
   (e orcamento de exploracao na mesma spec).

Siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia (com leitura
minima para artefactos longos):

- a user story informada (se for pasta, leia `README.md` e os `TASK-*.md` para revisao)
- o handoff de revisao persistido no manifesto da user story, quando existir (secao `## Handoff para Revisao Pos-User Story`)
- a feature referenciada pela user story
- `decision_refs`, quando existirem
- apenas os arquivos de codigo citados pela user story e pela evidencia recebida
- `PROJETOS/COMUM/GOV-SCRUM.md` (em especial `## Review Pos-User-Story` e `## Procedimento de Review-Ready e Fechamento de User Story`)
- `PROJETOS/COMUM/GOV-USER-STORY.md`
- `SCOPE-LEARN.md` no diretorio da user story, quando existir, e
  `PROJETOS/COMUM/TEMPLATE-SCOPE-LEARN.md` como referencia de formato

Nao execute descoberta autonoma de feature ou user story.

Nao existe ainda ficheiro dedicado `PROMPT-REVISAR-US.md`; o procedimento normativo desta sessao e o presente documento mais os normativos acima. Quando existir `REV-US-<N>-<NN>.md` na pasta da user story, trate-o como instancia local dos parametros e do contexto dessa US; nao substitui este documento nem os normativos referenciados.

Antes do Passo 0, valide os parametros recebidos. Se `FEATURE_ID`,
`US_ID`, `US_PATH`, `BASE_COMMIT`, `TARGET_COMMIT`, `EVIDENCIA` ou
`REVIEW_MODE` estiverem
malformados, ambiguos ou nao reproduziveis, responda `BLOQUEADO` em vez de
inferir o alvo da revisao.

Se qualquer parametro vier como `auto` ou `nao_informado`, resolva-o a partir
do handoff da user story. Se o handoff estiver ausente, incompleto ou inconsistente,
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

## Pre-condicao: preflight do runtime e sync do indice derivado Postgres

Antes do Passo 0, execute o preflight do runtime e sincronize o indice derivado de `PROJETOS/` quando elegivel:

1. rode `./bin/ensure-fabrica-projects-index-runtime.sh`
2. se o preflight devolver exit `0`, rode `./bin/sync-fabrica-projects-db.sh` e consulte no DB o estado atual da user story: `status`, `task_instruction_mode`, tasks abertas, feature associada
3. se o preflight falhar e a revisao exigir `sync_runs`, comparacao DB real ou outro runtime operacional, responda `BLOQUEADO`
4. compare o resultado com o Markdown canonico; o **Markdown prevalece**
5. registre `DRIFT_INDICE: <nenhuma | descricao>` antes do bloco `REVISAO POS-USER-STORY`, incluindo exit code e motivo quando o preflight falhar
6. apos qualquer gravacao em `PROJETOS/` que altere user story, task, feature, handoff de review ou `SCOPE-LEARN.md`, execute novo sync apenas se o preflight permanecer OK

Normativa complementar: `PROJETOS/COMUM/SPEC-RUNTIME-POSTGRES-MATRIX.md` (matriz
quando o sync e obrigatorio ou dispensavel, variaveis, ordem `host.env` / bootstrap / sync).

**URL ausente ou preflight falho nesta sessao:** registe `DRIFT_INDICE` descrevendo
que o sync nao correu; **nao** instale Postgres, Docker, gestores de pacotes nem
binarios externos como parte da sessao salvo pedido humano explicito; para revisao
documental prossiga com Markdown + Git conforme a matriz; para runtime real, bloqueie cedo.

Gravacoes no `README.md` da US, `REV-US-*.md` ou `SCOPE-LEARN.md`:
`PROJETOS/COMUM/SPEC-EDITOR-ARTEFACTOS.md`.

## Contrato Operacional Pos-PRD

- esta sessao deve rodar no `agente senior`, isto e, no modelo configurado em
  `FABRICA_AUDITOR_MODEL`, acessado via OpenRouter; o default esperado e
  `openrouter/anthropic/claude-opus-4.6`
- esta sessao nao introduz confirmacao humana adicional apos o PRD; os
  checkpoints abaixo pertencem ao proprio gate do agente senior
- o resultado operacional do gate deve ser `APROVADO`, `AJUSTAR` ou
  `REPROVADO`
- override humano apos o PRD so e valido quando houver conflito reproduzivel
  entre handoff e evidencia manual, cancelamento declarado ou contexto
  externo novo
- divergencia **indice derivado vs Markdown** e telemetria operacional em
  `DRIFT_INDICE`; isso nao substitui a leitura canonica do manifesto da user story
  nem a validacao de alinhamento com o PRD
- inferir o `ROUND` atual a partir do handoff persistido; se o handoff nao
  trouxer round explicito, assuma `ROUND: 1` como primeira revisao da user story
- resolver `REVIEW_MODE` com precedencia deterministica:
  - usar o valor recebido quando for `padrao` ou `revisao_criterio_emergente`
  - se vier `auto`, usar `revisao_criterio_emergente` apenas quando existir
    `SCOPE-LEARN.md` elegivel conforme esta sessao
  - em qualquer outro caso, usar `padrao`
- toda revisao deve explicitar alinhamento com o PRD, a feature de origem e os
  criterios de aceite da user story antes do veredito final
- antes do veredito final, execute
  `python3 scripts/framework_governance/validate_us_traceability.py --repo-root . --us-path <US_PATH>`;
  falha desse gate invalida `ready_for_review`
- se a correcao ainda pertencer ao escopo original, o agente senior deve
  preferir adicionar ou ajustar `TASK-N.md` dentro da propria user story em vez de
  propor backlog paralelo
- quando devolver a mesma user story para `active`, a saida deve anunciar
  explicitamente `TASK_ID: auto` e `ROUND: <N+1>` para o proximo loop local

### Passo 0 - Confirmacao de escopo e evidencia

Registre:

```text
REVISAO POS-USER-STORY
─────────────────────────────────────────
User Story:
Status atual:
Objetivo:
task_instruction_mode:
ROUND atual da user story:
Feature/criterios do PRD auditados:
BASE_COMMIT:
TARGET_COMMIT:
Evidencias disponiveis:
Limitacoes da revisao:
Risco de expandir escopo indevidamente:
SCOPE-LEARN presente: <nao | sim, status do frontmatter>
modo: <padrao | revisao_criterio_emergente>
```

Se nao houver evidencia minima para sustentar a revisao, responda `BLOQUEADO`.

Se a user story original estiver `todo` ou `active` e a evidencia nao provar todos
os criterios de aceitacao e itens de DoD, apresente antes de prosseguir:

```text
ALERTA — REVISAO PREMATURA
─────────────────────────────────────────
User story original ainda aberta: <todo | active>
Escopo coberto pela evidencia: <commit parcial / worktree parcial / outro>
Lacunas para considerar a user story done:
- <criterio/DoD ainda nao evidenciado>
Risco: abrir follow-up agora pode duplicar o escopo da user story original
```

Quando esse alerta aparecer, trate o caso por padrao como implementacao
parcial: nao abra artefato paralelo para escopo ainda pertencente a user story original
e use `correcao_requerida` com `status_resultante_user_story: active`, salvo
evidencia suficiente em contrario.

**Excecao — revisao de criterio emergente**

Quando existir `SCOPE-LEARN.md` com `status: aguardando_senior` ou `rascunho`
(ja tratado como submetido) e a user story estiver `active` com todas as tasks
`done`, use `modo: revisao_criterio_emergente`. Neste modo:

- nao exija `ready_for_review` para prosseguir
- resolva `BASE_COMMIT`, `TARGET_COMMIT` e `EVIDENCIA` a partir do ultimo commit
  da ultima task concluida ou de notas no `SCOPE-LEARN.md`, o que for mais
  reproduzivel
- `SCOPE-LEARN.md` **nao** e artefato paralelo de escopo indevido; formaliza
  lacuna nos criterios Given/When/Then face a evidencia de execucao

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
| 1 | bug / test-gap / scope-drift / architecture-drift | high/medium/low | ... | new-intake / ajuste na mesma US |

Destino sugerido consolidado: <nenhum | ajuste na mesma US | new-intake>
```

Nao gere arquivo neste passo.

### Passo 2 - Veredito proposto

Registre:

```text
VEREDITO PROPOSTO
─────────────────────────────────────────
veredito: <aprovada | correcao_requerida | cancelled>
status_resultante_user_story: <done | active | cancelled>
destino_proposto: <nenhum | new-intake>
reabrir user story original: <nao | sim, apos atualizar a mesma user story>
ROUND de retorno: <n-a | N+1>
saida persistida: <sincronizar user story revisada | user story original atualizada + sincronizar user story revisada | abrir intake fora desta sessao | nenhum artefato>
```

Regras deste passo:

- se o veredito for `aprovada`, use `status_resultante_user_story: done` e prossiga
  para o Passo 4
- se o veredito for `cancelled`, use `status_resultante_user_story: cancelled` e
  prossiga para o Passo 4
- se a revisao estiver marcada como `parcial` e os achados representarem apenas
  escopo ainda nao entregue da user story original, use `correcao_requerida` com
  `status_resultante_user_story: active`, `destino_proposto: nenhum` e
  `saida persistida: user story original atualizada + sincronizar user story revisada; retomar execucao da mesma user story`
- se a correcao ainda estiver dentro do escopo original e puder ser decomposta
  em task, use `correcao_requerida` com `status_resultante_user_story: active`,
  `destino_proposto: nenhum` e ajuste a user story original antes da cascata documental
- quando a mesma user story voltar para `active`, use
  `ROUND de retorno: <ROUND atual + 1>` e encerre com proximo passo explicito:
  `SESSION-IMPLEMENTAR-US.md` com `TASK_ID: auto`
- nao crie uma segunda user story local para duplicar trabalho que ainda cabe na user story
  original em status `todo`, `active` ou `ready_for_review` quando o escopo
  remanescente ainda pertence a mesma user story (`GOV-SCRUM.md`)
- quando `correcao_requerida` permanecer dentro do escopo original, execute o
  Passo 3 antes de qualquer sincronizacao `ready_for_review -> active`
- se o destino proposto for `new-intake`, nao gere user story local; ainda assim,
  sincronize a user story original no Passo 4 e registre que o proximo passo e
  abrir um intake no fluxo canonico
- em `modo: revisao_criterio_emergente`, o senior decide sobre o
  `SCOPE-LEARN.md` antes do handoff normal:
  - **Incorporar proposta:** atualizar `Given/When/Then` no manifesto com menção
    explicita a **aprendizado emergente** e referencia a `scope_learn_id` ou ao
    ficheiro; gravar `SCOPE-LEARN.md` com `status: incorporado` e secao
    `decisao_senior` completa
  - **Manter criterios (rejeitar proposta):** gravar `SCOPE-LEARN.md` com
    `status: rejeitado` e `decisao_senior`; nao alterar criterios sem outra
    decisao
  - **Escopo fora da US:** `destino_proposto: new-intake` e registrar em
    `decisao_senior`; `SCOPE-LEARN.md` pode ficar `incorporado` apenas como
    registro com resultado `new-intake`
  - se a incorporacao exigir **novas tasks** ou reabrir tasks, use
    `correcao_requerida`, execute o Passo 3 antes do Passo 4 e mantenha a user
    story `active`
  - se apos incorporar ou rejeitar **nao** houver tasks abertas e a entrega
    continuar alinhada aos criterios vigentes, prossiga para o Passo 4
    promovendo `active -> ready_for_review` com handoff conforme
    `SESSION-IMPLEMENTAR-US.md` (Passo 3.1), salvo o veredito seja `cancelled`

### Passo 3 - Persistencia da correcao na user story original

Execute este passo somente quando o veredito aprovado for
`correcao_requerida`, `status_resultante_user_story: active` e
`destino_proposto: nenhum`.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Atualizacoes obrigatorias:

1. manifesto da user story original:
   - registrar no proprio conteudo um resumo objetivo do gap apontado
     pela revisao e o recorte que volta para execucao
   - atualizar `last_updated`
   - se a correcao passar a exigir maior rigor operacional, promover
     `task_instruction_mode: optional -> required`
2. tasks atingidas pelo achado (incluindo follow-up de `SCOPE-LEARN.md` quando
   o senior incorporar criterio e exigir trabalho adicional):
   - se o gap reabrir uma task existente, ajustar a task correspondente e mover
     o status dela para `todo` ou `active`
   - reescrever objetivo, arquivos a ler ou tocar, testes ou validacoes e TDD
     quando aplicavel
   - manter `depends_on`, `parallel_safe` e `write_scope` coerentes com o novo
     plano da user story
   - manter tasks concluidas e fora do achado em `done`
3. nova task dentro da mesma user story, quando o gap ainda pertencer ao escopo
   original mas nao couber em task existente:
   - criar a proxima task rastreavel no formato ja usado pela user story
   - user story granularizada: criar o proximo `TASK-N.md` e atualizar a lista
     `## Tasks` no `README.md`
   - a nova task nasce com `user_story_id` coerente, `depends_on` explicito,
     `parallel_safe: false` por default e `write_scope` declarado
   - user story legada: adicionar a task ou checklist no proprio manifesto; se
     `task_instruction_mode: required`, atualizar tambem `## Instructions por Task`

Regras deste passo:

- user story granularizada: persistir delta no `README.md` e em cada `TASK-N.md`
  tocado; nao basta mudar apenas o status agregado da user story
- user story legada: preservar o arquivo unico atual; nao migrar a user story para pasta
  durante esta sessao
- se nenhuma alteracao precisar ser persistida na user story original apos o
  veredito, responda `BLOQUEADO` e nao siga para o Passo 4
- conclua este passo antes de qualquer sincronizacao `ready_for_review -> active`
- mantenha `## Handoff para Revisao Pos-User Story` como snapshot historico; esse
  bloco sera sobrescrito apenas no proximo fechamento para `ready_for_review`

### Passo 4 - Sincronizacao do veredito na user story revisada

Execute este passo sempre que o gate do agente senior estiver consolidado e
nao houver motivo para `REPROVADO`.
Se a revisao permanecer na mesma user story, conclua primeiro o Passo 3.

Antes de gravar cada atualizacao, anuncie:

```text
ATUALIZANDO: <arquivo>
  alteracao: <resumo curto>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

Atualizacoes obrigatorias:

1. manifesto da user story revisada:
   - `ready_for_review -> done` quando a revisao aprovar o fechamento
   - `ready_for_review -> active` quando o escopo original voltar para execucao
   - `ready_for_review -> cancelled` quando a revisao for encerrada sem conclusao valida
2. `FEATURE-*.md` pai (ou equivalente no projeto):
   - atualizar a linha da user story para o novo status
   - recalcular `audit_gate` da feature conforme `GOV-SCRUM.md`
3. quando o projeto ainda preservar artefatos legados de rastreabilidade
   ligados a esta user story, aplicar a cascata coerente com o estado gravado
   na feature e com `GOV-SCRUM.md`, sem promover `audit_gate` da feature por
   revisao isolada se ainda existir user story aberta
4. `modo: revisao_criterio_emergente` sem tasks pendentes apos atualizar
   manifesto e `SCOPE-LEARN.md`: promover `active -> ready_for_review`,
   persistir `## Handoff para Revisao Pos-User Story` conforme
   `SESSION-IMPLEMENTAR-US.md`; na rodada seguinte de revisao, tratar como fluxo
   padrao com `ready_for_review`

Regras deste passo:

- quando a entrada ja era `ready_for_review`, a user story original nao deve
  permanecer em `ready_for_review` apos o veredito final desta sessao (deve ir a
  `done`, `active` ou `cancelled`); quando a entrada for
  `modo: revisao_criterio_emergente` com user story `active`, e permitido
  encerrar com `active -> ready_for_review` e handoff para revisao de entrega
  habitual
- `ready_for_review` nunca conta como user story encerrada na recalculadora da feature
- `ready_for_review -> active` so pode ser gravado depois que o Passo 3
  persistir o delta da mesma user story em `README.md`, `TASK-N.md` ou no manifesto
  legado com suas instructions inline
- se a feature ja estiver com `audit_gate: approved`, qualquer tentativa de reabrir
  user story no mesmo ciclo deve responder `BLOQUEADO` (`GOV-SCRUM.md`)
- quando o resultado final for `ready_for_review -> active`, encerre a sessao
  com handoff explicito de retomada: `TASK_ID: auto` e `ROUND: <N+1>`

### Passo 5 - Follow-up estrutural (excepcional)

Por padrao, `GOV-SCRUM.md` proibe abrir uma nova user story local para correcoes
que ainda cabem na user story original. Use este passo apenas quando o achado for
estruturalmente fora do escopo da US e o destino for `new-intake`.

Registre:

```text
FOLLOW-UP: new-intake
─────────────────────────────────────────
Resumo do gap fora da US original:
Proximo passo: fluxo canonico de intake no projeto
─────────────────────────────────────────
```

Nao gere pasta `US-*/` paralela para continuar trabalho que devia permanecer na
mesma user story.

### Passo 6 - Sincronizacao documental pos-intake

Execute somente apos abertura formal de novo intake quando o Passo 5 aplicar.
Atualize `AUDIT-LOG.md` ou artefatos de rastreio do projeto conforme governanca,
sem reabrir a user story original fora do veredito acordado.

Se qualquer sincronizacao conflitar com o estado atual dos artefatos,
responda `BLOQUEADO` e nao grave nada.

## Escopo desta Sessao

Esta sessao governa exclusivamente revisao pos-**User Story**. Para execucao
local da user story, use `SESSION-IMPLEMENTAR-US.md`.
