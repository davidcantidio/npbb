---
doc_id: "GOV-AUDITORIA.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
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
- follow-ups classificados por destino e transformados em `issue-local`, `new-intake` ou `cancelled` (com justificativa) quando houver `hold`

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
- ausencia de docstring isolada nao bloqueia por si so; so bloqueia quando combinada com alta complexidade, compartilhamento relevante ou dificuldade real de manutencao/auditoria
- opiniao sem evidencia nao e achado; cada nao conformidade precisa apontar trecho, modulo, diff, teste ou comportamento observavel

## Status do Artefato de Auditoria

- `planned`: rodada ainda nao executada
- `active`: auditoria em andamento
- `done`: auditoria concluida
- `cancelled`: rodada abandonada com justificativa
- `provisional`: rodada sem commit SHA valido ou com worktree sujo; nunca aprova gate

## Gate de Auditoria da Fase

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

## Follow-ups

- correcao local e contida pode abrir `issue-local` na mesma fase
- refatoracao estrutural ou correcao sistemica deve abrir `new-intake` com `intake_kind: audit-remediation`
- um follow-up e estrutural/sistemico quando:
  - envolve arquitetura ou contratos amplos
  - atravessa multiplos modulos ou camadas
  - exige rediscutir escopo, riscos, rollout ou dependencias
  - nao cabe como ajuste pontual dentro da fase auditada
- o `AUDIT-LOG.md` deve registrar quais follow-ups nasceram de cada `hold` e qual foi o destino de cada um

## Procedimento Pos-Hold

Apos qualquer auditoria com veredito `hold`, o PM deve classificar e encaminhar
os follow-ups bloqueantes antes de retomar o desenvolvimento normal.

```
Para cada follow-up bloqueante no relatorio:
  issue-local -> criar ISSUE-*.md na fase atual e seguir o ciclo normal
  new-intake  -> criar INTAKE-<PROJETO>-<SLUG>.md com intake_kind audit-remediation
  cancelled   -> registrar a justificativa no AUDIT-LOG sem gerar artefato novo

Em todos os casos:
  atualizar AUDIT-LOG com o destino final e a referencia correspondente
  manter o gate da fase em hold ate existir nova rodada com veredito go
```

Um mesmo relatorio pode conter destinos mistos. O fluxo interativo canonico
para esse roteamento e `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`.

## Modelo Operacional Recomendado

- recomendacao: usar IA auditora independente da IA implementadora
- fallback aceitavel: mesma IA em sessao separada, lendo apenas artefatos, diff e evidencias
- qualquer auditoria deve julgar aderencia, risco, cobertura de testes, saude estrutural do codigo e rastreabilidade da remediacao

## Artefatos Vinculados

- prompt de auditoria: `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- session de auditoria: `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- session de remediacao pos-hold: `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`
- template de relatorio: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- template de log: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`
- spec de thresholds estruturais: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
