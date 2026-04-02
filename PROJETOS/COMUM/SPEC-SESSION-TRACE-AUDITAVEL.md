---
doc_id: "SPEC-SESSION-TRACE-AUDITAVEL.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SPEC - Session trace auditavel

## Objetivo

Garantir que traces de sessao sejam uteis para auditoria e tuning do framework,
sem perda silenciosa de payloads nem "limpeza" enganosa de lacunas do log.

## Contrato atual

- `session-capture.v1` e `session-capture.v2` continuam legiveis
- `session-trace.v2` e o formato de saida canonico
- `session-trace.v1` continua valido para compatibilidade de leitura

## Regras obrigatorias do v2

- todo campo truncado em `events` deve carregar:
  - `*_truncated: true`
  - `*_checksum`
  - `*_artifact`
- o payload completo truncado deve ser externalizado para artefato sob
  `logs/codex-session-artifacts/<session_id>/`
- ausencia de conteudo observavel deve aparecer como
  `*_absence_reason: not_provided`, nao como string vazia silenciosa
- o JSON do trace continua canonico, com chaves ordenadas

## O que registrar

- prompts do utilizador
- saidas observaveis do assistente
- tool calls e tool results
- artefatos gerados
- validacoes
- metadados Git

## O que nao registrar como alvo

- chain-of-thought privado
- payloads secretos ou credenciais em claro

## Ferramentas e ficheiros

| Superficie | Papel |
|---|---|
| `scripts/session_logs/core.py` | normalizacao, externalizacao e validacao |
| `scripts/session_logs/build_trace.py` | gera o trace canonico |
| `scripts/session_logs/collect_traces.py` | coleta em lote |
| `scripts/session_logs/session_capture.schema.json` | schema de entrada |
| `scripts/session_logs/session_trace.schema.json` | schema de saida |
| `scripts/session_logs/README.md` | operacao e exemplos |

## Relacoes

| Documento | Papel |
|---|---|
| `GOV-FRAMEWORK-MASTER.md` | indexa esta spec |
| `SESSION-MAPA.md` | aponta a superficie de observabilidade |
| `FEATURE-8` do OPENCLAW-FRAMEWORK-V4 | backlog da remediacao telemetrica |
