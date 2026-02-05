# Mapa do Dominio Eventos

## Escopo
Evento e a entidade central do modulo. Relaciona-se com status/tipo/subtipo, divisao demandante, diretoria/agencia, tags/territorios e subdominios (ativacoes, gamificacoes, questionarios e formulario de leads).

## Arquivos-chave por camada
### Models
- `app/models/models.py`
  - `StatusEvento`, `TipoEvento`, `SubtipoEvento`, `Evento`
  - Join tables: `EventoTag`, `EventoTerritorio`
  - Relacionados: `FormularioLeadConfig`, `QuestionarioPagina/Pergunta/Opcao/Resposta`, `Ativacao`, `Gamificacao`, `CotaCortesia`

### Routers
- `app/routers/eventos.py` (prefixo `/evento`): CRUD, CSV import/export, dicionarios, form-config, questionario, gamificacoes, ativacoes, missing-fields
- `app/routers/ativacao.py` (prefixo `/ativacao`): update/delete ativacao (visibilidade por evento)
- `app/routers/gamificacao.py` (prefixo `/gamificacao`): update/delete gamificacao (visibilidade por evento)
- `app/routers/ingressos.py` (prefixo `/ingressos`): ingressos ativos + solicitacoes (relacionados a evento)
- `app/routers/leads.py` (prefixo `/leads`): referencias de eventos (id/nome) e filtros por evento

### Schemas
- `app/schemas/evento.py` (EventoCreate/Update/Read/ListItem, DataHealthRead)
- `app/schemas/formulario_lead.py`
- `app/schemas/questionario.py`
- `app/schemas/gamificacao.py`
- `app/schemas/ativacao.py`
- `app/schemas/ingressos.py`

### Services / Utils
- `app/services/data_health.py` (compute_event_data_health + config em `docs/eventos_saude_dados_config.json`)
- `app/services/questionario.py` (load/replace estrutura)
- `app/utils/urls.py` (build_evento_public_urls)
- `app/utils/log_sanitize.py` (logs de import)

### Migrations (eventos e relacionados)
- `alembic/versions/289b4605dc23_init.py` (tabelas base: evento/tipo/subtipo/tag/territorio)
- `alembic/versions/39a29b379b54_create_status_evento_table.py`
- `alembic/versions/11df2091aeb2_add_investimento_to_evento.py`
- `alembic/versions/f2a7b9c4d1e0_add_divisao_demandante_table.py`
- `alembic/versions/b7c2d5f9a8e1_gamificacao_belongs_to_evento_and_ativacao_selects.py`
- `alembic/versions/1a2b3c4d5e6f_add_lead_filter_indexes.py` (indexes em evento.estado/cidade)

### Testes
- `tests/test_eventos_endpoints.py`
- `tests/test_eventos_import_logging.py`
- `tests/test_formulario_lead_config_endpoints.py`
- `tests/test_questionario_endpoints.py`
- `tests/test_ativacao_endpoints.py`
- `tests/test_gamificacao_endpoints.py`
- `tests/test_dashboard_leads_*` (filtros por evento)

## Endpoints (resumo)
### Evento (prefixo `/evento`)
- `GET /evento` (lista com filtros + X-Total-Count)
- `GET /evento/{id}`
- `POST /evento`
- `PUT /evento/{id}`
- `DELETE /evento/{id}`
- `GET /evento/export/csv`
- `POST /evento/import/csv`
- `POST /evento/tags`
- `GET /evento/all/*` (cidades, estados, diretorias, divisoes-demandantes, tipos/subtipos, status, tags, territorios, formulario-templates, formulario-campos)
- `GET/PUT /evento/{id}/form-config`
- `GET/PUT /evento/{id}/questionario`
- `GET/POST /evento/{id}/gamificacoes`
- `GET/POST /evento/{id}/ativacoes`
- `GET /evento/{id}/missing-fields`

### Outros relacionados
- `PUT/DELETE /gamificacao/{id}`
- `PUT/DELETE /ativacao/{id}`
- `GET /ingressos/ativos` e `POST /ingressos/solicitacoes`
- `GET /leads/referencias/eventos`

## Integracoes / Fluxos
- Importacao/Exportacao CSV de eventos (`/evento/import/csv`, `/evento/export/csv`)
- URLs publicas de landing/checkin/questionario geradas por `build_evento_public_urls`
