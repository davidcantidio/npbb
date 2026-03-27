---
doc_id: "US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-5"
decision_refs: []
---

# US-5-01 - Modelo e migracao de emissao unitaria

## User Story

Como equipe de plataforma,
quero persistir emissoes internas unitarias ligadas a evento, diretoria, categoria e destinatario com identificador unico auditavel,
para que cada destinatario em modo interno com QR tenha um registro inequivoco antes de API e UI consumirem o fluxo.

## Feature de Origem

- **Feature**: FEATURE-5 (Emissao interna unitaria com QR)
- **Comportamento coberto**: primeiro criterio de aceite da feature — um registro por destinatario com identificador unico imutavel ou versionado de forma auditavel; base de dados alinhada a estrategia da sec. 6 do manifesto.

## Contexto Tecnico

- Depende de **FEATURE-2** e **FEATURE-3** (dominio de coexistencia/rollout e categorias/modos de fornecimento) para FKs e semantica de categoria.
- Storage de binarios ou URLs de artefatos segue decisao pendente do PRD sec. 7; o modelo deve permitir referencia externa ou blob sem antecipar politica de retencao.
- Stack alvo do monolito: SQLModel/Alembic em `backend/app/models` e migracoes sob `backend`.

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir em `TASK-*.md` quando existirem testes de migracao ou invariantes.
- **Green**: a definir em `TASK-*.md`.
- **Refactor**: a definir em `TASK-*.md`.

## Criterios de Aceitacao (Given / When / Then)

- **Given** uma categoria em modo interno emitido com QR (FEATURE-3) e entidades de evento/diretoria existentes,
  **when** a migracao e aplicada,
  **then** existe entidade (ou conjunto coerente) de emissao unitaria com FKs para evento, diretoria, categoria e destinatario conforme manifesto da feature.
- **Given** dois pedidos de emissao para o mesmo destinatario na mesma categoria e escopo de unicidade acordado,
  **when** a restricao de unicidade e exercida no banco ou camada de dominio documentada nesta US,
  **then** o segundo caso e rejeitado ou versionado de forma auditavel (sem ambiguidade na especificacao desta US).
- **Given** um registro de emissao criado,
  **when** se exige alteracao de identidade canonica,
  **then** a politica e imutabilidade do identificador ou versionamento auditavel esta definida e coberta por teste ou constraint documentada.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md) — ADR de dominio (unicidade, identidade, FK destinatario)
- [TASK-2.md](./TASK-2.md) — Migration Alembic (tabela + FKs + constraints)
- [TASK-3.md](./TASK-3.md) — Modelos SQLModel
- [TASK-4.md](./TASK-4.md) — Testes de invariantes e validacao da migration

## Arquivos Reais Envolvidos

- `backend/app/models/models.py` (ou modulo de dominio de ingressos/ativos evoluido)
- `backend/alembic/versions/` (novas revisoes)
- `features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/FEATURE-5.md`

## Artefato Minimo

- Migracao aplicavel e modelo documentado; invariantes de unicidade e auditabilidade verificaveis.

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

- [FEATURE-5](../../FEATURE-5.md)
- [PRD do projeto](../../../../PRD-ATIVOS-INGRESSOS.md)
- Outras USs: nenhuma; requer **FEATURE-2** e **FEATURE-3** satisfeitas para execucao no dominio alvo
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
