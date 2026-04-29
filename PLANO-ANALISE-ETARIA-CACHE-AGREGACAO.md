# Plano de implementação: cache e pré-agregação — Análise etária de leads

**Escopo:** rota de API `GET /dashboard/leads/analise-etaria` e página `http://localhost:5173/dashboard/leads/analise-etaria`.  
**Código principal:** `backend/app/services/dashboard_service.py` (`build_age_analysis`), `frontend/src/hooks/useAgeAnalysis.ts`, `frontend/src/services/dashboard_age_analysis.ts`.  
**Relacionamento:** complementa a visão de plataforma em `plano_cache.md` (camada reutilizável, Redis, TanStack Query). Este documento detalha **ordem de entrega, chaves, invalidação e riscos** para este painel.

---

## 1. Contexto e restrições

- O cálculo atual carrega **múltiplas origens** (vínculo `lead_evento`, lote `lead_batch` GOLD, fallback `evento_nome`) e agrega em Python, com **deduplicação** `(lead_id, evento_id)`.
- Filtros de query: `data_inicio`, `data_fim` (sobre `Lead.data_criacao`), `evento_id` opcional.
- **Multi-tenant:** agências enxergam só eventos da própria `agencia_id` (`_apply_visibility`). Qualquer chave de cache (cliente ou servidor) deve incluir o **escopo do usuário** (ou equivalente), não só os parâmetros da URL.
- `age_reference_date` hoje é `date.today()`: a resposta **muda por dia** mesmo sem alteração de leads — considerar isso no TTL e na chave de cache.
- A API já retorna `generated_at` e versão de contrato (`AGE_ANALYSIS_RESPONSE_VERSION` no frontend).

---

## 2. Objetivos por fase (incrementais)

| Fase | Objetivo | Reduz carga no banco? | Esforço relativo |
|------|----------|------------------------|------------------|
| A | Cache no **cliente** (mesma sessão, mesma chave de filtros) | Não (reduz HTTP repetido) | Baixo |
| B | **Cache no servidor** (memória/Redis) da resposta JSON por chave canônica + TTL | Sim, entre requests | Médio |
| C | **Invalidação** coordenada (versão de domínio + bump em importações/alterações críticas) | Evita dado muito defasado | Médio |
| D | **Pré-agregação / camada de fatos** (SQL, MV ou tabela) alinhada às regras atuais | Sim, de forma estrutural | Alto |

Recomenda-se entregar **A → B** antes de investir pesado em **D**, salvo se EXPLAIN/auditoria mostrar gargalo exclusivamente em índice/query.

---

## 3. Fase A — Frontend (ganho rápido)

1. **Adotar TanStack Query** (ou equivalente) no projeto, com `QueryClient` global, conforme `plano_cache.md` §5.
2. Substituir o fetch manual em `useAgeAnalysis` por `useQuery`:
   - `queryKey`: incluir `normalizedFilters` + **identificador de tenant** (ex.: `userId` ou hash estável de escopo) + opcionalmente dia da referência se quiser alinhar ao `age_reference_date`.
   - `staleTime`: 2–5 minutos (alinhar com política de negócio); `gcTime` para manter ao navegar na SPA.
3. Ajustar UX: manter padrão atual de *refresh* explícito (botão "Atualizar" se existir) via `refetch()`.
4. **Testes:** atualizar testes de `LeadsAgeAnalysisPage` / hook para mockar o provider de query, se necessário.

**Critério de pronto:** repetir a mesma combinação de filtros na mesma sessão não dispara nova requisição enquanto `staleTime` vencer; troca de filtros dispara request **uma vez** por chave.

---

## 4. Fase B — Cache no backend (resposta do endpoint)

1. **Chave de cache canônica** (ordem sugerida, serialização estável):
   - `domínio` fixo, ex. `age_analysis_v1`
   - `user_id` ou `agencia_id` (conforme modelo de acesso; refletir exatamente `_apply_visibility`)
   - `evento_id | null`, `data_inicio | null`, `data_fim | null` (mesma semântica de `AgeAnalysisQuery`)
   - `reference_day` = data UTC/local acordada para alinhar com `age_reference_date` (evita hit errado após meia-noite)
   - `config_hash` opcional: variáveis de ambiente que alteram cálculo (`DASHBOARD_BB_COVERAGE_THRESHOLD_PCT`, `DASHBOARD_ENABLE_EVENTO_NOME_BACKFILL`, etc.)

2. **Armazenamento:** Redis preferível em produção; memória com LRU por processo só em dev (ver `plano_cache.md` §2.1).

3. **TTL:** iniciar com 300s; ajustar com métricas.

4. **Integração:** decorador ou wrapper em `dashboard_leads_age_analysis` / `build_age_analysis` — **não** alterar a função de negócio na primeira iteração; apenas envolver o resultado já serializável `AgeAnalysisResponse`.

5. **Headers HTTP (opcional):** `Cache-Control: private, max-age=…` alinhado ao TTL, se o CDN/browser puder reutilizar sem vazar entre usuários (só com autenticação e sem cache compartilhado indevido).

**Critério de pronto:** duas requisições idênticas (mesmo usuário, mesmos filtros) dentro do TTL → **sem** reexecução de `build_age_analysis` (log/metric de hit/miss).

---

## 5. Fase C — Invalidação (versão de domínio)

1. Tabela ou registro `dashboard_versions` / `cache_generation` por domínio `leads` ou `age_analysis` (ver `plano_cache.md` §2.2).
2. Incluir `version` (ou contador) na chave de cache do servidor **ou** invalidar padrão em massa com prefixo.
3. **Pontos de bump** (a mapear no código):
   - conclusão de import de leads / promoção de batch para GOLD
   - alterações que afetam `lead_evento`, `lead` relevantes ao painel, ou `evento` (nome/cidade) usados no backfill
4. Documentar o que **não** exige invalidação imediata (ex.: campos do lead sem impacto no dashboard).

**Critério de pronto:** após import conhecido, próximo GET reflete dados novos (dentro de SLA de propagação definido) ou o usuário força `refetch` e invalida versão.

---

## 6. Fase D — Pré-agregação / camada de fatos no PostgreSQL (Supabase)

> O MCP Supabase agiliza `apply_migration`, `execute_sql` e inspeção de schema; **não** substitui o desenho da regra de negócio.

1. **Decisão de desenho (ADR curto):**
   - **Opção D1:** tabela `lead_event_fact` (ou similar) preenchida por **job** ou **triggers** (mais controle, mais código de sync).
   - **Opção D2:** `MATERIALIZED VIEW` + `REFRESH` periódico (mais simples de operar; latência conhecida).
2. Replicar em SQL, na medida do possível, a ordem de precedência: `lead_evento` → `batch` → `evento_nome` (backfill) e **deduplicação** alinhada a `_merge_and_dedupe_facts`.
3. Se a lógica de nome/ambiguidade for **demasiado** diferente de SQL, manter Fase B/C e fatiar: primeiro MV só para o caminho “principal” (ex.: `lead_evento` + batch), e Python para o restante, até paridade de testes.
4. **Índices** nas FKs e em `data_criacao` (ver auditorias em `auditoria/evidencias/` e `plano_cache.md` §4.1).
5. **Testes de regressão:** `backend/tests/test_dashboard_age_analysis_endpoint.py` como fonte de verdade; comparar agregados antes/depois em dataset de teste.
6. **Documentação:** atualizar `docs/WORKFLOWS.md` ou seção de dashboards se a origem de dados passar a ser a MV/tabela.

**Critério de pronto:** tempo de p95 do endpoint cai alvo acordado; resultados batem com o pipeline Python em fixtures controladas; plano de refresh/invalidação documentado.

---

## 7. Observabilidade (transversal)

- Log estruturado ou métrica: duração `build_age_analysis`, duração total do handler, `cache_hit`, tamanho aproximado do payload, `agencia_id` hash.
- Opção: span OpenTelemetry se já existir no projeto.

---

## 8. Riscos e mitigação

| Risco | Mitigação |
|-------|------------|
| Cache servindo dado de outro tenant | Chave **sempre** com escopo de usuário/agência; testes de autorização. |
| Divergência Python vs SQL na Fase D | Paridade de teste; entrega em fatias; manter `build_age_analysis` como fallback até feature flag. |
| `age_reference_date` muda de dia | Incluir dia na chave B ou TTL curto + documentar. |
| PgBouncer/transaction mode | MV refresh e jobs em conexão adequada; evitar `REFRESH` em tráfego errado de pool. |

---

## 9. Checklist de conclusão (definição de “feito”)

- [ ] Fase A: TanStack Query + chaves com escopo.  
- [ ] Fase B: cache no servidor com métrica hit/miss.  
- [ ] Fase C: bump de versão em pelo menos o fluxo principal de carga de dados.  
- [ ] (Opcional) Fase D: fatos/MV com testes de paridade.  
- [ ] Documentação deste plano revista (datas, owners, limites conhecidos).  

---

## 10. Referências no repositório

- Endpoint: `backend/app/routers/dashboard.py`  
- Lógica: `backend/app/services/dashboard_service.py`  
- Testes: `backend/tests/test_dashboard_age_analysis_endpoint.py`  
- Frontend: `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`, `frontend/src/hooks/useAgeAnalysis.ts`  
- Plano irmão (plataforma): `plano_cache.md`  

---

*Documento gerado para orientar a implementação incremental; revisar após a primeira leitura de carga reativa (k6) ou `EXPLAIN ANALYZE` em produção/staging.*
