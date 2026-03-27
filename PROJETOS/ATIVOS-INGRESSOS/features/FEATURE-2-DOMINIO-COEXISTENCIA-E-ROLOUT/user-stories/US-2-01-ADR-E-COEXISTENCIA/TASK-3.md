---
doc_id: "TASK-3.md"
user_story_id: "US-2-01-ADR-E-COEXISTENCIA"
task_id: "T3"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md"
tdd_aplicavel: false
---

# TASK-3 - Decisoes de transicao, gate por evento e impacto em rotas

## objetivo

Documentar decisoes de transicao (ex.: dual-read, feature gate por evento) com
criterio de activacao, impacto nas rotas e contratos existentes de `/ativos` e
`/ingressos`, sem contradizer `PRD-ATIVOS-INGRESSOS.md` sec. **8** nem a
estrategia de rollout descrita na sec. 4.1.

## precondicoes

- T2 concluida: separacao legado vs novo dominio redigida no ADR.
- PRD sec. 8 e trechos de rollout em 4.1 disponiveis.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: `false`.
- `write_scope`: mesmo ficheiro ADR.

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (4.1, 8)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md` (criterios de aceite e estrategia)

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Descrever o mecanismo de **activacao gradual por evento** (feature flag ou
   equivalente) ao nivel de decisao de arquitectura: o que significa "evento no
   novo fluxo" vs "evento apenas legado", alinhado ao PRD 8 e ao manifesto
   FEATURE-2.
2. Se aplicavel ao desenho aprovado, explicitar **dual-read** ou outra tatica
   de leitura/escrita durante transicao; indicar criterios de activacao e
   desactivacao em linguagem verificavel (nao implementar codigo nesta US).
3. Listar **impacto esperado** nas rotas e clientes existentes do baseline
   (PRD 4.0): `/ativos`, `/ingressos`, frontends referidos no PRD — o ADR deve
   deixar claro que eventos nao migrados mantem comportamento legado.
4. Incluir subseccao **rollback**: alinhar com PRD sec. 8 (preservacao de dados
   reconciliados quando possivel); nao prometer invariantes que o PRD nao
   afirma.
5. Registar **correlation_id** (ou padrao equivalente) apenas como ponto de
   extensao referenciado pelo FEATURE-2/PRD, sem desenhar implementacao nesta
   task.

## comandos_permitidos

- `rg` / `grep` *(opcional, leitura de referencias a rollout ou flags em docs
  existentes)*

## resultado_esperado

Secao do ADR legivel por implementacao e revisao, cobrindo o terceiro bloco
Given/When/Then da US-2-01 (transicao, criterio de activacao, rotas).

## testes_ou_validacoes_obrigatorias

- Tabela ou lista: "Criterio de activacao" / "Impacto em rotas legadas" /
  "Comportamento se rollback".
- Revisao explicita: nenhuma frase contradiz PRD sec. 8 (deploy gradual,
  flags, rollback).

## stop_conditions

- Parar se for necessario inventar politica de produto nao presente no PRD ou
  na FEATURE-2; devolver lacuna ao PM em vez de preencher com suposicao.
