---
doc_id: "ISSUE-F1-03-001-SERVICO-GERACAO-QR.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-03-001 - Serviço de geração de QR

## User Story

Como sistema, quero gerar um QR-code único por ativação que aponta para a URL da landing, para que o visitante possa escanear e acessar o formulário.

## Contexto Tecnico

URL do QR: `/eventos/:evento_id/ativacoes/:ativacao_id` ou `/e/:evento_id/a/:ativacao_id` para URLs mais curtas. Lib `qrcode` em Python ou similar. O QR pode ser gerado como imagem (PNG/SVG) ou URL armazenada. Conforme PRD seção 5.2 e 7.1.

## Plano TDD

- Red: teste que valida geração de QR para URL válida
- Green: implementar serviço
- Refactor: extrair configuração de base URL

## Criterios de Aceitacao

- Given evento_id e ativacao_id, When gero QR, Then imagem ou URL retornada
- Given ativação criada, When QR gerado, Then qr_code_url populado na ativação
- Given URL base configurável, When gero QR, Then URL completa correta

## Definition of Done da Issue

- [ ] Serviço gera QR para URL da landing
- [ ] qr_code_url populado ao criar/atualizar ativação
- [ ] Teste unitário do serviço passa

## Tarefas Decupadas

- [ ] T1: Implementar serviço de geração de QR (lib qrcode ou segno)
- [ ] T2: Integrar geração no fluxo de criação/atualização de ativação
- [ ] T3: Adicionar teste unitário

## Arquivos Reais Envolvidos

- `backend/app/services/`
- `backend/app/models/models.py`
- `backend/tests/`

## Artifact Minimo

- `backend/app/services/qr_service.py` ou similar
- Teste em `backend/tests/`

## Dependencias

- [EPIC-F1-01](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
