# Página de Ativos (Cotas de Ingressos)

## 1. Nome da Tela
**Página de Ativos (Cotas de Ingressos Cortesia)**  
Responsável por exibir, acompanhar e ajustar a distribuição de ingressos cortesia para cada Diretoria em cada Evento.

---

## 2. Referência Visual
- Print original usado como base: `C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\menu\Ativos\ativos.png`  Representa o estilo de layout dessa página.

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação
Mantém a estrutura padrão:
- Dashboard
- Eventos
- **Ativos** (nova)
- Cupons
- Logo e menu lateral idênticos ao original

### 3.2 Header Superior
Mesmos elementos:
- Menu sanduíche (expandir/contrair)
- Fullscreen
- Modo escuro
- Botão atualizar
- Perfil do usuário
- Breadcrumb: Dashboard > Ativos

### 3.3 Conteúdo Principal — Cards de Ativos

Cada item da tabela representa **um par Evento + Diretoria**.
substituindo as informações sobre produto trazidas na referência, por informações dos ingressos. O campos exibidos serão thumb do evento, diretoria, ingressos retirados / ingressos restantes
- Nova interface ainda será definida, mas seu comportamento está descrito abaixo.


  
- **Informação principal (centro do card):**  
  Exibição do consumo da cota:  
  **`23 / 45`**  
  (23 usados de 45 disponíveis)

- **Indicador visual:**  
  - Barra de progresso  
  - Ou chip percentual (ex.: **51% utilizado**)  
  *(decidir posteriormente, mas o documento já prevê)*

- **Ações do card:**
  - Botão **“Atribuir ingressos”**  
    Abre modal para atualizar a quantidade disponível ou registrar nova cota

### 3.4 Filtros (opcional, mas recomendado)
- Filtro por **Evento**
- Filtro por **Diretoria**
- Filtro por **Status do Evento** (se aplicável)

---

## 4. Comportamento da Tela

- Ao carregar, lista todos os cards (um por evento + diretoria com cota cadastrada).
- **Botão Atualizar** recarrega apenas os dados dos cards (sem recarregar a página toda).
- Cards são atualizados automaticamente após ajuste de cotas.
- O botão **Atribuir ingressos** abre um modal com campos:
  - Quantidade total disponibilizada
  - (Opcional) Histórico de ajustes anteriores
- Ao salvar, a cota é recalculada e o card reflete imediatamente o novo total.
- Rolagem: vertical, com cards em grid.
- Não há paginação, assim como no dashboard original.

---

## 5. Regras de Negócio Identificadas

- Cada diretoria pode ter uma quantidade **única** de ingressos por evento (já refletido no modelo `cota_cortesia`).
- A quantidade “usados” deve refletir:
  - Quantos convites foram emitidos  
  - Quantos convidados foram confirmados (dependendo da regra)
- A quantidade “disponível” é ajustada manualmente pelo botão “Atribuir ingressos”.
- Não é permitido:
  - Atribuir valor negativo
  - Definir valor menor que o número de ingressos já usados
- Cards devem ser ordenáveis (por evento, diretoria ou consumo) — prioridade média.

---

## 6. Diferenças Entre o Original e a Nossa Versão


### Nossa Versão (Página de Ativos):
- **Nenhuma tabela.**
- **Leads não aparecem aqui.**
- Nova visualização baseada em **cards por evento + diretoria**.
- Foco total em **ingressos cortesia**:
  - Capacidade total disponível
  - Quantos já foram usados
  - Controle manual das cotas
- A ação principal é **“Atribuir ingressos”**, não manipular leads.
  - Exportação CSV
  - Ações por linha (ver/editar/excluir)
- Possui:
  - Busca
  - Filtros


---

## 7. Comportamentos Confirmados

- **Ingressos usados = convites emitidos**  
  Cada convite enviado consome 1 ingresso da cota da diretoria para aquele evento.

- **Exportação CSV confirmada**  
  A página de Ativos permitirá exportar os dados de cotas e consumo em formato CSV.

- **Usuário pode acrescentar e remover cotas**  
  É permitido ajustar o total de ingressos disponíveis, tanto para aumentar quanto para reduzir a cota da diretoria.

- **Cada card terá acesso à lista de convidados**  
  O card abre uma tela filha contendo:
  - lista de convidados vinculados àquela cota  
  - ação para remover convidados  
  - remoção de convidado devolve o ingresso para o saldo disponível

---

## 8. Desdobramento em Requisitos (Backlog da Tela)

### Backend
- Endpoint: `GET /ativos`  
  Retorna lista de: evento, diretoria, usados, disponíveis.
- Endpoint: `POST /ativos/:evento_id/:diretoria_id/atribuir`  
  Ajusta quantidade total disponível.
- Endpoint: `GET /ativos/:evento_id/:diretoria_id`  
  Detalhes da cota / histórico (opcional).
- Ajustar queries de:
  - total de convites emitidos
  - total de ingressos disponíveis

### Frontend
- Página `<AtivosPage />`
- Componente `<AtivoCard />`
- Componente `<AtribuirIngressosModal />`
- Filtros:
  - Evento
  - Diretoria
- Grid responsivo para cards
- Barra superior com: Buscar / Filtrar / Atualizar (similar ao original)
- Estado de carregamento/esqueleto
- Atualizar card ao salvar modal

---

