---
doc_id: "TASK-4.md"
user_story_id: "US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/"
tdd_aplicavel: false
---

# T4 - UI: painel minimo de ocorrencias / problemas

## objetivo

Na pagina do dashboard de ativos, adicionar secao **Painel de ocorrencias/problemas** que consome a API da **T3**: mostrar **contagem total** e **lista resumida** (ultimos N com tipo, descricao curta, data). Nao implementar drill-down completo nem fluxos do Intake sec. 14; link “ver detalhes” pode ser omitido ou desativado (TBD) desde que o minimo v1 permaneca util para operacao.

## precondicoes

- **T3** `done`.
- Mesmo contexto de `evento`/filtros que o restante dashboard (US-8-02/03).

## orquestracao

- `depends_on`: `["T3"]`.
- `parallel_safe`: false.
- `write_scope`: `frontend/src/` (componentes do painel de problemas no modulo dashboard ativos).

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US
- [TASK-3.md](TASK-3.md)
- `frontend/src/components/dashboard/` — padroes de card/tabela
- [Intake sec. 14](../../../../INTAKE-ATIVOS-INGRESSOS.md) *(para nao expandir escopo alem do minimo)*

## passos_atomicos

1. Criar componente de painel (card ou painel lateral) alinhado visualmente ao dashboard de leads.
2. Chamar endpoint da T3 com `evento_id` atual; estados loading/empty/error.
3. Renderizar `total` em destaque e lista com colunas minimas acordadas na T3.
4. Garantir acessibilidade basica (titulo, lista semantica ou tabela).
5. Se N < total, indicar “mostrando ultimos N” conforme contrato da API.

## comandos_permitidos

- `cd frontend && npm run build`
- `cd frontend && npm run lint` *(se existir)*

## resultado_esperado

Utilizador abre o painel e ve resumo operacional util, cumprindo o segundo criterio Given/When/Then da US-8-04.

## testes_ou_validacoes_obrigatorias

- `npm run build` sem erros.
- Smoke manual com evento com e sem problemas.

## stop_conditions

- Parar se API da T3 instavel ou sem contrato documentado — estabilizar T3 primeiro.
