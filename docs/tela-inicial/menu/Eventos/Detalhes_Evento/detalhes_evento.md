# Pagina de Detalhes do Evento

## 1. Nome da Tela
**Detalhes do Evento**

Tela que centraliza todas as informacoes de um evento e, no sistema original, agrega abas de modulos relacionados (Formulario de Lead, Gamificacao, Ativacoes, Questionario, etc).

Status no novo sistema (MVP):
- Frontend: existe a rota `/eventos/:id`, mas no MVP ela exibe apenas um JSON simples do evento (placeholder), sem abas.
- Backend: CRUD de evento esta implementado em `/evento` (ver `docs/eventos_api.md`).

---

## 2. Referencia Visual
- Sistema original: prints na pasta `docs/tela-inicial/menu/Eventos/Detalhes_Evento/` (quando disponiveis).
- Novo sistema (MVP): ainda nao replica a UI original com tabs.

---

## 3. Conteudo (MVP)
No MVP, a pagina de detalhe mostra os dados basicos do evento (como JSON ou card simples), incluindo:
- Identificacao: `id`, `nome`
- Local: `cidade`, `estado`
- Organizacao: `diretoria_id`, `agencia_id`
- Status e datas (previstas/realizadas)
- Relacionamentos N:N: `tag_ids`, `territorio_ids`

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
- Aba **Formulario de Lead**: configuracao de landing/campos/URLs (ver `docs/tela-inicial/menu/Eventos/Novo evento/form_formulario_leads/form_formulario_leads.md`).
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
- [x] Rota `/eventos/:id` (placeholder)
- [ ] UI completa de detalhe com tabs e edicao
