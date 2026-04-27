Você atuará como um Arquiteto de Software Sênior nível Enterprise com foco em performance, dados e sistemas analíticos.

## CONTEXTO

Repositório: `npbb`
Stack:

* Backend: FastAPI + SQLModel
* Banco: Supabase (PostgreSQL com PgBouncer)
* Frontend: React (sem TanStack Query atualmente)
* Dashboards: calculados sob demanda via endpoints (ex: `/dashboard/leads/analise-etaria`)

Problema atual:

* Dashboards estão sendo calculados em tempo de requisição (Python + loops + joins)
* Sem cache estruturado (nem frontend, nem backend)
* Alto custo de CPU + latência crescente
* Escala ruim conforme crescimento de leads/eventos
* Arquitetura não reaproveitável para novos dashboards

Objetivo:

1. Resolver imediatamente a performance do dashboard atual
2. Criar uma arquitetura de cache + agregação reutilizável
3. Permitir expansão progressiva para outros dashboards/queries
4. Minimizar interferência no código existente (strangler pattern)

---

## MISSÃO

Você deve:

### FASE 1 — DIAGNÓSTICO TÉCNICO

Analise o código e identifique:

* Onde estão os gargalos reais (queries, loops, joins, deduplicação)
* Quais queries são mais custosas
* Onde há recomputação desnecessária
* Oportunidades de mover lógica para SQL

Saída:

* Lista priorizada de gargalos
* Estimativa qualitativa de impacto

---

### FASE 2 — FUNDAÇÃO GLOBAL (FAZER UMA VEZ)

Implemente uma arquitetura padrão reutilizável:

#### 2.1 Backend Cache Layer

Criar um módulo central:

```
backend/app/core/cache.py
```

Com:

* get_cache(key)
* set_cache(key, value, ttl)
* build_cache_key(domain, params, version)
* suporte a TTL configurável
* preparado para Redis (ou fallback memória)

#### 2.2 Versionamento de Invalidação

Criar mecanismo:

```
dashboard_versions
```

* tabela ou storage simples
* chave por domínio (ex: "leads", "eventos")
* função: get_version(domain), bump_version(domain)

Toda key de cache deve incluir versionamento.

#### 2.3 Query Wrapper Padronizado

Criar decorator/helper:

```
@cached_dashboard(domain="leads", ttl=300)
```

Responsável por:

* montar cache_key
* buscar cache
* executar função original se miss
* salvar resultado

---

### FASE 3 — OTIMIZAÇÃO DO DASHBOARD ATUAL

Alvo: `/dashboard/leads/analise-etaria`

#### 3.1 Eliminar processamento pesado em Python

Refatorar `build_age_analysis` para:

* reduzir loops
* mover agregações para SQL (GROUP BY)
* evitar carregar todas as linhas para memória

#### 3.2 Criar camada de fatos (IMPORTANTÍSSIMO)

Criar estrutura SQL:

Opção A (preferencial):

* tabela ou view: `lead_event_fact`

Campos:

* evento_id
* lead_id
* data_criacao
* data_nascimento
* is_cliente_bb
* agencia_id

Regra:

* deduplicado por (evento_id, lead_id)

#### 3.3 Criar agregação SQL

Mover cálculos de:

* faixas etárias
* contagem
* cobertura BB

para SQL (ou materialized view)

#### 3.4 Aplicar cache no endpoint

* TTL inicial: 5 minutos
* chave baseada em filtros + versão

---

### FASE 4 — BANCO (SUPABASE)

Usando MCP Supabase:

#### 4.1 Criar índices críticos

* lead_evento(evento_id, lead_id)
* lead(data_criacao)
* lead(batch_id)
* lead(is_cliente_bb)
* lead(evento_nome) (se ainda usado)

#### 4.2 Rodar EXPLAIN ANALYZE

Para queries críticas:

* antes e depois
* comparar custo

#### 4.3 (Opcional mas recomendado)

Criar:

* materialized view OU
* tabela de snapshot

Para dashboards mais pesados

---

### FASE 5 — FRONTEND (CACHE REAL)

#### 5.1 Introduzir TanStack Query

* instalar
* configurar QueryClient global

#### 5.2 Refatorar hooks

Substituir:

* `useAgeAnalysis`

Por:

* `useQuery`

Com:

* queryKey baseada em filtros
* staleTime (2–5 min)
* cache persistente

#### 5.3 Evitar refetch desnecessário

* desabilitar refetch on focus
* debounce de filtros

---

### FASE 6 — PADRÃO REUTILIZÁVEL

Criar um guia interno:

Para qualquer novo dashboard:

1. Criar query SQL agregada OU usar fact table
2. Criar endpoint usando @cached_dashboard
3. Definir query key no frontend
4. Definir TTL adequado
5. Integrar com versionamento

---

### FASE 7 — OBSERVABILIDADE

Adicionar logs/metrics:

* tempo do endpoint
* tempo de query
* cache hit/miss
* volume de dados

---

## REGRAS IMPORTANTES

* NÃO criar funções monolíticas
* SEGUIR padrão modular existente
* USAR strangler pattern (não quebrar fluxo atual)
* OTIMIZAR primeiro o que gera maior impacto
* EVITAR overengineering desnecessário
* DOCUMENTAR cada decisão técnica

---

## ENTREGÁVEIS

Você deve entregar:

1. Código implementado (backend + frontend)
2. Scripts SQL (índices, views, etc.)
3. Refatoração do endpoint atual
4. Infraestrutura de cache reutilizável
5. Guia de expansão para novos dashboards
6. Evidência de melhoria (antes/depois)

---

## OBJETIVO FINAL

Transformar o sistema de dashboards em:

* Rápido
* Escalável
* Cacheável
* Reutilizável
* Baseado em agregação (não em loops Python)

Se algo estiver mal estruturado, corrija — não apenas adapte.
