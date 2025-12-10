# Aba de Gamificação (Cadastro / Edição)

## 1. Nome da Tela
**Gamificação do Evento**

Aba usada para registrar mecânicas gamificadas relacionadas a um evento, permitindo cadastrar múltimas gamificações, cada uma representando uma ação, atividade ou premiação dentro do evento.

---

## 2. Referência Visual
Print disponível:  
`docs/tela-inicial/menu/Eventos/Editar/gamificacao.png`

---

## 3. Estrutura da Tela (Componentes Visíveis)

### 3.1 Navegação
Abas do evento:
- Evento  
- Formulário de Lead  
- **Gamificação** (aba atual)  
- Ativações  
- Questionário  

### 3.2 Formulário de Gamificação
Campos exibidos:

1. **Nome da gamificação** (texto obrigatório)  
2. **Descrição** (textarea obrigatório)  
3. **Título do feedback de sucesso**  
4. **Descrição do feedback de sucesso**  

Botão **Adicionar** para registrar uma nova gamificação.

### 3.3 Lista de Gamificações Adicionadas
Tabela contendo:

- Nome  
- Prêmio (não exibido no formulário atual, mas aparece na lista)  
- Ações:
  - Editar  
  - Excluir  

---

## 4. Comportamento

- Ao preencher os campos e clicar **Adicionar**, a gamificação é associada ao evento.  
- A lista é atualizada imediatamente.  
- Editar abre os campos carregados.  
- Excluir remove definitivamente a gamificação do evento.  
- Não há limite de gamificações por evento.  

---

## 5. Regras de Negócio Identificadas

- Cada gamificação pertence **a um único evento**.  
- Um evento pode ter **várias gamificações** (relação 1:N).  
- Campos “Nome” e “Descrição” são obrigatórios.  
- O campo “Prêmio” existe no original, então deve ser incluído no modelo.  
- A gamificação é **puramente descritiva** — não interfere em cotas, convidados, leads ou ativações.  
- Remover o evento deve remover gamificações vinculadas (ON DELETE CASCADE).  

---

## 6. Diferenças Entre o Original e a Nossa Versão

### Original:
- Foco em mecânicas de gamificação usadas em ativações.  
- Contém “Nome”, “Descrição”, “Prêmio” e textos de feedback.  

### Nossa Versão:
- Mantém todos os campos originais.  
- Pode servir como metadado adicional para BI ou relatórios.  
- Nenhuma lógica de pontuação ou mecânica dinâmica será implementada no MVP.  

---

## 7. Pendências / Dúvidas

- Confirmar se “Prêmio” é um campo obrigatório no cadastro do item.  
- Confirmar se feedbacks são exibidos ao usuário final em alguma interface.  
- Confirmar se haverá limite de caracteres ou anexos.  

---

## 8. Backlog da Função

### Backend (FastAPI)
- Modelo SQLAlchemy/SQLModel para `gamificacao`  
- Endpoints:
  - `POST /eventos/{id}/gamificacao`
  - `GET /eventos/{id}/gamificacao`
  - `PUT /gamificacao/{id}`
  - `DELETE /gamificacao/{id}`
- Regras:
  - Validar obrigatórios
  - Cascade ao excluir evento

### Frontend (React)
- Aba `<EventoGamificacao />`
- Componentes:
  - Formulário de criação/edição
  - Lista de gamificações
  - Botões editar/excluir
- Validação de campos obrigatórios
- Estado persistente ao trocar abas

---
