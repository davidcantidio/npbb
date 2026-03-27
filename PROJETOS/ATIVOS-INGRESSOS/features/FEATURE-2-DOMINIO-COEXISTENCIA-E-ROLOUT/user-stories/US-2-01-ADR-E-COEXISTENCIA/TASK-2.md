---
doc_id: "TASK-2.md"
user_story_id: "US-2-01-ADR-E-COEXISTENCIA"
task_id: "T2"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md"
tdd_aplicavel: false
---

# TASK-2 - Legado agregado versus novo dominio ate ao rollout

## objetivo

Redigir no ADR a seccao que explica, sem ambiguidade, o que permanece no
modelo agregado actual (`CotaCortesia`, `SolicitacaoIngresso`, rotas e
comportamento descritos no PRD 4.0) e o que pertence ao **novo dominio** ate ao
corte de rollout, em linha com o primeiro criterio Given/When/Then da US-2-01.

## precondicoes

- T1 concluida: ficheiro ADR e esqueleto existem.
- PRD sec. 4.0 e 4.1 relidos para nao contradizer baseline nem arquitectura
  geral.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: `false`.
- `write_scope`: mesmo ficheiro ADR que T1.

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (4.0, 4.1)
- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Preencher a seccao "modelo agregado legado" com o que permanece: entidades,
   rotas `/ativos` e `/ingressos`, unicidade `evento_id + diretoria_id` em
   `CotaCortesia`, papéis de `SolicitacaoIngresso`, alinhado ao texto do PRD
   4.0 (sem inventar endpoints novos).
2. Preencher a seccao "novo dominio (em transicao)" com o que o PRD 4.1 e o
   manifesto FEATURE-2 introduzem como alvo (categorias, conciliacao, emissao
   unitaria, dashboard, correlacao, etc.) marcando claramente que estas
   capacidades estao **fora** do comportamento actual do baseline ate estarem
   implementadas e activadas por evento.
3. Definir em uma subseccao "ate ao corte de rollout" o significado operacional
   do corte (coerente com PRD sec. 8): o que continua obrigatoriamente
   funcional no legado para eventos nao migrados.
4. Evitar duplicar o PRD como lista de backlog; manter o ADR como decisao e
   limite de convivencia.

## comandos_permitidos

- `rg` / `grep` *(confirmar nomes de entidades e rotas no PRD e no codigo apenas
  como leitura, sem alterar ficheiros de aplicacao)*

## resultado_esperado

O ADR contem narrativa clara "o que fica no agregado / o que e novo dominio
ate ao rollout", verificavel por revisao por pares contra PRD 4.0–4.1.

## testes_ou_validacoes_obrigatorias

- Checklist: cada bullet do PRD 4.0 sobre baseline esta reflectido como
  "permanece no legado" ou explicitamente marcado como alvo futuro, sem
  contradicoes.
- Revisar contra o primeiro bloco Given/When/Then da US-2-01.

## stop_conditions

- Parar se o estado actual do codigo divergir do PRD 4.0; registar a divergencia
  no ADR como "lacuna" e escalar — nao inventar comportamento para fechar o
  gap.
