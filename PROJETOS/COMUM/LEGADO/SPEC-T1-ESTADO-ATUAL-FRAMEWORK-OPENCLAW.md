---
doc_id: "SPEC-T1-ESTADO-ATUAL-FRAMEWORK-OPENCLAW.md"
version: "1.0"
status: "historical"
owner: "PM"
last_updated: "2026-03-26"
---

# SPEC-T1 — Estado atual do framework OpenClaw

> Registro normativo do **estado efetivo** do framework **antes** da migração documental
> descrita em [SPEC-PIPELINE-PRD-SEM-FEATURES.md](SPEC-PIPELINE-PRD-SEM-FEATURES.md). Este ficheiro **não** substitui [GOV-FRAMEWORK-MASTER.md](GOV-FRAMEWORK-MASTER.md);
> permanece como **baseline histórica** para comparar com o alvo. Para o desenho da migração e critérios de aceite atuais, use a SPEC de pipeline (T2).

## 1. Entrypoints e cadeia normativa

| Fonte | Cadeia declarada | Observação |
|--------|------------------|------------|
| [AGENTS.md](../../AGENTS.md) | `Intake -> PRD -> Features -> User Stories -> Tasks -> Revisoes -> Auditorias de Feature` | Não menciona SQLite/Postgres; layout canónico aponta para `GOV-FRAMEWORK-MASTER.md`. |
| [boot-prompt.md](boot-prompt.md) | Mesma hierarquia; `feature-first` no PRD e planejamento | Nível 3 instrui ler PRD e **entender features do projeto, user stories planejadas**, etc. |
| [SESSION-MAPA.md](SESSION-MAPA.md) | Pós-PRD: `Feature -> User Story -> Task` | Oito prompts ativos; `SESSION-PLANEJAR-PROJETO` cobre **PRD → features, US e tasks**. |

**Nota (alvo futuro):** incluir etapa explícita `Execução` e alinhar nomenclatura com `Review` vs `Revisoes` em todos os entrypoints.

## 2. GOV-FRAMEWORK-MASTER (v2.6)

- **Delivery-first / feature-first:** PRD e planejamento centrados em features; referência explícita a `TEMPLATE-PRD.md` para estrutura de features.
- **Estrutura de pastas:** `PRD-<PROJETO>.md` + `features/FEATURE-*/...` (ver [GOV-FRAMEWORK-MASTER.md](GOV-FRAMEWORK-MASTER.md)).
- **Modos:** `boot-prompt` descobre Feature/US/Task; `SESSION-MAPA` — intake/PRD humanos, pós-PRD na hierarquia Feature > US > Task.

## 3. PRD hoje: acoplamento forte a Features e User Stories

### [TEMPLATE-PRD.md](TEMPLATE-PRD.md)

- Secção **# 12. Features do Projeto** como eixo principal.
- Cada feature inclui tabela **User Stories planejadas** (US ID, título, SP, dependências).
- Checklist (§16) exige features com critérios de aceite, `depende_de`, **lista de US planejadas**, impacts por camada.

### [PROMPT-INTAKE-PARA-PRD.md](PROMPT-INTAKE-PARA-PRD.md)

- PRD deve usar **`Features do Projeto` como eixo principal**.
- Rastreabilidade mínima: `feature -> fase -> epico -> issue` (via `GOV-ISSUE-FIRST.md`).
- Requisitos mínimos do PRD incluem **`Features do Projeto`** e critérios por feature.

### [SESSION-CRIAR-PRD.md](SESSION-CRIAR-PRD.md)

- Princípio: **`feature-first` no PRD**; secção **`Features do Projeto`** como eixo do rascunho.
- Validação exige secção `Features do Projeto`, critérios por feature e rastreabilidade **`Feature -> User Story -> Task`**.
- Resumo do rascunho conta **User Stories planejadas**.

**Conclusão T1:** o framework ativo **exige** que o PRD liste features e, no template/prompt, user stories planejadas — em tensão com o alvo «PRD sem Features/US» no ficheiro PRD.

## 4. Planejamento pós-PRD: SESSION-PLANEJAR-PROJETO (v3.0)

- **Um único prompt** para PRD → features, user stories e tasks (com gate do agente senior).
- **Pré-condição:** sync do índice **SQLite** via `./bin/sync-openclaw-projects-db.sh`; comparação DB vs Markdown; **`DRIFT_INDICE`**; Markdown prevalece.
- Bloqueio se PRD (ou base+adendo) **não trouxer features claras**, critérios por feature ou rastreabilidade mínima Feature → US → Task.
- Ordem obrigatória: **Features → User Stories → Tasks**.

**Conclusão T1:** a decomposição não está fatiada em etapas documentais separadas (prompts/sessions dedicados); está concentrada em [SESSION-PLANEJAR-PROJETO.md](SESSION-PLANEJAR-PROJETO.md).

## 5. Índice operacional: `scripts/openclaw_projects_index/`

### Contrato atual ([README.md](../../scripts/openclaw_projects_index/README.md), [schema.sql](../../scripts/openclaw_projects_index/schema.sql))

- **Motor:** SQLite derivado; **fonte de verdade:** Markdown + Git.
- **Schema v4** (`PRAGMA user_version = 4`): `projects`, `features`, `user_stories`, `tasks`, `feature_audits`, `governance_documents`, `project_documents`, `documents`, **FTS5** `documents_fts`, `document_chunks`, `embeddings` (BLOB), `sync_meta`.
- **Variáveis:** `OPENCLAW_REPO_ROOT`, `OPENCLAW_PROJECTS_DB` (default sob `openclaw-workspace/.openclaw/openclaw-projects.sqlite`).
- **Sync:** [sync.py](../../scripts/openclaw_projects_index/sync.py) — varredura `PROJETOS/**/*.md`, PyYAML no front matter, classificação feature-first.
- **Chunks:** [chunk_documents.py](../../scripts/openclaw_projects_index/chunk_documents.py) opcional; embeddings previstos como pipeline externo.

### Lacunas em relação ao alvo Postgres (para trabalho posterior T13–T14)

- Não há tabelas **`execution_commits`** nem **`sync_runs`** (apenas `sync_meta` com chaves como `last_sync_at`, `repo_root`, `schema_bundle_version`).
- Vetores: `embeddings.embedding` é **BLOB** SQLite, não **pgvector**.
- Nome `governance_documents` vs alvo com `documents` genérico + governança — alinhamento na spec Postgres.

### Integração com bin

- [sync-openclaw-projects-db.sh](../../bin/sync-openclaw-projects-db.sh) delega para `sync.py`.

## 6. Resumo executivo T1

| Dimensão | Estado atual |
|----------|--------------|
| PRD | Template, prompt de intake→PRD e sessão criar-PRD **centrados em Features e US no PRD**. |
| Pipeline documental | Decomposição pós-PRD **monolítica** em `SESSION-PLANEJAR-PROJETO` + gate senior. |
| Índice | **SQLite v4** com FTS5, chunks e embeddings BLOB; **sem** `execution_commits` / `sync_runs`. |
| Markdown/Git | Canónicos explicitamente no índice e na governança. |

## 7. Leitura obrigatória coberta por T1

Ficheiros e diretório analisados para elaborar esta SPEC:

- [AGENTS.md](../../AGENTS.md)
- [GOV-FRAMEWORK-MASTER.md](GOV-FRAMEWORK-MASTER.md)
- [SESSION-MAPA.md](SESSION-MAPA.md)
- [SESSION-CRIAR-PRD.md](SESSION-CRIAR-PRD.md)
- [SESSION-PLANEJAR-PROJETO.md](SESSION-PLANEJAR-PROJETO.md)
- [PROMPT-INTAKE-PARA-PRD.md](PROMPT-INTAKE-PARA-PRD.md)
- [TEMPLATE-PRD.md](TEMPLATE-PRD.md)
- [boot-prompt.md](boot-prompt.md)
- [scripts/openclaw_projects_index/](../../scripts/openclaw_projects_index/) (`schema.sql`, `README.md`, `sync.py`, `chunk_documents.py`, `requirements.txt`)

## 8. Delta pós-migração documental (referência)

As secções **1–7** descrevem o estado **antes** das entregas alinhadas a [SPEC-PIPELINE-PRD-SEM-FEATURES.md](SPEC-PIPELINE-PRD-SEM-FEATURES.md). Em resumo, o framework passou a:

- Separar o contrato do PRD (`GOV-PRD.md`, `TEMPLATE-PRD.md` revisado) do backlog em manifestos `FEATURE-*.md` (`GOV-FEATURE.md`).
- Fatir a decomposição em `SESSION-DECOMPOR-PRD-EM-FEATURES.md`, `SESSION-DECOMPOR-FEATURE-EM-US.md`, `SESSION-DECOMPOR-US-EM-TASKS.md` com `PROMPT-*-PARA-*` correspondentes.
- Tratar `SESSION-PLANEJAR-PROJETO.md` como **router legado**.
- Declarar Postgres como read model alvo em [SPEC-INDICE-PROJETOS-POSTGRES.md](SPEC-INDICE-PROJETOS-POSTGRES.md) (implementação em `scripts/` evolui em paralelo).

Os **entrypoints** e o **índice SQLite** podem ainda refletir texto ou tooling em transição; ver SPEC de pipeline e `SESSION-MAPA.md` para o contrato vigente.
