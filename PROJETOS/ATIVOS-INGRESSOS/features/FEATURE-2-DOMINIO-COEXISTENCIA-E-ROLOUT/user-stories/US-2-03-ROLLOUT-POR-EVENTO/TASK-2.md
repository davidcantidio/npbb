---
doc_id: "TASK-2.md"
user_story_id: "US-2-03-ROLLOUT-POR-EVENTO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - T1
parallel_safe: false
write_scope:
  - "backend/app/services/event_rollout_gate.py"
  - "backend/tests/"
tdd_aplicavel: true
---

# TASK-2 - Servico canonico de resolucao do modo por evento

## objetivo

Centralizar a leitura do gate em um unico modulo (por exemplo
`event_rollout_gate.py` ou nome alinhado ao repo) exportando API estavel para
os routers: dado `Session` + `evento_id`, retornar se o fluxo deve ser
**novo** ou **legado**, com semantica identica em todos os pontos de uso.
Suporta o refactor citado na US (helper de resolucao).

## precondicoes

- T1 `done`: persistencia e migracao do gate disponiveis.
- Convencao de default (legado) alinhada a T1.

## orquestracao

- `depends_on`: T1.
- `parallel_safe`: `false` (sobreposto a ficheiros de servico e testes
  unitarios do mesmo modulo).
- `write_scope`: novo servico + testes unitarios dedicados.

## arquivos_a_ler_ou_tocar

- `backend/app/services/event_rollout_gate.py` *(criar)*
- `backend/app/models/models.py` *(somente leitura de tipos / relacionamentos)*
- `backend/tests/test_event_rollout_gate.py` *(criar; nome ajustavel ao padrao do repo)*

## testes_red

- testes_a_escrever_primeiro:
  - Caso: evento A marcado novo fluxo -> retorno `novo` (ou booleano
    `use_new_flow=True` conforme API escolhida).
  - Caso: evento B sem marcacao -> retorno `legado`.
  - Caso: `evento_id` inexistente -> comportamento definido (recomendado:
    legado ou erro HTTP tratado nos routers; documentar na implementacao).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_event_rollout_gate.py`
- criterio_red:
  - Testes falham ate o servico e dados de fixture existirem.

## passos_atomicos

1. Definir assinatura publica minima (funcao ou classe) e documentar no modulo.
2. Escrever testes red com fixtures de sessao SQLite de teste do projeto.
3. Implementar leitura do estado persistido de T1 sem logica duplicada em
   routers.
4. Green nos testes unitarios; refatorar nomes para consistencia com PRD
   (rollout / legado / migrado).

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `ruff check` / `ruff format`

## resultado_esperado

Um unico ponto de verdade para "este evento esta no novo fluxo?" consumivel por
`ativos.py` e `ingressos.py`, coberto por testes unitarios.

## testes_ou_validacoes_obrigatorias

- Suite dos novos testes unitarios 100% green.
- Nenhuma consulta ad-hoc ao modelo do gate fora deste modulo *(salvo
  excecao documentada no PR)*.

## stop_conditions

- Parar se T1 alterar o contrato de persistencia sem atualizar esta task.
- Parar se a API publica nao conseguir expressar ambos os modos sem ambiguidade.
