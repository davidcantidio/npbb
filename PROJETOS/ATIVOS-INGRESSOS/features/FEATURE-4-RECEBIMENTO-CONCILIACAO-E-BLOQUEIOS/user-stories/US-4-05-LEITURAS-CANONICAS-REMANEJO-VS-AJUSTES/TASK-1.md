---
doc_id: "TASK-1.md"
user_story_id: "US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md"
tdd_aplicavel: false
---

# TASK-1 - ADR do modelo canonico de leituras (remanejado vs ajustes)

## objetivo

Publicar um ADR que fixe o **modelo canonico de leituras** para o dominio Ativos/Ingressos: mapeamento explícito entre **entidades ou fontes persistidas** (apos US-4-01+) e cada **dimensao de leitura** exposta a clientes internos — em particular **remanejado** isolado de **aumento**, **reducao** e saldos relacionados (ex.: nao distribuido, disponivel sob regras de recebimento), alinhado ao PRD sec. 2.6 / 3 e ao criterio 4 da FEATURE-4 sec. 4 e sec. 10.

## precondicoes

- [FEATURE-4.md](../../FEATURE-4.md) e [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) lidos para vocabulario canonicos (`remanejado`, `aumentado`, `reduzido`, conciliacao).
- Estrutura de persistencia entregue ou planejada pela [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) conhecida o suficiente para nomear tabelas/eventos no mapeamento (se ainda nao existir no codigo, o ADR declara **alvo** e referencia a US-4-01 como fonte de verdade quando implementada).

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter (ficheiro ADR unico).

## arquivos_a_ler_ou_tocar

- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md` *(criar; criar pasta `docs/adr/` se nao existir)*
- [FEATURE-4.md](../../FEATURE-4.md) *(sec. 4, 10)*
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) *(sec. 2.6, 3, estados operacionais)*
- [README.md desta US](./README.md) *(criterios Given/When/Then)*

## passos_atomicos

1. Criar `docs/adr/` se necessario e o ficheiro ADR indicado no `write_scope`.
2. Documentar **contexto** e **decisao**: leituras de dashboard/API interna devem expor remanejado como medida propria; aumento e reducao como medidas distintas; proibir agregacoes que somem remanejado em aumento ou reducao sem campo dedicado.
3. Incluir **tabela ou lista** entidade/fonte → leitura exposta (nome do campo ou metrica), com notas de auditoria quando aplicavel.
4. Referenciar explicitamente alinhamento futuro com [FEATURE-8](../../../FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/FEATURE-8.md) como consumidor, sem desenhar FEATURE-8 nesta task.
5. Referenciar cruzado [FEATURE-4.md](../../FEATURE-4.md) sec. 10 (ADR vinculado).

## comandos_permitidos

- `mkdir -p docs/adr` *(se necessario)*
- Revisao local do Markdown *(editor)*

## resultado_esperado

- ADR versionado em Git com mapeamento entidades→leituras suficiente para implementacao em TASK-2/TASK-3 sem ambiguidade sobre separacao remanejado vs ajustes.

## testes_ou_validacoes_obrigatorias

- O ADR cobre explicitamente os tres criterios Given/When/Then da US que exigem documento: publicacao, mapeamento persistido→leitura, e referencia para comparacao com consultas de saldo (US-4-03/US-4-04) na TASK-4.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o projeto exigir outro caminho de ADR (pasta ou convencao de nome) nao documentado — obter decisao no gate antes de gravar.
- Parar se for necessario inventar entidades de persistencia sem base na US-4-01/PRD; limitar-se a placeholders claramente rotulados como **alvo** ate modelo existir.
