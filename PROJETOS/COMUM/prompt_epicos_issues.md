# Prompt de Execução — Criação dos Épicos e Issues do Projeto ETL de Leads

## Contexto

Você é um agente de engenharia responsável por materializar o planejamento de um projeto no repositório `npbb`. O PRD de referência é a fusão do ETL de leads com o mecanismo de importação do backend (arquivo `PROJETOS/LEAD-ETL-FUSION/PRD-LEAD-ETL-FUSION.md`).

Seu objetivo é criar **todos os arquivos de planejamento** — `EPICS.md` de cada fase e os arquivos individuais de épico — seguindo rigorosamente os templates e regras de nomeação definidos no PRD (seção 9).

---

## Tarefa

Crie a seguinte estrutura de arquivos dentro da pasta `PROJETOS/LEAD-ETL-FUSION/`, populando cada arquivo com conteúdo real (não placeholders):

```
PROJETOS/
└── LEAD-ETL-FUSION/
    ├── F1-NUCLEO-ETL/
    │   ├── EPICS.md
    │   ├── EPIC-F1-01-EXTRAIR-NUCLEO-COMPARTILHADO.md
    │   └── EPIC-F1-02-MODELO-CANONICO-LEAD-ROW.md
    │
    ├── F2-INTEGRACAO-BACKEND/
    │   ├── EPICS.md
    │   ├── EPIC-F2-01-USECASE-ETL-IMPORT.md
    │   ├── EPIC-F2-02-ENDPOINTS-PREVIEW-COMMIT.md
    │   └── EPIC-F2-03-SCHEMAS-E-DEPRECACAO-NORMALIZE.md
    │
    ├── F3-REFATORACAO-CLI/
    │   ├── EPICS.md
    │   ├── EPIC-F3-01-ORCHESTRATOR-CONSUME-CORE.md
    │   └── EPIC-F3-02-REMOCAO-DUPLICACOES.md
    │
    └── F4-UI-IMPORTACAO-AVANCADA/
        ├── EPICS.md
        ├── EPIC-F4-01-TAB-IMPORTACAO-AVANCADA.md
        ├── EPIC-F4-02-DQ-REPORT-WIDGET.md
        └── EPIC-F4-03-COERENCIA-NORMATIVA-E-GATE.md
```

---

## Regras obrigatórias

### Nomeação e frontmatter
- Todo arquivo começa com frontmatter YAML com os campos: `doc_id`, `version` (`"1.0"`), `status` (`"todo"`), `owner` (`"PM"`), `last_updated` (data de hoje).
- `doc_id` é o nome do arquivo sem extensão.
- `status` de todos os épicos e issues começa como `"todo"`.

### Conteúdo dos `EPICS.md`
Cada `EPICS.md` deve ter:
- **Objetivo da Fase** — uma frase que descreve o resultado concreto ao final da fase.
- **Gate de Saída da Fase** — critério objetivo de conclusão (ex: suite de testes passando, endpoint respondendo, `make eval-integrations: PASS`).
- **Tabela de Épicos** com colunas: `Epic ID | Nome | Objetivo | Status | Documento`.
- **Escopo desta Entrega** — o que está incluso e o que está explicitamente fora.

### Conteúdo dos arquivos de épico
Cada arquivo de épico deve ter:
- **Objetivo** — resultado técnico mensurável.
- **Resultado de Negócio Mensurável** — impacto verificável no sistema ou no usuário.
- **Definition of Done** — lista com critérios específicos e verificáveis para este épico (não genéricos).
- **Issues** — entre 2 e 4 issues por épico, cada uma com:
  - User story no formato `Como <papel>, quero <ação> para <resultado>`.
  - **Plano TDD** com os 3 passos: `Red`, `Green`, `Refactor`.
  - **Critérios de aceitação** no formato `Given / When / Then` (mínimo 2 por issue).
- **Artifact Mínimo do Épico** — path do arquivo de evidência a ser gerado em `artifacts/`.
- **Dependências** — links relativos para PRD, SCRUM-GOV e DECISION-PROTOCOL.

### Regras de conteúdo
- Nenhum placeholder como `"..."`, `"<texto>"` ou `"TODO"` — todo campo deve ter conteúdo real derivado do PRD.
- Ao planejar épicos e issues: considerar arquitetura modular, manutenibilidade e evitar monolitos (arquivos/funções grandes demais); priorizar responsabilidade única, baixo acoplamento e alta coesão.
- Issues de épicos diferentes não se referenciam diretamente — dependências entre épicos passam apenas pelo `EPICS.md` da fase.
- O plano TDD de cada issue deve mencionar arquivos reais do repositório (ex: `tests/core/test_column_normalize.py`, `backend/tests/test_leads_import_etl_endpoint.py`).
- Critérios de aceitação devem ser verificáveis por um agente automatizado ou por inspeção direta de output — sem critérios subjetivos.
- Ao concluir uma fase, a pasta da fase deve ser movida para `PROJETOS/LEAD-ETL-FUSION/feito/`, com links e automações ajustados no mesmo change set.

---

## Conteúdo esperado por fase

### F1 — Núcleo ETL

**Gate de saída:** todos os testes existentes em `backend/tests/` e `etl/` continuam passando após a migração dos módulos para `core/leads_etl/`.

**EPIC-F1-01** cobre a migração física de `etl/transform/column_normalize.py`, `etl/transform/segment_mapper.py`, `etl/validate/framework.py` e `etl/validate/checks_*.py` para `core/leads_etl/`, mantendo reexports nos paths originais.

**EPIC-F1-02** cobre a criação de `core/leads_etl/models/lead_row.py` — modelo Pydantic canônico com todos os campos possíveis de um lead, sem dependência de FastAPI, SQLModel ou ORM.

---

### F2 — Integração Backend

**Gate de saída:** `POST /leads/import/etl/preview` e `POST /leads/import/etl/commit` respondem corretamente para um XLSX fora do padrão; testes de endpoint passando.

**EPIC-F2-01** cobre `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py` — use case que orquestra extract → transform → validate → persist, com assinatura `async def import_leads_with_etl(file, evento_id, db, strict) -> ImportEtlResult`.

**EPIC-F2-02** cobre os dois novos endpoints em `backend/app/routers/leads.py`: `/leads/import/etl/preview` (dry-run, retorna DQ report + session_token) e `/leads/import/etl/commit` (persiste linhas aprovadas dado session_token).

**EPIC-F2-03** cobre a criação de `backend/app/schemas/lead_import_etl.py` (schemas `ImportEtlPreviewResponse`, `DQCheckResult`, `ImportEtlResult`) e a marcação de `backend/app/utils/lead_import_normalize.py` como deprecated com comentário canônico apontando para `core/leads_etl/transform/column_normalize`.

---

### F3 — Refatoração CLI

**Gate de saída:** `cli_extract.py` e `cli_spec.py` continuam funcionando sem alterações de interface; `etl/orchestrator/s*_core.py` importa de `core/leads_etl/` em vez de paths relativos internos.

**EPIC-F3-01** cobre a atualização dos arquivos `etl/orchestrator/s1_core.py` até `s4_core.py` para importar `column_normalize`, `segment_mapper` e o framework de validação de `core/leads_etl/`.

**EPIC-F3-02** cobre a remoção das duplicações em `etl/transform/` (mantendo apenas os reexports criados na F1) e a deleção definitiva de `backend/app/utils/lead_import_normalize.py` após confirmação de cobertura de testes.

---

### F4 — UI Importação Avançada

**Gate de saída:** `make eval-integrations: PASS` e `make ci-quality: PASS`; tab "Importação avançada" funcional em `/leads`; `artifacts/phase-f4/validation-summary.md` gerado com decisão `promote | hold`.

**EPIC-F4-01** cobre a adição de uma tab "Importação avançada" no frontend em `/leads`, que consome `POST /leads/import/etl/preview` e exibe o DQ report antes de permitir o commit.

**EPIC-F4-02** cobre o componente de DQ report no frontend — tabela expansível com colunas `check_name | severity | affected_rows | sample`, botão "Importar mesmo assim" habilitado apenas para linhas com `severity=warning` (bloqueado para `severity=error`).

**EPIC-F4-03** é o épico obrigatório de coerência normativa e gate. Deve conter exatamente as 3 issues abaixo:
- **ISSUE-F4-03-01:** Validar consistência entre `core/leads_etl/` e contratos documentados — `make eval-integrations` falha se houver divergência entre implementação e modelo canônico.
- **ISSUE-F4-03-02:** Validar cobertura de testes cross-camada — `make ci-quality` falha se não houver teste end-to-end cobrindo extract → transform → validate → persist.
- **ISSUE-F4-03-03:** Consolidar evidência de fase em `artifacts/phase-f4/validation-summary.md` com status de todos os épicos F1–F4 e decisão `promote | hold` com justificativa.

---

## Output esperado

Ao final da execução, todos os arquivos listados na estrutura acima devem existir no repositório com conteúdo completo. Nenhum arquivo deve ter campos vazios ou placeholders. Execute um `find PROJETOS/LEAD-ETL-FUSION -type f -name "*.md" | sort` ao final e liste os arquivos criados como confirmação.
