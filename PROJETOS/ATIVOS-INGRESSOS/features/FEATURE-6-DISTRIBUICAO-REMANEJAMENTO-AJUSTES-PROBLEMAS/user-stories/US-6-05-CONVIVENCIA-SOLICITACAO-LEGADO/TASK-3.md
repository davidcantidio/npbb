---
doc_id: "TASK-3.md"
user_story_id: "US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/tests/test_feature6_convivencia_legado.py"
  - "backend/tests/conftest.py"
tdd_aplicavel: true
---

# TASK-3 - Testes automatizados com dados legados nos cenarios FEATURE-6

## objetivo

Implementar suite de testes (integracao/API) que exercite **distribuicao,
remanejamento, ajuste de previsao e problema operacional** com **dados legados**
(`CotaCortesia`, `SolicitacaoIngresso` em estados relevantes) presentes na base
de teste, demonstrando que operacoes novas **nao corrompem** registos legados nem
violam as invariantes documentadas no ADR (T2), cumprindo o segundo criterio
Given/When/Then da US-6-05.

## precondicoes

- T2 concluida: ADR com matriz e invariantes utilizavel como especificacao de
  teste.
- US-6-01 a US-6-04 **implementadas e merged**: endpoints e transicoes novos
  existem para serem chamados nos testes. Se alguma US faltar, restringir a
  subconjunto ja entregue e documentar skip/xfail com justificativa no doc ou no
  teste (nao inventar API).
- Padrao de testes do repo: `TESTING=true` / SQLite em pytest conforme
  `AGENTS.md`.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: `false` (partilha convencoes de fixtures com T4).
- `write_scope`: modulo de teste dedicado; `conftest.py` apenas se necessario
  para fixtures partilhadas com T4.

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md`
- `backend/tests/test_ingressos_endpoints.py` *(padrao de sessao e criacao de
  `SolicitacaoIngresso`)*
- `backend/tests/test_ativos_endpoints.py`
- `backend/tests/conftest.py` *(se existir fixture reutilizavel)*
- Codigo de servicos/routers introduzido por US-6-01..04
- `AGENTS.md` *(comando pytest canónico)*

## testes_red

- **testes_a_escrever_primeiro**:
  - Pelo menos um cenario por eixo (distribuicao, remanejamento, ajuste, problema)
    que: (1) cria ou reutiliza cota + `SolicitacaoIngresso` legado; (2) invoca a
    operacao FEATURE-6 correspondente; (3) assegura que linhas legadas permanecem
    coerentes (status, integridade referencial, contagens conforme ADR).
  - Casos negativos ou de bloqueio previstos no ADR (ex.: nao misturar dados sem
    migracao) quando aplicavel.
- **comando_para_rodar**:
  - `cd backend && PYTHONPATH=<repo_root>:<repo_root>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_feature6_convivencia_legado.py`
  - *(substituir `<repo_root>` pelo root do monolito; mesmo padrao que `AGENTS.md`)*
- **criterio_red**:
  - Antes da implementacao completa das rotas/dominio, os testes novos devem
    falhar por comportamento em falta ou assercao correta sobre estado legado; se
    ja passarem sem implementar nada, parar e rever escopo dos testes (podem estar
    a testar demais pouco).

## passos_atomicos

1. Escrever os testes listados em `testes_red` no modulo dedicado.
2. Rodar pytest e confirmar falha inicial (`red`) coerente.
3. Implementar ou completar codigo minimo nas US precedentes **se ainda nao
   existir** (fora do escopo desta US-6-05 exceto correcoes bloqueantes) — em
   principio apenas **ajustes de teste/fixtures** nesta task; se faltar feature,
   parar com `stop_conditions`.
4. Iterar ate `green` mantendo invariantes do ADR.
5. Refactor leve dos testes (nomes, helpers) mantendo suite verde.

## comandos_permitidos

- `cd backend && PYTHONPATH=<repo>:<repo>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q ...`
- `rg` / leitura de codigo

## resultado_esperado

Existe `backend/tests/test_feature6_convivencia_legado.py` com cenarios que
cobrem os quatro eixos (ou subconjunto documentado se US predecessora em falta),
verde na CI local, alinhado ao ADR.

## testes_ou_validacoes_obrigatorias

- Comando pytest da US / `AGENTS.md` passa para o modulo novo (e suite relevante
  se o time exigir regressao completa).
- Releitura cruzada: cada teste principal mapeia a uma linha ou invariante do
  ADR (comentario ou docstring curta com referencia).

## stop_conditions

- Parar se US-6-01..04 nao estiverem entregues: nao simular API inexistente;
  devolver lista de US em falta ao PM e manter apenas testes de baseline legado
  se o gate aprovar escopo reduzido.
