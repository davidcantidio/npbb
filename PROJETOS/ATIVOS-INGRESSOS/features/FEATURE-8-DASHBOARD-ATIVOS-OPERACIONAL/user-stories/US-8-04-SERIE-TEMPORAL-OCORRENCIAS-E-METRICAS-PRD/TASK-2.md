---
doc_id: "TASK-2.md"
user_story_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/"
tdd_aplicavel: false
---

# T2 - UI: filtro e eixo temporal no dashboard de ativos

## objetivo

No shell do dashboard de ativos (rota entregue pela [US-8-02](../US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC/README.md), widgets pela [US-8-03](../US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS/README.md)), adicionar **controlo de intervalo de datas** e visualizacao de **serie temporal** que consome a API da **T1**, mantendo **coerencia** com as oito dimensoes ja exibidas (mesmos filtros de evento/contexto; alteracao de datas reflete todos os graficos dependentes da serie ou subconjunto acordado na implementacao).

## precondicoes

- **T1** `done`.
- US-8-02 e US-8-03 implementadas na mesma branch ou integradas — superficie navegavel disponivel.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: false (mesma area de pagina dashboard ativos que T4/T5).
- `write_scope`: componentes, hooks ou paginas sob `frontend/src/` dedicados ao dashboard de ativos (nao alterar dashboard de leads salvo reutilizacao de componente partilhado sem mudar comportamento de leads).

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US
- [TASK-1.md](TASK-1.md)
- `frontend/src/components/dashboard/` — padroes de grafico leads
- `frontend/src/config/dashboardManifest.ts` *(se existir analogo para ativos, alinhar)*
- Cliente HTTP / hooks existentes no frontend para chamadas API autenticadas

## passos_atomicos

1. Localizar pagina ou layout do **Dashboard > Ativos** e o estado de filtro de evento ja existente.
2. Adicionar estado de **intervalo** (`dateFrom`, `dateTo`) com defaults razoaveis (ex.: ultimos 30 dias ou ciclo do evento — documentar).
3. Integrar chamada ao endpoint da T1 com os parametros acordados; tratar loading e erro (mensagem operacional minima).
4. Renderizar grafico de linhas ou area reutilizando biblioteca ja usada no dashboard de leads (Chart.js, Recharts, etc. — seguir repo).
5. Validar manualmente que, para um evento de teste, valores exibidos nao contradizem os cards/tabelas das oito dimensoes para o mesmo contexto (mesmo evento, mesma janela quando aplicavel).
6. Ajustar tipos TypeScript e qualquer constante de rota.

## comandos_permitidos

- `cd frontend && npm run build`
- `cd frontend && npm run lint` *(se configurado)*
- Leitura: `rg`, `git diff`

## resultado_esperado

Utilizador aplica filtro/eixo temporal e ve acompanhamento por data alinhado a API e as dimensoes da US-8-03, cumprindo o primeiro criterio de aceitacao da US-8-04 no frontend.

## testes_ou_validacoes_obrigatorias

- `npm run build` sem erros de TypeScript.
- Smoke manual: alterar datas e ver atualizacao da serie.

## stop_conditions

- Parar se a API da T1 nao estiver disponivel na branch — desbloquear T1 primeiro.
- Parar se a US-8-03 nao tiver widgets base — completar US-8-03 antes de integrar UI temporal visivel.
