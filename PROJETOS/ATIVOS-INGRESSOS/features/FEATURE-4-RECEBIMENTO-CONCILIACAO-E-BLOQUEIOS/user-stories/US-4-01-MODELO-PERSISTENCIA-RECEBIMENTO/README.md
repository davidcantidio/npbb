---
doc_id: "US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS"
decision_refs: []
---

# US-4-01 - Modelo de persistencia de recebimento e conciliacao

## User Story

**Como** engenheiro de plataforma,
**quero** persistir entidades de recebimento, conciliacao e referencias a artefatos com indices por evento e categoria,
**para** que registros e regras de saldo tenham base de dados auditavel alinhada ao PRD e ao manifesto da FEATURE-4.

## Feature de Origem

- **Feature**: FEATURE-4 - Recebimento, conciliacao e bloqueios por ticketeira
- **Comportamento coberto**: modelagem e migrations (recebimentos, divergencias, bloqueios, referencias a artefatos); base para trilha de auditoria.

## Contexto Tecnico

- Depende de [FEATURE-2](../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md) e [FEATURE-3](../../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md) para existencia de evento, diretoria, categoria e modo externo canonicos.
- Politica de storage LGPD em aberto (PRD sec. 7): aceitar placeholder (referencia externa + metadados) ate decisao formal.
- Contrato com FEATURE-7 (cargas automatizadas) deve permanecer extensivel sem quebrar o modelo.

## Plano TDD (opcional no manifesto da US)

- **Red**: nao aplicavel (planejamento; TDD na desdobramento em tasks).
- **Green**: nao aplicavel
- **Refactor**: nao aplicavel

## Criterios de Aceitacao (Given / When / Then)

- **Given** o desenho do manifesto FEATURE-4 sec. 6–7,
  **when** as migrations forem aplicadas,
  **then** existem estruturas para recebimento/conciliacao e vinculo a evento, diretoria, categoria e modo externo (conforme modelo acordado com FEATURE-3).
- **Given** um registro de recebimento persistido,
  **when** o sistema persiste metadados minimos,
  **then** ha campos ou tabelas preparados para trilha auditavel (ator, instante, natureza da alteracao) consumiveis pelas US seguintes.
- **Given** a necessidade de artefatos (ficheiro, link, texto),
  **when** o modelo for revisto,
  **then** a persistencia nao assume binarios obrigatorios no core ate fecho da politica LGPD (placeholder documentado).

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — Migration: recebimento e divergencia (conciliacao) com indices
- [TASK-2.md](./TASK-2.md) — Migration: bloqueio, referencias a artefatos e auditoria minima
- [TASK-3.md](./TASK-3.md) — Modelos SQLModel alinhados ao schema
- [TASK-4.md](./TASK-4.md) — Validacao final, downgrade multiplo e registo LGPD

## Arquivos Reais Envolvidos

- `backend/` migrations e modelos de dominio (caminhos exatos na fase de tasks)
- [FEATURE-4.md](../../FEATURE-4.md)

## Artefato Minimo

- Esquema persistido e migrations revisaveis que suportem US-4-02 e seguintes.

## Handoff para Revisao Pos-User Story

status: nao_iniciado
base_commit: nao_informado
target_commit: nao_informado
evidencia: nao_informado
commits_execucao: []
validacoes_executadas: []
arquivos_de_codigo_relevantes: []
limitacoes: []

## Dependencias

- [FEATURE-4](../../FEATURE-4.md)
- [FEATURE-2](../../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md)
- [FEATURE-3](../../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md)
- [PRD ATIVOS-INGRESSOS](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma (primeira da cadeia de recebimento nesta feature)
- [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

## Navegacao Rapida

- [FEATURE-4](../../FEATURE-4.md)
