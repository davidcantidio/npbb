# Pagina Inicial (Dashboard)

## 1. Nome da Tela
**Pagina Inicial (Dashboard Geral)**

Primeira tela exibida apos o login. Fornece visao consolidada de eventos, ativacoes, investimentos e ingressos (ativos/cotas).

Status no novo sistema:
- Frontend: nao implementado.
- Backend: nao implementado.

---

## 2. Referencia Visual
Print do sistema original:
`docs/tela-inicial/tela_inicial.png`

---

## 3. Estrutura da Tela
### 3.1 Menu lateral
- Dashboard (pagina atual)
- Eventos
- Ativos (cotas de ingressos)
- Leads (na nova versao pode ser removido ou virar submenu)
- Cupons
- Convidadores / Convidados (opcional - pode virar link externo na area de Ativos)

### 3.2 Barra superior
- Botao tela cheia
- Botao atualizar
- Botao modo escuro
- Perfil do usuario (nome + permissao)

### 3.3 Filtros
| Filtro | Tipo | Observacao |
|---|---|---|
| Data | intervalo | afeta todos os indicadores |
| Evento | selecao unica | filtra por um evento |
| Estado | selecao unica | UF |
| Cidade | selecao unica | local |
| Limpar filtros | botao | reseta filtros |

### 3.4 Atalhos de periodo
Botoes: **Todos** | **1M** | **6M** | **1A**

### 3.5 Indicadores (KPIs)
- Total de eventos no periodo
- Total de ativacoes realizadas
- Total investido
- Ingressos usados

### 3.6 Grafico principal
Tipo combinado (barras + linha), por mes:
- Eventos por mes
- Ativacoes por mes
- Total investido por mes

### 3.7 Blocos secundarios
Sugestao de blocos (grid responsivo):
- Eventos por Estado
- Ativacoes por Tipo
- Investimento por Diretoria
- Ingressos usados por Diretoria
- Eventos mais ativos (top 5)

---

## 4. Regras e comportamento (observado no original)
- Alterar qualquer filtro atualiza KPIs/graficos automaticamente.
- Filtros sao combinaveis.
- Periodo "Todos" exibe historico completo.
- Botao "Atualizar" recarrega os dados.

---

## 5. Chamadas de API observadas (sistema original)
Exemplos capturados no original (referencia):
- `POST /auth/login`
- `GET /auth/me`
- Dashboards:
  - `GET /dash/leads/periodo`
  - `GET /dash/leads/estado`
  - `GET /dash/leads/cidade`
  - `GET /dash/leads`
  - `GET /dash/porcentagem/leads/evento`
  - `GET /dash/faixa/etaria`
- Auxiliares:
  - `GET /evento/all/cidades`
  - `GET /evento/all/estados`

Observacao: no novo sistema esses endpoints ainda nao existem; servem apenas como base para planejar o contrato.

---

## 6. Backlog (requisitos)
### Backend (proposta)
- `GET /dashboard`
  - Params: `data_inicio`, `data_fim`, `evento_id`, `estado`, `cidade`
  - Retorno:
    - `kpis` (eventos, ativacoes, investido, ingressos_usados)
    - `series_mensais` (meses + series)
    - `blocos` (agregacoes para cards)

### Frontend (proposta)
- Pagina `<Dashboard />`
- Componentes:
  - filtros
  - KPI cards
  - grafico principal
  - blocos secundarios
