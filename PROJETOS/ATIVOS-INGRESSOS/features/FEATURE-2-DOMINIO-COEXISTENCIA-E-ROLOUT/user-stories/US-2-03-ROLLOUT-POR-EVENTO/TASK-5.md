---
doc_id: "TASK-5.md"
user_story_id: "US-2-03-ROLLOUT-POR-EVENTO"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - T4
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/"
  - "backend/docs/auditoria_eventos/"
tdd_aplicavel: false
---

# TASK-5 - Coerencia documental: criterio de ativacao e ADR US-2-01

## objetivo

Satisfazer o terceiro criterio Given/When/Then da US: quando o gate for
alterado na implementacao (T1–T4), a **descricao do criterio de ativacao**
permanece coerente com o ADR ou documentacao viva da
[US-2-01](../US-2-01-ADR-E-COEXISTENCIA/README.md) *(ou e atualizada na mesma
entrega)* — sem contradicao entre "como marcar evento", default legado, e
efeitos em `/ativos` e `/ingressos`.

## precondicoes

- T4 `done`: comportamento e testes fechados o suficiente para documentar o
  criterio final.
- Artefato US-2-01 existente (rascunho ou aprovado) para atualizar ou cruzar
  referencias.

## orquestracao

- `depends_on`: T4.
- `parallel_safe`: `false`.
- `write_scope`: apenas markdown/docs listados; nenhum codigo de aplicacao.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`
- Ficheiros ADR ou `backend/docs/auditoria_eventos/` referenciados na US-2-01
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 4.1, 8)*

## passos_atomicos

1. Revisar o estado final do gate (nomes de campo/tabela, default, quem pode
   alterar) conforme entregue em T1–T4.
2. Atualizar o ADR ou doc vivo da US-2-01 com secao explicita "Ativacao por
   evento" *(ou equivalente)*: como A fica migrado, como B permanece legado,
   referencia aos testes de T4.
3. Se US-2-01 ainda nao tiver arquivo ADR concreto, criar ou anexar sob o
   caminho ja citado no contexto da US-2-01 *(sem duplicar o PRD como
   backlog)*.
4. Referenciar em uma linha o modulo `event_rollout_gate` *(ou nome final)* e
   a revisao Alembic do gate.

## comandos_permitidos

- `rg -n "rollout|gate|novo fluxo|legado" PROJETOS/ATIVOS-INGRESSOS backend/docs backend/app` *(ajustar paths conforme achados)*
- `git diff` para revisao de consistencia

## resultado_esperado

Leitor consegue ir do ADR/doc ao criterio operacional e aos testes; nenhuma
divergencia entre documentacao e implementacao na mesma entrega.

## testes_ou_validacoes_obrigatorias

- Revisao por par: checklist de coerencia (default legado, marcacao explicita,
  rotas afetadas).
- Links relativos validos entre US-2-01, US-2-03 e FEATURE-2.

## stop_conditions

- Parar se US-2-01 estiver indefinida como local do ADR — registrar lacuna e
  escopo minimo aceite com PM antes de inventar nova arvore de pastas.
