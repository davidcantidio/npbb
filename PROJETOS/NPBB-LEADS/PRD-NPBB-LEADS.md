# PRD — NPBB: Pipeline de Leads Bronze → Silver → Gold
**version:** 2.0.0 | **last_updated:** 2026-03-03
**status:** aprovado | **owner:** David

---

## 1. Visão do Produto

Substituir as duas telas de importação existentes ("Importação" e "Importação
Avançada") por um único fluxo unificado que processa arquivos de leads em três
camadas progressivas de qualidade: Bronze (arquivo bruto preservado), Silver
(dados mapeados com relacionamentos, sem tratamento) e Gold (dados tratados,
normalizados e validados pelo pipeline ETL).

O objetivo é que **toda origem de dado seja rastreável desde o arquivo original
até o lead tratado no banco**, com rastreabilidade completa de quem enviou,
quando, por qual plataforma e qual estado de processamento cada lote atingiu.

---

## 2. Fluxo Geral (Bronze → Silver → Gold)

Operador faz upload do arquivo (CSV ou XLSX)
│
▼
[BRONZE] ─ arquivo preservado como-está no storage + metadados de envio
│         (quem enviou, plataforma de origem, data de envio)
│
▼ Operador realiza mapeamento assistido na UI
[SILVER] ─ dados como vieram do arquivo, mas com:
│         - evento vinculado
│         - colunas mapeadas para campos canônicos
│         - aliases de coluna salvos para reuso futuro
│         - relacionamentos FK estabelecidos no banco
│
▼ Sistema executa pipeline de tratamento automático
[GOLD]   ─ dados normalizados, deduplicados, validados pelo lead_pipeline
- CPF, telefone, datas normalizados
- duplicidades (CPF × evento) removidas
- contrato Databricks validado
- relatório de qualidade gerado (report.json + summary.md)

---

## 3. Escopo

### Dentro do escopo
- Upload único de CSV ou XLSX com registro de metadados de envio
- Armazenamento do arquivo bruto (Postgres bytea ou link de storage externo)
- UI de mapeamento de colunas com sugestão automática e salvamento de aliases
- Persistência Silver: dados brutos com relacionamentos, sem normalização
- Pipeline Gold: integração do `lead_pipeline` existente (PROJETOS/lead_pipeline/)
  como serviço interno executado pelo backend FastAPI
- Relatório de qualidade por lote (status PASS / PASS_WITH_WARNINGS / FAIL)
- Unificação das telas "Importação" e "Importação Avançada" em uma única UI

### Fora do escopo
- Integração com Google Drive (fase futura — por ora, storage local ou bytea)
- Pipeline de auditoria de PPT (`audit-ppt`) — não faz parte deste fluxo
- Notificação por email de resultado do pipeline
- Agendamento de reprocessamento automático

---

## 4. Modelo de Dados (novas tabelas / campos)

### `lead_batches` — lotes de importação
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID PK | identificador do lote |
| `enviado_por` | FK → users | quem fez o upload |
| `plataforma_origem` | varchar | ex: "email", "whatsapp", "drive", "manual" |
| `data_envio` | timestamptz | quando o arquivo chegou ao remetente |
| `data_upload` | timestamptz | quando foi feito o upload no sistema |
| `nome_arquivo_original` | varchar | nome original do arquivo |
| `arquivo_bronze` | bytea \| varchar | arquivo bruto ou URL no storage |
| `stage` | enum | `bronze` \| `silver` \| `gold` |
| `evento_id` | FK → eventos | evento vinculado (definido no mapeamento) |
| `pipeline_status` | varchar | `pending` \| `pass` \| `pass_with_warnings` \| `fail` |
| `pipeline_report` | jsonb | report.json gerado pelo lead_pipeline |

### `lead_column_aliases` — aliases de colunas reutilizáveis
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID PK | |
| `nome_coluna_original` | varchar | nome exato da coluna no arquivo fonte |
| `campo_canonico` | varchar | campo canônico do banco (ex: "cpf", "email") |
| `plataforma_origem` | varchar | contexto onde esse alias é válido |
| `criado_por` | FK → users | operador que definiu o mapeamento |

### `leads_silver` — dados brutos mapeados (sem normalização)
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID PK | |
| `batch_id` | FK → lead_batches | |
| `row_index` | int | linha de origem no arquivo |
| `dados_brutos` | jsonb | linha como veio do arquivo, após mapeamento de colunas |
| `evento_id` | FK → eventos | |

> Nota: a tabela `leads` existente passa a representar o estado **Gold** —
> linhas promovidas após pipeline bem-sucedido.

---

## 5. Stack Vinculante
- Backend: FastAPI + SQLModel + Alembic (padrão do projeto)
- Frontend: React + MUI (padrão do projeto)
- Auth: JWT obrigatório em todos os endpoints
- Pipeline ETL: `PROJETOS/lead_pipeline/` — importado como módulo Python interno
- PYTHONPATH: sempre `/workspace:/workspace/backend`
- Testes: `TESTING=true` usa SQLite; testes de pipeline rodam com fixtures de arquivo

---

## 6. Requisitos Funcionais

| ID | Requisito | Fase | Prioridade |
|---|---|---|---|
| RF-01 | Upload de CSV/XLSX com registro de quem enviou, plataforma e data de envio | Bronze | Must |
| RF-02 | Arquivo original preservado integralmente no banco ou storage | Bronze | Must |
| RF-03 | UI unificada (remover "Importação Avançada" como rota separada) | Bronze | Must |
| RF-04 | Sugestão automática de mapeamento de colunas por nome e aliases salvos | Silver | Must |
| RF-05 | Operador define evento de referência e confirma mapeamento de colunas | Silver | Must |
| RF-06 | Aliases de coluna salvos por plataforma de origem para reuso futuro | Silver | Must |
| RF-07 | Dados brutos mapeados persistidos em `leads_silver` com FK para o lote | Silver | Must |
| RF-08 | Pipeline Gold executado automaticamente após confirmação Silver | Gold | Must |
| RF-09 | Relatório de qualidade por lote acessível na UI (status + métricas) | Gold | Must |
| RF-10 | Leads aprovados pelo pipeline promovidos para tabela `leads` (Gold) | Gold | Must |
| RF-11 | Lote com status FAIL não promove nenhum lead; exibe erros ao operador | Gold | Must |

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Meta |
|---|---|---|
| NF-01 | Upload de arquivo até 50MB sem timeout | < 30s de resposta da API |
| NF-02 | Pipeline Gold executado de forma assíncrona (não bloqueia a UI) | Background task FastAPI |
| NF-03 | Aliases de mapeamento reutilizáveis entre lotes do mesmo remetente | Lookup automático por plataforma_origem |
| NF-04 | Rastreabilidade completa: todo lead Gold tem `batch_id` e `row_index` de origem | FK obrigatória |

---

## 8. Fases

| Fase | Nome | Objetivo | Status |
|---|---|---|---|
| F1 | Bronze — Ingestão | Upload + preservação do arquivo + metadados de envio + UI unificada | 🔲 |
| F2 | Silver — Mapeamento | Mapeamento de colunas, aliases, vinculação de evento, persistência silver | 🔲 |
| F3 | Gold — Pipeline | Execução do lead_pipeline, validação, promoção para tabela leads | 🔲 |

---

## 9. Definition of Done do Projeto
- [ ] Fluxo Bronze → Silver → Gold funcional de ponta a ponta
- [ ] UI de importação unificada (rotas antigas removidas ou redirecionadas)
- [ ] Arquivo original recuperável a partir do lote
- [ ] Relatório de qualidade visível na UI por lote
- [ ] Leads Gold com FK rastreável até o arquivo de origem
- [ ] CI verde (sem regressão nos 283+ testes existentes)

---

## 10. Referências de Código Existente
- Pipeline ETL: `PROJETOS/lead_pipeline/` — `run_pipeline()`, `PipelineConfig`, `PipelineResult`
- Profiles de fonte suportados: `source_adapter.py` — canonico, bb_v1, bb_v2, park, ticketing, ssf_*, nps, landing, batuke, vert_battle
- Contratos de qualidade: `contracts.py` — `validate_databricks_contract()`
- Normalização: `normalization.py` — CPF, telefone, email, datas, local
- Mapeamento de headers: `constants.py` — `HEADER_SYNONYMS` (base para alias automático)
- Taxonomia de eventos: `event_taxonomy.py` — `classify_event_type()`

