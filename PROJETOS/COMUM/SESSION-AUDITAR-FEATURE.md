---
doc_id: "SESSION-AUDITAR-FEATURE.md"
version: "1.4"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SESSION-AUDITAR-FEATURE - Auditoria de Feature em Sessao de Chat

## Parametros obrigatorios

```text
PROJETO:       <nome do projeto>
FEATURE_ID:    <FEATURE-<N>-<NOME>>
FEATURE_PATH:  <caminho completo da pasta da feature>
RODADA:        <R<NN>>
BASE_COMMIT:   <sha ou "worktree">
AUDIT_LOG:     <caminho completo do AUDIT-LOG.md>
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1, 2 e 3. Depois leia o
manifesto da feature, as user stories da feature (ler `README.md` e todos os
`TASK-*.md` de cada US), o ultimo relatorio da feature e use:

- `PROJETOS/COMUM/GOV-AUDITORIA.md`
- `PROJETOS/COMUM/GOV-AUDITORIA-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

Use `PROJETOS/COMUM/GOV-AUDITORIA.md` para vereditos, severidades e remediacao
geral. Use `PROJETOS/COMUM/GOV-AUDITORIA-FEATURE.md` para o contrato
feature-first do relatorio e da superficie de auditoria. Se qualquer um desses
arquivos ou `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md` nao existir ou nao
puder ser lido, responda `BLOQUEADO` e pare.

## Pre-condicao: Sync do indice derivado Postgres

Antes do Passo 0, sincronize o indice derivado de `PROJETOS/`:

1. rode `./bin/ensure-fabrica-projects-index-runtime.sh`
2. se o preflight devolver exit `0`, rode `./bin/sync-fabrica-projects-db.sh`
3. consulte no DB o estado atual da feature: `status`, `audit_gate` e user
   stories abertas relevantes para a rodada apenas quando o sync tiver corrido
4. compare o resultado com o Markdown canonico da feature e do `AUDIT-LOG.md`;
   o **Markdown prevalece**
5. registre `DRIFT_INDICE: <nenhuma | descricao>` antes da pre-checagem,
   incluindo exit code e motivo quando o preflight falhar
6. apos qualquer gravacao em `PROJETOS/` que altere relatorio, `AUDIT-LOG.md`,
   feature ou user stories, execute novo sync apenas se o preflight permanecer OK

Normativa complementar: `PROJETOS/COMUM/SPEC-RUNTIME-POSTGRES-MATRIX.md` (matriz
quando o sync e obrigatorio ou dispensavel, variaveis, ordem `host.env` / bootstrap / sync).

**URL ausente ou preflight falho nesta sessao:** registe `DRIFT_INDICE` descrevendo
que o sync nao correu; **nao** instale Postgres, Docker, gestores de pacotes nem
binarios externos como parte da sessao salvo pedido humano explicito; **nao** cancele
a rodada de auditoria apenas por falta de sync; prossiga com Markdown + Git conforme a matriz.

Ao gravar `AUDIT-LOG.md` ou relatorios em `auditorias/`, siga
`PROJETOS/COMUM/SPEC-EDITOR-ARTEFACTOS.md` (patches pequenos, evitar reescrita total).

## Contrato operacional pos-PRD

- esta sessao deve rodar no `agente senior`
- esta sessao nao introduz confirmacao humana adicional apos o PRD
- divergencia **indice derivado vs Markdown** e telemetria operacional em
  `DRIFT_INDICE`; isso nao substitui a leitura canonica da feature, do
  relatorio ou do `AUDIT-LOG.md`
- todo veredito deve comparar a feature auditada contra o PRD, as user stories
  da feature, os criterios de aceite e o historico de follow-ups
- a remediacao local canonica desta sessao e `same-feature`; quando o log ainda
  usar o enum legado `issue-local`, trate-o como adaptador equivalente

## Passo 0 - Pre-checagem de elegibilidade

Antes de qualquer leitura de escopo, verifique se a feature esta apta para nova
rodada.

1. localize o manifesto da feature em `{{FEATURE_PATH}}`
2. liste as user stories em `{{FEATURE_PATH}}/user-stories/US-*/README.md`
3. se o manifesto da feature nao existir, se nenhuma User Story for encontrada,
   se algum `README.md` estiver ausente ou se nao houver rastreabilidade minima
   para ligar feature, USs e `AUDIT-LOG.md`, responda `BLOQUEADO`
4. para cada User Story, leia `README.md` e determine `status`
5. se qualquer US estiver `todo`, `active` ou `ready_for_review`, a feature nao
   e elegivel para auditoria

Somente se todas as User Stories estiverem `done` ou `cancelled`, leia o
`AUDIT-LOG.md` do projeto. Localize a entrada mais recente da feature na tabela
de Rodadas e verifique seu veredito.

Se o `AUDIT-LOG.md` ainda usar a coluna legada `Fase`, trate-a como alias de
compatibilidade para `Feature`. Ao filtrar e ao gravar entradas, use
exatamente `{{FEATURE_ID}}`.

- se o veredito da rodada mais recente for `go` ou se nao houver rodada
  anterior, a feature e elegivel
- se o veredito da rodada mais recente for `hold`, execute a verificacao abaixo

**Verificacao de follow-ups da rodada hold imediatamente anterior**

Identifique o `Audit ID` da rodada `hold` mais recente. Na secao
`Resolucoes de Follow-ups`, considere apenas as linhas em que:

- `Audit ID de Origem` = `Audit ID` da rodada `hold` mais recente
- `Feature` = `{{FEATURE_ID}}` ou coluna legada `Fase` com o mesmo valor

Para cada follow-up dessa rodada, determine a situacao pelo tipo:

| Tipo/compatibilidade | Como verificar | Elegivel para encerrar? |
|---|---|---|
| `US-*` | ler o `status` no `README.md` da pasta | `done` ou `cancelled` |
| `ISSUE-*` legado | ler o `status` no frontmatter do arquivo ou `README.md` | `done` ou `cancelled` |
| `INTAKE-*.md` | verificar se o arquivo existe e tem intake_kind registrado | sempre elegivel |
| `cancelled` | a linha no log ja registra o destino como `cancelled` | sempre elegivel |

Apresente:

```text
PRE-CHECAGEM DE ELEGIBILIDADE
-----------------------------------------
Feature auditada:          <FEATURE_ID>
Manifesto da feature:      <ok | ausente>
User Stories encontradas:  <N>
Gate atual da feature:     <pending | hold | approved | desconhecido>
DRIFT_INDICE:              <nenhuma | descricao>

User Stories da feature:
| US | Status | Elegivel para auditoria? |
|---|---|---|
| US-* | done/cancelled/todo/active/ready_for_review | sim/nao |

Rodada hold de referencia: <Audit ID | nenhuma>

Follow-ups bloqueantes dessa rodada:
| Ref | Tipo | Destino | Status atual | Elegivel? |
|---|---|---|---|---|
| US-* / ISSUE-* | bloqueante | same-feature / issue-local / new-intake | todo/active/ready_for_review/done/cancelled | sim/nao |

Follow-ups nao bloqueantes dessa rodada:
| Ref | Tipo | Destino | Status atual |
|---|---|---|---|
| INTAKE-*.md | nao bloqueante | new-intake | criado |
| - | nao bloqueante | cancelled | registrado no log |

Resultado: <ELEGIVEL | BLOQUEADO>
-----------------------------------------
```

**Regra de elegibilidade:** a nova rodada so pode prosseguir se:

- todas as User Stories da feature estiverem `done` ou `cancelled`
- todos os follow-ups **bloqueantes** `same-feature` ou `issue-local` da rodada
  `hold` imediatamente anterior estiverem `done` ou `cancelled`

`ready_for_review` ainda nao conta como encerrada. `INTAKE-*.md` e entradas
`cancelled` nunca bloqueiam nova rodada.

Se o resultado for `BLOQUEADO`, encerre a sessao sem produzir relatorio, sem
atualizar o log e sem mudar o gate.

## Passo 1 - Escopo auditado

Liste, no minimo:

- manifesto da feature
- user stories da feature
- `TASK-*.md` de cada US auditada
- testes e validacoes executadas
- diff ou commit base auditado
- ultimo relatorio da feature, quando existir

## Passo 2 - Achados preliminares

Apresente os achados em categorias. Em caso de monolito acima de threshold,
ofereca:

```text
MONOLITO DETECTADO: <arquivo ou funcao>
```

Se o achado for local a esta feature, mas nao couber em nenhuma US atual sem
drift, registre isso explicitamente e proponha remediacao via nova User Story
na mesma Feature, mesmo que o roteamento documental posterior ainda use o enum
legado `issue-local` no log.

## Passo 3 - Veredito proposto

Apresente:

```text
VEREDITO PROPOSTO
-----------------------------------------
veredito:
gate_da_feature:
follow-ups bloqueantes:
follow-up padrao:
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Passo 4 - Gravacao

Antes de gravar cada artefato, anuncie:

```text
GERANDO: <arquivo>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

O relatorio deve ser gravado em:

`{{FEATURE_PATH}}/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`

Ao atualizar o `AUDIT-LOG.md`, grave `{{FEATURE_ID}}` na coluna `Fase` por
compatibilidade apenas quando o log ainda nao tiver migrado para a coluna
`Feature`.

## Passo 5 - Pos-Hold

Execute somente se o veredito for `hold`.

Apos gravar o relatorio e atualizar o `AUDIT-LOG`, registre:

```text
AUDITORIA CONCLUIDA - VEREDITO: hold
-----------------------------------------
Follow-ups bloqueantes: <N>
Follow-ups nao bloqueantes: <N>
-----------------------------------------
Proximo passo: use SESSION-REMEDIAR-HOLD.md para converter os
follow-ups nos artefatos corretos (same-feature, new-intake ou cancelled).

RELATORIO_PATH: <caminho do relatorio recem-gravado>
AUDIT_LOG_PATH: <caminho do AUDIT-LOG>
FEATURE_ID: <FEATURE-...>
FEATURE_PATH: <caminho da feature>
-----------------------------------------
Cole SESSION-REMEDIAR-HOLD.md em uma nova sessao com os parametros acima.
```

## Passo 6 - Pos-Go e encerramento do projeto

Execute somente se o veredito for `go`.

Depois de consolidar a rodada aprovada:

1. liste todas as features em `PROJETOS/{{PROJETO}}/features/FEATURE-*`
2. para cada feature, verifique se todas as User Stories estao `done` ou
   `cancelled`
3. verifique se o gate da feature esta aprovado no manifesto ou no `AUDIT-LOG.md`

Apresente:

```text
ENCERRAMENTO DE PROJETO
-----------------------------------------
Features do projeto:
| Feature | User Stories encerradas? | Gate aprovado? | Encerrada? |
|---|---|---|---|
| FEATURE-* | sim/nao | sim/nao | sim/nao |

Resultado: <APTO PARA ENCERRAMENTO | AINDA NAO APTO>
-----------------------------------------
```
