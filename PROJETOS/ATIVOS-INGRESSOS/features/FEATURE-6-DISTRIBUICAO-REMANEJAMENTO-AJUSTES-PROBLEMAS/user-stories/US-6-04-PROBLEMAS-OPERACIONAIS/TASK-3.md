---
doc_id: "TASK-3.md"
user_story_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/tests/test_problemas_operacionais_endpoints.py"
tdd_aplicavel: true
---

# T3 - Testes de API: problemas operacionais por evento

## objetivo

Cobrir com pytest a criacao de ocorrencia, listagem filtrada por evento e **isolamento** entre eventos (problemas do evento A nao aparecem na listagem do evento B), usando ambiente de teste SQLite conforme [AGENTS.md](../../../../../../AGENTS.md).

## precondicoes

- T2 `done`: endpoints implementados e importaveis na app de teste.
- Fixtures existentes em `backend/tests/` para sessao DB, usuario autenticado e criacao de `Evento` — reutilizar em vez de duplicar.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: false.

## arquivos_a_ler_ou_tocar

- `backend/tests/conftest.py` *(fixtures)*
- `backend/tests/test_ingressos_endpoints.py` *(padrao de cliente API e auth)*
- `backend/app/main.py`
- Rotas e schemas implementados na T2

## testes_red

- testes_a_escrever_primeiro:
  - Criar problema no `evento_id=E1` e verificar 201/200 e persistencia.
  - Listar por `E1` contem o registro; listar por `E2` (outro evento) **nao** contem o registro de `E1`.
  - Paginacao/limite: segundo registro em `E1` respeita `limit=1` (primeira pagina nao retorna ambos se contrato assim definir).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_problemas_operacionais_endpoints.py -q`
- criterio_red:
  - Os testes acima devem falhar antes da implementacao estar completa; se passarem sem implementacao, parar e rever escopo dos asserts ou da task T2.

## passos_atomicos

1. Escrever os testes listados em `testes_red` (ficheiro dedicado ou extensao de suite existente se o projeto preferir modulo unico — documentar escolha).
2. Rodar pytest e confirmar falha inicial (red) onde aplicavel.
3. Se falha for por gap na T2, corrigir T2 antes de fechar esta task (coordenacao na mesma US).
4. Ajustar implementacao ate todos os testes passarem (green).
5. Refatorar fixtures duplicadas se necessario, mantendo a suite green.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_problemas_operacionais_endpoints.py -q`
- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q` *(regressao se router compartilhado)*

## resultado_esperado

Suite automatizada documenta e protege os criterios de aceitacao relacionados a persistencia, filtro por evento e isolamento.

## testes_ou_validacoes_obrigatorias

- `pytest tests/test_problemas_operacionais_endpoints.py` verde no CI local.
- Nenhum teste flaky por ordem de execucao; usar transacoes ou fixtures isoladas.

## stop_conditions

- Parar se fixtures nao permitirem dois eventos na mesma sessao sem refator de `conftest` — escalar para task auxiliar ou revisao de escopo.
