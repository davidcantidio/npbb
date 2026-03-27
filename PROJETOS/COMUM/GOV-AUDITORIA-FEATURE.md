---
doc_id: "GOV-AUDITORIA-FEATURE.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
---

# GOV-AUDITORIA-FEATURE

## Objetivo

Fechar o contrato especifico da etapa `Auditoria de Feature` no modelo v3.0
`feature -> user story -> task`, sem reabrir a semantica operacional
`phase/issue`.

## Precedencia Normativa

- `GOV-AUDITORIA.md` define vereditos, severidades, regras gerais de
  julgamento, rastreabilidade e remediacao pos-`hold`
- este documento define o escopo ativo da auditoria por `Feature`, a forma do
  relatorio canonico e as regras de compatibilidade legada da superficie
  feature-first
- `SPEC-ANTI-MONOLITO.md` continua sendo a fonte unica de thresholds para
  `monolithic-file` e `monolithic-function`

## Contrato Canonico

- a auditoria formal ativa do v3.0 acontece por `Feature`
- o relatorio canonico deve seguir
  `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md`
- a sessao interativa canonica e
  `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- o prompt canonico de apoio e `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- o log canonico de rodadas e follow-ups continua em `AUDIT-LOG.md`, usando a
  coluna `Feature` como semantica primaria
- o gate resultante da rodada deve ser registrado como `gate_da_feature`
- follow-up local canonico desta etapa e `same-feature`

## Compatibilidade Legada

- `PROJETOS/COMUM/LEGADO/TEMPLATE-AUDITORIA-RELATORIO.md` permanece apenas
  como referencia historica para `PROJETOS/COMUM/LEGADO/GOV-ISSUE-FIRST.md`;
  nao e template ativo do v3.0
- registros antigos `issue-local` no `AUDIT-LOG.md` ou em relatorios
  historicos devem ser lidos como adaptador de `same-feature`
- se o `AUDIT-LOG.md` ainda usar a coluna legada `Fase`, trate-a como alias de
  compatibilidade para `Feature` e grave nela o `FEATURE_ID` sem reintroduzir
  semantica de fase no restante da instrucao
- referencias historicas `ISSUE-*` podem ser lidas para prestacao de contas,
  mas nao devem ser emitidas como artefato novo da auditoria feature-first

## Artefatos Vinculados

- governanca geral compartilhada: `PROJETOS/COMUM/GOV-AUDITORIA.md`
- template canonico do relatorio: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md`
- session canonica de auditoria: `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md`
- session canonica de remediacao pos-hold:
  `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md`
- template do log: `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`
- compatibilidade legada issue-first:
  `PROJETOS/COMUM/LEGADO/TEMPLATE-AUDITORIA-RELATORIO.md`
