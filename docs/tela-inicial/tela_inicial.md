# Página Inicial (Dashboard)

## 1. Nome da Tela
**Página Inicial (Dashboard geral do sistema)**  
Primeira interface exibida após o login.

---

## 2. Referência Visual
*(print: `C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\tela_inicial.png`)*

---

## 3. Estrutura da Tela (componentes visíveis)

### 3.1 Menu Lateral Esquerdo
- Dashboard  
- Leads  
- Eventos  
- Ativos  

### 3.2 Barra Superior (header)
- Botão: **tela cheia**
- Botão: **atualizar**
- Botão: **modo escuro**
- Perfil do usuário (nome + permissão)

### 3.3 Filtros Superiores
- Filtro de **Data** (ícone calendário)
- Filtro **Evento** (dropdown)
- Filtro **Estado** (dropdown)
- Filtro **Local** (dropdown)
- Botão **Limpar filtros**

### 3.4 Indicadores Principais
- **147.259 Eventos**
- **182.258 Check-ins**
- **1.333 Questionários**

### 3.5 Intervalos de Período
- Todos  
- 1M  
- 6M  
- 1A  

### 3.6 Gráfico Principal
Gráfico combinado contendo:
- Barras de **Check-ins**
- Barras de **Leads**
- Linha pontilhada de **Questionários**
- Eixo X: meses (Jan → Dez)
- Eixo Y: escala até ~40.000

### 3.7 Blocos Secundários (não detalhados no print)
- Mapas  
- Listas  
- Cards adicionais  
*(o original usa blocos extras para distribuição geográfica e breakdown por categorias)*

---

## 4. Comportamento

- Todos os elementos do dashboard são **reativos aos filtros superiores**.  
- Alterar qualquer filtro atualiza:
  - Indicadores
  - Gráfico principal
  - Blocos secundários
- O botão **Limpar filtros** retorna a visão para o estado padrão.
- Os botões de período (Todos / 1M / 6M / 1A) **limitam o range temporal dos dados**.
- O botão de **atualizar** força recarregamento dos gráficos/contadores.
- **Modo escuro** altera o tema do dashboard, mas mantém estrutura.

---

## 5. Regras de Negócio Identificadas (a partir da tela original)

- Métricas exibidas dependem do período selecionado.
- Gráfico principal agrega dados por mês.
- Filtros provavelmente impactam:
  - Lista de eventos
  - Check-ins associados
  - Leads associados
  - Questionários preenchidos
- Evento → Estado → Local podem ser filtros encadeados (cascata).
- Indicadores usam:
  - Contagem total de eventos  
  - Total de check-ins registrados  
  - Total de questionários respondidos

*(Algumas regras ainda precisam ser confirmadas no app original.)*

---

## 6. Diferenças Entre o Original e a Nossa Versão

### No Original:
- Indicadores:  
  - Eventos  
  - Check-ins  
  - Questionários  
- Gráfico principal baseado em:
  - Check-ins  
  - Leads  
  - Questionários

### Na Nossa Versão:
- Indicadores relacionados **apenas aos eventos**, tais como:
  - Total de eventos
  - Total de ativações realizadas
  - Total de investimento (soma)
  - Total de leads (se relevante)

- Gráfico principal será ligado à **evolução de eventos**, por exemplo:
  - Nº de eventos por mês  
  - Nº de ativações por mês  
  - Total de investimento por mês  

- A aba “Gamificação” não existe.  


---

## 7. Pendências / Dúvidas / Informações Faltantes

## 7. Comportamentos Confirmados

- **Filtro “Local” significa Cidade**  
  O campo "Local" exibido no dashboard original corresponde diretamente à "Cidade" na nossa modelagem. Não existe distinção entre “cidade” e “local físico”.

- **Filtros utilizam seleção única**  
  Todos os dropdowns do dashboard funcionam com seleção única (não há múltipla seleção).

- **Gráficos secundários serão mantidos**  
  Os gráficos adicionais exibidos abaixo do gráfico principal no dashboard original serão replicados, apenas ajustados para refletir dados de eventos/ativações.

- **Período “Todos” exibe o histórico completo**  
  A opção “Todos” retorna todos os registros disponíveis no banco, sem limites de data.

- **Sem paginação ou scroll nos blocos inferiores**  
  A área inferior do dashboard exibe todos os blocos simultaneamente, sem paginação ou carregamento incremental.

---

## 8. Desdobramento em Requisitos (Backlog da Tela Inicial)

### Backend
- Criar endpoint `/dashboard` aceitando filtros:
  - data_inicio / data_fim  
  - evento_id  
  - Estado  
  - cidade/local  
- Endpoint deve retornar:
  - Indicadores consolidados  
  - Dados agregados para gráfico principal  
  - Dados para blocos secundários (versão simplificada inicialmente)
- Implementar lógica de agregação mensal:
  - Eventos por mês  
  - Ativações por mês  
  - Investimento por mês (somado)

### Frontend
- Componente `<SidebarMenu />`
- Componente `<DashboardHeader />`
- Componente `<DashboardFilters />`
- Componente `<DashboardCards />`
- Gráfico principal `<EventosChart />`
- Blocos secundários (versão simplificada)
- Implementar reatividade dos filtros (contexto ou Zustand/Recoil)
- Implementar botão “Limpar filtros”
- Implementar range de período (Todos / 1M / 6M / 1A)
- Implementar modo escuro (opcional, mas presente no original)

---

