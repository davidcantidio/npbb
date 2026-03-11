---
doc_id: "ISSUE-F4-01-002-EXIBICAO-E-DOWNLOAD-QR.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F4-01-002 - Exibição e download de QR

## User Story

Como operador, quero visualizar o QR da ativação na interface e baixá-lo para impressão ou compartilhamento.

## Contexto Tecnico

Campo qr_code_url da ativação contém URL ou path para imagem do QR. Exibir na listagem ou detalhe da ativação. Botão para download (PNG/SVG). Conforme PRD seção 12 (Fase 4).

## Plano TDD

- Red: testes E2E para exibição e download
- Green: implementar componente
- Refactor: extrair para componente reutilizável

## Criterios de Aceitacao

- Given ativação com qr_code_url, When visualizo, Then imagem do QR exibida
- Given QR exibido, When clico em download, Then arquivo baixado
- Given ativação sem QR (criação recente), When visualizo, Then placeholder ou loading

## Definition of Done da Issue

- [ ] QR exibido na interface (listagem ou detalhe)
- [ ] Botão de download funcional
- [ ] Tratamento de ativação sem QR
- [ ] Testes E2E

## Tarefas Decupadas

- [ ] T1: Componente de exibição do QR
- [ ] T2: Botão de download
- [ ] T3: Integrar na página de ativações
- [ ] T4: Testes E2E

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Componente QR
- Integração na página
- Testes

## Dependencias

- [ISSUE-F4-01-001](./ISSUE-F4-01-001-LISTAGEM-E-FORMULARIO-ATIVACOES.md)
- [EPIC-F1-03](../../F1-FUNDACAO-MODELO-BACKEND/EPIC-F1-03-QR-E-ENDPOINT-LANDING.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
