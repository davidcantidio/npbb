---
doc_id: "F2-AFL-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F2 Criação Rápida de Evento — Epics

## Objetivo da Fase

Permitir que o operador crie um evento diretamente durante o fluxo de mapeamento de leads, sem perder o contexto do mapeamento em andamento, eliminando a necessidade de navegar para outra tela.

## Gate de Saída da Fase

- [ ] Opção "Criar evento rapidamente" visível no dropdown de eventos quando nenhum resultado é encontrado
- [ ] Modal com campos mínimos (`nome`, `data_inicio_prevista`, `cidade`, `estado`, `diretoria_id`) funcional
- [ ] Após criação, o evento recém-criado é automaticamente selecionado no dropdown
- [ ] Evento criado aparece na listagem completa em `/eventos`
- [ ] Erro de criação exibe mensagem sem perder estado do mapeamento
- [ ] CI verde sem regressão

## Epics da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---------|------|----------|--------|-----------|
| `EPIC-F2-01` | Modal de Criação Rápida de Evento | Implementar modal de criação inline de evento no fluxo de mapeamento de leads. | 🔲 | [EPIC-F2-01-MODAL-CRIACAO-RAPIDA-EVENTO.md](./EPIC-F2-01-MODAL-CRIACAO-RAPIDA-EVENTO.md) |

## Escopo desta Entrega

**Incluso:**
- Componente `QuickCreateEventoModal` reutilizável (PRD 3.4)
- Integração com dropdown de eventos no fluxo de mapeamento
- Chamada a `POST /evento/` (endpoint já existente) e reload de referências
- Tratamento de erro com preservação de estado do mapeamento

**Fora de escopo:**
- Alterações no endpoint `POST /evento/` (já funcional)
- Edição completa de evento (feito via `/eventos/:id/editar`)
- Criação rápida de evento em outros contextos além do mapeamento
