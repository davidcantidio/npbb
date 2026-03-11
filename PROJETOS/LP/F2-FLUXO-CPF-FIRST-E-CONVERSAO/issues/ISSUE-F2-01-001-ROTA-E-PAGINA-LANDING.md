---
doc_id: "ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-001 - Rota e página landing com contexto de ativação

## User Story

Como visitante, quero acessar a landing via URL `/eventos/:evento_id/ativacoes/:ativacao_id` para preencher o formulário de lead no contexto correto da ativação.

## Contexto Tecnico

Nova rota no frontend que chama GET /eventos/:evento_id/ativacoes/:ativacao_id/landing e renderiza a página com contexto de evento e ativação. Conforme PRD seção 5.2 e 7.2.

## Plano TDD

- Red: teste que valida rota e carregamento de payload
- Green: implementar rota e página
- Refactor: extrair hooks ou componentes reutilizáveis

## Criterios de Aceitacao

- Given URL /eventos/1/ativacoes/1, When carrego página, Then payload da landing é buscado
- Given payload retornado, When renderizo, Then contexto de evento e ativação disponível
- Given evento ou ativação inexistentes, When carrego, Then tratamento de erro (404)
- Given query param ?token=, When carrego, Then token passado para API (validação na F3)

## Definition of Done da Issue

- [ ] Rota `/eventos/:evento_id/ativacoes/:ativacao_id` criada
- [ ] Página carrega payload do endpoint de landing
- [ ] Contexto de evento e ativação disponível para formulário
- [ ] Tratamento de 404

## Tarefas Decupadas

- [ ] T1: Criar rota e componente de página
- [ ] T2: Integrar chamada ao endpoint de landing
- [ ] T3: Tratar erros (404, loading)

## Arquivos Reais Envolvidos

- `frontend/src/` (rotas, páginas)
- `frontend/src/api/` ou similar

## Artifact Minimo

- Página de landing em `frontend/src/`
- Rota configurada

## Dependencias

- [EPIC-F2-01](../EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [F1](../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
