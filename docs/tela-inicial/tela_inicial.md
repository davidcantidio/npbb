# Página Inicial (Dashboard)

## 1. Nome da Tela
**Página Inicial (Dashboard Geral)**  
Primeira tela exibida após o login.  
Fornece visão consolidada de eventos, ativações, investimentos e ingressos.

---

## 2. Referência Visual
Print do sistema original:  
`docs/tela-inicial/tela_inicial.png`

---

## 3. Estrutura da Tela

### 3.1 Menu Lateral Esquerdo
- Dashboard (página atual)
- Eventos
- Ativos (cotas de ingressos)
- Convidadores / Convidados (opcional)  
*(Módulo Leads removido no novo sistema)*

### 3.2 Barra Superior
- Botão tela cheia
- Botão atualizar
- Botão modo escuro
- Perfil do usuário (nome + permissão)

### 3.3 Filtros Superiores
| Filtro          | Tipo                  | Comportamento                  |
|-----------------|-----------------------|--------------------------------|
| Data            | Intervalo de datas    | Aplicável a todos os indicadores |
| Evento          | Seleção única         | Filtra por um evento específico |
| Estado          | Seleção única         |                                |
| Cidade (Local)  | Seleção única         |                                |
| Limpar filtros  | Botão                 | Reseta todos os filtros        |

### 3.4 Intervalos de Período
Botões rápidos: **Todos** | **1M** | **6M** | **1A**  
Aplicam filtro automático de data.

### 3.5 Indicadores Principais (KPIs)

| KPI                          | Descrição                                             |
|------------------------------|-------------------------------------------------------|
| Total de eventos no período  | Quantidade de eventos filtrados                       |
| Total de ativações realizadas| Quantidade de ativações concluídas                    |
| Total investido              | Soma de investimentos (patrocínio + promoção)         |
| Ingressos usados             | Total de convites emitidos (consumo de cotas)         |

### 3.6 Gráfico Principal
Tipo: Combinado (barras + linha)  
Eixo X: Meses (Jan → Dez)  
Eixo Y esquerdo: Quantidade  
Eixo Y direito: Valor (R$)  

Séries:
- Eventos por mês (barras azuis)
- Ativações por mês (barras verdes)
- Total investido por mês (linha laranja)

### 3.7 Blocos Secundários
Layout em grid responsivo (scroll vertical)

| Bloco                          | Tipo de Visualização          |
|--------------------------------|-------------------------------|
| Eventos por Estado             | Mapa ou barras horizontais    |
| Ativações por Tipo             | Gráfico de pizza ou barras    |
| Investimento por Diretoria     | Barras horizontais            |
| Ingressos usados por Diretoria | Barras verticais + %          |
| Eventos mais ativos            | Lista com top 5               |

---

## 4. Comportamento da Tela

| Ação                          | Resultado                                                                 |
|-------------------------------|---------------------------------------------------------------------------|
| Alterar qualquer filtro       | Atualiza KPIs, gráfico principal e blocos secundários automaticamente     |
| Clicar em período (1M/6M/1A)  | Preenche filtro de data e atualiza toda a tela                            |
| Limpar filtros                | Volta ao estado “Todos” (histórico completo)                              |
| Botão Atualizar               | Força recarregamento dos dados                                            |
| Modo escuro                   | Altera tema visual (não afeta dados)                                      |
| Estado carregando             | Spinner central enquanto dados são buscados                               |

---

## 5. Regras de Negócio Principais

- Todos os dados são **filtrados** antes de qualquer agregação
- Agregações mensais para o gráfico principal
- “Local” = Cidade (mesmo campo no banco)
- Filtros são sempre **seleção única**
- Período “Todos” exibe histórico completo
- Sem paginação nos blocos inferiores (scroll único)
- Lead existe apenas como backend (Salesforce) — não aparece no Dashboard

---

## 6. Diferenças – Sistema Original × Nova Versão

| Item                     | Sistema Original                          | Nova Versão                                      |
|--------------------------|-------------------------------------------|--------------------------------------------------|
| Foco                     | Leads, Check-ins, Questionários           | Eventos, Ativações, Investimentos, Ingressos     |
| KPIs                     | Eventos, Check-ins, Questionários         | Eventos, Ativações, Investido, Ingressos usados  |
| Gráfico principal        | Leads × Check-ins × Questionários         | Eventos / mês, Ativações / mês, Investido / mês  |
| Módulos visíveis         | Leads proeminente                         | Leads removido; Ativos e Convidados adicionados  |
| Métricas                 | Captura de leads                          | Operação interna e gestão de cotas               |

---

## 7. Pendências / Dúvidas

- Definir cores exatas e biblioteca de gráficos (Chart.js, Recharts ou ApexCharts)?
- Blocos secundários: quais entram no MVP? (sugerido todos)
- Exportação de dados do Dashboard (CSV/PDF) será necessária no MVP?
- Incluir indicador de “Ingressos disponíveis” nos KPIs?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- Endpoint principal: `GET /dashboard`
  Parâmetros: `data_inicio`, `data_fim`, `evento_id`, `estado`, `cidade`
- Retorno JSON com:
  - kpis { eventos, ativacoes, investido, ingressos_usados }
  - series_mensais { meses, eventos, ativacoes, investido }
  - blocos { eventos_por_estado, ativacoes_por_tipo, investimento_por_diretoria, ingressos_por_diretoria, eventos_mais_ativos }
- Funções de agregação mensais otimizadas (usar queries SQL eficientes)

### Frontend
- Página `<Dashboard />`
- Componentes reutilizáveis:
  - `<DashboardHeader />`
  - `<DashboardFilters />`
  - `<PeriodButtons />`
  - `<KPI Cards />`
  - `<MainChart />`
  - `<SecondaryBlocks />` (grid responsivo)
- Estado global de filtros (React Context ou Zustand)
- Reatividade total com debouncing nos filtros
- Skeleton loading durante carregamento
- Suporte completo a tema escuro
- Tooltips explicativos nos KPIs e gráficos

Pronto para colar no Notion, Confluence, GitHub ou documento de especificação!