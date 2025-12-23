# Aba de Gamificacao (Evento)

Contrato MVP (decisao): `docs/gamificacao_decisao_mvp.md`

## 1. Nome da Tela
**Gamificacao do Evento**

Aba/tela usada para cadastrar mecanicas gamificadas relacionadas a um evento (ex.: desafios, premios, textos de feedback).

Status no novo sistema:
- Frontend: nao implementado.
- Backend: parcialmente implementado (modelos/migrations existem; endpoints pendentes).

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
- **Titulo do feedback de sucesso** (obrigatorio)
- **Descricao do feedback de sucesso** (obrigatorio; referencia mostra contador 0/240)
- **Premio**: aparece como coluna na tabela da tela original; confirmar se e campo de input dedicado ou se e derivado (ex.: titulo_feedback).

### 3.2 Lista de gamificacoes
Tabela com:
- Nome
- Premio
- Acoes: editar / excluir

---

## 4. Regras de negocio (proposta)
- Gamificacao esta vinculada a uma ativacao (DECISAO: opcao B).
  - Relacao: 1:1 com `Ativacao` via `gamificacao.ativacao_id` (UNIQUE).
  - Consequencia: o evento pode ter multiplas gamificacoes (1:N) indiretamente, via suas ativacoes.
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
- Para criar/editar, a gamificacao precisa ser vinculada a uma `ativacao_id` do evento.

---

## 6. Backlog (status)
### Backend
- [ ] Modelo/tabelas de `gamificacao`
- [ ] Endpoints CRUD e validacoes

### Frontend
- [ ] Aba/pagina de gamificacao no detalhe do evento
- [ ] Formulario + lista + modal de confirmacao de exclusao
