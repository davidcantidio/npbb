---
doc_id: "GOV-AUDITORIA.md"
version: "2.4"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
---

# GOV-AUDITORIA

## Objetivo

Formalizar a etapa `Tasks -> Auditorias` como gate final de governanca de cada fase, com avaliacao funcional e de saude estrutural do codigo.

## Regra Canonica

- a auditoria formal padrao acontece por fase
- a auditoria nao substitui desenvolvimento; ela valida o que foi entregue
- a fase so pode ir para `feito/` apos auditoria com veredito `go`
- cada rodada de auditoria deve produzir relatorio em `auditorias/` e entrada em `AUDIT-LOG.md`
- a auditoria deve avaliar aderencia funcional, riscos, cobertura de testes e saude estrutural do codigo
- thresholds de `monolithic-file` e `monolithic-function` vivem exclusivamente em `SPEC-ANTI-MONOLITO.md`
- `GOV-AUDITORIA.md`, prompts e templates de auditoria nao devem duplicar thresholds estruturais; qualquer mudanca futura de `warn/block` deve ocorrer apenas em `SPEC-ANTI-MONOLITO.md`

## Inputs Obrigatorios da Auditoria

- `INTAKE-*.md` aplicavel ao escopo auditado
- `PRD-*.md`
- manifesto da fase
- epicos e issues da fase
- `AUDIT-LOG.md`
- ultimo relatorio da fase, quando existir
- commit base auditado
- diffs e testes relevantes

## Outputs Obrigatorios

- `auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
- nova entrada em `AUDIT-LOG.md`
- atualizacao do gate de auditoria no manifesto da fase
- follow-ups classificados por destino e transformados em `issue-local`
  (`ISSUE-*/` ou `ISSUE-*.md`), `new-intake` ou `cancelled` (com justificativa)
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

- `go`: aprovou o gate; fase pode fechar
- `hold`: gate reprovado; manter fase `active` e abrir/remapear follow-ups
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

## Gate de Auditoria da Fase

> O template de checklist de transição para o manifesto da fase vive em `GOV-ISSUE-FIRST.md`.

Estados operacionais do gate dentro do manifesto da fase:

- `not_ready`: fase ainda tem epicos ou issues pendentes
- `pending`: fase pronta para auditoria, ainda sem rodada aprovada
- `hold`: ultima auditoria reprovou o gate
- `approved`: ultima auditoria aprovou o gate com veredito `go`

## Regras de Rastreabilidade

- auditoria formal exige commit SHA e arvore limpa
- se a arvore estiver suja, a auditoria deve ser marcada como `provisional`
- `provisional` pode apontar riscos e follow-ups, mas nao fecha fase
- cada rodada precisa apontar para a anterior quando houver continuidade ou supersedencia
- cada entrada da secao `Resolucoes de Follow-ups` do `AUDIT-LOG.md` deve
  registrar o `Audit ID de Origem` da rodada `hold` que gerou o item
- nova rodada apos `hold` so pode iniciar quando todas as issues de follow-ups
  **bloqueantes** da rodada anterior estiverem `done` ou `cancelled`; issues nao
  bloqueantes abertas nao impedem a nova rodada mas devem aparecer no relatorio
  como contexto
- o relatorio de cada rodada apos `hold` deve incluir uma secao de prestacao de
  contas dos follow-ups da rodada anterior, declarando explicitamente o status
  final de cada follow-up gerado pelo hold; declarar "follow-ups resolvidos"
  sem listar e verificar cada item individualmente e nao conformidade de
  auditoria

## Follow-ups

- correcao local e contida pode abrir `issue-local` na mesma fase
- `issue-local` pode ser uma pasta `ISSUE-*/` com `README.md` + `TASK-*.md` ou,
  por compatibilidade, um arquivo unico `ISSUE-*.md`
- refatoracao estrutural ou correcao sistemica deve abrir `new-intake` com `intake_kind: audit-remediation`
- um follow-up e estrutural/sistemico quando:
  - envolve arquitetura ou contratos amplos
  - atravessa multiplos modulos ou camadas
  - exige rediscutir escopo, riscos, rollout ou dependencias
  - nao cabe como ajuste pontual dentro da fase auditada
- o `AUDIT-LOG.md` deve registrar quais follow-ups nasceram de cada `hold` e qual foi o destino de cada um

## Modelo Operacional Recomendado

- recomendacao: usar IA auditora independente da IA implementadora
- fallback aceitavel: mesma IA em sessao separada, lendo apenas artefatos, diff e evidencias
- qualquer auditoria deve julgar aderencia, risco, cobertura de testes, saude estrutural do codigo e rastreabilidade da remediacao

## Procedimento Pós-Hold

Após qualquer auditoria com veredito `hold`, o PM deve executar o seguinte
algoritmo antes de retomar o desenvolvimento:

```
Para cada follow-up bloqueante no relatório:
  │
  ├─ followup_destination = issue-local
  │     └─→ criar recurso de issue local na fase atual
  │          → preferir pasta `ISSUE-*/` com `README.md` + `TASK-*.md`
  │          → usar `ISSUE-*.md` apenas para follow-up simples
  │          → ciclo normal: SESSION-IMPLEMENTAR-ISSUE
  │
  ├─ followup_destination = new-intake
  │     └─→ criar INTAKE-<PROJETO>-<SLUG>.md
  │          → intake_kind: audit-remediation
  │          → source_mode: audit-derived
  │          → ciclo completo independente:
  │            SESSION-CRIAR-PRD → SESSION-PLANEJAR-PROJETO
  │            → execução e auditoria própria do novo escopo
  │
  └─ followup_destination = cancelled
        └─→ registrar justificativa no AUDIT-LOG
             → nenhum artefato gerado

Em todos os casos:
  → atualizar AUDIT-LOG com destino e referência de cada follow-up
  → gate da fase permanece hold até nova rodada com veredito go
```

Um relatório pode conter follow-ups com destinos mistos. O SESSION canônico
para executar este procedimento é `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`.

O ciclo da fase só pode ser retomado — e nova rodada de auditoria solicitada —
após todos os follow-ups **bloqueantes** terem sido endereçados (issue criada,
intake criado ou cancelamento justificado). Follow-ups não bloqueantes podem
ser tratados em paralelo sem travar a fase.

## Artefatos Vinculados

- prompt de auditoria: `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- session de auditoria: `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- session de remediação pós-hold: `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`
- template de relatório: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- template de log: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`
- spec de thresholds estruturais: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
