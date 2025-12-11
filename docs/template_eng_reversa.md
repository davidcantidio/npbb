# [NOME DA TELA]

## 1. Nome da Tela
Descreva o nome exato da tela e sua funÃ§Ã£o.  
Ex.: **Cadastro de Evento**, **Listagem de Leads**, **Dashboard Inicial**, etc.

---

## 2. ReferÃªncia Visual
- Inserir print: `./print.png`
- Caso haja mais de um estado da tela (ex.: modal, estado vazio, erro), adicionar prints extras.

---

## 3. Estrutura da Tela (Componentes VisÃ­veis)
Liste, de cima para baixo, todos os elementos que o usuÃ¡rio vÃª.

### Exemplos:
- Menu lateral  
- Header com aÃ§Ãµes  
- Filtros superiores  
- Tabela / cards / grÃ¡ficos  
- Modais  
- BotÃµes de aÃ§Ã£o  

Se houver seÃ§Ãµes, dividir em subtÃ­tulos:

#### 3.1 NavegaÃ§Ã£o  
#### 3.2 Filtros  
#### 3.3 ConteÃºdo Principal  
#### 3.4 AÃ§Ãµes da Tela  

---

## 4. Comportamento da Tela
Como os elementos reagem Ã s interaÃ§Ãµes:

- O que acontece ao mudar filtros  
- Como a tabela Ã© atualizada  
- Se hÃ¡ paginaÃ§Ã£o, scroll infinito ou lazy loading  
- Quando modais aparecem  
- Feedbacks (toast, alertas, validaÃ§Ãµes visuais)  

---

## 5. Regras de NegÃ³cio Identificadas
Liste as regras lÃ³gicas que a tela implica.

Exemplos:
- â€œNÃ£o Ã© possÃ­vel excluir um evento com ativaÃ§Ãµes vinculadasâ€
- â€œFiltros sÃ£o combinÃ¡veis (data + evento + estado)â€
- â€œDropdown de subtipo depende do tipo selecionadoâ€

Se algo nÃ£o estiver claro, marcar como **pendente de confirmaÃ§Ã£o**.

---

## 6. DiferenÃ§as Entre o Original e a Nossa VersÃ£o
Divida em dois blocos:

### Original:
- Descrever fielmente o comportamento/elementos que existem hoje.

### Nossa VersÃ£o:
- O que serÃ¡ mantido  
- O que serÃ¡ mudado  
- O que serÃ¡ removido  
- O que serÃ¡ adicionado  

*(Essa Ã© a parte mais importante do template.)*

---

## 7. PendÃªncias / DÃºvidas / InformaÃ§Ãµes Faltantes

Liste tudo que ainda precisa ser descoberto/analisado:

- Campos cujo significado Ã© incerto  
- Regras que precisam ser testadas no app original  
- DecisÃµes que dependem do time/PO  
- Fluxos que precisam de mais prints  

---

## 8. Desdobramento em Requisitos (Backlog da Tela)
Transforme tudo em tarefas claras.

### Backend
- Endpoints necessÃ¡rios  
- Filtros aceitos  
- Formatos de resposta  
- Regras de validaÃ§Ã£o  
- Regras de agregaÃ§Ã£o (se for dashboard)  
- Regras de CRUD (criar, editar, listar, excluir)

### Frontend
- Componentes necessÃ¡rios  
- Estados e interaÃ§Ãµes  
- Comportamento dos filtros  
- FormulÃ¡rios  
- Modalidades de listagem  
- LÃ³gica visual (ex.
