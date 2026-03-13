---
doc_id: "EPIC-F2-02-REGISTRO-CONVERSAO-E-BLOQUEIO.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
---

# EPIC-F2-02 - Registro de Conversão e Bloqueio

## Objetivo

Estender POST /leads para receber ativacao_id, registrar conversão em conversao_ativacao, e bloquear CPF duplicado em ativação de conversão única. Conforme PRD seções 4, 7.1 e 8.2.

## Resultado de Negocio Mensuravel

Cada submit com CPF válido registra conversão na ativação correspondente; em ativação única, o mesmo CPF não pode converter duas vezes.

## Contexto Arquitetural

- POST /leads existente; estender request com ativacao_id
- Response estendido: conversao_registrada, bloqueado_cpf_duplicado
- Índice (ativacao_id, cpf) para lookup rápido de bloqueio

## Definition of Done do Epico

- [x] POST /leads aceita ativacao_id quando acesso via ativação
- [x] Conversão registrada em conversao_ativacao
- [x] Ativação única: bloqueio retorna bloqueado_cpf_duplicado = true
- [x] Frontend exibe mensagem clara quando bloqueado
- [x] Testes backend e Playwright cobrindo cenários

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Extensão POST /leads com ativacao_id e registro de conversão | Backend: receber ativacao_id, registrar conversão | 3 | done | [ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md](./issues/ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md) |
| ISSUE-F2-02-002 | Bloqueio CPF duplicado e integração frontend | Bloqueio em ativação única; frontend trata resposta | 2 | done | [ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md](./issues/ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md) |

## Artifact Minimo do Epico

- `backend/app/` (endpoints, serviços)
- `frontend/src/` (tratamento de resposta)
- `backend/tests/`, `frontend/e2e/`

## Dependencias

- [F1](../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [EPIC-F2-01](./EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F2_LP_EPICS.md)
