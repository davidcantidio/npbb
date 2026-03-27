---
doc_id: "TASK-1.md"
user_story_id: "US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md"
tdd_aplicavel: false
---

# TASK-1 - Contrato de consumo: aumentado, reduzido e remanejado (FEATURE-6)

## objetivo

Publicar especificacao interna que fixe o **contrato de consumo** para leituras operacionais de **distribuicao / remanejamento / ajustes de previsao** alinhado ao PRD sec. 2.3 e 2.6 e ao manifesto [FEATURE-6.md](../../FEATURE-6.md): mapeamento explicito **endpoint HTTP (ou view) + campo JSON** para cada semantica `aumentado`, `reduzido` e `remanejado`, **sem** duplicar o ADR de modelo persistido da [US-4-05](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES/README.md) — esse ADR (`docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md`) permanece fonte do **modelo canonico entidade→leitura**; este documento e a ponte **API/view → semantica** para integradores e FEATURE-8.

## precondicoes

- [README.md desta US](./README.md) e [FEATURE-6.md](../../FEATURE-6.md) sec. 2, 4 e 7 lidos.
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) sec. 2.6 e vocabulario `aumentado` / `reduzido` / `remanejado` confirmados.
- [TASK-1 US-4-05](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES/TASK-1.md) lido: caminho alvo do ADR e separacao semantica esperada.

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter (ficheiro de contrato unico sob `docs/ativos-ingressos/`).

## arquivos_a_ler_ou_tocar

- `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md` *(criar; criar pasta `docs/ativos-ingressos/` se nao existir)*
- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md` *(referencia; criado pela US-4-05 se ainda ausente)*
- `backend/app/routers/ingressos.py` *(apenas leitura: convencoes de prefixo `/ingressos` e auth)*
- `backend/app/routers/ativos.py` *(apenas leitura: decidir se leituras F6 estendem `/ativos` ou `/ingressos` sem contradizer US-4-05)*

## passos_atomicos

1. Criar `docs/ativos-ingressos/` se necessario e o ficheiro indicado no `write_scope`.
2. Documentar **decisao de colocacao**: rotas sob `/ingressos` (alinhado a FEATURE-6 sec. 7) **ou** extensao de `/ativos` se o ADR e a US-4-05 ja fixarem leituras canonicas ai — justificar numa linha para evitar dois contratos concorrentes sem relacao.
3. Incluir **tabela** colunas: semantica PRD (`aumentado`, `reduzido`, `remanejado`) | metodo e path | nome do campo (ou sub-objeto) | tipo | notas anti-duplicacao (mesmo movimento nao conta em dois campos).
4. Referenciar cruzado o ADR US-4-05 para fonte de dados; onde o ADR ainda for placeholder, marcar celulas como **alvo** e dependencia de US-4-01/US-6-02.
5. Mencionar consumo futuro [FEATURE-8](../../../FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/FEATURE-8.md) sem desenhar dashboard.

## comandos_permitidos

- `mkdir -p docs/ativos-ingressos` *(se necessario)*
- Revisao local do Markdown *(editor)*

## resultado_esperado

- Contrato versionado em Git suficiente para TASK-2/TASK-3 implementarem agregacao e HTTP sem reinterpretar semantica.
- Criterio Given/When/Then da US sobre "qual endpoint ou campo corresponde a cada semantica" satisfeito ao nivel documental.

## testes_ou_validacoes_obrigatorias

- Revisao: cada uma das tres semanticas tem pelo menos uma linha na tabela de mapeamento.
- Revisao: documento cita explicitamente PRD 2.6 e o path do ADR US-4-05.

## stop_conditions

- Parar e reportar `BLOQUEADO` se produto exigir prefixo ou audiencia (roles) diferente do que FEATURE-6/PRD permitem inferir — obter decisao no gate antes de gravar o contrato.
- Parar se nao for possivel escolher entre `/ingressos` e `/ativos` sem contradizer US-4-05 TASK-3 — escalar ao gate com lacuna objetiva.
