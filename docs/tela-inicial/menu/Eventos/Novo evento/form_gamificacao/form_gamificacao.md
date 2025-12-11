# Aba de GamificaÃ§Ã£o (Cadastro / EdiÃ§Ã£o)

## 1. Nome da Tela
**GamificaÃ§Ã£o do Evento**

Aba usada para registrar mecÃ¢nicas gamificadas relacionadas a um evento, permitindo cadastrar mÃºltimas gamificaÃ§Ãµes, cada uma representando uma aÃ§Ã£o, atividade ou premiaÃ§Ã£o dentro do evento.

---

## 2. ReferÃªncia Visual
Print disponÃ­vel:  
`docs/tela-inicial/menu/Eventos/Editar/gamificacao.png`

---

## 3. Estrutura da Tela (Componentes VisÃ­veis)

### 3.1 NavegaÃ§Ã£o
Abas do evento:
- Evento  
- FormulÃ¡rio de Lead  
- **GamificaÃ§Ã£o** (aba atual)  
- AtivaÃ§Ãµes  
- QuestionÃ¡rio  

### 3.2 FormulÃ¡rio de GamificaÃ§Ã£o
Campos exibidos:

1. **Nome da gamificaÃ§Ã£o** (texto obrigatÃ³rio)  
2. **DescriÃ§Ã£o** (textarea obrigatÃ³rio)  
3. **TÃ­tulo do feedback de sucesso**  
4. **DescriÃ§Ã£o do feedback de sucesso**  

BotÃ£o **Adicionar** para registrar uma nova gamificaÃ§Ã£o.

### 3.3 Lista de GamificaÃ§Ãµes Adicionadas
Tabela contendo:

- Nome  
- PrÃªmio (nÃ£o exibido no formulÃ¡rio atual, mas aparece na lista)  
- AÃ§Ãµes:
  - Editar  
  - Excluir  

---

## 4. Comportamento

- Ao preencher os campos e clicar **Adicionar**, a gamificaÃ§Ã£o Ã© associada ao evento.  
- A lista Ã© atualizada imediatamente.  
- Editar abre os campos carregados.  
- Excluir remove definitivamente a gamificaÃ§Ã£o do evento.  
- NÃ£o hÃ¡ limite de gamificaÃ§Ãµes por evento.  

---

## 5. Regras de NegÃ³cio Identificadas

- Cada gamificaÃ§Ã£o pertence **a um Ãºnico evento**.  
- Um evento pode ter **vÃ¡rias gamificaÃ§Ãµes** (relaÃ§Ã£o 1:N).  
- Campos â€œNomeâ€ e â€œDescriÃ§Ã£oâ€ sÃ£o obrigatÃ³rios.  
- O campo â€œPrÃªmioâ€ existe no original, entÃ£o deve ser incluÃ­do no modelo.  
- A gamificaÃ§Ã£o Ã© **puramente descritiva** â€” nÃ£o interfere em cotas, convidados, leads ou ativaÃ§Ãµes.  
- Remover o evento deve remover gamificaÃ§Ãµes vinculadas (ON DELETE CASCADE).  

---

## 6. DiferenÃ§as Entre o Original e a Nossa VersÃ£o

### Original:
- Foco em mecÃ¢nicas de gamificaÃ§Ã£o usadas em ativaÃ§Ãµes.  
- ContÃ©m â€œNomeâ€, â€œDescriÃ§Ã£oâ€, â€œPrÃªmioâ€ e textos de feedback.  

### Nossa VersÃ£o:
- MantÃ©m todos os campos originais.  
- Pode servir como metadado adicional para BI ou relatÃ³rios.  
- Nenhuma lÃ³gica de pontuaÃ§Ã£o ou mecÃ¢nica dinÃ¢mica serÃ¡ implementada no MVP.  

---

## 7. PendÃªncias / DÃºvidas

- Confirmar se â€œPrÃªmioâ€ Ã© um campo obrigatÃ³rio no cadastro do item.  
- Confirmar se feedbacks sÃ£o exibidos ao usuÃ¡rio final em alguma interface.  
- Confirmar se haverÃ¡ limite de caracteres ou anexos.  

---

## 8. Backlog da FunÃ§Ã£o

### Backend (FastAPI)
- Modelo SQLAlchemy/SQLModel para `gamificacao`  
- Endpoints:
  - `POST /eventos/{id}/gamificacao`
  - `GET /eventos/{id}/gamificacao`
  - `PUT /gamificacao/{id}`
  - `DELETE /gamificacao/{id}`
- Regras:
  - Validar obrigatÃ³rios
  - Cascade ao excluir evento

### Frontend (React)
- Aba `<EventoGamificacao />`
- Componentes:
  - FormulÃ¡rio de criaÃ§Ã£o/ediÃ§Ã£o
  - Lista de gamificaÃ§Ãµes
  - BotÃµes editar/excluir
- ValidaÃ§Ã£o de campos obrigatÃ³rios
- Estado persistente ao trocar abas

---
