---
doc_id: "ISSUE-F4-01-002-EXIBICAO-E-DOWNLOAD-QR.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.2 - Estrutura de URL do QR"
  - "PRD 12 - Fase 4 — Operador e Métricas"
  - "PRD 13.1 - Modelo e Ativações"
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

## Instructions por Task

### T1
- objetivo: criar o componente visual do QR da ativação
- precondicoes: `qr_code_url` já disponível na API de ativações
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Implementar componente para renderizar a imagem/URL do QR
  2. Tratar ausência temporária de `qr_code_url`
  3. Manter layout compatível com a listagem/detalhe do operador
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: QR pode ser visualizado com fallback coerente
- testes_ou_validacoes_obrigatorias:
  - teste de componente
- stop_conditions:
  - parar se a API não expuser `qr_code_url`

### T2
- objetivo: disponibilizar download do QR em formato utilizável
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Implementar CTA de download associado ao QR
  2. Garantir nome de arquivo e tipo coerentes com o artefato real
  3. Não quebrar quando o QR ainda não existir
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operador consegue baixar o QR sem usar a API manualmente
- testes_ou_validacoes_obrigatorias:
  - teste de interação
- stop_conditions:
  - nenhuma

### T3
- objetivo: integrar exibição e download à página de ativações
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Inserir o componente na listagem ou detalhe escolhido
  2. Reaproveitar contexto da ativação já carregado pela página
  3. Garantir consistência com estados de loading e erro
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: QR e download aparecem no fluxo normal do operador
- testes_ou_validacoes_obrigatorias:
  - teste integrado
- stop_conditions:
  - nenhuma

### T4
- objetivo: validar visualização e download do QR com E2E
- precondicoes: T1, T2 e T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/`
- passos_atomicos:
  1. Testar ativação com QR disponível
  2. Testar download acionado pelo operador
  3. Testar placeholder/loading para ativação sem QR
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: comportamento do QR fica coberto por regressão
- testes_ou_validacoes_obrigatorias:
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

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
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
