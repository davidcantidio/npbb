---
doc_id: "GOV-AUDITORIA.md"
version: "3.1"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# GOV-AUDITORIA

## Objetivo

Formalizar a etapa `Review -> Auditoria de Feature` como gate final de
governanca de cada feature, com avaliacao funcional e de saude estrutural do
codigo.

## Regra Canonica

- a auditoria formal padrao acontece por feature
- a auditoria nao substitui desenvolvimento; ela valida o que foi entregue
- a feature so pode ir para `features/encerradas/` apos auditoria com veredito `go`
- cada rodada de auditoria deve produzir relatorio em `auditorias/` e entrada em `AUDIT-LOG.md`
- a auditoria deve avaliar aderencia funcional, riscos, cobertura de testes e saude estrutural do codigo
- o contrato especifico do relatorio feature-first vive em
  `GOV-AUDITORIA-FEATURE.md` e `TEMPLATE-AUDITORIA-FEATURE.md`
- `PROJETOS/COMUM/LEGADO/TEMPLATE-AUDITORIA-RELATORIO.md` permanece apenas como
  compatibilidade historica da superficie issue-first arquivada em
  `PROJETOS/COMUM/LEGADO/GOV-ISSUE-FIRST.md`
- thresholds de `monolithic-file` e `monolithic-function` vivem exclusivamente em `SPEC-ANTI-MONOLITO.md`
- `GOV-AUDITORIA.md`, prompts e templates de auditoria nao devem duplicar thresholds estruturais; qualquer mudanca futura de `warn/block` deve ocorrer apenas em `SPEC-ANTI-MONOLITO.md`

## Inputs Obrigatorios da Auditoria

- `INTAKE-*.md` aplicavel ao escopo auditado
- `PRD-*.md`
- manifesto da feature
- user stories e tasks da feature
- `AUDIT-LOG.md`
- ultimo relatorio da feature, quando existir
- commit base auditado
- diffs e testes relevantes

## Outputs Obrigatorios

- `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md` ou variante equivalente do
  projeto, usando `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md`
- nova entrada em `AUDIT-LOG.md`
- atualizacao do gate de auditoria no manifesto da feature
- follow-ups classificados por destino e transformados em `same-feature`
  (User Story ou Task na mesma feature), `new-intake` ou `cancelled`
  (com justificativa)
  quando houver `hold`
- quando a rodada suceder um `hold`: secao "Prestacao de Contas dos Follow-ups
  Anteriores" listando cada follow-up gerado pelo hold anterior com seu status
  final verificado; esta secao e obrigatoria e nao pode ser substituida por
  declaracao generica de resolucao

## Classes Canonicas de Achado

- `bug`
- `code-smell`
- `monolithic-file`
- `monolithic-function`
- `missing-docstring`
- `test-gap`
- `architecture-drift`
- `scope-drift`

## Severidade Canonica

- `critical`
- `high`
- `medium`
- `low`

## Vereditos

- `go`: aprovou o gate; feature pode fechar
- `hold`: gate reprovado; manter feature `active` e abrir/remapear follow-ups
- `cancelled`: rodada encerrada sem conclusao valida

## Regras de Julgamento

- `hold` e obrigatorio quando houver achado material `critical` ou `high`
- `hold` tambem e obrigatorio para achado `medium` com risco claro de manutencao, erro, regressao ou expansao incorreta
- `go` so e permitido quando restarem no maximo achados `medium` ou `low` nao bloqueantes, explicitamente registrados
- use `SPEC-ANTI-MONOLITO.md` como criterio de threshold antes de classificar um achado estrutural como bloqueante
- ao julgar `monolithic-file` ou `monolithic-function`, o auditor deve usar `SPEC-ANTI-MONOLITO.md` como fonte normativa do threshold aplicado e nao pode substituir o spec por criterio local do relatorio, prompt ou template
- ausencia de docstring isolada nao bloqueia por si so; so bloqueia quando combinada com alta complexidade, compartilhamento relevante ou dificuldade real de manutencao/auditoria
- opiniao sem evidencia nao e achado; cada nao conformidade precisa apontar trecho, modulo, diff, teste ou comportamento observavel

## Status do Artefato de Auditoria

- `planned`: rodada ainda nao executada
- `active`: auditoria em andamento
- `done`: auditoria concluida
- `cancelled`: rodada abandonada com justificativa
- `provisional`: rodada sem commit SHA valido ou com worktree sujo; nunca aprova gate

## Gate de Auditoria da Feature

> A referencia de checklist e estados vigentes vive em `GOV-SCRUM.md`,
> `GOV-FEATURE.md` e no manifesto `FEATURE-<N>.md`.

Estados operacionais do gate dentro do manifesto da feature:

- `not_ready`: feature ainda tem user stories pendentes
- `pending`: feature pronta para auditoria, ainda sem rodada aprovada
- `hold`: ultima auditoria reprovou o gate
- `approved`: ultima auditoria aprovou o gate com veredito `go`

## Regras de Rastreabilidade

- auditoria formal exige commit SHA e arvore limpa
- se a arvore estiver suja, a auditoria deve ser marcada como `provisional`
- `provisional` pode apontar riscos e follow-ups, mas nao fecha feature
- cada rodada precisa apontar para a anterior quando houver continuidade ou supersedencia
- cada entrada da secao `Resolucoes de Follow-ups` do `AUDIT-LOG.md` deve
  registrar o `Audit ID de Origem` da rodada `hold` que gerou o item
- nova rodada apos `hold` so pode iniciar quando todos os follow-ups
  `same-feature` **bloqueantes** da rodada anterior estiverem `done` ou
  `cancelled`; follow-ups nao
  bloqueantes abertas nao impedem a nova rodada mas devem aparecer no relatorio
  como contexto
- o relatorio de cada rodada apos `hold` deve incluir uma secao de prestacao de
  contas dos follow-ups da rodada anterior, declarando explicitamente o status
  final de cada follow-up gerado pelo hold; declarar "follow-ups resolvidos"
  sem listar e verificar cada item individualmente e nao conformidade de
  auditoria

## Follow-ups

- correcao local e contida deve abrir `same-feature` na mesma feature
- `same-feature` pode reutilizar uma US existente ou abrir nova
  `user-stories/US-*/` com `README.md` e `TASK-*.md`
- registros legados `issue-local` no `AUDIT-LOG.md` devem ser lidos como
  adaptador de `same-feature`
- todo follow-up `same-feature` deve seguir `GOV-USER-STORY.md`; quando a user
  story usar `task_instruction_mode: required` e uma task envolver codigo com
  cobertura automatizavel, o plano TDD da US deve descer para a task via
  `tdd_aplicavel` e `testes_red`, conforme `SPEC-TASK-INSTRUCTIONS.md`
- refatoracao estrutural ou correcao sistemica deve abrir `new-intake` com `intake_kind: audit-remediation`
- um follow-up e estrutural/sistemico quando:
  - envolve arquitetura ou contratos amplos
  - atravessa multiplos modulos ou camadas
  - exige rediscutir escopo, riscos, rollout ou dependencias
  - nao cabe como ajuste pontual dentro da feature auditada
- o `AUDIT-LOG.md` deve registrar quais follow-ups nasceram de cada `hold` e
  qual foi o destino de cada um

## Modelo Operacional Recomendado

- recomendacao: usar IA auditora independente da IA implementadora
- regra operacional para OpenClaw multi-agente: usar o modelo configurado em
  `OPENCLAW_AUDITOR_MODEL`, acessado via OpenRouter, como agente senior de
  gate; o default esperado e
  `openrouter/anthropic/claude-opus-4.6`
- intake e PRD permanecem como unicos gates humanos normais; auditoria e
  remediacao pos-hold nao dependem de aprovacao humana passo a passo
- fallback aceitavel: mesma IA em sessao separada, lendo apenas artefatos, diff e evidencias
- qualquer auditoria deve julgar aderencia, risco, cobertura de testes, saude estrutural do codigo e rastreabilidade da remediacao
- todo gate de auditoria deve conferir alinhamento explicito ao PRD e a
  feature auditada antes de aprovar ou abrir follow-up
- override humano apos o PRD so existe como excecao explicita para conflito
  reproduzivel de parametros/evidencias, cancelamento declarado ou contexto
  externo novo

## Procedimento Pós-Hold

Após qualquer auditoria com veredito `hold`, o `agente senior` deve executar o
seguinte algoritmo antes de retomar o desenvolvimento. O PM so pode
sobrescrever o destino de um follow-up de forma explicita e justificada:

```
Para cada follow-up bloqueante no relatório:
  │
  ├─ followup_destination = same-feature
  │     └─→ criar ou reabrir User Story na feature atual
  │          → preferir reutilizar a US existente quando o gap ainda
  │            pertencer ao mesmo escopo
  │          → criar nova pasta `US-*/` apenas quando o ajuste nao couber
  │            numa US atual sem drift
  │          → ciclo normal: SESSION-IMPLEMENTAR-TASK ou SESSION-IMPLEMENTAR-US -> SESSION-REVISAR-US
  │
  ├─ followup_destination = new-intake
  │     └─→ criar INTAKE-<PROJETO>-<SLUG>.md
  │          → intake_kind: audit-remediation
  │          → source_mode: audit-derived
  │          → ciclo completo independente:
  │            SESSION-CLARIFICAR-INTAKE → SESSION-CRIAR-PRD
  │            → SESSION-DECOMPOR-PRD-EM-FEATURES → execução e
  │              auditoria própria do novo escopo
  │
  └─ followup_destination = cancelled
        └─→ registrar justificativa no AUDIT-LOG
             → nenhum artefato gerado

Em todos os casos:
  → atualizar AUDIT-LOG com destino e referência de cada follow-up
  → gate da feature permanece hold ate nova rodada com veredito go
```

Um relatório pode conter follow-ups com destinos mistos. O SESSION canônico
para executar este procedimento é `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`.

O ciclo da feature so pode ser retomado — e nova rodada de auditoria
solicitada — apos todos os follow-ups **bloqueantes** terem sido enderecados
(`same-feature`, `new-intake` ou cancelamento justificado). Follow-ups nao
bloqueantes podem ser tratados em paralelo sem travar a feature.

## Artefatos Vinculados

- prompt de auditoria: `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- governanca feature-first: `PROJETOS/COMUM/GOV-AUDITORIA-FEATURE.md`
- session de auditoria de feature: `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- session de remediação pós-hold: `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`
- template de relatório canônico:
  `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md`
- template de relatório legado issue-first:
  `PROJETOS/COMUM/LEGADO/TEMPLATE-AUDITORIA-RELATORIO.md`
- template de log: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`
- spec de thresholds estruturais: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
