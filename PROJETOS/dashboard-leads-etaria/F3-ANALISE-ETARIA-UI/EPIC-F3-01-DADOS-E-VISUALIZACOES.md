# EPIC-F3-01 — Dados e Visualizações da Análise Etária
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Implementar a página `LeadsAgeAnalysisPage` com consumo da API de análise etária,
KPI cards do painel consolidado, gráfico de barras empilhadas com distribuição etária
por evento, tabela de eventos com colunas configuráveis e painel consolidado com
Top 3, média e mediana. A página consome o endpoint criado na F1 e renderiza dentro
do `DashboardLayout` criado na F2.

## 2. Contexto Arquitetural
- Página em `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- Componentes em `frontend/src/components/dashboard/`
- API client via hook customizado (`useAgeAnalysis`) usando fetch/axios existente
- Endpoint: `GET /api/v1/dashboard/leads/analise-etaria`
- Resposta tipada: `AgeAnalysisResponse` (tipos espelhados do backend)
- Gráfico: avaliar biblioteca existente no projeto ou adicionar recharts

## 3. Riscos e Armadilhas
- Tipagem do frontend deve espelhar exatamente os schemas do backend
- Gráfico com muitos eventos pode ficar ilegível — prever scroll horizontal ou paginação
- Tabela com muitas colunas pode precisar de scroll horizontal em mobile
- Cálculos de média/mediana devem vir do backend — frontend apenas exibe

## 4. Definition of Done do Épico
- [ ] Hook `useAgeAnalysis` consome a API e retorna dados tipados
- [ ] KPI cards renderizam base total, clientes BB e faixa dominante
- [ ] Gráfico de barras empilhadas renderiza distribuição etária por evento
- [ ] Tabela de eventos renderiza todas as colunas da seção 3.2 do PRD
- [ ] Painel consolidado exibe Top 3, média, mediana e concentração Top 3
- [ ] Filtros de período e evento funcionais
- [ ] Dados reais da API renderizados corretamente

---
## Issues

### DLE-F3-01-001 — Criar tipos TypeScript e hook de consumo da API
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Definir os tipos TypeScript que espelham os schemas Pydantic do backend
(`AgeAnalysisResponse`, `EventoAgeAnalysis`, `AgeBreakdown`, `FaixaEtariaMetrics`) e
criar um hook customizado (`useAgeAnalysis`) que consome o endpoint e gerencia loading,
error e data.

**Critérios de Aceitação:**
- [ ] Tipos definidos em `frontend/src/types/dashboard.ts` (ou mesmo módulo do manifesto)
- [ ] `useAgeAnalysis(filters)` aceita `evento_id`, `data_inicio`, `data_fim` opcionais
- [ ] Hook retorna `{ data, isLoading, error, refetch }`
- [ ] Token JWT incluído automaticamente nas requisições (reusar padrão do projeto)
- [ ] Tipo de resposta reflete exatamente o schema do backend (seção 5 do PRD)

**Tarefas:**
- [ ] T1: Definir tipos TypeScript para `FaixaEtariaMetrics`, `AgeBreakdown`, `EventoAgeAnalysis`, `ConsolidadoAgeAnalysis`, `AgeAnalysisResponse`
- [ ] T2: Criar hook `useAgeAnalysis` em `frontend/src/hooks/useAgeAnalysis.ts`
- [ ] T3: Integrar com mecanismo de autenticação existente
- [ ] T4: Tratar estados de loading, error e data vazia

**Notas técnicas:**
Seguir o padrão de hooks do projeto (verificar se usa React Query, SWR ou fetch manual).

---
### DLE-F3-01-002 — Implementar KPI Cards do painel consolidado
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F3-01-001

**Descrição:**
Criar os KPI cards que aparecem no topo da página de análise etária, exibindo métricas
consolidadas: base total de leads, clientes BB (volume + percentual com indicador de
cobertura), faixa dominante e eventos no filtro.

**Critérios de Aceitação:**
- [ ] Card "Base Total" exibe contagem total de leads no filtro
- [ ] Card "Clientes BB" exibe volume e percentual; indicador de cobertura (barra ou badge)
- [ ] Card "Faixa Dominante" exibe nome da faixa com maior volume (ex.: "26–40")
- [ ] Card "Eventos" exibe quantidade de eventos no filtro
- [ ] Cards com design consistente: ícone, valor principal, valor secundário, tendência (opcional)
- [ ] Componente `KpiCard` genérico e reutilizável

**Tarefas:**
- [ ] T1: Criar componente genérico `KpiCard.tsx` em `frontend/src/components/dashboard/`
- [ ] T2: Implementar card "Base Total"
- [ ] T3: Implementar card "Clientes BB" com indicador de cobertura
- [ ] T4: Implementar card "Faixa Dominante"
- [ ] T5: Compor os 4 cards no topo da página com grid responsivo

---
### DLE-F3-01-003 — Implementar gráfico de barras empilhadas (distribuição etária)
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F3-01-001

**Descrição:**
Criar o gráfico de barras empilhadas que visualiza a distribuição etária por evento.
Cada barra representa um evento; as seções empilhadas representam as faixas 18–25,
26–40, fora de 18–40 e sem informação. Suportar hover com tooltip detalhado.

**Critérios de Aceitação:**
- [ ] Gráfico de barras empilhadas com uma barra por evento
- [ ] Seções coloridas: 18–25 (azul), 26–40 (verde), fora 18–40 (laranja), sem info (cinza)
- [ ] Legenda visível com nome de cada faixa e cor correspondente
- [ ] Hover/tooltip exibe volume e percentual de cada faixa para o evento
- [ ] Eixo Y: volume de leads; Eixo X: nome do evento (truncado se longo)
- [ ] Scroll horizontal quando há muitos eventos (>10)
- [ ] Responsivo: altura se ajusta ao viewport

**Tarefas:**
- [ ] T1: Avaliar e instalar biblioteca de gráficos (recharts recomendado)
- [ ] T2: Criar componente `AgeDistributionChart.tsx`
- [ ] T3: Mapear dados da API para formato esperado pelo gráfico
- [ ] T4: Implementar tooltip customizado com volume e percentual
- [ ] T5: Implementar legenda e responsividade
- [ ] T6: Tratar cenário com muitos eventos (scroll horizontal)

**Notas técnicas:**
Se o projeto já usa uma biblioteca de gráficos, priorizar consistência. Caso contrário,
recharts é a escolha recomendada para React (leve, declarativo, boa tipagem TS).

---
### DLE-F3-01-004 — Implementar tabela de eventos com colunas configuráveis
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F3-01-001

**Descrição:**
Criar a tabela de eventos que exibe todas as métricas da seção 3.2 do PRD: evento
(nome + local), base, clientes BB (% e volume), não clientes, faixas etárias (18–25,
26–40, fora) e faixa dominante. Suportar ordenação por coluna.

**Critérios de Aceitação:**
- [ ] Tabela exibe todos os campos da seção 3.2 do PRD
- [ ] Colunas de percentual formatadas com 1 casa decimal + símbolo %
- [ ] Ordenação por qualquer coluna numérica (click no header)
- [ ] Indicação visual de coluna ordenada e direção (asc/desc)
- [ ] Scroll horizontal em telas pequenas
- [ ] Células de clientes BB exibem "—" quando cobertura insuficiente (null do backend)
- [ ] Linha de evento é clicável (futuro: navegação para detalhe do evento)

**Tarefas:**
- [ ] T1: Criar componente `EventsAgeTable.tsx`
- [ ] T2: Definir colunas com formatação (percentual, volume, texto)
- [ ] T3: Implementar ordenação por coluna no header
- [ ] T4: Tratar valores null (cobertura BB insuficiente) com placeholder "—"
- [ ] T5: Implementar scroll horizontal responsivo
- [ ] T6: Estilizar zebra-striping e hover para legibilidade

---
### DLE-F3-01-005 — Implementar painel consolidado com Top 3, média e mediana
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F3-01-001

**Descrição:**
Criar o painel de resumo consolidado que aparece no topo da página (abaixo dos KPI
cards), destacando os Top 3 eventos por volume, média por evento, mediana por evento
e concentração Top 3.

**Critérios de Aceitação:**
- [ ] Top 3 eventos listados com nome, volume e percentual da base total
- [ ] Média por evento exibida com 1 casa decimal
- [ ] Mediana por evento exibida como inteiro
- [ ] Concentração Top 3 exibida como percentual
- [ ] Tooltip na mediana explica: "Valor central ao ordenar eventos por volume"
- [ ] Tooltip na média explica: "Soma total dividida pela quantidade de eventos"
- [ ] Layout em linha ou cards horizontais, integrado ao design da página

**Tarefas:**
- [ ] T1: Criar componente `ConsolidatedPanel.tsx`
- [ ] T2: Implementar seção Top 3 com ranking visual (1º, 2º, 3º)
- [ ] T3: Implementar métricas estatísticas (média, mediana, concentração)
- [ ] T4: Adicionar tooltips interpretativos
- [ ] T5: Integrar no layout da página abaixo dos KPI cards

---
### DLE-F3-01-006 — Implementar filtros de período e evento
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F3-01-001

**Descrição:**
Criar o painel de filtros da análise etária com seletores de período (data início/fim)
e evento específico. Os filtros atualizam os query params da URL e disparam nova
chamada à API.

**Critérios de Aceitação:**
- [ ] Seletor de período com date pickers para data início e data fim
- [ ] Dropdown/select de evento com busca (lista de eventos disponíveis)
- [ ] Opção "Todos os eventos" como default do seletor de evento
- [ ] Filtros refletidos na URL como query params (deep link suportado)
- [ ] Alteração de filtro dispara nova chamada à API via hook `useAgeAnalysis`
- [ ] Botão "Limpar filtros" restaura estado default

**Tarefas:**
- [ ] T1: Criar componente `AgeAnalysisFilters.tsx`
- [ ] T2: Implementar date pickers de período
- [ ] T3: Implementar dropdown de eventos (consumir lista de eventos da API existente)
- [ ] T4: Sincronizar filtros com query params da URL
- [ ] T5: Conectar filtros ao hook `useAgeAnalysis`

**Notas técnicas:**
Reusar componentes de date picker e select existentes no projeto. Consultar
`frontend/src/components/` para componentes de formulário disponíveis.

## 5. Notas de Implementação Globais
- Todos os componentes devem aceitar props tipadas — evitar `any`
- Formatação de números: usar `Intl.NumberFormat('pt-BR')` para consistência
- Percentuais sempre com 1 casa decimal e símbolo %
- Cores das faixas etárias devem ser consistentes entre gráfico, tabela e KPI cards
