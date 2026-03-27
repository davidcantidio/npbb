---
doc_id: "TASK-3.md"
user_story_id: "US-4-02-REGISTRO-RECEBIDO-CONFIRMADO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/tests/test_recebimento_confirmado.py"
tdd_aplicavel: false
---

# TASK-3 - Testes de dominio e API para recebido confirmado

## objetivo

Garantir cobertura automatizada dos tres blocos Given/When/Then da US-4-02:
persistencia consultavel por eixos; artefato com rastreabilidade minima; historico
com tempo e ator. Usar `TESTING=true` / SQLite conforme convencao do repositorio.

## precondicoes

- TASK-1 e TASK-2 `done`.
- Padrao de testes de API do backend identificado (fixtures de sessao, usuario,
  seeds de evento/diretoria/categoria/modo se existirem).
- `AGENTS.md` e `docs/SETUP.md` para comandos de pytest corretos.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: `false`.
- `write_scope`: ficheiro(s) de teste dedicados; nao alterar producao salvo bug
  bloqueante descoberto nos testes.

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ativos_endpoints.py` *(padrao de cliente e auth)*
- `backend/tests/conftest.py` *(fixtures)*
- `backend/app/routers/recebimentos_ativos.py`
- `backend/app/services/recebimento_confirmado_service.py`
- `backend/tests/test_recebimento_confirmado.py` *(criar)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`); testes sao a propria entrega desta task.

## passos_atomicos

1. Criar fixture ou helper que prepara evento, diretoria, categoria e modo
   externos validos *(reutilizar factories existentes ou criar minimos na suite
   de teste)*.
2. Caso 1 — eixos validos: POST lote, depois GET com filtros; assert quantidade
   persistida e chaves de eixos coerentes.
3. Caso 2 — com artefato: POST com link ou nota; assert campos de artefato ou
   referencia persistidos e visiveis na resposta GET.
4. Caso 3 — trilha: apos POST, assert que resposta ou GET inclui instante e
   identidade de ator (ou campos equivalentes definidos no modelo US-4-01).
5. Caso negativo minimo: eixo invalido ou ausente retorna 4xx documentado.
6. Executar suite alvo e corrigir apenas falhas dentro do escopo US-4-02.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_recebimento_confirmado.py`

## resultado_esperado

Ficheiro `backend/tests/test_recebimento_confirmado.py` com cenarios que
falhariam se os criterios de aceite da US-4-02 deixassem de ser satisfeitos;
pytest verde no escopo deste ficheiro.

## testes_ou_validacoes_obrigatorias

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_recebimento_confirmado.py`
- Releitura dos criterios Given/When/Then no README da US e checklist mental 1:1
  com os testes.

## stop_conditions

- Parar se fixtures exigirem dados que ainda nao existem pos-US-4-01 — tratar
  como bloqueio de dependencia, nao mockar o dominio inteiro de forma a anular
  o valor do teste.
- Parar se a suite global do backend tiver falhas pre-existentes nao relacionadas;
  isolar execucao ao ficheiro desta task e documentar no handoff da US.
