# Página de Ativos (Cotas de Ingressos)

## 1. Nome da Tela
**Página de Ativos (Cotas de Ingressos Cortesia)**  
Responsável por exibir, acompanhar e ajustar a distribuição de ingressos cortesia para cada Diretoria em cada Evento.

---

## 2. ReferÃªncia Visual
- Print original usado como base: `C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\menu\Ativos\ativos.png`  Representa o estilo de layout dessa Página.

---

## 3. Estrutura da Tela (Componentes VisÃ­veis)

### 3.1 Navegação
Mantém  a estrutura padrão descrita em: C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\tela_inicial.md


### 3.2 Header Superior
Mantém  a estrutura padrão descrita em: C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\tela_inicial.md


### 3.3 Conteúdo Principal de Cards de Ativos

Cada item da tabela representa traz os campos: 'evento', 'diretoria', disponibilidade (que traz informação da distribuição dos ingressos, por exemplo 9/15: nove ingressos distribuídos de 15)

  
- **Informação principal principal (centro do card):**  
  ExibiÃ§Ã£o do consumo da cota:  
  **`23 / 45`**  
  (23 usados de 45 disponÃ­veis)

- **Indicador visual:**  
  - Barra de progresso  
  - Ou chip percentual (ex.: **51% utilizado**)  


- **Ações do card:**
  - Botão **Atribuir ingressos**  
    Abre modal para atualizar a quantidade disponÃ­vel ou registrar nova cota para uma diretoria

### 3.4 Filtros (opcional, mas recomendado)
- Filtro por **Evento**
- Filtro por **Diretoria**
- Filtro por **data do Evento** 

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


---

## 5. Regras de Negócio Identificadas

- Cada diretoria pode ter uma quantidade **Única** de ingressos por evento (já refletido no modelo `cota_cortesia`).
- A quantidade â€œusadosâ€ deve refletir:
  - Quantos convites foram emitidos  
  - Quantos convidados foram confirmados (dependendo da regra)
- A quantidade indisponível é ajustada manualmente pelo botão atribuir ingressos.
- Não é permitido:
  - Atribuir valor negativo
  - Definir valor menor que o número de ingressos já usados
- Cards devem ser ordenáveis (por evento, diretoria ou consumo) 
---


## 7. Comportamentos Confirmados

- **Ingressos usados = convites emitidos**  
  Cada convite enviado consome 1 ingresso da cota da diretoria para aquele evento.

- **Exportação CSV confirmada**  
  A página de Ativos permitirá exportar os dados de cotas e consumo em formato CSV.

- **Usuário pode acrescentar e remover cotas**  
  é permitido ajustar o total de ingressos disponíveis, tanto para aumentar quanto para reduzir a cota da diretoria.

- **Cada card terá acesso á  lista de convidados**  
  O card abre uma tela filha contendo:
  - lista de convidados vinculados áquela cota  
  - ação para remover convidados  
  - remoção de convidado devolve o ingresso para o saldo disponível
  - referencia visual desta tela em  C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\code\npbb\docs\tela-inicial\menu\Ativos\tela_convidados_referencia.png

---

## 8. Desdobramento em Requisitos (Backlog da Tela)

### Backend
- Endpoint: `GET /ativos`  
  Retorna lista de: evento, diretoria, usados, disponÃ­veis.
- Endpoint: `POST /ativos/:evento_id/:diretoria_id/atribuir`  
  Ajusta quantidade total disponÃ­vel.
- Endpoint: `GET /ativos/:evento_id/:diretoria_id`  
  Detalhes da cota / histÃ³rico (opcional).
- Ajustar queries de:
  - total de convites emitidos
  - total de ingressos disponÃ­veis

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

