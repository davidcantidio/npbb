# Formulario de Evento (Criacao / Edicao)

## 1. Nome da Tela
**Formulario de Evento**

Tela usada para criar (e futuramente editar) um evento.

Status no novo sistema:
- Criacao: implementada em `/eventos/novo`
- Edicao: ainda nao implementada no front (endpoints `PUT /evento/{id}` ja existem)

---

## 2. Referencia Visual (sistema original)
`docs/tela-inicial/menu/Eventos/Novo evento/form_evento/form_novo_evento.png`

---

## 3. Campos do formulario (aba Evento)

Campos implementados no MVP (tela `/eventos/novo`):

| Campo | Tipo | Mapeamento | Obrigatorio |
|---|---|---|---|
| Agencia | dropdown | `evento.agencia_id` | sim (para usuarios nao-agencia) |
| Nome | texto | `evento.nome` | sim |
| Descricao | textarea | `evento.descricao` | sim (recomendado <= 240) |
| UF | dropdown (UF do Brasil) | `evento.estado` | sim |
| Cidade | autocomplete (cidades por UF) | `evento.cidade` | sim |
| Data de inicio | date | `evento.data_inicio_prevista` | sim |
| Data de fim | date | `evento.data_fim_prevista` | sim |
| Investimento | moeda (decimal) | `evento.investimento` | nao |
| Diretoria | dropdown | `evento.diretoria_id` | sim (no front atual) |
| Divisao demandante | dropdown (Divisoes demandantes) | `evento.divisao_demandante_id` | nao |
| Tipo de evento | dropdown | `evento.tipo_id` | sim |
| Subtipo | dropdown dependente | `evento.subtipo_id` | nao (mas deve pertencer ao tipo) |
| Territorios | multi-select | N:N via `evento_territorio` (`territorio_ids`) | nao |
| Tags | multi-select + texto livre | N:N via `evento_tag` (`tag_ids`) | nao |

Campos existentes no modelo que ainda nao estao na tela:
- `thumbnail`, `qr_code_url`
- `publico_projetado`, `publico_realizado`
- `concorrencia`, `gestor_id`
- `status_id` (o front nao seleciona no formulario; backend infere quando omitido)

---

## 4. Validacoes e regras

### 4.1 Regras client-side (frontend)
- Obrigatorios: nome, descricao, UF, cidade, diretoria, tipo, datas previstas (inicio/fim)
- UF: selecionada a partir das 27 UFs do Brasil
- Descricao: recomendado <= 240 (limite do banco)
- Datas:
  - `data_fim_prevista >= data_inicio_prevista`
- Subtipo (quando preenchido):
  - deve pertencer ao tipo selecionado
- Investimento (quando preenchido):
  - deve ser um numero >= 0

### 4.2 Regras server-side (backend)
- Usuario `tipo_usuario=agencia`:
  - o backend ignora `agencia_id` do payload e usa `current_user.agencia_id`
  - nao permite alterar `agencia_id` via `PUT`
- Subtipo:
  - se `subtipo_id` for informado, deve pertencer ao `tipo_id`
- Tags/territorios:
  - `tag_ids` e `territorio_ids` devem existir no banco (ids invalidos -> 400)
- Status (quando `status_id` nao e enviado):
  - se `data_inicio_prevista` > hoje -> `Previsto`
  - se `data_fim_prevista` < hoje -> `Realizado`
  - caso contrario -> `Confirmado`
  - se nao houver datas -> `A Confirmar`

---

## 5. Endpoints usados no formulario

### Criacao
- `POST /evento`

### Dicionarios (dropdowns / multi-select)
- `GET /agencias/` (para dropdown de agencia)
- `GET /evento/all/divisoes-demandantes`
- `GET /evento/all/diretorias`
- `GET /evento/all/tipos-evento`
- `GET /evento/all/subtipos-evento?tipo_id=...`
- `GET /evento/all/tags`
- `POST /evento/tags` (cria tags digitadas no autocomplete)
- `GET /evento/all/territorios`
- Dados locais: `frontend/src/data/estados-cidades.json` (lista de cidades por UF)

Notas:
- A tela usa UF via lista fixa (UFs do Brasil) e carrega a lista de cidades localmente, sem chamada a API (melhora performance e permite listar todas as cidades).
- `divisao_demandante` e um dominio proprio (tabela `divisao_demandante`) e o evento referencia por FK (`divisao_demandante_id`).

Contrato detalhado: `docs/eventos_api.md`.

---

## 6. Backlog (status)

### Backend
- [x] CRUD de evento: `GET/POST/PUT/DELETE /evento`
- [x] Validacao `subtipo_id` pertence a `tipo_id`
- [x] Relacionamentos N:N via `tag_ids` e `territorio_ids`
- [x] Dicionarios: divisoes demandantes, diretorias, tipos/subtipos, tags, territorios
- [x] Criacao dinamica de tags (autocomplete com texto livre + `POST /evento/tags`)
- [ ] Gestao de divisoes demandantes via admin (fase 2, se necessario)

### Frontend
- [x] Formulario de criacao em `/eventos/novo`
- [x] Validacoes de obrigatorios + datas + subtipo pertence ao tipo
- [x] Multi-select com chips para tags e territorios
- [ ] Tela de edicao (reutilizar formulario com `PUT /evento/{id}`)
- [ ] Auto-save por aba / fluxo com tabs (fase 2)
