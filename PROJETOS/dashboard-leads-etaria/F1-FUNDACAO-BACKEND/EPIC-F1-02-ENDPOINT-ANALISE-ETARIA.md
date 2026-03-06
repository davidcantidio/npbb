# EPIC-F1-02 — Endpoint de Análise Etária
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Implementar o endpoint `GET /api/v1/dashboard/leads/analise-etaria` com schemas de
resposta tipados, lógica de cálculo de faixas etárias (18–25, 26–40, fora de 18–40),
cobertura de dados BB e agregação consolidada (Top 3, média, mediana). O endpoint é
consumido exclusivamente pelo dashboard frontend e requer autenticação JWT.

## 2. Contexto Arquitetural
- Router FastAPI em `backend/app/routers/` — novo módulo `dashboard.py`
- Schemas Pydantic: `FaixaEtariaMetrics`, `AgeBreakdown`, `AgeAnalysisResponse`
- Query SQL com cálculo de idade via `data_nascimento` e agregação por evento
- Filtros: `evento_id` (opcional), `data_inicio` (opcional), `data_fim` (opcional)
- Autenticação Bearer token (JWT) — mesma dependência dos endpoints existentes
- Campos `is_cliente_bb` e `is_cliente_estilo` já disponíveis no modelo Lead (EPIC-F1-01)

## 3. Riscos e Armadilhas
- Cálculo de idade deve usar data atual como referência — atenção a leads nascidos em
  29/fev (anos bissextos)
- Leads com `data_nascimento NULL` devem ser excluídos dos percentuais de faixa mas
  contabilizados no `sem_info_volume`
- Performance com >100k leads — a query deve ser otimizada (< 2s p95)
- Divisão por zero quando não há leads com `data_nascimento` ou evento sem leads

## 4. Definition of Done do Épico
- [ ] Schemas `FaixaEtariaMetrics`, `AgeBreakdown`, `AgeAnalysisResponse` implementados
- [ ] Endpoint retorna `por_evento` (lista) e `consolidado` (objeto) conforme PRD
- [ ] Filtros `evento_id`, `data_inicio`, `data_fim` funcionando
- [ ] Faixas etárias calculadas corretamente (percentuais somam 100%)
- [ ] Cobertura BB calculada e threshold aplicado (payload retorna `null` quando cobertura < threshold)
- [ ] Consolidado inclui Top 3, média, mediana e concentração Top 3
- [ ] Endpoint protegido por JWT
- [ ] Testes unitários cobrindo cenários relevantes
- [ ] Endpoint documentado no OpenAPI (auto-gerado pelo FastAPI)

---
## Issues

### DLE-F1-02-001 — Criar schemas Pydantic da análise etária
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Implementar os schemas de resposta da análise etária conforme seção 5 do PRD:
`FaixaEtariaMetrics`, `AgeBreakdown`, `EventoAgeAnalysis`, `ConsolidadoAgeAnalysis` e
`AgeAnalysisResponse`. Os schemas devem ser rigorosamente tipados e documentados.

**Critérios de Aceitação:**
- [ ] `FaixaEtariaMetrics` com `volume: int` e `pct: float`
- [ ] `AgeBreakdown` com `faixa_18_25`, `faixa_26_40`, `fora_18_40`, `sem_info_volume`, `sem_info_pct_da_base`
- [ ] `EventoAgeAnalysis` com todos os campos de nível evento (seção 5.1 do PRD)
- [ ] `ConsolidadoAgeAnalysis` com `base_total`, faixas, `top_eventos`, `media_por_evento`, `mediana_por_evento`, `concentracao_top3_pct`
- [ ] `AgeAnalysisResponse` com `version`, `generated_at`, `filters`, `por_evento`, `consolidado`
- [ ] Schemas passam em testes de serialização com dados de exemplo

**Tarefas:**
- [ ] T1: Criar módulo `backend/app/schemas/dashboard.py`
- [ ] T2: Implementar `FaixaEtariaMetrics` e `AgeBreakdown`
- [ ] T3: Implementar `EventoAgeAnalysis` e `ConsolidadoAgeAnalysis`
- [ ] T4: Implementar `AgeAnalysisResponse` com envelope (version, generated_at, filters)
- [ ] T5: Escrever testes de serialização com fixtures de dados

**Notas técnicas:**
Usar `BaseModel` do Pydantic (não SQLModel) — estes schemas não representam tabelas.

---
### DLE-F1-02-002 — Implementar lógica de query da análise etária
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F1-02-001, DLE-F1-01-001

**Descrição:**
Criar o serviço/use-case que executa a query de análise etária: cálculo de idade a
partir de `data_nascimento`, classificação em faixas, agregação por evento, cálculo de
cobertura BB e geração do consolidado (Top 3, média, mediana, concentração).

**Critérios de Aceitação:**
- [ ] Idade calculada usando data atual como referência (`date.today()`)
- [ ] Faixas: 18–25, 26–40, fora de 18–40 — classificação correta para idades limite (18, 25, 26, 40)
- [ ] Leads com `data_nascimento NULL` contabilizados em `sem_info_volume`, excluídos dos percentuais
- [ ] Percentuais das faixas somam 100% (sobre base com `data_nascimento NOT NULL`)
- [ ] Cobertura BB = % de leads com `is_cliente_bb NOT NULL`
- [ ] Quando cobertura < threshold (80% default), `clientes_bb_volume` e `clientes_bb_pct` retornam `null`
- [ ] Consolidado: Top 3 por volume, média aritmética, mediana, concentração Top 3
- [ ] Filtros `evento_id`, `data_inicio`, `data_fim` aplicados corretamente
- [ ] Sem divisão por zero quando base filtrada é vazia

**Tarefas:**
- [ ] T1: Criar módulo de serviço `backend/app/services/dashboard_service.py`
- [ ] T2: Implementar função de cálculo de idade e classificação em faixa
- [ ] T3: Implementar query de agregação por evento com faixas e cobertura BB
- [ ] T4: Implementar lógica de consolidado (Top 3, média, mediana, concentração)
- [ ] T5: Implementar aplicação de filtros (evento_id, data_inicio, data_fim)
- [ ] T6: Tratar edge cases (base vazia, todos sem data_nascimento, cobertura zero)

**Notas técnicas:**
Avaliar se o cálculo deve ser feito em SQL (melhor performance) ou em Python (maior
flexibilidade). Para v1.0, priorizar clareza e correção; otimizar em iteração futura
se necessário. O threshold de cobertura BB deve ser configurável (default 80%).

---
### DLE-F1-02-003 — Implementar endpoint GET /api/v1/dashboard/leads/analise-etaria
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F1-02-002

**Descrição:**
Criar o router FastAPI com o endpoint `GET /api/v1/dashboard/leads/analise-etaria`,
integrando autenticação JWT, validação de query params e chamada ao serviço de análise
etária.

**Critérios de Aceitação:**
- [ ] Rota `GET /api/v1/dashboard/leads/analise-etaria` registrada no app
- [ ] Query params: `evento_id` (int, opcional), `data_inicio` (date, opcional), `data_fim` (date, opcional)
- [ ] Resposta tipada como `AgeAnalysisResponse` com status 200
- [ ] Autenticação JWT obrigatória — retorna 401 sem token válido
- [ ] Documentação OpenAPI auto-gerada com descrição do endpoint e exemplos
- [ ] Retorna 200 com dados vazios (não 404) quando filtro não encontra leads

**Tarefas:**
- [ ] T1: Criar `backend/app/routers/dashboard.py` com router prefix `/dashboard`
- [ ] T2: Implementar endpoint com dependência de autenticação
- [ ] T3: Validar e documentar query params
- [ ] T4: Registrar router no app principal (`backend/app/main.py`)
- [ ] T5: Testar endpoint via Swagger UI com diferentes combinações de filtros

---
### DLE-F1-02-004 — Testes unitários do endpoint de análise etária
**tipo:** test | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** DLE-F1-02-003

**Descrição:**
Cobrir o endpoint e o serviço de análise etária com testes unitários que validem
cálculos de faixa, cobertura BB, consolidado e edge cases.

**Critérios de Aceitação:**
- [ ] Teste: faixas etárias calculadas corretamente para idades 17, 18, 25, 26, 40, 41
- [ ] Teste: leads sem `data_nascimento` excluídos dos percentuais
- [ ] Teste: cobertura BB < 80% retorna `null` para campos BB
- [ ] Teste: cobertura BB ≥ 80% retorna valores calculados
- [ ] Teste: consolidado com Top 3 correto (volume decrescente)
- [ ] Teste: média e mediana calculadas conforme definição do PRD
- [ ] Teste: filtro por `evento_id` retorna apenas dados do evento selecionado
- [ ] Teste: base vazia retorna resposta válida com zeros
- [ ] Teste: endpoint retorna 401 sem autenticação

**Tarefas:**
- [ ] T1: Criar fixtures com leads de diferentes idades, eventos e estados de cruzamento BB
- [ ] T2: Testar serviço de cálculo (unit tests puros)
- [ ] T3: Testar endpoint via TestClient do FastAPI (integration tests)
- [ ] T4: Testar edge cases (sem leads, todos sem data_nascimento, cobertura zero)
- [ ] T5: Testar autenticação (401 sem token, 200 com token válido)

**Notas técnicas:**
Seguir o padrão de testes do projeto: `TESTING=true` ativa SQLite fallback. Usar
fixtures compartilhadas quando possível.

## 5. Notas de Implementação Globais
- O módulo `dashboard.py` (router e schemas) deve ser estruturado para acomodar futuros
  endpoints de dashboard sem refatoração
- Nomear o router com tag `dashboard` para agrupamento no OpenAPI
- O threshold de cobertura BB (80%) deve ser configurável via constante ou variável de
  ambiente, não hardcoded no serviço
