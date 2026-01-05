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

## 2.1 Contrato (MVP) - decisoes
### Campos (UI -> API/DB)
- **Nome da ativacao** -> `nome` (obrigatorio; max 100)
- **Mensagem do QR Code** -> `mensagem_qrcode` (opcional; max 240)
- **Mensagem** -> `descricao` (opcional; max 240)
  - Nota: hoje no DB `descricao` e obrigatorio e max 200; para o MVP vamos ajustar para ser opcional e max 240 (issue "alinhar modelo/DB").
- **Gamificacao** -> `gamificacao_id` (opcional)
  - Regra: se informado, deve pertencer ao mesmo evento (`gamificacao.evento_id == ativacao.evento_id`).
- Switches:
  - **Redireciona para pesquisa** -> `redireciona_pesquisa` (bool; default `false`)
  - **Check-in unico** -> `checkin_unico` (bool; default `false`)
  - **Termo de uso** -> `termo_uso` (bool; default `false`)
  - **Gerar cupom** -> `gera_cupom` (bool; default `false`)
    - Nota: o comportamento de gerar cupom/fluxo publico nao entra no MVP; por enquanto e apenas flag/configuracao.
- **Valor** -> `valor` (fora do MVP)
  - Decisao MVP: nao expor no formulario/API de ativacoes; backend seta `0.00` no create.

### Ordenacao (MVP)
- Lista de ativacoes: ordenar por `id` asc.

---

## 3. Estrutura (proposta)
### 3.1 Formulario de ativacao
Campos sugeridos:
- **Nome da ativacao** (obrigatorio)
- **Mensagem do QR Code** (opcional, max 240)
- **Mensagem** (opcional, max 240)
- **Gamificacao** (opcional; seleciona uma gamificacao cadastrada no evento, ou "Nenhuma")
- Switches:
  - Redireciona para pesquisa
  - Check-in unico
  - Termo de uso
  - Gerar cupom

### 3.2 Lista de ativacoes
Tabela/lista com:
- Nome
- Check-in unico (sim/nao)
- Gamificacao (nome ou sim/nao)
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

### 5.1 Payloads (MVP)
#### AtivacaoRead (response)
Campos retornados (MVP):
- `id`, `evento_id`, `nome`, `descricao`, `mensagem_qrcode`, `gamificacao_id`
- `redireciona_pesquisa`, `checkin_unico`, `termo_uso`, `gera_cupom`
- `created_at`, `updated_at`

#### POST /evento/{id}/ativacoes (create)
Request (MVP):
- `nome` (obrigatorio)
- `descricao` (opcional)
- `mensagem_qrcode` (opcional)
- `gamificacao_id` (opcional)
- switches (opcionais; default `false`)

#### PUT /ativacao/{id} (update)
Request (MVP):
- todos os campos acima como opcionais
- regra: payload sem campos retorna `400` com code `VALIDATION_ERROR_NO_FIELDS`

### 5.2 Regras e erros (MVP)
- Se `gamificacao_id` nao pertencer ao evento: `400` com code `GAMIFICACAO_OUT_OF_SCOPE`
- Exclusao bloqueada por dependencias: `409` com code `ATIVACAO_DELETE_BLOCKED` e `dependencies` no detail:
  - `ativacao_leads`
  - `cupons`
  - `respostas_questionario`
  - `investimentos`

---

## 6. Backlog (status)
### Backend
- [ ] Modelo/tabelas de `ativacao`
- [ ] Endpoints CRUD e validacoes

### Frontend
- [ ] Aba/pagina de ativacoes no detalhe do evento
- [ ] Formulario + lista + modal de confirmacao de exclusao
