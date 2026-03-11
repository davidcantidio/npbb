# PRD — Fusão do ETL de Leads com o Mecanismo de Importação do Backend

**Repositório:** `davidcantidio/npbb` | **Branch base:** `codex/audit_arc`  
**Status:** Proposta  
**Última atualização:** 2026-03-03

---

## 1. Contexto e Problema

### 1.1 Estado atual

O sistema possui **dois mecanismos paralelos e desconectados** de ingestão de leads:

| | ETL CLI (`etl/`) | Importação via Backend (`backend/`) |
|---|---|---|
| **Entrada** | XLSX, PDF, PPTX (fora do padrão) | CSV/XLSX via upload HTTP |
| **Acionamento** | Manual via CLI (`cli_extract.py`, `cli_spec.py`) | Interface web em `/leads` |
| **Pipeline** | 4 estágios (s1–s4) com extract → transform → validate | Upload → preview mapeamento → insert em `stg_leads` |
| **Normalização** | `etl/transform/column_normalize.py`, `segment_mapper.py` | `backend/app/utils/lead_import_normalize.py` |
| **Validação** | `etl/validate/` (8+ checks modulares, framework próprio) | Implícita no usecase de importação |
| **Destino final** | Não conectado ao banco via API | `stg_leads` → `leads` |

### 1.2 Problemas identificados

- **Duplicação de lógica de normalização:** `etl/transform/column_normalize.py` e `backend/app/utils/lead_import_normalize.py` resolvem problemas similares de forma isolada.
- **Validações ricas desperdiçadas:** O framework de validação do ETL (`checks_schema`, `checks_duplicates`, `checks_not_null`, `checks_cross_source`, etc.) não está disponível no fluxo de importação da UI.
- **Ausência de tratamento para leads fora do padrão na UI:** Arquivos com colunas não-padrão, PDFs ou fontes misturadas só podem ser processados via CLI — não há caminho pela interface.
- **ETL não persiste no banco:** Após o processamento, os dados precisam ser importados manualmente via outro mecanismo.

### 1.3 Objetivo da fusão

Elevar o ETL de pipeline CLI para **biblioteca compartilhada**, que sirva tanto ao fluxo de importação do backend (HTTP/UI) quanto ao uso em batch (CLI). O resultado é um único caminho canônico de entrada de leads: **qualquer fonte passa pelos mesmos estágios de normalização e validação antes de persistir**.

---

## 2. Escopo

### Em escopo
- Extração do núcleo de transform e validate do ETL para um pacote compartilhado (`core/leads_etl/`)
- Integração desse núcleo no usecase de importação do backend
- Novo endpoint de importação "avançada" que aceita arquivos fora do padrão
- Relatório de qualidade de dados (DQ report) acessível via API
- CLI refatorada para consumir o mesmo núcleo (sem duplicação)

### Fora do escopo
- Extratores de PDF/PPTX na UI (extraem dados de relatórios de evento, não de leads — ficam só na CLI)
- Refatoração de `stg_leads` ou do modelo de banco
- Mudanças no pipeline de dashboard/relatórios DOCX

---

## 3. Arquitetura Proposta

### 3.1 Estrutura de diretórios alvo

```
npbb/
├── core/
│   └── leads_etl/                  ← NOVO pacote compartilhado
│       ├── __init__.py
│       ├── transform/
│       │   ├── column_normalize.py  ← migrado de etl/transform/
│       │   ├── segment_mapper.py    ← migrado de etl/transform/
│       │   └── config/
│       │       └── segment_mapping.yml
│       ├── validate/
│       │   ├── framework.py         ← migrado de etl/validate/
│       │   ├── checks_schema.py
│       │   ├── checks_duplicates.py
│       │   ├── checks_not_null.py
│       │   ├── checks_percentages.py
│       │   ├── checks_cross_source.py
│       │   ├── alerts.py
│       │   └── config/
│       │       └── datasets.yml
│       └── models/
│           └── lead_row.py          ← Pydantic model canônico de uma linha de lead
│
├── etl/                             ← CLI pipeline (consome core/leads_etl/)
│   ├── extract/                     ← inalterado (extratores de PDF, PPTX, XLSX especializados)
│   ├── orchestrator/                ← refatorado para importar de core/leads_etl/
│   ├── cli_extract.py
│   ├── cli_spec.py
│   └── cli_catalog.py
│
└── backend/
    └── app/
        ├── modules/
        │   └── leads_publicidade/
        │       └── application/
        │           ├── leads_import_usecases.py       ← atualizado
        │           └── leads_import_etl_usecases.py   ← NOVO
        ├── routers/
        │   └── leads.py                               ← novos endpoints
        ├── schemas/
        │   ├── lead_import.py
        │   └── lead_import_etl.py                     ← NOVO
        └── utils/
            └── lead_import_normalize.py               ← deprecado / delegado a core/
```

### 3.2 Princípios arquiteturais obrigatórios

1. **Nenhum arquivo monolítico:** Cada responsabilidade tem seu próprio módulo. Nenhum arquivo ultrapassa ~200 linhas.
2. **Núcleo sem dependência do framework web:** `core/leads_etl/` não importa FastAPI, SQLModel ou qualquer ORM. É Python puro + Pydantic.
3. **Use cases como única camada com acesso ao banco:** Toda persistência fica em `leads_import_etl_usecases.py`.
4. **Configuração via YAML, não hardcode:** Mapeamentos de segmento, regras de schema e contratos de cobertura continuam em arquivos `.yml` no `core/`.
5. **Observabilidade preservada:** Os módulos `*_observability.py` do orchestrator devem seguir o mesmo padrão s1–s4 já existente.

---

## 4. Fluxo de Dados Unificado

```
                    ┌─────────────────────────────────────────────────┐
                    │           FONTE DE ENTRADA                       │
                    └───────────┬─────────────────────┬───────────────┘
                                │                     │
                         Upload HTTP            CLI batch
                    (CSV/XLSX padrão       (XLSX não-padrão,
                     ou não-padrão)         PDF, PPTX)
                                │                     │
                    ┌───────────▼─────────────────────▼───────────────┐
                    │           EXTRACT                                 │
                    │  (parser por tipo: xlsx_leads, pdf, pptx…)       │
                    └───────────────────────┬─────────────────────────┘
                                            │  DataFrame raw
                    ┌───────────────────────▼─────────────────────────┐
                    │  TRANSFORM  (core/leads_etl/transform/)          │
                    │  column_normalize → segment_mapper               │
                    └───────────────────────┬─────────────────────────┘
                                            │  DataFrame normalizado
                    ┌───────────────────────▼─────────────────────────┐
                    │  VALIDATE  (core/leads_etl/validate/)            │
                    │  checks_schema → checks_not_null →               │
                    │  checks_duplicates → checks_cross_source         │
                    └───────────┬───────────────────────┬─────────────┘
                                │ ValidationResult      │
                    ┌───────────▼──────────┐  ┌─────────▼─────────────┐
                    │   LOAD (backend)     │  │  DQ Report (CLI/API)  │
                    │   stg_leads → leads  │  │  render_dq_report.py  │
                    └──────────────────────┘  └───────────────────────┘
```

---

## 5. Componentes Novos e Alterados

### 5.1 `core/leads_etl/models/lead_row.py` — Modelo canônico *(novo)*

Define o contrato de dados entre transform e validate. Pydantic BaseModel com todos os campos possíveis de um lead (nome, email, telefone, cpf, segmento, origem, evento_id, etc.), todos opcionais com validadores de tipo. É o único lugar onde se define o que é um "lead válido".

### 5.2 `core/leads_etl/transform/column_normalize.py` — Normalização de colunas *(migrado + expandido)*

- Migra lógica de `etl/transform/column_normalize.py` e absorve `backend/app/utils/lead_import_normalize.py`
- Função principal: `normalize_columns(df: DataFrame, mapping: dict) -> DataFrame`
- Sem side effects; retorna novo DataFrame
- Testável de forma isolada

### 5.3 `core/leads_etl/validate/framework.py` — Framework de validação *(migrado)*

- Migrado de `etl/validate/framework.py`
- Interface: `run_checks(df: DataFrame, checks: list[CheckFn]) -> ValidationResult`
- `ValidationResult` contém: linhas aprovadas, linhas rejeitadas, alertas por check

### 5.4 `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py` — Use case ETL *(novo)*

Responsabilidades:
- Receber arquivo (UploadFile ou path)
- Chamar extrator adequado (by file type)
- Chamar `column_normalize` + `segment_mapper`
- Chamar `run_checks` com suite de validações configurável
- Persistir linhas aprovadas em `stg_leads` (via session)
- Retornar `ImportEtlResult` com contagens e relatório de qualidade

```python
# Assinatura pública
async def import_leads_with_etl(
    file: UploadFile,
    evento_id: int,
    db: Session,
    strict: bool = False,          # se True, rejeita lote inteiro se há erros
) -> ImportEtlResult:
    ...
```

### 5.5 `backend/app/routers/leads.py` — Endpoints novos *(atualizado)*

Adicionar dois endpoints ao router existente (sem alterar os atuais):

```
POST /leads/import/etl/preview
    → Retorna DQ report sem persistir (dry-run)
    → Aceita multipart/form-data com arquivo + evento_id

POST /leads/import/etl/commit
    → Persiste linhas aprovadas após preview confirmado pelo usuário
    → Recebe session_token do preview + evento_id
```

A separação preview/commit preserva o padrão já existente na UI de importação.

### 5.6 `backend/app/schemas/lead_import_etl.py` — Schemas *(novo)*

```python
class ImportEtlPreviewResponse(BaseModel):
    session_token: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    dq_report: list[DQCheckResult]

class DQCheckResult(BaseModel):
    check_name: str
    severity: Literal["error", "warning", "info"]
    affected_rows: int
    sample: list[dict]
```

---

## 6. Plano de Migração (sem quebrar o existente)

### Fase 1 — Extrair o núcleo (sem alterar comportamento)
1. Criar `core/leads_etl/` com `__init__.py`
2. Mover `etl/transform/column_normalize.py` → `core/leads_etl/transform/column_normalize.py` (com reexport em `etl/transform/` para não quebrar imports existentes)
3. Mover `etl/transform/segment_mapper.py` → `core/leads_etl/transform/segment_mapper.py` (idem)
4. Mover `etl/validate/framework.py` e `checks_*.py` → `core/leads_etl/validate/` (com reexports)
5. Criar `core/leads_etl/models/lead_row.py`
6. Rodar suite de testes existente — deve passar sem alterações

### Fase 2 — Integrar no backend
1. Criar `leads_import_etl_usecases.py` consumindo `core/leads_etl/`
2. Criar `lead_import_etl.py` schemas
3. Adicionar endpoints `/leads/import/etl/preview` e `/leads/import/etl/commit`
4. Deprecar `backend/app/utils/lead_import_normalize.py` (marcar com `# DEPRECATED: use core/leads_etl/transform/column_normalize`), sem deletar ainda

### Fase 3 — Refatorar CLI para consumir núcleo
1. Atualizar `etl/orchestrator/s*_core.py` para importar de `core/leads_etl/` em vez de caminhos relativos
2. Remover duplicações entre `etl/transform/` e `core/leads_etl/transform/` (manter apenas reexports)
3. Deletar `backend/app/utils/lead_import_normalize.py` após confirmação de cobertura de testes

### Fase 4 — UI (frontend)
1. Adicionar tab "Importação avançada" em `/leads` que usa os novos endpoints ETL
2. Exibir DQ report em formato de tabela expansível antes do commit
3. Botão "Importar mesmo assim" (com aviso) para linhas com warnings (não errors)

---

## 7. Testes Requeridos

Cada componente deve ter seu próprio arquivo de teste. Nenhum arquivo de teste deve testar mais de uma camada.

| Arquivo de teste | O que cobre |
|---|---|
| `tests/core/test_column_normalize.py` | Normalização com fixtures de DataFrames variados |
| `tests/core/test_segment_mapper.py` | Mapeamento via YAML |
| `tests/core/test_validate_framework.py` | Execução de checks e agregação de resultados |
| `tests/core/test_checks_duplicates.py` | Detecção de CPF/email duplicado |
| `tests/core/test_checks_schema.py` | Colunas obrigatórias ausentes |
| `backend/tests/test_leads_import_etl_usecase.py` | Use case completo com DB fake (in-memory) |
| `backend/tests/test_leads_import_etl_endpoint.py` | Endpoints preview e commit (TestClient) |

---

## 8. Critérios de Aceite

- [ ] `POST /leads/import/etl/preview` retorna DQ report com contagem correta de linhas válidas/inválidas para um XLSX fora do padrão
- [ ] `POST /leads/import/etl/commit` persiste apenas as linhas aprovadas na `stg_leads`
- [ ] Pipeline CLI (`cli_extract.py`) continua funcionando sem alterações de interface
- [ ] Todos os testes existentes continuam passando após a Fase 1
- [ ] Nenhum arquivo novo em `core/leads_etl/` ultrapassa 200 linhas
- [ ] `core/leads_etl/` não importa nada de `fastapi`, `sqlmodel` ou `alembic`
- [ ] `backend/app/utils/lead_import_normalize.py` marcado como deprecated na Fase 2

---

## 9. Estrutura de Governança do Projeto

### 9.1 Árvore de diretórios obrigatória

Todo o planejamento, rastreabilidade e governança deste PRD deve ser materializado na seguinte estrutura de arquivos no repositório:

```
PROJETOS/
├── COMUM/
│   ├── DECISION-PROTOCOL.md
│   ├── WORK-ORDER-SPEC.md
│   ├── SPRINT-LIMITS.md
│   └── GOV-SCRUM.md
│
└── LEAD-ETL-FUSION/
    ├── feito/                  ← fases concluidas saem da area ativa e vao para arquivo operacional
    ├── PRD-LEAD-ETL-FUSION.md
    ├── F1-NUCLEO-ETL/
    │   ├── EPICS.md            ← índice dos épicos da fase
    │   ├── EPIC-F1-01-EXTRAIR-NUCLEO-COMPARTILHADO.md
    │   └── EPIC-F1-02-MODELO-CANONICO-LEAD-ROW.md
    ├── F2-INTEGRACAO-BACKEND/
    │   ├── EPICS.md
    │   ├── EPIC-F2-01-USECASE-ETL-IMPORT.md
    │   ├── EPIC-F2-02-ENDPOINTS-PREVIEW-COMMIT.md
    │   └── EPIC-F2-03-SCHEMAS-E-DEPRECACAO-NORMALIZE.md
    ├── F3-REFATORACAO-CLI/
    │   ├── EPICS.md
    │   ├── EPIC-F3-01-ORCHESTRATOR-CONSUME-CORE.md
    │   └── EPIC-F3-02-REMOCAO-DUPLICACOES.md
    └── F4-UI-IMPORTACAO-AVANCADA/
        ├── EPICS.md
        ├── EPIC-F4-01-TAB-IMPORTACAO-AVANCADA.md
        ├── EPIC-F4-02-DQ-REPORT-WIDGET.md
        └── EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md
```

### 9.2 Arquivos de governança raiz (`PROJETOS/`)

Estes quatro arquivos devem existir em `PROJETOS/COMUM/` antes de qualquer trabalho nas fases. Eles estabelecem o contrato de operação do projeto.

**`GOV-SCRUM.md`** — define a cadeia `PRD → Fases → Épicos → Issues → Microtasks`. Deve incluir:
- fluxo de decomposição de trabalho (5 níveis)
- DoD por tipo de item (PRD, Fase, Épico, Issue, Microtask, Sprint)
- regras anti "jira inflation" (sem tarefa sem quebra, sem sprint como camada estrutural, sem datas inventadas)
- regra de arquivamento: fase concluída deve ser movida para `LEAD-ETL-FUSION/feito/`

**`SPRINT-LIMITS.md`** — define enforcement automático de limites. Deve incluir:
- `max_items_por_sprint: 12`
- `max_tamanho_por_task: 1 dia útil ou 3 story points`
- `max_itens_criticos_paralelos: 2 por escritório`
- contrato `SPRINT_OVERRIDE` com campos `override_key`, `coalescing_key`, `rollback_token`, `rollback_snapshot_ref`
- regra: violação gera status `BLOCKED_LIMIT` e abre evento `SPRINT_LIMIT_ALERT`
- regra operacional: fase concluída não permanece na área ativa do projeto

**`WORK-ORDER-SPEC.md`** — contrato de demanda entre camadas. Schema obrigatório com os campos: `work_order_id`, `idempotency_key`, `risk_class`, `risk_tier`, `data_sensitivity`, `expected_output`, `budget.hard_cap`, `status`. SLA classes: `instantaneo | normal | overnight`.

**`DECISION-PROTOCOL.md`** — protocolo de decisões com side effect. Deve cobrir:
- taxonomia de risco canônica (`R0`–`R3`)
- formato YAML da decision com `decision_id`, `risk_tier`, `side_effect_class`, `explicit_human_approval`, `rollback_plan`
- máquina de estados: `PENDING → APPROVED | REJECTED | KILLED | EXPIRED`
- SLA: risco alto p95 ≤ 15 min, risco médio p95 ≤ 60 min

### 9.3 Formato do `EPICS.md` por fase

Cada pasta de fase deve conter um `EPICS.md` seguindo este template:

```markdown
---
doc_id: "PHASE-Fx-EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# Fx <Nome da Fase> — Épicos

## Objetivo da Fase
<Uma frase descrevendo o resultado esperado ao final da fase.>

## Gate de Saída da Fase
<Comando ou critério objetivo que determina conclusão. Ex: todos os testes da fase passando.>

## Épicos da Fase
| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-Fx-01` | ... | ... | `todo|active|done` | [EPIC-Fx-01-NOME.md](./EPIC-Fx-01-NOME.md) |

## Escopo desta Entrega
<O que está incluso nesta fase. O que está fora.>
```

### 9.4 Formato dos arquivos de épico (`EPIC-Fx-NN-NOME.md`)

Cada épico deve ter seu próprio arquivo com este template:

```markdown
---
doc_id: "EPIC-Fx-NN-NOME.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# EPIC-Fx-NN — <Título do Épico>

## Objetivo
<Resultado técnico mensurável que este épico entrega.>

## Resultado de Negócio Mensurável
<Como isso impacta o sistema ou o usuário de forma verificável.>

## Definition of Done (Scrum)
- todas as issues do épico em estado `Done`
- <critério técnico específico, ex: testes passando, endpoint respondendo>
- evidência consolidada registrada

## Issues

### ISSUE-Fx-NN-01 — <Título>
**User story**
Como <papel>, quero <ação> para <resultado>.

**Plano TDD**
1. `Red`: <o que escrever para falhar>
2. `Green`: <implementação mínima>
3. `Refactor`: <limpeza e padronização>

**Critérios de aceitação**
- Given <contexto>, When <ação>, Then <resultado verificável>.

## Artifact Mínimo do Épico
- `artifacts/phase-fx/epic-fx-nn-<slug>.md` com evidências e status final

## Dependências
- [PRD](../../PRD-LEAD-ETL-FUSION.md)
- [GOV-SCRUM](../../COMUM/GOV-SCRUM.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
```

### 9.5 Épico obrigatório de coerência normativa (`EPIC-Fx-03-COERENCIA-NORMATIVA-E-GATE.md`)

A última fase (F4) deve conter obrigatoriamente o épico `EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md`, responsável por fechar o projeto com evidência auditável. Ele deve incluir as seguintes issues:

**ISSUE-F4-03-01 — Validar consistência entre `core/leads_etl/` e contratos documentados**
- Given: qualquer divergência entre a implementação e o modelo canônico `lead_row.py`, When: `make eval-integrations` roda, Then: gate falha.

**ISSUE-F4-03-02 — Validar cobertura de testes cross-camada**
- Given: ausência de testes para o fluxo ETL end-to-end (extract → transform → validate → persist), When: `make ci-quality` roda, Then: gate falha.

**ISSUE-F4-03-03 — Consolidar evidência de fase e decisão promote/hold**
- Given: evidências dispersas sem resumo único de fase, When: revisão de fase ocorre, Then: promoção fica bloqueada.
- Given: artifact único com resultado de gate e decisão final, When: revisão de fase ocorre, Then: fase apta a promover.

O artifact mínimo deste épico é `artifacts/phase-f4/validation-summary.md` com:
- status de `make eval-integrations` e `make ci-quality`
- status de todos os épicos F1–F4
- decisão de fase (`promote | hold`) com justificativa

### 9.6 Regras de nomeação e versionamento

- Todos os arquivos de fase: `EPIC-Fx-NN-NOME-EM-MAIUSCULO.md` (ex: `EPIC-F2-01-USECASE-ETL-IMPORT.md`)
- `version` começa em `"1.0"` e incrementa a cada alteração de escopo
- `status` válidos: `todo | active | done | cancelled`
- `owner` deve ser sempre explícito (ex: `"PM"`, `"backend-dev"`)
- Nenhum arquivo de épico deve referenciar issues de outro épico diretamente — dependências entre épicos passam pelo `EPICS.md` da fase

## 10. Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Divergência entre `column_normalize` do ETL e do backend | Alta | A Fase 1 expõe a divergência via testes — resolver antes da Fase 2 |
| Extratores de XLSX do ETL dependem de lógica específica de festival | Média | Manter `etl/extract/xlsx_leads.py` intacto; o núcleo só recebe DataFrame já extraído |
| UI quebrar preview atual durante refatoração de router | Baixa | Novos endpoints têm paths distintos (`/etl/preview`, `/etl/commit`) |
| Orquestrador s1–s4 com acoplamento forte ao path relativo | Média | Reexports em `etl/transform/` e `etl/validate/` durante Fase 1 evitam quebra |
