---
doc_id: "SESSION-REMEDIAR-HOLD.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria de Feature

## Quando usar

Use este prompt imediatamente apos qualquer auditoria de feature com veredito
`hold`, independente de como o relatorio foi produzido. Cobre todos os destinos
canonicos de follow-up em um unico fluxo guiado.

Nao use para auditorias com veredito `go` ou `cancelled`.

## Parametros obrigatorios

Preencha e cole junto com este prompt:

```text
PROJETO:         <nome do projeto>
FEATURE_ID:      <FEATURE-<N>-<NOME>>
FEATURE_PATH:    <caminho completo da pasta da feature>
RELATORIO_PATH:  <caminho completo do RELATORIO-AUDITORIA-*.md>
AUDIT_LOG_PATH:  <caminho completo do AUDIT-LOG.md>
OBSERVACOES:     <restricoes adicionais ou "nenhuma">
```

## Prompt

Voce e um engenheiro de produto senior operando em sessao de chat interativa.

Siga a ordem de leitura definida em `PROJETOS/COMUM/boot-prompt.md`, Niveis 1 e 2.
Nao execute os Niveis 3 a 6.

Leia tambem antes de qualquer acao:

- `PROJETOS/COMUM/GOV-AUDITORIA.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/GOV-USER-STORY.md`
- `PROJETOS/COMUM/TEMPLATE-USER-STORY.md`
- `PROJETOS/COMUM/TEMPLATE-TASK.md`
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/{{PROJETO}}/INTAKE-{{PROJETO}}.md`
- `PROJETOS/{{PROJETO}}/PRD-{{PROJETO}}.md`
- `{{FEATURE_PATH}}`
- `{{RELATORIO_PATH}}`
- `{{AUDIT_LOG_PATH}}`

## Pre-condicao: Sync do Indice SQLite

Antes do Passo 0, sincronize o indice SQLite derivado de `PROJETOS/`:

1. rode `./bin/sync-openclaw-projects-db.sh`
2. consulte no DB o estado atual da feature, das user stories nao encerradas e
   do relatorio mais recente
3. compare o resultado com o Markdown canonico da feature, do relatorio e do
   `AUDIT-LOG.md`; o **Markdown prevalece**
4. registre `DRIFT_INDICE: <nenhuma | descricao>` antes da classificacao
5. apos qualquer gravacao em `PROJETOS/` que altere feature, user story, intake
   de follow-up ou `AUDIT-LOG.md`, execute novo sync

## Contrato operacional pos-PRD

- a classificacao e aprovacao dos follow-ups deve ser feita pelo `agente senior`
- esta sessao nao introduz checkpoint humano adicional apos o PRD
- divergencia **SQLite vs Markdown** e telemetria operacional em
  `DRIFT_INDICE`; isso nao substitui a comprovacao de alinhamento com intake,
  PRD e feature afetada
- toda classificacao deve conferir alinhamento com o PRD, a feature afetada e
  os criterios de aceite antes de abrir remediacao local
- se surgir `new-intake`, o gate humano reaparece apenas quando esse intake
  entrar no fluxo canonico de intake/PRD

## Mapeamento deterministico de destino

Use os destinos operacionais abaixo:

| Destino operacional | Quando usar | Registro legado no `AUDIT-LOG.md` |
|---|---|---|
| `same-feature` | o ajuste continua dentro da feature atual | `issue-local` |
| `new-intake` | o ajuste excede a feature atual | `new-intake` |
| `cancelled` | nao deve virar trabalho novo | `cancelled` |

Enquanto o `AUDIT-LOG.md` ainda usar a coluna `Fase`, grave nela o valor de
`FEATURE_ID`.

## Passo 0 - Leitura e classificacao dos follow-ups

Antes de classificar qualquer follow-up:

- leia o intake principal `PROJETOS/{{PROJETO}}/INTAKE-{{PROJETO}}.md`
- leia o PRD `PROJETOS/{{PROJETO}}/PRD-{{PROJETO}}.md`
- leia o manifesto da feature em `{{FEATURE_PATH}}`
- se o intake principal, o PRD ou o manifesto da feature nao puderem ser
  localizados ou lidos, responda `BLOQUEADO` e pare sem classificar
  follow-ups

Leia `{{RELATORIO_PATH}}`. Extraia todos os follow-ups das secoes
"Follow-ups Bloqueantes" e "Follow-ups nao bloqueantes".

Para cada follow-up:

- identifique a feature, criterio ou trecho do PRD afetado
- determine se o ajuste cabe em uma US existente da mesma feature ou exige uma
  nova US na mesma feature
- registre explicitamente o sinal de alinhamento ou de drift que justifica
  `same-feature` versus `new-intake`
- se nao for possivel comprovar alinhamento com intake, PRD e feature afetada,
  responda `BLOQUEADO` e pare sem classificar

Apresente:

```text
CLASSIFICACAO DOS FOLLOW-UPS
─────────────────────────────────────────
Relatorio: {{RELATORIO_PATH}}
Veredito:  hold
DRIFT_INDICE: <nenhuma | descricao>
─────────────────────────────────────────

Follow-ups Bloqueantes:
| # | Resumo | Destino operacional | Registro legado | Feature/PRD afetado | US candidata / motivo explicito | Alinhamento ou drift |
|---|---|---|---|---|---|---|
| B1 | ... | same-feature / new-intake / cancelled | issue-local / new-intake / cancelled | ... | ... | ... |

Follow-ups Nao Bloqueantes:
| # | Resumo | Destino operacional | Registro legado | Feature/PRD afetado | US candidata / motivo explicito | Alinhamento ou drift |
|---|---|---|---|---|---|---|
| N1 | ... | same-feature / new-intake / cancelled | issue-local / new-intake / cancelled | ... | ... | ... |

─────────────────────────────────────────
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Passo 1 - Rota `same-feature`

Execute somente se houver follow-ups classificados como `same-feature`.

Para cada um:

- prefira reutilizar a US existente quando o gap ainda pertencer claramente ao
  seu escopo original
- se nenhuma US atual acomodar o escopo corretivo sem drift, criar uma nova
  pasta `US-<N>-<NN>-<SLUG>/` em `{{FEATURE_PATH}}/user-stories/`
- usar `README.md` baseado em `TEMPLATE-USER-STORY.md`
- gerar `TASK-*.md` baseados em `TEMPLATE-TASK.md` conforme o
  `task_instruction_mode`
- manter `status: todo` na nova US e registrar a referencia ao relatorio de origem
- atualizar o manifesto da feature para refletir a US criada ou reaberta

```text
RASCUNHO: US-<N>-<NN>-<SLUG>/
─────────────────────────────────────────
<conteudo completo do README.md e resumo das TASK-*.md>
─────────────────────────────────────────
Destino: {{FEATURE_PATH}}/user-stories/
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Passo 2 - Rota `new-intake`

Execute somente se houver follow-ups classificados como `new-intake`.

Para cada um, gere rascunho completo de `INTAKE-{{PROJETO}}-<SLUG>.md`
seguindo `TEMPLATE-INTAKE.md`.

```text
RASCUNHO: INTAKE-{{PROJETO}}-<SLUG>.md
─────────────────────────────────────────
<conteudo completo>
─────────────────────────────────────────
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Passo 3 - Rota `cancelled`

Para cada follow-up classificado como `cancelled`, registre a justificativa
tecnica da classificacao. Nenhum artefato e gerado.

## Passo 4 - Atualizacao do `AUDIT-LOG`

Apos todos os passos anteriores, atualize `{{AUDIT_LOG_PATH}}`:

- preserve a linha da rodada e o gate ja gravados pela sessao de auditoria
- atualize a secao `Resolucoes de Follow-ups` com uma linha por follow-up
- preencha `Audit ID de Origem` com o identificador derivado de `{{RELATORIO_PATH}}`
- preencha `Fase` com `FEATURE_ID` por compatibilidade
- para `same-feature`, `Ref` aponta para a US criada/reaberta e o `Destino`
  legado deve ser `issue-local`
- para `new-intake`, `Ref` aponta para o `INTAKE-*.md` gerado
- para `cancelled`, use `n/a` em `Ref` e registre a justificativa em `Observacoes`

```text
GERANDO: atualizacao da secao Resolucoes de Follow-ups em {{AUDIT_LOG_PATH}}
─────────────────────────────────────────
<diff da atualizacao proposta>
Resultado esperado do gate: `APROVADO | AJUSTAR | REPROVADO`
```

## Regras inegociaveis

- nunca inventar escopo, componente ou risco ausente no relatorio
- nunca reclassificar `new-intake` como `same-feature` sem justificativa explicita
- se houver override humano, registre explicitamente a excecao e a motivacao
- follow-up nao bloqueante classificado como `same-feature` deve ser gerado e sinalizado como nao bloqueante
- nao gerar novos artefatos `ISSUE-*`; referencias historicas podem apenas ser lidas
