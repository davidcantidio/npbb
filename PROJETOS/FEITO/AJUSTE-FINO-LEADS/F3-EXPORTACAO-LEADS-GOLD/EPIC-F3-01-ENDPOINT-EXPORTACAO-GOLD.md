---
doc_id: "EPIC-F3-01-ENDPOINT-EXPORTACAO-GOLD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F3-01 — Endpoint e Serviço de Exportação Gold
**projeto:** AJUSTE-FINO-LEADS | **fase:** F3 | **status:** ✅

---
## 1. Resumo do Épico

Criar o endpoint `GET /leads/export/gold` e o serviço de geração de arquivos de exportação (.xlsx e .csv). O endpoint filtra leads cujo batch possui `stage=gold` e `pipeline_status IN (pass, pass_with_warnings)`, opcionalmente filtrando por `evento_id`, e retorna o arquivo binário com header `Content-Disposition` para download direto.

## 2. Contexto Arquitetural

- Modelo `Lead` em `backend/app/models/models.py` — campo `batch_id` referencia `LeadBatch`
- Modelo `LeadBatch` em `backend/app/models/` — campos `stage` e `pipeline_status`
- Router de leads: `backend/app/routers/leads.py`
- Dashboard endpoint: `GET /dashboard/leads` em `backend/app/routers/`
- Geração XLSX: biblioteca `openpyxl` (já no projeto ou adicionar)
- Geração CSV: módulo `csv` da stdlib com encoding UTF-8 BOM e separador `;`
- PYTHONPATH: `/workspace:/workspace/backend`

## 3. Riscos e Armadilhas

- Exportação com muitos registros pode ser lenta — considerar streaming ou limite de registros
- O join entre `Lead` e `LeadBatch` para filtrar por `stage` e `pipeline_status` deve ser eficiente (índices)
- CSV com encoding UTF-8 BOM é necessário para compatibilidade com Excel em pt-BR
- Se `openpyxl` não estiver no `requirements.txt`, adicioná-lo como dependência
- Leads sem `batch_id` (leads legados) não devem ser incluídos na exportação Gold

## 4. Definition of Done do Épico

- [ ] Serviço `generate_gold_export(db, evento_id, formato)` retorna bytes do arquivo gerado
- [ ] Query filtra corretamente por `stage=gold` e `pipeline_status IN (pass, pass_with_warnings)`
- [ ] Filtro opcional por `evento_id` funcional
- [ ] Arquivo .xlsx contém todas as colunas da tabela 4.7 do PRD
- [ ] Arquivo .csv usa separador `;` e encoding UTF-8 com BOM
- [ ] Nomenclatura do arquivo segue padrão: `leads_ouro_[slug]_YYYY-MM-DD.[ext]`
- [ ] HTTP 204 retornado quando nenhum lead é encontrado
- [ ] Endpoint protegido por JWT (401 sem token)
- [ ] CI verde sem regressão

---
## Issues

### AFL-F3-01-001 — Serviço de Geração de Arquivo de Exportação Gold
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** nenhuma

**User Story:**
Como engenheiro de backend, quero um serviço que gere arquivos .xlsx e .csv com os dados dos leads Gold filtrados, para que o endpoint de exportação tenha uma camada de negócio reutilizável e testável independentemente do HTTP.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_leads_export.py` que cria 3 leads Gold (batch com `stage=gold`, `pipeline_status=pass`) e 1 lead Silver, chama `generate_gold_export(db, evento_id=None, formato="xlsx")` e verifica que o retorno é um bytes não vazio contendo apenas os 3 leads Gold. Repetir para `formato="csv"` validando separador `;` e BOM.
- **Green:** Criar `backend/app/services/leads_export.py` com função `generate_gold_export(db, evento_id, formato)`. Implementar query com join `Lead → LeadBatch` filtrando `stage=gold` e `pipeline_status`. Gerar bytes usando `openpyxl` para xlsx e `csv.writer` para csv.
- **Refactor:** Extrair mapeamento de colunas (campo modelo → nome coluna exportação) para constante reutilizável.

**Critérios de Aceitação:**

- **Given** existem 5 leads Gold e 3 leads Silver no banco
  **When** `generate_gold_export(db, evento_id=None, formato="xlsx")` é chamado
  **Then** o arquivo gerado contém exatamente 5 linhas de dados (+ header) com as colunas do PRD 4.7

- **Given** existem leads Gold de 2 eventos diferentes
  **When** `generate_gold_export(db, evento_id=42, formato="csv")` é chamado
  **Then** o arquivo contém apenas leads do evento 42, separador é `;` e os 3 primeiros bytes são o BOM UTF-8 (`\xef\xbb\xbf`)

- **Given** nenhum lead Gold existe no banco
  **When** `generate_gold_export(db, evento_id=None, formato="xlsx")` é chamado
  **Then** a função retorna `None` (sinalização para HTTP 204)

**Tarefas:**
- [ ] T1: Verificar se `openpyxl` está em `backend/requirements.txt`; adicionar se necessário
- [ ] T2: Criar `backend/app/services/leads_export.py`
- [ ] T3: Implementar query com join Lead → LeadBatch filtrando `stage=gold`, `pipeline_status IN (pass, pass_with_warnings)`
- [ ] T4: Implementar geração de bytes .xlsx via `openpyxl` com colunas do PRD 4.7
- [ ] T5: Implementar geração de bytes .csv com separador `;`, encoding UTF-8 BOM
- [ ] T6: Implementar lógica de nomenclatura do arquivo conforme PRD 4.8
- [ ] T7: Escrever pytest cobrindo cenários: todos os eventos, evento específico, sem leads, formato xlsx, formato csv

**Notas técnicas:**
Colunas de exportação (PRD 4.7): Nome completo, E-mail, CPF, Telefone, Evento de origem, Cidade, Estado, Data de compra, Data de criação, Sobrenome, Gênero, RG, Logradouro, CEP, Bairro, Número, Complemento, Estágio (fixo "Ouro"). Campos de F1-02 que não existirem devem ser exportados como vazio.

---

### AFL-F3-01-002 — Endpoint GET /leads/export/gold
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** AFL-F3-01-001

**User Story:**
Como operador do Dashboard de Leads, quero acessar um endpoint de exportação que retorne um arquivo com os leads Gold, para que eu possa fazer download direto do navegador.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_leads_export_endpoint.py` que chama `GET /leads/export/gold?formato=xlsx` com JWT válido e verifica status 200 com header `Content-Disposition` contendo `leads_ouro_`. Chamar sem JWT e verificar 401. Chamar com banco sem leads Gold e verificar 204.
- **Green:** Adicionar rota `GET /leads/export/gold` em `backend/app/routers/leads.py` que chama `generate_gold_export()`, retorna `StreamingResponse` com `Content-Disposition: attachment` e `Content-Type` correto, ou 204 se não houver dados.
- **Refactor:** Usar `Response` do FastAPI com media_type adequado ao formato solicitado.

**Critérios de Aceitação:**

- **Given** existem leads Gold no banco
  **When** `GET /leads/export/gold?formato=xlsx` é chamado com JWT válido
  **Then** resposta tem status 200, `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` e `Content-Disposition` com nome de arquivo `leads_ouro_todos_YYYY-MM-DD.xlsx`

- **Given** existem leads Gold no banco
  **When** `GET /leads/export/gold?evento_id=42&formato=csv` é chamado com JWT válido
  **Then** resposta tem status 200, `Content-Type: text/csv; charset=utf-8` e nome de arquivo contendo slug do evento

- **Given** nenhum lead Gold existe para os filtros selecionados
  **When** `GET /leads/export/gold` é chamado
  **Then** resposta tem status 204 sem corpo

- **Given** a requisição não possui JWT
  **When** `GET /leads/export/gold` é chamado
  **Then** resposta tem status 401

**Tarefas:**
- [ ] T1: Adicionar rota `GET /leads/export/gold` em `backend/app/routers/leads.py`
- [ ] T2: Definir query params: `evento_id: Optional[int] = None`, `formato: str = "xlsx"`
- [ ] T3: Chamar `generate_gold_export()` do serviço
- [ ] T4: Retornar `StreamingResponse` ou `Response` com headers corretos
- [ ] T5: Retornar 204 quando serviço retorna `None`
- [ ] T6: Escrever pytest (com leads, sem leads, com evento_id, sem JWT)

## 5. Artifact Mínimo do Épico

`artifacts/ajuste-fino-leads/phase-f3/epic-f3-01-export-evidence.md` — output de pytest demonstrando geração correta de .xlsx e .csv, com contagem de linhas e validação de headers.

## 6. Dependências

- [PRD Refino Leads v2](../PRD_Refino_Leads_v2.md) — Seções 4.5, 4.7, 4.8, 4.9
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
- Dependência opcional: EPIC-F1-02 (campos extras no modelo Lead)
