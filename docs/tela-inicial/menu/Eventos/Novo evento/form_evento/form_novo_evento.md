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
| Nome | texto | `evento.nome` | sim |
| Descricao | textarea | `evento.descricao` | sim (recomendado <= 240) |
| Divisao demandante | texto | `evento.divisao_demandante` | nao (por enquanto) |
| Cidade | texto | `evento.cidade` | sim |
| UF | texto (2 letras) | `evento.estado` | sim |
| Agencia | dropdown | `evento.agencia_id` | sim (para usuarios nao-agencia) |
| Diretoria | dropdown | `evento.diretoria_id` | sim (no front atual) |
| Tipo de evento | dropdown | `evento.tipo_id` | sim |
| Subtipo | dropdown dependente | `evento.subtipo_id` | nao (mas deve pertencer ao tipo) |
| Status | dropdown | `evento.status` | sim |
| Inicio previsto | date | `evento.data_inicio_prevista` | sim |
| Fim previsto | date | `evento.data_fim_prevista` | sim |
| Inicio realizado | date | `evento.data_inicio_realizada` | nao |
| Fim realizado | date | `evento.data_fim_realizada` | nao |
| Tags | multi-select | N:N via `evento_tag` (`tag_ids`) | nao |
| Territorios | multi-select | N:N via `evento_territorio` (`territorio_ids`) | nao |

Campos existentes no modelo que ainda nao estao na tela:
- `thumbnail`, `qr_code_url`
- `publico_projetado`, `publico_realizado`
- `concorrencia`, `gestor_id`

---

## 4. Validacoes e regras

### 4.1 Regras client-side (frontend)
- Obrigatorios: nome, descricao, cidade, UF, diretoria, tipo, datas previstas (inicio/fim)
- UF: exatamente 2 letras (ex.: `SP`)
- Descricao: recomendado <= 240 (limite do banco)
- Datas:
  - `data_fim_prevista >= data_inicio_prevista`
  - se datas realizadas forem preenchidas: `data_fim_realizada >= data_inicio_realizada`
- Subtipo (quando preenchido):
  - deve pertencer ao tipo selecionado

### 4.2 Regras server-side (backend)
- Usuario `tipo_usuario=agencia`:
  - o backend ignora `agencia_id` do payload e usa `current_user.agencia_id`
  - nao permite alterar `agencia_id` via `PUT`
- Subtipo:
  - se `subtipo_id` for informado, deve pertencer ao `tipo_id`
- Tags/territorios:
  - `tag_ids` e `territorio_ids` devem existir no banco (ids invalidos -> 400)

---

## 5. Endpoints usados no formulario

### Criacao
- `POST /evento`

### Dicionarios (dropdowns / multi-select)
- `GET /agencias/` (para dropdown de agencia)
- `GET /evento/all/diretorias`
- `GET /evento/all/tipos-evento`
- `GET /evento/all/subtipos-evento?tipo_id=...`
- `GET /evento/all/tags`
- `GET /evento/all/territorios`

Notas:
- A tela atual usa cidade/UF como texto livre. Existem endpoints auxiliares `GET /evento/all/cidades` e `GET /evento/all/estados`, mas eles refletem valores ja existentes em eventos.
- Nao existe (ainda) um endpoint de "divisoes demandantes"; por isso `divisao_demandante` e texto livre no MVP.

Contrato detalhado: `docs/eventos_api.md`.

---

## 6. Backlog (status)

### Backend
- [x] CRUD de evento: `GET/POST/PUT/DELETE /evento`
- [x] Validacao `subtipo_id` pertence a `tipo_id`
- [x] Relacionamentos N:N via `tag_ids` e `territorio_ids`
- [x] Dicionarios: diretorias, tipos/subtipos, tags, territorios
- [ ] Criacao dinamica de tags (fase 2)
- [ ] Endpoint de divisoes demandantes (a definir)

### Frontend
- [x] Formulario de criacao em `/eventos/novo`
- [x] Validacoes de obrigatorios + datas + subtipo pertence ao tipo
- [x] Multi-select com chips para tags e territorios
- [ ] Tela de edicao (reutilizar formulario com `PUT /evento/{id}`)
- [ ] Auto-save por aba / fluxo com tabs (fase 2)

