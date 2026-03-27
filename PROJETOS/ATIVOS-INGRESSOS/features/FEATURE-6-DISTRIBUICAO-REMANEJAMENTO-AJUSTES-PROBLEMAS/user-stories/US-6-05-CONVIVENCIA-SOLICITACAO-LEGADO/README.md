---
doc_id: "US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-6"
decision_refs: []
---

# US-6-05 - Convivencia com SolicitacaoIngresso legado

## User Story

**Como** responsavel pela migracao gradual do modulo de ingressos,
**quero** convivencia controlada entre o fluxo novo (FEATURE-6) e `SolicitacaoIngresso` legado,
**para** operacao continuar ate o corte documentado no PRD 4.0 / 2.6 sem regressao silenciosa.

## Feature de Origem

- **Feature**: FEATURE-6 (Distribuicao, remanejamento, ajustes e problemas operacionais)
- **Comportamento coberto**: documentacao e testes de compatibilidade com solicitacoes agregadas legadas durante a transicao.

## Contexto Tecnico

- PRD baseline e coexistencia com cotas e solicitacoes agregadas; endpoints e telas legados permanecem ate rollout.
- Esta US fecha o criterio de aceite da feature sobre convivencia: documentar limites, mapeamento de estados e cenarios de teste.
- Execucao apos US-6-01 a US-6-04 para validar o conjunto contra o legado.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel no manifesto
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** o escopo de convivencia definido no PRD sec. 4.0 e restricoes de sec. 2.6,
  **when** a documentacao de convivencia e publicada (ADR, secao em doc de rollout ou README tecnico referenciado pelo repo),
  **then** fica explicito quais operacoes usam fluxo novo versus legado e quais dados nao se misturam sem migracao.
- **Given** cenarios criticos (distribuicao, remanejamento, ajuste, problema) com dados legados presentes,
  **when** a suite de testes acordada executa,
  **then** nao ha corromper dados legados nem violar invariantes documentadas.
- **Given** um operador usando apenas fluxo legado durante a janela de transicao,
  **when** o sistema processa solicitacoes existentes,
  **then** o comportamento permanece dentro do contrato legado documentado ate migracao.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

| Task | Documento |
|------|-----------|
| T1 | [TASK-1.md](TASK-1.md) — esqueleto do ADR de convivencia FEATURE-6 x `SolicitacaoIngresso` |
| T2 | [TASK-2.md](TASK-2.md) — matriz novo/legado, limites de dados e mapeamento de estados |
| T3 | [TASK-3.md](TASK-3.md) — testes automatizados com dados legados (cenarios FEATURE-6) |
| T4 | [TASK-4.md](TASK-4.md) — contrato fluxo exclusivamente legado e secao «Como validar» no ADR |

## Arquivos Reais Envolvidos

- Modelos e routers legados de `SolicitacaoIngresso` (caminhos reais a mapear na execucao)
- Documentacao de rollout / migracao sob `PROJETOS/ATIVOS-INGRESSOS/` ou `docs/` conforme convencao do time
- Testes de integracao ou regressao

## Artefato Minimo

- Documento de convivencia referenciado no repositorio mais testes que cobrem cenarios PRD 4.0 / 2.6.

## Handoff para Revisao Pos-User Story

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [FEATURE-6](../../FEATURE-6.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: [US-6-01](../US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md), [US-6-02](../US-6-02-REMANEJAMENTO-AUDITAVEL/README.md), [US-6-03](../US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO/README.md), [US-6-04](../US-6-04-PROBLEMAS-OPERACIONAIS/README.md) — todas `done` antes da validacao final de convivencia
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
