---
doc_id: "TASK-3.md"
user_story_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/"
  - "backend/app/services/"
tdd_aplicavel: true
---

# T3 - API de listagem e consulta de auditoria de remanejamentos

## objetivo

Expor endpoint(s) GET (paginados se necessario) para **listar e navegar** remanejamentos por evento e, quando aplicavel, por lote ou filtros acordados com o modelo da T1/T2. O contrato de resposta e as queries devem garantir que o consumidor distingua **remanejamento** de registros que representem apenas **aumento ou reducao de previsao** (PRD 2.6 / terceiro criterio da US): usar tipo discriminador, rota separada ou view somente-leitura que nao misture linhas de US-6-03.

## precondicoes

- TASK-1 e TASK-2 `done`: existem dados de exemplo ou seeds que permitem testar listagem apos POST de remanejamento.
- Acordo implicito no branch: tabela ou view de **ajustes de previsao** (US-6-03) ainda pode nao existir — neste caso, documentar na resposta OpenAPI que apenas eventos `remanejamento` sao retornados e que endpoints de ajuste serao distintos.

## orquestracao

- `depends_on`: `["T1", "T2"]`.
- `parallel_safe`: `false`.
- `write_scope`: extensoes em `ingressos.py`, schemas e eventual metodo de consulta no servico de remanejamento.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py` ou modulo de leitura dedicado
- Servico implementado na T2
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO/README.md` *(para nao colidir semanticamente)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste: GET por `evento_id` retorna lista ordenada contendo remanejamento criado pela T2; cada item expoe origem, destino, quantidade, instante, ator e motivo quando existir.
  - Teste: resposta **nao** inclui registros de tipo “ajuste de previsao” quando estes forem introduzidos por outra tabela/rota (mock ou fixture futura); se ainda nao houver tabela de ajustes, assertar que o serializer so emite `kind=remanejamento` ou equivalente.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q -k remanej_list`
- criterio_red:
  - Testes falham antes da implementacao do GET.

## passos_atomicos

1. Escrever testes red para listagem e discriminacao semantica.
2. Implementar query com filtros (evento obrigatorio; opcionais: intervalo de datas, diretoria, categoria) e paginacao alinhada a outras rotas de ativos.
3. Serializar resposta estavel para o frontend (TASK-4).
4. Documentar no OpenAPI filtros e forma de navegar a cadeia (ex.: `id`, `parent_allocation_id` se existir no modelo).
5. Implementar ate testes green.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q`
- `cd backend && .venv/bin/ruff check app/routers/ingressos.py app/services/ app/schemas/`

## resultado_esperado

API de auditoria utilizavel por revisor/operador que cumpre o terceiro Given/When/Then da US sem misturar com aumento/reducao de previsao.

## testes_ou_validacoes_obrigatorias

- Testes automatizados green.
- Verificacao manual: apos POST (T2), GET devolve a mesma operacao na lista.

## stop_conditions

- Parar se o modelo da T1 nao suportar filtros minimos por evento sem full scan perigoso — considerar indice adicional (voltar a T1 com revisao incremental aprovada).
- Parar se US-6-03 ja tiver misturado tipos na mesma tabela sem discriminador — exigir ADR ou correcao de modelo antes de expor listagem.
