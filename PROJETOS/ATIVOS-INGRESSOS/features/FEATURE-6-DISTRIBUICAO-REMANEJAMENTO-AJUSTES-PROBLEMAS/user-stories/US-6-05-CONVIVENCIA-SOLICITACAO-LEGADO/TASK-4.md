---
doc_id: "TASK-4.md"
user_story_id: "US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_feature6_convivencia_legado.py"
  - "docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md"
tdd_aplicavel: true
---

# TASK-4 - Contrato fluxo exclusivamente legado e fecho de validacao

## objetivo

Cobrir o **terceiro** criterio Given/When/Then da US-6-05: com operador usando
**apenas** o fluxo legado durante a janela de transicao, o sistema mantem
comportamento dentro do **contrato legado** documentado no ADR (rotas e estados
`SolicitacaoIngresso` / cotas sem depender das operacoes novas). Atualizar o ADR
com secao **Como validar** (comandos pytest, escopo de ficheiros) e referencia
cruzada ao modulo de testes, fechando a rastreabilidade documento ↔ suite.

## precondicoes

- T3 concluida: modulo `test_feature6_convivencia_legado.py` existe e esta verde
  para cenarios com fluxo novo + legado.
- ADR T2 completo quanto ao contrato legado.

## orquestracao

- `depends_on`: `["T3"]`.
- `parallel_safe`: `false`.
- `write_scope`: mesmo modulo de testes (novos casos legado-puro) + ADR (secao
  validacao).

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md`
- `backend/tests/test_feature6_convivencia_legado.py`
- `backend/tests/test_ingressos_endpoints.py`
- `backend/app/routers/ingressos.py`
- `AGENTS.md`

## testes_red

- **testes_a_escrever_primeiro**:
  - Cenarios que exercitem **somente** endpoints legados de solicitacao / listagem
    conforme PRD 4.0 (`GET /ingressos/ativos`, `POST /ingressos/solicitacoes`,
    fluxo admin se aplicavel ao contrato), com cotas e solicitacoes em estados
    representativos, **sem** invocar operacoes FEATURE-6 novas (ou com feature
    flag / evento nao migrado simulado, se o desenho assim definir no ADR).
  - Assercoes alinhadas ao texto do ADR sobre o que o legado garante ate migracao.
- **comando_para_rodar**:
  - `cd backend && PYTHONPATH=<repo_root>:<repo_root>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_feature6_convivencia_legado.py -k legacy_only`
  - *(ou marcador equivalente definido na implementacao)*
- **criterio_red**:
  - Testes novos falham ate o contrato estar coberto; se passarem antes de
    implementar assercoes, rever cenarios (fracas).

## passos_atomicos

1. Escrever testes `legacy_only` (ou classe/módulo claramente separado) conforme
   `testes_red`.
2. Confirmar ciclo red → green.
3. No ADR, adicionar ou completar secao **Como validar**: comandos copy-paste
   (pytest), variaveis `TESTING`/`SECRET_KEY`, lista de ficheiros de teste,
   interpretacao dos cenarios (novo+legado vs legado so).
4. Referenciar no ADR o `user_story_id` US-6-05 e link relativo ao repo de
   governanca se convencao do projeto exigir.

## comandos_permitidos

- `cd backend && PYTHONPATH=<repo>:<repo>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q ...`
- Edicao de Markdown do ADR e de ficheiros de teste

## resultado_esperado

Suite cobre fluxo legado isolado; ADR contem instrucoes de validacao executaveis;
terceiro criterio da US verificavel por leitura + execucao de pytest.

## testes_ou_validacoes_obrigatorias

- `python -m pytest` no modulo acima passa no ambiente CI local descrito em
  `AGENTS.md`.
- Revisor consegue executar apenas os comandos do ADR e reproduzir validacao.

## stop_conditions

- Parar se o desenho de rollout (evento ainda nao migrado) nao estiver modelavel
  nos testes sem codigo de producao adicional: documentar lacuna no ADR e
  escalar decisao de produto.
