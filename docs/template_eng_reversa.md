# [NOME DA TELA]

## 1. Nome da Tela
Descreva o nome exato da tela e sua função.  
Ex.: **Cadastro de Evento**, **Listagem de Leads**, **Dashboard Inicial**, etc.

---

## 2. Referência Visual
- Inserir print: `./print.png`
- Caso haja mais de um estado da tela (ex.: modal, estado vazio, erro), adicionar prints extras.

---

## 3. Estrutura da Tela (Componentes Visíveis)
Liste, de cima para baixo, todos os elementos que o usuário vê.

### Exemplos:
- Menu lateral  
- Header com ações  
- Filtros superiores  
- Tabela / cards / gráficos  
- Modais  
- Botões de ação  

Se houver seções, dividir em subtítulos:

#### 3.1 Navegação  
#### 3.2 Filtros  
#### 3.3 Conteúdo Principal  
#### 3.4 Ações da Tela  

---

## 4. Comportamento da Tela
Como os elementos reagem às interações:

- O que acontece ao mudar filtros  
- Como a tabela é atualizada  
- Se há paginação, scroll infinito ou lazy loading  
- Quando modais aparecem  
- Feedbacks (toast, alertas, validações visuais)  

---

## 5. Regras de Negócio Identificadas
Liste as regras lógicas que a tela implica.

Exemplos:
- “Não é possível excluir um evento com ativações vinculadas”
- “Filtros são combináveis (data + evento + estado)”
- “Dropdown de subtipo depende do tipo selecionado”

Se algo não estiver claro, marcar como **pendente de confirmação**.

---

## 6. Diferenças Entre o Original e a Nossa Versão
Divida em dois blocos:

### Original:
- Descrever fielmente o comportamento/elementos que existem hoje.

### Nossa Versão:
- O que será mantido  
- O que será mudado  
- O que será removido  
- O que será adicionado  

*(Essa é a parte mais importante do template.)*

---

## 7. Pendências / Dúvidas / Informações Faltantes

Liste tudo que ainda precisa ser descoberto/analisado:

- Campos cujo significado é incerto  
- Regras que precisam ser testadas no app original  
- Decisões que dependem do time/PO  
- Fluxos que precisam de mais prints  

---

## 8. Desdobramento em Requisitos (Backlog da Tela)
Transforme tudo em tarefas claras.

### Backend
- Endpoints necessários  
- Filtros aceitos  
- Formatos de resposta  
- Regras de validação  
- Regras de agregação (se for dashboard)  
- Regras de CRUD (criar, editar, listar, excluir)

### Frontend
- Componentes necessários  
- Estados e interações  
- Comportamento dos filtros  
- Formulários  
- Modalidades de listagem  
- Lógica visual (ex.
