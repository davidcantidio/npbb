# EPIC-F3-02 — Cobertura BB, Estados e Qualidade
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Implementar os banners de aviso de dados BB (amarelo e vermelho conforme threshold de
cobertura), tratamento completo dos estados da interface (loading com skeleton loaders,
empty, error com retry) e tooltips interpretativos para métricas que requerem
contextualização (média vs. mediana, faixa dominante).

## 2. Contexto Arquitetural
- Componentes em `frontend/src/components/dashboard/`
- Lógica de cobertura BB vem do campo `cobertura_bb_pct` da resposta da API
- Thresholds: ≥ 80% (normal), 20–80% (amarelo), < 20% (vermelho)
- Estados de interface controlados pelo hook `useAgeAnalysis` (loading, error, data)
- Padrão de toast/notificação existente no projeto para erros

## 3. Riscos e Armadilhas
- Banner de cobertura deve ser informativo sem ser alarmista — UX de transparência
- Skeleton loaders devem espelhar o layout real para evitar layout shift
- Retry de erro não deve causar loop infinito se a API estiver fora

## 4. Definition of Done do Épico
- [ ] Banner amarelo exibido quando cobertura BB entre 20% e 80%
- [ ] Banner vermelho exibido quando cobertura BB < 20%
- [ ] Sem banner quando cobertura ≥ 80%
- [ ] Skeleton loaders em KPI cards, gráfico e tabela durante loading
- [ ] Estado empty: "Nenhum lead encontrado para os filtros aplicados"
- [ ] Estado error: toast de erro com botão de retry
- [ ] Tooltips interpretativos para média, mediana e faixa dominante

---
## Issues

### DLE-F3-02-001 — Implementar banners de aviso de dados BB
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Criar componentes de banner de aviso que indicam a qualidade dos dados de cruzamento
BB. O banner é exibido no topo da página de análise etária e dentro de cards de evento
individual quando relevante.

**Critérios de Aceitação:**
- [ ] Banner amarelo (⚠️) quando cobertura entre 20% e 80%: "Dados parcialmente disponíveis. Realize o cruzamento completo com a base do Banco."
- [ ] Banner vermelho (🔴) quando cobertura < 20%: "Dados de vínculo BB indisponíveis para este evento — realize o cruzamento com a base de dados do Banco."
- [ ] Sem banner quando cobertura ≥ 80%
- [ ] Banner no topo da página usa cobertura consolidada
- [ ] Texto do banner inclui instrução de ação ao operador
- [ ] Banner é dismissível (X) mas reaparece ao recarregar/mudar filtro
- [ ] Componente `CoverageBanner` genérico e reutilizável

**Tarefas:**
- [ ] T1: Criar componente `CoverageBanner.tsx` com props: `coverage`, `threshold_warning`, `threshold_danger`
- [ ] T2: Implementar variante amarela (warning)
- [ ] T3: Implementar variante vermelha (danger)
- [ ] T4: Integrar no topo da página `LeadsAgeAnalysisPage`
- [ ] T5: Integrar em cards de evento individual (na tabela ou detalhe)

**Notas técnicas:**
Thresholds (80% e 20%) devem ser constantes configuráveis no frontend, alinhados com
o backend. Usar mesmos valores definidos no PRD seção 4.4.

---
### DLE-F3-02-002 — Implementar estados da interface (loading, empty, error)
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Tratar todos os estados da interface conforme seção 7.3 do PRD: loading com skeleton
loaders que espelham o layout real, estado vazio com mensagem orientativa e estado de
erro com toast e botão de retry.

**Critérios de Aceitação:**
- [ ] Estado loading: skeleton loaders nos KPI cards (4 retângulos), no gráfico (área retangular) e na tabela (linhas fantasma)
- [ ] Estado empty: mensagem centralizada "Nenhum lead encontrado para os filtros aplicados" com ícone ilustrativo
- [ ] Estado error: toast de erro com mensagem descritiva + botão "Tentar novamente"
- [ ] Retry chama `refetch` do hook sem recarregar a página
- [ ] Sem flash de conteúdo: transição suave de skeleton para dados
- [ ] Estado "dados parciais": tooltips com "(dados parciais)" nos valores afetados

**Tarefas:**
- [ ] T1: Criar componentes skeleton: `KpiCardSkeleton`, `ChartSkeleton`, `TableSkeleton`
- [ ] T2: Implementar lógica condicional na página (loading → skeleton, error → toast, empty → mensagem)
- [ ] T3: Implementar toast de erro com botão retry (reusar toast existente do projeto)
- [ ] T4: Implementar estado vazio com mensagem e ícone
- [ ] T5: Testar transições de estado (loading → data, loading → error, loading → empty)

---
### DLE-F3-02-003 — Tooltips interpretativos e documentação visual
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** DLE-F3-01-005

**Descrição:**
Adicionar tooltips interpretativos em métricas que requerem contextualização para o
usuário final: faixa dominante, média vs. mediana, concentração Top 3 e cobertura BB.
Os textos seguem as notas interpretativas do PRD.

**Critérios de Aceitação:**
- [ ] Tooltip na média: "Soma dos volumes dividida pela quantidade de eventos"
- [ ] Tooltip na mediana: "Volume central quando os eventos são ordenados por tamanho. Quando poucos eventos são muito grandes, a mediana é mais representativa do tamanho típico."
- [ ] Tooltip na concentração Top 3: "Percentual da base total representada pelos 3 maiores eventos"
- [ ] Tooltip na faixa dominante: "Faixa etária com maior volume de leads neste evento"
- [ ] Tooltip na cobertura BB: "Percentual de leads com informação de vínculo BB disponível"
- [ ] Ícone de info (ℹ️) ao lado da métrica indica presença de tooltip
- [ ] Tooltips acessíveis (focusable via teclado, role="tooltip")

**Tarefas:**
- [ ] T1: Criar componente `InfoTooltip.tsx` com ícone e texto
- [ ] T2: Adicionar tooltips aos KPI cards relevantes
- [ ] T3: Adicionar tooltips ao painel consolidado (média, mediana, concentração)
- [ ] T4: Garantir acessibilidade (ARIA attributes, keyboard navigation)

**Notas técnicas:**
Reusar componente de tooltip existente no projeto se houver. Caso contrário, usar
`@radix-ui/react-tooltip` ou Tailwind-based tooltip.

## 5. Notas de Implementação Globais
- Banners e estados devem ser testados com dados reais e cenários extremos
- Skeleton loaders devem ter dimensões próximas ao conteúdo real para evitar layout shift
- Cores dos banners: amarelo (#FEF3C7 bg / #92400E text) e vermelho (#FEE2E2 bg / #991B1B text)
  — ajustar conforme sistema de cores do projeto
