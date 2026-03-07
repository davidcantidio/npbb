---
doc_id: "SPRINT-LIMITS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-07"
---

# SPRINT-LIMITS

## Limites Canonicos

```yaml
max_items_por_sprint: 12
max_issues_por_sprint: 5
max_story_points_por_sprint: 13
max_tamanho_por_task: "1 dia util ou 3 story points"
max_tamanho_por_issue: "5 story points"
max_tarefas_por_issue: 8
max_itens_criticos_paralelos: "2 por escritorio"
```

## Contrato SPRINT_OVERRIDE

```yaml
SPRINT_OVERRIDE:
  override_key: "override-2026-03-03-001"
  coalescing_key: "phase-fx-capacity"
  rollback_token: "rollback-token-placeholder"
  rollback_snapshot_ref: "snapshot://phase-fx/before-override"
```

## Enforcement

- violacao de qualquer limite gera status `BLOCKED_LIMIT`
- ao bloquear, o sistema deve abrir o evento `SPRINT_LIMIT_ALERT`
- nenhum override pode ocorrer sem preenchimento completo do contrato `SPRINT_OVERRIDE`
- override sem plano de rollback deve ser rejeitado

## Regras Operacionais

- item acima do tamanho maximo deve ser quebrado antes de entrar na sprint
- issue acima do tamanho maximo deve ser quebrada antes de entrar na sprint
- mais de dois itens criticos paralelos por escritorio exige override explicito
- items bloqueados por limite nao podem ser marcados como `active`
- consolidacao de sprint nao substitui governanca por fase, epico e issue
- sprint deve apontar para arquivos `issues/ISSUE-*.md` como fonte canonica do escopo
- `SPRINT-*.md` nao deve duplicar criterios de aceitacao, DoD ou tarefas da issue
- fase concluida nao permanece entre fases ativas do projeto; apos fechar o gate, deve ser movida para `<projeto>/feito/`

## Manifesto Canonico de Sprint

Todo `sprints/SPRINT-*.md` deve conter apenas:

- objetivo da sprint
- capacidade declarada em issues e story points
- tabela `Issue ID | Nome | SP | Status | Documento`
- riscos, bloqueios e necessidade de `SPRINT_OVERRIDE` quando houver
- decisao de encerramento da sprint com base em fatos, nunca datas inventadas
