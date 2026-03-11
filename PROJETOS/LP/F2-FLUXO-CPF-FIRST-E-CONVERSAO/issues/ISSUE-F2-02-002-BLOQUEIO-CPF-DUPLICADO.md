---
doc_id: "ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-02-002 - Bloqueio CPF duplicado e integração frontend

## User Story

Como sistema, quero bloquear o cadastro do mesmo CPF em ativação de conversão única quando já houver conversão, e exibir mensagem clara ao visitante.

## Contexto Tecnico

Em ativação com conversao_unica = true, verificar se (ativacao_id, cpf) já existe em conversao_ativacao. Se sim, retornar bloqueado_cpf_duplicado = true e não registrar nova conversão. Frontend exibe mensagem clara. Conforme PRD seções 4 e 8.2.

## Plano TDD

- Red: testes para bloqueio e response
- Green: implementar verificação e tratamento no frontend
- Refactor: extrair mensagens para i18n se aplicável

## Criterios de Aceitacao

- Given ativação com conversao_unica, When POST com CPF já convertido, Then bloqueado_cpf_duplicado = true
- Given bloqueado_cpf_duplicado = true, When frontend recebe, Then mensagem clara exibida
- Given ativação com conversao_multipla, When POST com mesmo CPF, Then nova conversão registrada (não bloqueia)

## Definition of Done da Issue

- [ ] Backend verifica (ativacao_id, cpf) em ativação única antes de registrar
- [ ] Response bloqueado_cpf_duplicado quando bloqueado
- [ ] Frontend exibe mensagem clara
- [ ] Testes backend e frontend

## Tarefas Decupadas

- [ ] T1: Implementar verificação de bloqueio no backend
- [ ] T2: Tratar resposta no frontend e exibir mensagem
- [ ] T3: Adicionar testes

## Arquivos Reais Envolvidos

- `backend/app/api/` ou `backend/app/services/`
- `frontend/src/`
- `backend/tests/`

## Artifact Minimo

- Lógica de bloqueio no backend
- Tratamento no frontend
- Testes

## Dependencias

- [ISSUE-F2-02-001](./ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md)
- [EPIC-F2-01](../EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
