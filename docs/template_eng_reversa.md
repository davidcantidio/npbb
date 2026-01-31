# [NOME DA TELA]

Template para documentar telas do sistema original e traduzir em requisitos para o novo sistema.

---

## 1. Nome da Tela
Descreva o nome exato da tela e sua funcao.

Exemplos:
- **Cadastro de Evento**
- **Listagem de Leads**
- **Dashboard Inicial**

---

## 2. Referencia Visual
- Inserir print: `./print.png`
- Se houver mais de um estado (modal, vazio, erro), adicionar prints extras.
- Se a tela depender de um fluxo, liste os passos para reproduzir.

---

## 3. Estrutura da Tela (componentes visiveis)
Liste, de cima para baixo, todos os elementos que o usuario ve.

Exemplos:
- Menu principal no cabecalho
- Painel lateral de filtros/funcionalidades
- Header com acoes
- Filtros superiores
- Tabela / cards / graficos
- Modais
- Botoes de acao

Se houver secoes, dividir em subtitulos:
- 3.1 Navegacao
- 3.2 Filtros
- 3.3 Conteudo principal
- 3.4 Acoes da tela

---

## 4. Comportamento da Tela
Como os elementos reagem as interacoes:
- O que acontece ao mudar filtros
- Como a tabela e atualizada
- Se ha paginacao, scroll infinito ou lazy loading
- Quando modais aparecem
- Feedbacks (toast, alertas, validacoes visuais)

---

## 5. Regras de Negocio Identificadas
Liste as regras logicas que a tela implica.

Exemplos:
- "Nao e possivel excluir um evento com ativacoes vinculadas"
- "Filtros sao combinaveis (data + evento + estado)"
- "Dropdown de subtipo depende do tipo selecionado"

Se algo nao estiver claro, marcar como **pendente de confirmacao**.

---

## 6. Diferencas (Original x Novo Sistema)
Divida em dois blocos:

### Original
- Descrever fielmente comportamento/elementos do sistema atual.

### Novo sistema
- O que sera mantido
- O que sera mudado
- O que sera removido
- O que sera adicionado

---

## 7. Pendencias / Duvidas
Liste tudo que ainda precisa ser descoberto/analisado:
- Campos cujo significado e incerto
- Regras que precisam ser testadas no app original
- Decisoes que dependem do time/PO
- Fluxos que precisam de mais prints

---

## 8. Backlog (requisitos)
Transforme tudo em tarefas claras.

### Backend
- Endpoints necessarios
- Filtros aceitos
- Formatos de resposta
- Regras de validacao
- Regras de agregacao (se for dashboard)
- Regras de CRUD (criar, editar, listar, excluir)

### Frontend
- Paginas/rotas
- Componentes necessarios
- Estados e interacoes
- Comportamento dos filtros
- Formularios e validacoes
- Modalidades de listagem (tabela, cards, etc)

---

## 9. Modelo de dados (opcional)
Se fizer sentido, documente entidades/tabelas envolvidas:
- tabelas e campos
- relacionamentos (1:N, N:N)
- indices/constraints importantes
