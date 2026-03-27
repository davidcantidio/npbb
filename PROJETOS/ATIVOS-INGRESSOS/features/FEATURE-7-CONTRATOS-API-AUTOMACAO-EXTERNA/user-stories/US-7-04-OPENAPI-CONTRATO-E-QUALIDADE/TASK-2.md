---
doc_id: "TASK-2.md"
user_story_id: "US-7-04-OPENAPI-CONTRATO-E-QUALIDADE"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_ingressos_externo_contract.py"
tdd_aplicavel: true
---

# TASK-2 - Contract tests e carga negativa da API de ingestao externa

## objetivo

Implementar suite automatizada que valide o contrato publico (alinhado ao OpenAPI consolidado na T1) e cenarios de carga negativa: payload invalido, falhas de autenticacao/autorizacao, e comportamento de idempotencia; a suite deve **falhar** quando a API divergir do contrato ou deixar de rejeitar entradas malformadas como esperado.

## precondicoes

- T1 concluida (`done`): OpenAPI e descricoes de idempotencia disponiveis.
- US-7-03 concluida: endpoints testaveis via `TestClient` ou fluxo equivalente usado no repo.
- Credenciais ou fixtures de integrador autenticado disponiveis (US-7-02), reutilizando padrao de testes existente no `backend/tests/`.

## orquestracao

- `depends_on`: `["T1"]` (contrato e documentacao como referencia normativa).
- `parallel_safe`: `false`.
- `write_scope`: ficheiro de testes dedicado; nao alterar logica de negocio salvo para corrigir bugs revelados pelos testes (fora de escopo salvo acordo em revisao).

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ativos_ingressos_externo_contract.py` (criar)
- OpenAPI gerado ou fixture derivada do schema apos T1
- Router e dependencias de auth da ingestao externa (somente leitura para desenhar casos)
- Testes existentes em `backend/tests/` como referencia de `client`, `engine`, seeds

## testes_red

- testes_a_escrever_primeiro:
  - Caso feliz minimo por operacao de ingestao acordada (status e corpo conforme contrato).
  - Caso payload JSON malformado ou campo obrigatorio ausente: esperar 4xx com estrutura de erro alinhada ao contrato.
  - Caso sem credencial ou token invalido: esperar 401/403 conforme politica US-7-02.
  - Caso idempotencia: duas submissoes com a mesma chave documentada; assert sobre status e semantica (ex.: mesma resposta, sem duplicar efeito colateral) conforme T1/US-7-01.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_externo_contract.py`
- criterio_red:
  - Os testes novos devem falhar antes da implementacao de ajustes na API ou de fixtures incompletas; se passarem sem codigo novo, parar e revisar se o contrato ja estava satisfeito ou se os asserts estao fracos.

## passos_atomicos

1. Escrever os testes listados em `testes_red` (e casos negativos adicionais objetivos, sem explosao combinatoria).
2. Rodar o comando red e confirmar falha inicial ligada ao comportamento ou contrato esperado.
3. Ajustar apenas o minimo necessario na API, schemas ou auth para satisfazer o contrato e os testes (respeitando limites da US-7-03/7-04; nao inventar endpoints novos).
4. Rodar novamente a suite alvo e confirmar green.
5. Refatorar extracao de helpers de teste (fixtures, carregamento de schema) mantendo a suite green.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_externo_contract.py`
- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` (validacao de regressao ampla quando a suite local estiver verde)

## resultado_esperado

Suite dedicada executavel em CI e localmente; falha quando o comportamento publico divergir do OpenAPI ou quando entradas invalidas nao forem tratadas conforme o contrato.

## testes_ou_validacoes_obrigatorias

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_externo_contract.py`
- Incluir o mesmo alvo no fluxo CI do repositorio, se ainda nao estiver coberto pelo `Makefile`/`ci-quality`.

## stop_conditions

- Parar se T1 nao estiver `done` ou se o OpenAPI nao for obtivel de forma deterministica nos testes.
- Parar se for necessario alterar escopo funcional da US-7-03 sem revisao (novo endpoint ou semantica nao documentada).
