# Aba de Gamificacao (Evento)

Contrato MVP (decisao): `docs/gamificacao_decisao_mvp.md`

## 1. Nome da Tela
**Gamificacao do Evento**

Aba/tela usada para cadastrar mecanicas gamificadas relacionadas a um evento (ex.: desafios, premios, textos de feedback).

Status no novo sistema:
- Frontend: implementado (MVP: criar/editar/excluir/listar).
- Backend: implementado (endpoints + validacoes + permissoes).

---

## 2. Objetivo
- Cadastrar multiplas gamificacoes para um evento.
- Permitir editar/excluir itens.
- (Fase futura) Associar gamificacao a ativacoes e/ou cupons.

---

## 3. Estrutura (proposta)
### 3.1 Formulario
- **Nome da gamificacao** (obrigatorio)
- **Descricao** (obrigatorio; referencia mostra contador 0/240)
- **Premio** (obrigatorio)
- **Titulo do feedback de sucesso** (obrigatorio)
- **Descricao do feedback de sucesso** (obrigatorio; referencia mostra contador 0/240)
Observacao: a tela original exibe a coluna **Premio** na tabela; no MVP manter `premio` como campo do contrato.

### 3.2 Lista de gamificacoes
Tabela com:
- Nome
- Premio
- Acoes: editar / excluir

---

## 4. Regras de negocio (proposta)
- Gamificacao pertence a um unico evento e e selecionada em uma ativacao (conforme tela de referencia).
  - Relacao: 1:N `Evento` -> `Gamificacao` via `gamificacao.evento_id`.
  - Na `Ativacao`, existe selecao opcional de `gamificacao_id` (inclui opcao "Nenhuma").
- Campos obrigatorios (referencia):
  - nome, descricao, titulo_feedback, texto_feedback
- Limites (referencia):
  - `descricao` e `texto_feedback`: max 240 chars (contador na UI original).

---

## 5. Endpoints (proposta / a confirmar)
Sugerido seguir o padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/gamificacoes` (lista)
- `POST /evento/{id}/gamificacoes` (cria)
- `PUT /gamificacao/{id}` (edita)
- `DELETE /gamificacao/{id}` (remove)

Observacao (contrato decidido):
- A gamificacao e criada no contexto do evento; a vinculacao ocorre na ativacao via `gamificacao_id` (ou "Nenhuma").

---

## 6. Backlog (status)
### Backend
- [ ] Modelo/tabelas de `gamificacao`
- [ ] Endpoints CRUD e validacoes

### Frontend
- [ ] Aba/pagina de gamificacao no detalhe do evento
- [ ] Formulario + lista + modal de confirmacao de exclusao
