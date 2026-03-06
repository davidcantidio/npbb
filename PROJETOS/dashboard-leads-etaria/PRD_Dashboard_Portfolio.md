# PRD — Dashboard Portfolio
**Arquitetura de Subpainéis + Análise Etária por Evento**

| | |
|---|---|
| **Versão** | 1.0 |
| **Data** | Março 2026 |
| **Status** | 🟢 Em desenvolvimento |

---

## 1. Objetivo e Contexto

Este documento especifica a arquitetura e os requisitos funcionais para a implantação do módulo **Dashboard Portfolio** — um painel navegável com múltiplas análises segmentadas por domínio. A primeira entrega implantará a **análise etária por evento** (`dashboard > leads > análise etária por evento`). As demais trilhas (ex.: `dashboard > eventos > fechamento`) têm arquitetura definida aqui, mas ficam fora do escopo de desenvolvimento imediato.

> **Problema a resolver:** Hoje, relatórios analíticos são gerados fora do sistema e distribuídos manualmente. O Dashboard Portfolio centraliza essas análises em um subpainel navegável, auditável e sempre atualizado com os dados já ingeridos pelo pipeline ETL.

### 1.1 Hierarquia de Navegação (arquitetura geral)

A estrutura de rotas segue o padrão: `dashboard / <domínio> / <análise>`. Os exemplos abaixo estabelecem o contrato de navegação — apenas a análise etária será implementada agora.

| Caminho | Domínio | Análise | Status |
|---|---|---|---|
| `dashboard > leads > análise etária` | Leads | Análise Etária por Evento | 🟢 Escopo v1.0 |
| `dashboard > eventos > fechamento` | Eventos | Relatório de Fechamento | ⏸ Fora do escopo |
| `dashboard > leads > conversão` | Leads | Conversão por Evento | ⏸ Backlog |
| `dashboard > publicidade > cobertura` | Publicidade | Cobertura por Mídia | ⏸ Backlog |

---

## 2. Arquitetura do Subpainel (Frontend)

### 2.1 Componente DashboardLayout

O layout raiz (`/dashboard`) renderiza uma sidebar de navegação baseada em um **manifesto de dashboards** cadastrado no frontend. Cada entrada do manifesto define: rota, domínio, nome da análise, ícone e se está disponível (`enabled`).

> **Princípio de extensibilidade:** Novos dashboards são adicionados apenas inserindo uma nova entrada no manifesto + o componente de página correspondente. Não há alteração no layout raiz nem nas rotas já existentes.

### 2.2 Estrutura de Rotas

```
/dashboard                            → DashboardHome (seletor visual de análises)
/dashboard/leads/analise-etaria       → LeadsAgeAnalysisPage
/dashboard/eventos/fechamento         → [componente futuro — rota reservada]
```

### 2.3 DashboardHome — Painel Seletor

A página raiz do dashboard renderiza **cards clicáveis**, um por análise disponível. Cards com `enabled: false` exibem um badge **"Em breve"** e são não-clicáveis. O layout em grid de 3 colunas facilita a adição futura de novos cards sem redesign.

---

## 3. Dashboard — Análise Etária por Evento (v1.0)

### 3.1 Visão Geral da Análise

A análise etária apresenta a distribuição de leads por faixa etária, segmentada por evento e consolidada em visão geral. Os dados têm duas camadas:

- **Camada evento:** métricas individuais de um evento selecionado.
- **Camada consolidada:** agregação de todos os eventos do portfólio (ou do filtro aplicado).

### 3.2 Campos Exibidos — Nível Evento

| Campo | Tipo | Origem | Observação |
|---|---|---|---|
| Evento (nome + local) | string | `evento.nome`, `.cidade`, `.estado` | Label do card |
| Base (leads) | int | `COUNT(lead.id)` | Total de leads do evento |
| Clientes BB (%) | decimal | Cruzamento externo | Ver seção 4.1 |
| Clientes BB (volume) | int | Cruzamento externo | Ver seção 4.1 |
| Não clientes (%) | decimal | Cruzamento externo | Complementar a Clientes BB |
| Não clientes (volume) | int | Cruzamento externo | |
| Leads 18–25 (%) | decimal | `data_nascimento → age` | Ver seção 4.2 |
| Leads 18–25 (volume) | int | `data_nascimento → age` | |
| Leads 26–40 (%) | decimal | `data_nascimento → age` | |
| Leads 26–40 (volume) | int | `data_nascimento → age` | |
| Fora de 18–40 (%) | decimal | `data_nascimento → age` | |
| Fora de 18–40 (volume) | int | `data_nascimento → age` | |
| Nota / faixa dominante | string | calculado | Ex.: "Faixa dominante: 26–40" |

### 3.3 Campos Exibidos — Geral Consolidado

| Campo | Tipo | Descrição |
|---|---|---|
| Base total (leads) | int | Soma de todos os leads no filtro |
| Clientes BB (% e volume) | decimal/int | Cruzamento externo (ver seção 4.1) |
| Não clientes (% e volume) | decimal/int | Complementar |
| Leads 18–25 (% e volume) | decimal/int | Faixa etária |
| Leads 26–40 (% e volume) | decimal/int | Faixa etária |
| Fora de 18–40 (% e volume) | decimal/int | Faixa etária |
| Top 1 / Top 2 / Top 3 por volume | string/int | Eventos com maior base de leads |
| Concentração Top 3 (%) | decimal | % da base total representada pelos Top 3 |
| Média por evento | decimal | Soma total / quantidade de eventos |
| Mediana por evento | int | Valor central ao ordenar por volume |

> **Nota — Média:** soma dos volumes de todos os eventos dividida pela quantidade de eventos.
>
> **Nota — Mediana:** volume que fica no meio quando os eventos são ordenados do menor para o maior.
>
> **Nota interpretativa:** Quando poucos eventos são muito grandes, a média sobe mais do que o tamanho típico da carteira — a mediana é o indicador mais representativo do tamanho típico de evento.

---

## 4. Modelo de Dados — Extensões Necessárias

### 4.1 Campos `is_cliente_bb` e `is_cliente_estilo` — Lead Gold

Dois campos boolean nullable devem ser adicionados ao modelo `Lead` (tabela `lead`):

| Campo | Tipo DB | Nullable | Descrição |
|---|---|---|---|
| `is_cliente_bb` | `BOOLEAN` | SIM | `True` = cliente BB confirmado; `NULL` = pendente cruzamento |
| `is_cliente_estilo` | `BOOLEAN` | SIM | `True` = cliente Estilo confirmado; `NULL` = pendente cruzamento |

`is_cliente_bb` representa o resultado do cruzamento com a base de dados externa do Banco do Brasil. `is_cliente_estilo` representa o produto Estilo. Ambos podem ficar nulos quando o cruzamento ainda não foi realizado para aquele lote de leads.

> ⚠️ **Regra de negócio — Transparência de Dados Faltantes**
>
> Quando `is_cliente_bb` for `NULL` para a maioria dos leads de um evento, o dashboard deve exibir um aviso explícito:
> *"Dados de vínculo BB indisponíveis para este evento — realize o cruzamento com a base de dados do Banco."*
>
> O dashboard **não deve** omitir ou inferir valores ausentes.

### 4.2 Cálculo de Faixa Etária

A faixa etária é derivada do campo `lead.data_nascimento` existente. O cálculo é feito no momento da query (não persiste a faixa calculada), usando a data atual como referência de idade. Leads com `data_nascimento NULL` são contabilizados separadamente como "sem informação de idade" e **não entram nos percentuais de faixa**.

| Faixa | Critério | Observação |
|---|---|---|
| 18–25 | `18 ≤ idade ≤ 25` | Jovens adultos |
| 26–40 | `26 ≤ idade ≤ 40` | Adultos |
| Fora de 18–40 | `idade < 18 OU idade > 40` | Inclui menores e 40+ |
| Sem informação | `data_nascimento IS NULL` | Exibido separadamente, fora dos % |

### 4.3 Endpoint de API — Análise Etária

Novo endpoint REST, consumido exclusivamente pelo dashboard:

```
GET /api/v1/dashboard/leads/analise-etaria
```

**Query params:**
- `evento_id` *(opcional)* — se omitido, retorna consolidado geral
- `data_inicio` *(opcional)*
- `data_fim` *(opcional)*

Requer autenticação Bearer token. Retorna payload tipado com seções `por_evento` (lista) e `consolidado` (objeto). Ver schema completo na seção 5.

### 4.4 Lógica de Cobertura de Dados BB

O dashboard deve calcular, para cada evento, o percentual de leads com `is_cliente_bb NOT NULL` (cobertura do cruzamento). Se a cobertura for inferior a um threshold configurável (default: 80%), um banner de aviso é exibido no card do evento e na visão consolidada.

| Cobertura | Comportamento |
|---|---|
| ≥ 80% | Dados exibidos normalmente |
| 20%–80% | ⚠️ Banner amarelo — "Dados parcialmente disponíveis. Realize o cruzamento completo." |
| < 20% | 🔴 Banner vermelho — "Dados de vínculo BB indisponíveis para este evento." |

---

## 5. Schemas de API (Pydantic)

### 5.1 Resposta — `AgeAnalysisResponse`

```
GET /api/v1/dashboard/leads/analise-etaria
```

| Campo | Tipo | Descrição |
|---|---|---|
| `version` | int | Versão do schema (atualmente `1`) |
| `generated_at` | datetime | Timestamp UTC de geração |
| `filters` | objeto | Filtros efetivamente aplicados |
| `por_evento` | lista | Um item por evento no filtro |
| `por_evento[].evento_id` | int | ID do evento |
| `por_evento[].evento_nome` | string | Nome do evento |
| `por_evento[].cidade` | string | Cidade do evento |
| `por_evento[].estado` | string | UF do evento |
| `por_evento[].base_leads` | int | Total de leads |
| `por_evento[].clientes_bb_volume` | int\|null | `NULL` se cobertura < threshold |
| `por_evento[].clientes_bb_pct` | float\|null | `NULL` se cobertura < threshold |
| `por_evento[].cobertura_bb_pct` | float | % de leads com `is_cliente_bb NOT NULL` |
| `por_evento[].faixas` | objeto | Faixas 18-25, 26-40, fora, sem_info |
| `por_evento[].faixa_dominante` | string | Nome da faixa com maior volume |
| `consolidado` | objeto | Agregação de todos os eventos |
| `consolidado.base_total` | int | Soma total de leads |
| `consolidado.clientes_bb_volume` | int\|null | Sujeito à cobertura |
| `consolidado.clientes_bb_pct` | float\|null | Sujeito à cobertura |
| `consolidado.faixas` | objeto | Distribuição etária consolidada |
| `consolidado.top_eventos` | lista | Top 3 por volume de leads |
| `consolidado.media_por_evento` | float | Média aritmética |
| `consolidado.mediana_por_evento` | float | Mediana |
| `consolidado.concentracao_top3_pct` | float | % do total representado pelos Top 3 |

### 5.2 Schema de Faixas (objeto `faixas`)

```python
class FaixaEtariaMetrics(BaseModel):
    volume: int
    pct: float  # percentual sobre base com data_nascimento NOT NULL

class AgeBreakdown(BaseModel):
    faixa_18_25: FaixaEtariaMetrics
    faixa_26_40: FaixaEtariaMetrics
    fora_18_40: FaixaEtariaMetrics
    sem_info_volume: int        # leads sem data_nascimento (excluído dos %)
    sem_info_pct_da_base: float # % destes sobre o total bruto do evento
```

---

## 6. Migrações de Banco de Dados

### 6.1 Alterações no Modelo `Lead`

Dois campos são adicionados à tabela `lead`, ambos **nullable** para garantir retrocompatibilidade com registros existentes:

| Campo | Tipo SQL | Default | Comando |
|---|---|---|---|
| `is_cliente_bb` | `BOOLEAN NULL` | `NULL` | `ALTER TABLE lead ADD COLUMN is_cliente_bb BOOLEAN` |
| `is_cliente_estilo` | `BOOLEAN NULL` | `NULL` | `ALTER TABLE lead ADD COLUMN is_cliente_estilo BOOLEAN` |

O arquivo de migração Alembic deve ser criado em `backend/alembic/versions/` com revision ID único. Os dois campos são incluídos na mesma migration por afinidade semântica.

### 6.2 Alterações no Modelo Python (`app/models/models.py`)

```python
class Lead(SQLModel, table=True):
    # ... campos existentes ...

    # Cruzamento com base BB — nullable até que o cruzamento seja realizado
    is_cliente_bb: Optional[bool] = Field(
        default=None,
        index=True,
        description="True = cliente BB confirmado; NULL = cruzamento pendente",
    )

    # Produto Estilo — nullable até que o cruzamento seja realizado
    is_cliente_estilo: Optional[bool] = Field(
        default=None,
        index=True,
        description="True = cliente Estilo confirmado; NULL = cruzamento pendente",
    )
```

### 6.3 Índices Recomendados

- `ix_lead_is_cliente_bb` — índice em `is_cliente_bb` (consultas de dashboard filtram por este valor)
- `ix_lead_is_cliente_estilo` — índice em `is_cliente_estilo`
- Índice composto `(evento_nome, is_cliente_bb, data_nascimento)` pode ser avaliado após medir performance em produção

---

## 7. Experiência do Usuário (UX)

### 7.1 Fluxo de Navegação

1. Usuário acessa `/dashboard` — vê o **DashboardHome** com cards de análises disponíveis.
2. Clica em **"Análise Etária por Evento"** — navega para `/dashboard/leads/analise-etaria`.
3. Aplica filtros (período, evento específico) via painel lateral ou dropdowns.
4. Visualiza a análise consolidada no topo e, abaixo, o detalhamento por evento.
5. Cards de aviso de dados BB ausentes são exibidos inline quando relevante.

### 7.2 Componentes Visuais da Análise Etária

- **KPI Cards:** base total, clientes BB (com cobertura indicator), faixa dominante.
- **Gráfico de barras empilhadas:** distribuição etária por evento (18–25, 26–40, fora, sem info).
- **Tabela de eventos:** colunas configuráveis, ordenável por volume/percentual.
- **Painel consolidado:** resumo geral no topo da página com destaque para Top 3 eventos.
- **Banner de aviso:** exibido quando cobertura BB < threshold, com instrução de ação ao operador.

### 7.3 Estados da Interface

| Estado | Comportamento |
|---|---|
| Carregando | Skeleton loaders nos cards e tabela |
| Sem dados | "Nenhum lead encontrado para os filtros aplicados" |
| BB sem cobertura | Banner amarelo ou vermelho conforme threshold |
| Dados parciais | Valores com nota "(dados parciais)" no tooltip |
| Erro de API | Toast de erro + botão de retry |

---

## 8. Requisitos Não Funcionais

| Dimensão | Requisito | Detalhe |
|---|---|---|
| Performance | < 2s p95 | Query de análise etária com até 100k leads |
| Autenticação | JWT obrigatório | Endpoint `/dashboard/*` requer Bearer token válido |
| Caching | Opcional — TTL 5 min | Cache de resposta do endpoint consolidado |
| Extensibilidade | Zero-change no layout | Novos dashboards via manifesto, sem alterar `DashboardLayout` |
| Retrocompatibilidade | Sem breaking changes | Campos `is_cliente_bb` nullable — registros existentes não quebram |

---

## 9. Critérios de Aceite — v1.0

### 9.1 Arquitetura de Navegação

1. `DashboardHome` exibe ao menos 1 card ativo (Análise Etária) e cards "Em breve" para as demais trilhas.
2. A rota `/dashboard/leads/analise-etaria` é acessível e protegida por autenticação.
3. Adicionar uma nova entrada ao manifesto de dashboards renderiza um novo card sem alteração de layout.

### 9.2 Análise Etária — Dados

1. Os percentuais das faixas etárias somam 100% (excluindo leads sem `data_nascimento`, que são exibidos à parte).
2. Leads com `is_cliente_bb NULL` exibem banner de aviso — nunca são contados como "não cliente".
3. O consolidado geral calcula corretamente Top 3, média e mediana conforme definições da seção 3.3.
4. Filtro por `evento_id` retorna apenas dados do evento selecionado.

### 9.3 Migração de Banco

1. Migration Alembic aplica sem erro em banco limpo e em banco com dados existentes.
2. Campos `is_cliente_bb` e `is_cliente_estilo` existem na tabela `lead` com default `NULL`.
3. Rollback da migration remove os campos sem efeito colateral.

### 9.4 UX e Transparência

1. Banner de dados BB ausentes é exibido quando cobertura < 80% (default).
2. A mensagem do banner instrui o operador a realizar o cruzamento com a base do banco.
3. Tooltips de faixa dominante e nota de média/mediana reproduzem as definições da seção 3.3.

---

## 10. Fora do Escopo — v1.0

- Implementação de qualquer dashboard além de análise etária por evento.
- Integração automática com base de dados BB (o cruzamento é feito externamente e importado via campo `is_cliente_bb`).
- Exportação de dados do dashboard para Excel/PDF.
- Permissionamento granular por dashboard (todos os usuários autenticados têm acesso — RBAC pode ser adicionado em versão futura).
- Dashboard de fechamento de evento (`dashboard > eventos > fechamento`) — arquitetura prevista mas implementação fora deste sprint.

---

## 11. Checklist de Entregáveis Técnicos

| # | Entregável | Camada | Prioridade |
|---|---|---|---|
| 1 | Migration Alembic: add `is_cliente_bb`, `is_cliente_estilo` em `lead` | DB | 🔴 Alta |
| 2 | Atualizar `app/models/models.py`: campos no modelo `Lead` | Backend | 🔴 Alta |
| 3 | Atualizar schemas `LeadListItemRead` + novo `AgeAnalysisResponse` | Backend | 🔴 Alta |
| 4 | Endpoint `GET /api/v1/dashboard/leads/analise-etaria` | Backend | 🔴 Alta |
| 5 | Manifesto de dashboards (frontend config) | Frontend | 🔴 Alta |
| 6 | Componente `DashboardLayout` + `DashboardHome` (seletor) | Frontend | 🔴 Alta |
| 7 | Página `LeadsAgeAnalysisPage` com KPI cards + tabela + gráfico | Frontend | 🔴 Alta |
| 8 | Banner de aviso de dados BB ausentes (lógica de cobertura) | Frontend | 🔴 Alta |
| 9 | Testes unitários do endpoint (faixas etárias, cobertura BB) | Testes | 🟡 Média |
| 10 | Documentação OpenAPI do novo endpoint | Docs | 🟡 Média |
