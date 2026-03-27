---
doc_id: "US-5-03-CONTRATO-MINIMO-PAYLOAD-QR"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
task_instruction_mode: "required"
feature_id: "FEATURE-5"
decision_refs: []
---

# US-5-03 - Contrato minimo do payload QR

## User Story

Como arquiteto de produto,
quero documentar e implementar o contrato minimo do payload do QR alinhado ao PRD e ao intake,
para que um validador futuro de uso unico tenha identidade persistida suficiente sem inventar semantica fora do escopo acordado.

## Feature de Origem

- **Feature**: FEATURE-5 (Emissao interna unitaria com QR)
- **Comportamento coberto**: terceiro criterio de aceite da feature — contrato de dados minimo para futura validacao (campos obrigatorios, sem semantica extra além de PRD sec. 3 / hipoteses congeladas e intake sec. 15 referenciada no manifesto).

## Contexto Tecnico

- **US-5-01** fornece onde persiste a identidade; **US-5-02** expoe a emissao — a serializacao do QR deve alinhar-se ao servico de emissao.
- Artefato documental: ADR ou documento sob `features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/` (ou `docs/`) com campos obrigatorios e exemplos nao sensiveis.
- Nao inclui scanner, validacao no portao nem estado `qr_validado` (PRD 2.4 fora / sec. 6).

## Plano TDD (opcional no manifesto da US)

- **Red**: a definir em `TASK-*.md`.
- **Green**: a definir em `TASK-*.md`.
- **Refactor**: a definir em `TASK-*.md`.

## Criterios de Aceitacao (Given / When / Then)

- **Given** o PRD sec. 3 (hipoteses sobre identidade para validador futuro) e o intake,
  **when** o documento de contrato minimo e publicado,
  **then** lista campos obrigatorios do payload (ou referencia inequivoca ao identificador persistido) e explicita o que fica **fora** do escopo do validador neste corte.
- **Given** uma emissao concluida via API,
  **when** o payload do QR e gerado,
  **then** ele cumpre o contrato minimo documentado e permanece reversivel para a entidade de emissao sem ambiguidade.
- **Given** evolucao futura do validador,
  **when** o time consulta apenas esta US e o doc de contrato,
  **then** consegue distinguir compatibilidade esperada versus mudanca de major version do contrato.

## Definition of Done da User Story

- [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
- [ ] Todas as tasks tem `depends_on`, `parallel_safe` e `write_scope` coerentes com a ordem de execucao
- [ ] Criterios Given/When/Then verificados
- [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
- [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

## Tasks

- [TASK-1.md](./TASK-1.md)
- [TASK-2.md](./TASK-2.md)
- [TASK-3.md](./TASK-3.md)

## Arquivos Reais Envolvidos

- Documento de contrato (path a fixar na implementacao, sob a feature ou `docs/`)
- Modulo de geracao de payload/QR no backend alinhado a **US-5-02**
- [INTAKE-ATIVOS-INGRESSOS.md](../../../../INTAKE-ATIVOS-INGRESSOS.md) (rastreio pergunta sec. 15)

## Artefato Minimo

- Documento de contrato versionado + implementacao que gera payload conforme o contrato + teste(s) de forma ou golden file nao sensivel.

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
- Outras USs: [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) e [US-5-02](../US-5-02-SERVICO-E-API-EMISSAO/README.md) devem estar `done`
- [GOV-USER-STORY.md](../../../../../COMUM/GOV-USER-STORY.md)
