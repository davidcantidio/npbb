---
doc_id: "TASK-4.md"
user_story_id: "US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
  - "T2"
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_endpoints.py"
tdd_aplicavel: true
---

# TASK-4 - Suite de testes integrando criterios Given/When/Then da US-3-02

## objetivo

Cobrir com testes automatizados os tres criterios de aceitacao Given/When/Then da US: alteracao autorizada com persistencia correta; negacao 403 sem efeitos para nao autorizado; presenca estavel dos dois modos canonicos nas leituras relevantes.

## precondicoes

- TASK-1, TASK-2 e TASK-3 concluidas (`done`).
- Fixture e padroes existentes em `backend/tests/test_ativos_endpoints.py` compreendidos (SQLite em memoria, `TestClient`, seed de evento/diretoria/usuario).

## orquestracao

- `depends_on`: `T1`, `T2`, `T3`.
- `parallel_safe`: `false`.

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ativos_endpoints.py`
- `backend/app/main.py` *(overrides de dependencia, se necessario)*
- `README.md` desta US *(criterios de aceite)*

## testes_red

- testes_a_escrever_primeiro:
  - Cenario **autorizado**: dado usuario com permissao de configuracao, ao atualizar subset valido de categorias, entao resposta de sucesso e GET subsequente reflete o subset (Given/When/Then 1).
  - Cenario **403**: dado usuario sem permissao, ao tentar escrita de configuracao, entao 403 e configuracao inalterada (Given/When/Then 2).
  - Cenario **modos canonicos**: dado cliente autenticado, ao obter contrato/listagem que inclua modo de fornecimento, entao corpo contem ambos valores canonicos acordados (Given/When/Then 3).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q`
- criterio_red:
  - Os testes novos ou estendidos devem falhar antes da implementacao final estar completa; se ja passarem na primeira execucao, revisar se estao a asserir o comportamento correto ou se a implementacao precedeu os testes.

## passos_atomicos

1. Escrever ou estender os testes listados em `testes_red` usando fixtures existentes; adicionar seeds minimos para entidades introduzidas pela US-3-01 quando necessario.
2. Rodar o comando red e confirmar falha inicial nos cenarios novos (ou falha por assercao ate green).
3. Ajustar implementacao nas tasks anteriores apenas se os testes revelarem lacunas (coordenacao minima, sem alargar escopo da US).
4. Rodar o comando novamente ate todos os testes relevantes passarem (green).
5. Refatorar testes duplicados mantendo a suite verde.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q`

## resultado_esperado

- `test_ativos_endpoints.py` documenta e valida os tres GWT da US-3-02.
- Nenhum teste flaky; tempos compativeis com a suite existente.

## testes_ou_validacoes_obrigatorias

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q` sem falhas.
- Cobertura minima: pelo menos um assert por criterio GWT na US.

## stop_conditions

- Parar se fixtures nao conseguirem representar permissao vs nao-permissao sem decisao de modelo (retornar `BLOQUEADO` com lacuna listada).
- Parar se for necessario criar ficheiro de teste separado: documentar justificativa e alinhar `write_scope` no handoff.
