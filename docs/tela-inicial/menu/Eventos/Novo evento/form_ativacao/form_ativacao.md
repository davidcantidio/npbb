# Aba de Ativacoes (Evento)

## 1. Nome da Tela
**Ativacoes do Evento**

Aba/tela usada para criar, editar e listar ativacoes pertencentes a um evento.

Status no novo sistema:
- Frontend: nao implementado.
- Backend: nao implementado.

---

## 2. Objetivo
Permitir que o usuario cadastre ativacoes (acoes do evento) e configure regras como:
- check-in unico por ativacao
- termo de uso
- gerar cupom
- redirecionamento para pesquisa
- mensagens exibidas no QR code

---

## 3. Estrutura (proposta)
### 3.1 Formulario de ativacao
Campos sugeridos:
- **Nome da ativacao** (obrigatorio)
- **Mensagem do QR Code** (opcional, max 240)
- **Mensagem** (opcional, max 240)
- Switches:
  - Redireciona para pesquisa
  - Check-in unico
  - Termo de uso
  - Gerar cupom

### 3.2 Lista de ativacoes
Tabela/lista com:
- Nome
- Check-in unico (sim/nao)
- Acoes: visualizar / editar / excluir

---

## 4. Regras de negocio (proposta)
- Uma ativacao pertence a um unico evento.
- Nao permitir exclusao se existirem dependencias (ex.: leads registrados na ativacao) - regra a definir.
- Validacoes:
  - nome obrigatorio
  - limites de tamanho (mensagens)

---

## 5. Endpoints (proposta / a confirmar)
Sugerido seguir o padrao do modulo de eventos (`/evento`):
- `GET /evento/{id}/ativacoes` (lista)
- `POST /evento/{id}/ativacoes` (cria)
- `PUT /ativacao/{id}` (edita)
- `DELETE /ativacao/{id}` (remove)

---

## 6. Backlog (status)
### Backend
- [ ] Modelo/tabelas de `ativacao`
- [ ] Endpoints CRUD e validacoes

### Frontend
- [ ] Aba/pagina de ativacoes no detalhe do evento
- [ ] Formulario + lista + modal de confirmacao de exclusao
