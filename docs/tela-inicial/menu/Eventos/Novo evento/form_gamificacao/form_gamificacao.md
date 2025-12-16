# Aba de Gamificacao (Evento)

## 1. Nome da Tela
**Gamificacao do Evento**

Aba/tela usada para cadastrar mecanicas gamificadas relacionadas a um evento (ex.: desafios, premios, textos de feedback).

Status no novo sistema:
- Frontend: nao implementado.
- Backend: nao implementado.

---

## 2. Objetivo
- Cadastrar multiplas gamificacoes para um evento.
- Permitir editar/excluir itens.
- (Fase futura) Associar gamificacao a ativacoes e/ou cupons.

---

## 3. Estrutura (proposta)
### 3.1 Formulario
- **Nome** (obrigatorio)
- **Descricao** (obrigatorio)
- Premio (a confirmar no original)
- Titulo do feedback de sucesso (opcional)
- Descricao do feedback de sucesso (opcional)

### 3.2 Lista de gamificacoes
Tabela com:
- Nome
- Premio
- Acoes: editar / excluir

---

## 4. Regras de negocio (proposta)
- Gamificacao pertence a um unico evento (1:N).
- Campos obrigatorios: nome e descricao.
- Definir limite de caracteres e se existe campo "premio" obrigatorio.

---

## 5. Endpoints (proposta / a confirmar)
Sugerido seguir o padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/gamificacoes` (lista)
- `POST /evento/{id}/gamificacoes` (cria)
- `PUT /gamificacao/{id}` (edita)
- `DELETE /gamificacao/{id}` (remove)

---

## 6. Backlog (status)
### Backend
- [ ] Modelo/tabelas de `gamificacao`
- [ ] Endpoints CRUD e validacoes

### Frontend
- [ ] Aba/pagina de gamificacao no detalhe do evento
- [ ] Formulario + lista + modal de confirmacao de exclusao
