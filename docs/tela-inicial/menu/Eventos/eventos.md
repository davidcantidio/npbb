# Pagina de Eventos (Listagem)

## 1. Nome da Tela
**Listagem de Eventos**

Tela principal que exibe todos os eventos cadastrados, com acoes rapidas de visualizar e excluir, alem de filtros e paginacao.

Status no novo sistema:
- Frontend: implementado em `/eventos`
- Backend: endpoints em `/evento` (ver `docs/eventos_api.md`)
Detalhe do evento: `docs/tela-inicial/menu/Eventos/Detalhes_Evento/detalhes_evento.md`.

---

## 2. Referencia Visual
Print do sistema original:
`docs/tela-inicial/menu/Eventos/eventos.png`

---

## 3. Estrutura da Tela

### 3.1 Cabecalho da pagina
- Menu principal no cabecalho (Dashboard, Eventos, Ativos, Leads, Cupons).
- Titulo: **Eventos**
- Botao **+ Novo** (navega para `/eventos/novo`)
- Botao **Atualizar**

### 3.2 Painel lateral de filtros
Os filtros ficam no painel lateral, refletindo o conteudo da listagem principal.
Filtros disponiveis (com botao **Aplicar** e **Limpar filtros**):
- Evento (texto -> `search`)
- Estado (UF -> `estado`)
- Local (cidade -> `cidade`)
- Diretoria (dropdown -> `diretoria_id`)
- Data (date -> `data`)

### 3.3 Tabela de Eventos
Colunas exibidas no front atual:
1. **ID**
2. **QRCode** (icone que abre `qr_code_url` em nova aba quando existir)
3. **Nome do Evento** (link para `/eventos/:id`)
4. **Periodo** (datas previstas)
5. **Cidade / UF**
6. **Diretoria**
7. **Status** (dropdown com cores)
8. **Acoes** (ver / editar / excluir)

### 3.4 Paginacao
- Paginacao numerica (1..N)
- Seletor de itens por pagina: 10/25/50/100

---

## 4. Comportamento da Tela

| Acao | Comportamento |
|---|---|
| **+ Novo** | Abre formulario de criacao do evento (`/eventos/novo`) |
| **Visualizar** | Abre detalhe do evento (`/eventos/:id`) (no MVP: placeholder) |
| **Excluir** | Modal de confirmacao; chama `DELETE /evento/{id}` e exibe erro caso o backend bloqueie (409) |
| **Editar** | Navega para `/eventos/:id/editar` (reutiliza o formulario e chama `PUT /evento/{id}`) |
| **Status** | Dropdown na coluna **Status**; ao alterar, chama `PUT /evento/{id}` com `status_id` |
| **Atualizar** | Recarrega os dados da listagem |
| **Aplicar** | Aplica filtros e volta para pagina 1 |
| **Limpar filtros** | Remove filtros e volta para pagina 1 |

---

## 5. Regras de Negocio
- Ordenacao: mais recente primeiro (backend ordena por `Evento.id desc`).
- Exclusao bloqueada quando existir vinculo (o backend retorna `409 EVENTO_DELETE_BLOCKED` com `dependencies`).
- Visibilidade: usuario `tipo_usuario=agencia` ve apenas eventos da propria `agencia_id`.
- Status: exibido como chip com cores (Previsto=neutro, A Confirmar=warning, Confirmado=info, Realizado=success, Cancelado=error).

---

## 6. Chamadas de API (novo sistema)

### Listagem
- `GET /evento?skip=0&limit=25&search=...&estado=...&cidade=...&data=YYYY-MM-DD&diretoria_id=...`
  - Header: `X-Total-Count` (total com filtros aplicados)

### Dicionarios (para filtros)
- `GET /evento/all/cidades`
- `GET /evento/all/estados`
- `GET /evento/all/diretorias`
- `GET /evento/all/status-evento`

### Exportacao
- `GET /evento/export/csv` (download da listagem filtrada)

### Acoes por linha
- `GET /evento/{id}` (detalhe)
- `PUT /evento/{id}` (atualizacao, incluindo `status_id`)
- `DELETE /evento/{id}` (exclusao)

Contrato completo dos endpoints: `docs/eventos_api.md`.

---

## 7. Backlog (status)

### Backend
- [x] `GET /evento` (paginado + filtros `search/estado/cidade/data/diretoria_id` + `X-Total-Count`)
- [x] `GET /evento/{id}`
- [x] `POST /evento`
- [x] `PUT /evento/{id}`
- [x] `DELETE /evento/{id}` com validacao de dependencias (409 com `dependencies`)
- [x] Dicionarios: `GET /evento/all/cidades`, `GET /evento/all/estados`, `GET /evento/all/diretorias`
- [x] Exportacao CSV (`GET /evento/export/csv`)

### Frontend
- [x] Pagina `/eventos` com filtros e paginacao
- [x] Componente de linha (`EventoRow`) com QRCode e acoes
- [x] Botao **+ Novo** -> `/eventos/novo`
- [x] Exclusao com modal e feedback de erro
- [x] Coluna Diretoria na grid e filtro por Diretoria
- [x] Editar evento (tela `/eventos/:id/editar` + integracao `PUT /evento/{id}`)
- [x] Exportacao CSV (botao na listagem + download)
