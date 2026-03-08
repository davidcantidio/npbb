---
doc_id: "SPRINT-LIMITS.md"
version: "1.2"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
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

## Enforcement

- violacao de limite gera estado operacional `BLOCKED_LIMIT`
- `BLOCKED_LIMIT` nao substitui o status documental canonico do item
- nenhum item bloqueado por limite pode ser marcado como `active` antes de decomposicao ou override valido
- consolidacao de sprint nao substitui governanca por fase, epico e issue
- fase concluida nao permanece entre fases ativas; apos fechar o gate, deve ser movida para `<projeto>/feito/`

## Regras Operacionais

- item acima do tamanho maximo deve ser quebrado antes de entrar na sprint
- issue acima do tamanho maximo deve ser quebrada antes de entrar na sprint
- task acima do tamanho maximo deve ser quebrada antes de receber `instructions`
- `instructions` obrigatorias devem permanecer atomicas, sequenciais e sem branching pesado
- sprint deve apontar para `issues/ISSUE-*.md` como fonte canonica do escopo
- `SPRINT-*.md` nao deve duplicar criterios, DoD ou tarefas da issue

## Manifesto Canonico de Sprint

Todo `sprints/SPRINT-*.md` deve conter apenas:

- objetivo da sprint
- capacidade declarada em issues e story points
- tabela `Issue ID | Nome | SP | Status | Documento`
- riscos, bloqueios e necessidade de override quando houver
- decisao de encerramento baseada em fatos
