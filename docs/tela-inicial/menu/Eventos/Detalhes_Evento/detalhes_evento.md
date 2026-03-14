# Pagina de Detalhes do Evento

## 1. Nome da Tela
**Detalhes do Evento**

Tela que centraliza todas as informacoes de um evento e, no sistema original, agrega abas de modulos relacionados (Landing Page, Gamificacao, Ativacoes, Questionario, etc).

Status no novo sistema (MVP):
- Frontend: implementado em `/eventos/:id`, com exibicao estruturada dos dados (inclui datas previstas/realizadas, QRCode, diretoria e dominios relacionados).
- Backend: CRUD de evento esta implementado em `/evento` (ver `docs/eventos_api.md`).

---

## 2. Referencia Visual
- Sistema original: prints na pasta `docs/tela-inicial/menu/Eventos/Detalhes_Evento/` (quando disponiveis).
- Novo sistema (MVP): ainda nao replica a UI original com tabs.

---

## 3. Conteudo (MVP)
No MVP, a pagina de detalhe mostra os dados basicos do evento, incluindo:
- Identificacao: `id`, `nome`
- Local: `cidade`, `estado`
- Organizacao: `agencia_id`, `diretoria_id`, `divisao_demandante_id`
- Status: `status_id` (FK para `status_evento`) + datas previstas
- Relacionamentos N:N: `tag_ids`, `territorio_ids`

Acoes disponiveis:
- **Editar**: navega para `/eventos/:id/editar` (reutiliza o formulario e chama `PUT /evento/{id}`).
- **Excluir**: confirma e chama `DELETE /evento/{id}` (pode retornar 409 se houver dependencias).

---

## 4. Chamadas de API (novo sistema)
- `GET /evento/{id}`: carrega os dados do evento.
  - `404`: evento nao encontrado (ou fora do escopo para usuario `tipo_usuario=agencia`).
- `PUT /evento/{id}`: atualiza o evento (UI de edicao ainda nao existe no front).
- `DELETE /evento/{id}`: exclui o evento (pode retornar 409 se houver dependencias).

Contrato detalhado: `docs/eventos_api.md`.

---

## 5. Escopo futuro (fase 2)
O objetivo e evoluir a pagina `/eventos/:id` para uma tela com abas, alinhada ao sistema original:
- Aba **Evento**: visualizar/editar dados do evento (reutilizar o formulario de `docs/tela-inicial/menu/Eventos/Novo evento/form_evento/form_novo_evento.md`).
- Aba **Landing Page**: configuracao de landing/campos/URLs (ver `docs/tela-inicial/menu/Eventos/Novo evento/form_formulario_leads/form_formulario_leads.md`).
- Aba **Gamificacao**: cadastro/lista de gamificacoes (ver `docs/tela-inicial/menu/Eventos/Novo evento/form_gamificacao/form_gamificacao.md`).
- Aba **Ativacoes**: CRUD de ativacoes e regras (ver `docs/tela-inicial/menu/Eventos/Novo evento/form_ativacao/form_ativacao.md`).
- Aba **Questionario**: editor de paginas/perguntas/opcoes (ver `docs/tela-inicial/menu/Eventos/Novo evento/form_questionario/form_questionario.md`).

Observacao: endpoints por aba ainda nao estao implementados (apenas o CRUD basico de `evento`).

---

## 6. Backlog (status)
### Backend
- [x] `GET /evento/{id}`
- [x] `PUT /evento/{id}`
- [x] `DELETE /evento/{id}` com bloqueio por dependencias (409)
- [ ] Endpoints por aba (lead form, gamificacao, ativacoes, questionario, etc)

### Frontend
- [x] Rota `/eventos/:id` (detalhe do evento)
- [x] Editar evento (rota `/eventos/:id/editar` + integracao `PUT /evento/{id}`)
- [ ] UI completa de detalhe com tabs e edicao por aba (fase 2)
