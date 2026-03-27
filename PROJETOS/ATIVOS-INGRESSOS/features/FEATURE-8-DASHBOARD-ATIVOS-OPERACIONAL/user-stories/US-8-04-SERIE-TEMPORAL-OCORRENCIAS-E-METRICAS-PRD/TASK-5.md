---
doc_id: "TASK-5.md"
user_story_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
task_id: "T5"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
  - "T4"
parallel_safe: false
write_scope:
  - "frontend/src/"
  - "backend/app/"
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/user-stories/US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD/README.md"
tdd_aplicavel: false
---

# T5 - Metrica PRD 2.5 (leading/lagging) + export ou widget + handoff

## objetivo

Entregar **pelo menos uma** metrica **leading ou lagging** explicitada no [PRD sec. 2.5](../../../../PRD-ATIVOS-INGRESSOS.md) (**Metricas leading** / **Metricas lagging**), mapeada para:

- **widget dedicado** no dashboard de ativos (recomendado: **lagging** — *quantidade de problemas operacionais por evento*, alinhada ao `total` da API da T3 / painel da T4), **e/ou**
- **export** (CSV ou endpoint de download autenticado) com as mesmas colunas minimas necessarias para o utilizador validar o numero.

Incluir **legenda ou texto de ajuda** no UI (ou tooltip) que cite o nome da metrica no PRD e a formula operacional usada (ex.: “contagem de registos `problema_registrado` por `evento_id` no intervalo X” — ajustar a implementacao real).

Ao concluir, atualizar no [README.md](README.md) desta US o bloco **Handoff para Revisao Pos-User Story** — campo `limitacoes:` com bullets objetivos: recorte v1 (lista resumida vs drill-down TBD Intake 14); qual metrica PRD 2.5 foi escolhida; se outras metricas do PRD ficam fora de escopo ate proxima iteracao.

## precondicoes

- **T2** e **T4** `done` *(metrica integrada na mesma experiencia de dashboard; export pode viver so no backend se o widget ja mostrar o valor)*.

## orquestracao

- `depends_on`: `["T2", "T4"]`.
- `parallel_safe`: false.
- `write_scope`: `frontend/src/` (widget + legenda, botao export se aplicavel), `backend/app/` (endpoint export se aplicavel), `README.md` desta US para `limitacoes` e referencias no handoff.

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US
- [TASK-2.md](TASK-2.md), [TASK-4.md](TASK-4.md)
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.5
- `frontend/src/components/dashboard/`

## passos_atomicos

1. Confirmar com PRD a metrica escolhida (default: lagging *quantidade de problemas operacionais por evento*); se PM exigir outra da lista 2.5, ajustar implementacao mantendo rastreabilidade no texto da legenda.
2. Se widget: card ou linha dedicada mostrando o valor derivado de dados ja carregados (T3/T4) ou chamada leve read-only; texto de mapeamento PRD visivel.
3. Se export: implementar `GET` (ou `POST` se filtros complexos) que devolve CSV com cabecalhos claros; RBAC alinhado ao dashboard; limite de linhas/tempo documentado.
4. Preencher `limitacoes:` e, se aplicavel, `arquivos_de_codigo_relevantes` / `evidencia` no handoff do README quando a US for encaminhada a revisao (valores `nao_informado` apenas ate a execucao real).
5. `npm run build` e testes backend tocados, se existirem para export.

## comandos_permitidos

- `cd frontend && npm run build`
- `cd backend && PYTHONPATH=$(pwd)/..:$(pwd) SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(se adicionar testes ao export)*

## resultado_esperado

Terceiro criterio Given/When/Then da US-8-04 satisfeito com rastreio ao PRD 2.5; handoff documenta recortes v1 e metrica escolhida.

## testes_ou_validacoes_obrigatorias

- Smoke: widget mostra valor coerente com painel de problemas para o mesmo evento (quando metrica for contagem por evento).
- Se export: download abre em folha de calculo e colunas batem com API.

## stop_conditions

- Parar se nenhum dado suportar a metrica escolhida em ambiente de staging — documentar em `limitacoes` e escolher metrica leading alternativa com dados (ex.: percentual de categorias configuradas) com aprovacao PM.
