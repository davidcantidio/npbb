# PÃ¡gina Inicial (Dashboard)

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
- Dashboard (Página atual)
- Eventos
- Ativos (cotas de ingressos)
- Leads 
- Cupons
- Convidadores / Convidados (opcional)  - Esta funcionalidade será um link para a plataforma de distribuição de ativos colocada dentro da seção ativos


### 3.2 Barra Superior
- Botão tela cheia
- Botão atualizar
- Botão modo escuro
- Perfil do usuário (nome + permissÃ£o)

### 3.3 Filtros Superiores
| Filtro          | Tipo                  | Comportamento                  |
|-----------------|-----------------------|--------------------------------|
| Data            | Intervalo de datas    | AplicÃ¡vel a todos os indicadores |
| Evento          | SeleÃ§Ã£o Ãºnica         | Filtra por um evento especÃ­fico |
| Estado          | SeleÃ§Ã£o Ãºnica         |                                |
| Cidade (Local)  | SeleÃ§Ã£o Ãºnica         |                                |
| Limpar filtros  | BotÃ£o                 | Reseta todos os filtros        |

### 3.4 Intervalos de PerÃ­odo
BotÃµes rÃ¡pidos: **Todos** | **1M** | **6M** | **1A**  
Aplicam filtro automÃ¡tico de data.

### 3.5 Indicadores Principais (KPIs)

| KPI                          | DescriÃ§Ã£o                                             |
|------------------------------|-------------------------------------------------------|
| Total de eventos no perÃ­odo  | Quantidade de eventos filtrados                       |
| Total de ativaÃ§Ãµes realizadas| Quantidade de ativaÃ§Ãµes concluÃ­das                    |
| Total investido              | Soma de investimentos (patrocÃ­nio + promoÃ§Ã£o)         |
| Ingressos usados             | Total de convites emitidos (consumo de cotas)         |

### 3.6 GrÃ¡fico Principal
Tipo: Combinado (barras + linha)  
Eixo X: Meses (Jan â†’ Dez)  
Eixo Y esquerdo: Quantidade  
Eixo Y direito: Valor (R$)  

SÃ©ries:
- Eventos por mÃªs (barras azuis)
- AtivaÃ§Ãµes por mÃªs (barras verdes)
- Total investido por mÃªs (linha laranja)

### 3.7 Blocos SecundÃ¡rios
Layout em grid responsivo (scroll vertical)

| Bloco                          | Tipo de VisualizaÃ§Ã£o          |
|--------------------------------|-------------------------------|
| Eventos por Estado             | Mapa ou barras horizontais    |
| AtivaÃ§Ãµes por Tipo             | GrÃ¡fico de pizza ou barras    |
| Investimento por Diretoria     | Barras horizontais            |
| Ingressos usados por Diretoria | Barras verticais + %          |
| Eventos mais ativos            | Lista com top 5               |

---

## 4. Comportamento da Tela

| AÃ§Ã£o                          | Resultado                                                                 |
|-------------------------------|---------------------------------------------------------------------------|
| Alterar qualquer filtro       | Atualiza KPIs, grÃ¡fico principal e blocos secundÃ¡rios automaticamente     |
| Clicar em perÃ­odo (1M/6M/1A)  | Preenche filtro de data e atualiza toda a tela                            |
| Limpar filtros                | Volta ao estado â€œTodosâ€ (histÃ³rico completo)                              |
| BotÃ£o Atualizar               | ForÃ§a recarregamento dos dados                                            |
| Modo escuro                   | Altera tema visual (nÃ£o afeta dados)                                      |
| Estado carregando             | Spinner central enquanto dados sÃ£o buscados                               |

---

## 5. Regras de NegÃ³cio Principais

- Todos os dados sÃ£o **filtrados** antes de qualquer agregaÃ§Ã£o
- AgregaÃ§Ãµes mensais para o grÃ¡fico principal
- â€œLocalâ€ = Cidade (mesmo campo no banco)
- Filtros sÃ£o sempre **seleÃ§Ã£o Ãºnica**
- PerÃ­odo â€œTodosâ€ exibe histÃ³rico completo
- Sem paginaÃ§Ã£o nos blocos inferiores (scroll Ãºnico)
- Lead existe apenas como backend (Salesforce) â€” nÃ£o aparece no Dashboard

---

## 6. DiferenÃ§as â€“ Sistema Original Ã— Nova VersÃ£o

| Item                     | Sistema Original                          | Nova VersÃ£o                                      |
|--------------------------|-------------------------------------------|--------------------------------------------------|
| Foco                     | Leads, Check-ins, QuestionÃ¡rios           | Eventos, AtivaÃ§Ãµes, Investimentos, Ingressos     |
| KPIs                     | Eventos, Check-ins, QuestionÃ¡rios         | Eventos, AtivaÃ§Ãµes, Investido, Ingressos usados  |
| GrÃ¡fico principal        | Leads Ã— Check-ins Ã— QuestionÃ¡rios         | Eventos / mÃªs, AtivaÃ§Ãµes / mÃªs, Investido / mÃªs  |
| MÃ³dulos visÃ­veis         | Leads proeminente                         | Leads removido; Ativos e Convidados adicionados  |
| MÃ©tricas                 | Captura de leads                          | OperaÃ§Ã£o interna e gestÃ£o de cotas               |

---

## 7. PendÃªncias / DÃºvidas

- Definir cores exatas e biblioteca de grÃ¡ficos (Chart.js, Recharts ou ApexCharts)?
- Blocos secundÃ¡rios: quais entram no MVP? (sugerido todos)
- ExportaÃ§Ã£o de dados do Dashboard (CSV/PDF) serÃ¡ necessÃ¡ria no MVP?
- Incluir indicador de â€œIngressos disponÃ­veisâ€ nos KPIs?

---

## 8. Backlog da Tela (Requisitos)

### Backend
- Endpoint principal: `GET /dashboard`
  ParÃ¢metros: `data_inicio`, `data_fim`, `evento_id`, `estado`, `cidade`
- Retorno JSON com:
  - kpis { eventos, ativacoes, investido, ingressos_usados }
  - series_mensais { meses, eventos, ativacoes, investido }
  - blocos { eventos_por_estado, ativacoes_por_tipo, investimento_por_diretoria, ingressos_por_diretoria, eventos_mais_ativos }
- FunÃ§Ãµes de agregaÃ§Ã£o mensais otimizadas (usar queries SQL eficientes)

### Frontend
- PÃ¡gina `<Dashboard />`
- Componentes reutilizÃ¡veis:
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
- Tooltips explicativos nos KPIs e grÃ¡ficos

Chamadas à API capturadas (após login):
POST https://api.bbleads.com.br/auth/login → 200
GET https://api.bbleads.com.br/auth/me → 200 (duas vezes)
Dashboards e auxiliares:
GET /dash/leads/cidade, /dash/leads/estado, /dash/leads, /dash, /dash/porcentagem/leads/evento, /dash/faixa/etaria, /dash/leads/periodo (algumas primeiras 401 antes do token, depois 200)
GET /evento/all/cidades, /evento/all/estados → 200