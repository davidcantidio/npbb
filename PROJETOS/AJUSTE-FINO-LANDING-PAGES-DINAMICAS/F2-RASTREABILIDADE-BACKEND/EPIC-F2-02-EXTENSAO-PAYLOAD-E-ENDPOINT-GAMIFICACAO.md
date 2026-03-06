# EPIC-F2-02 — Extensão Payload Landing e Endpoint Gamificação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Estender o payload de `GET /ativacoes/{id}/landing` com os objetos `ativacao` e
`gamificacoes`, garantir que `POST /leads/` retorne `ativacao_lead_id` na response,
e criar o endpoint `POST /ativacao-leads/{ativacao_lead_id}/gamificacao` para
persistência da conclusão de gamificação.

**Resultado de Negócio Mensurável:** O frontend recebe todos os dados necessários
para renderizar conteúdo da ativação e gamificação, e a conclusão de gamificação é
persistida de forma rastreável em `AtivacaoLead`.

## 2. Contexto Arquitetural
- Router de ativações: `backend/app/routers/ativacoes.py` (ou equivalente)
- Router de leads: `backend/app/routers/leads.py` (ou equivalente)
- Schemas: `backend/app/schemas/`
- Use cases: `backend/app/modules/`
- Payload atual do landing já retorna `evento`, `template`, `formulario`, `marca`, `acesso`
- Novo: adicionar `ativacao` (objeto) e `gamificacoes` (array)
- Endpoint de gamificação é público — autenticação por opacidade do `ativacao_lead_id`

## 3. Riscos e Armadilhas
- O payload de landing é cacheável — garantir que `gamificacoes` esteja no cache key ou invalidar cache
- `ativacao_lead_id` deve ser retornado no submit mesmo quando não há gamificação — o frontend precisa dele
- Endpoint de gamificação público deve validar que `ativacao_lead_id` existe antes de atualizar
- `gamificacoes` deve ser sempre array, mesmo quando FK aponta para 1 gamificação — antecipa suporte futuro a múltiplas

## 4. Definition of Done do Épico
- [ ] `GET /ativacoes/{id}/landing` retorna campo `ativacao` com `id`, `nome`, `descricao`, `mensagem_qrcode`
- [ ] `GET /ativacoes/{id}/landing` retorna campo `gamificacoes` como array de objetos com `id`, `nome`, `descricao`, `premio`, `titulo_feedback`, `texto_feedback`
- [ ] `gamificacoes` retorna `[]` quando ativação não tem gamificação vinculada
- [ ] `POST /leads/` retorna `ativacao_lead_id` na response
- [ ] `POST /ativacao-leads/{id}/gamificacao` persiste `gamificacao_id`, `gamificacao_completed=true` e `gamificacao_completed_at=now()`
- [ ] Endpoint de gamificação retorna 404 quando `ativacao_lead_id` não existe
- [ ] Endpoint de gamificação retorna 400 quando `gamificacao_id` inválido
- [ ] Nenhum campo removido do payload existente
- [ ] Schemas Pydantic criados/atualizados e documentação OpenAPI refletindo as mudanças
- [ ] Testes de contrato cobrindo cenários com e sem gamificação

---
## Issues

### AFLPD-F2-02-001 — Estender payload de landing com ativação e gamificações
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Estender o endpoint `GET /ativacoes/{id}/landing` para incluir os objetos `ativacao`
(com `id`, `nome`, `descricao`, `mensagem_qrcode`) e `gamificacoes` (array de
gamificações vinculadas à ativação). Criar schemas Pydantic correspondentes.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_ativacoes_endpoints.py` que chama `GET /ativacoes/{id}/landing` e asserta presença dos campos `ativacao` e `gamificacoes` na response.
- **Green:** Adicionar query de ativação e gamificações ao handler, criar schemas `LandingAtivacaoSchema` e `GamificacaoPublicSchema`, incluir no payload.
- **Refactor:** Extrair lógica de montagem do payload estendido para use case separado se o handler ficar complexo.

**Critérios de Aceitação:**
- Given ativação com gamificação vinculada, When `GET /ativacoes/{id}/landing` chamado, Then response contém `ativacao.nome`, `ativacao.descricao` e `gamificacoes` com 1 item
- Given ativação sem gamificação, When `GET /ativacoes/{id}/landing` chamado, Then response contém `gamificacoes: []`
- Given ativação com `mensagem_qrcode`, When endpoint chamado, Then `ativacao.mensagem_qrcode` presente na response
- Given payload existente, When endpoint chamado, Then campos `evento`, `template`, `formulario`, `marca`, `acesso` continuam presentes e inalterados

**Tarefas:**
- [ ] T1: Criar schema `LandingAtivacaoSchema` com campos `id`, `nome`, `descricao`, `mensagem_qrcode`
- [ ] T2: Criar schema `GamificacaoPublicSchema` com campos `id`, `nome`, `descricao`, `premio`, `titulo_feedback`, `texto_feedback`
- [ ] T3: Atualizar schema de response do landing para incluir `ativacao` e `gamificacoes`
- [ ] T4: Atualizar handler para carregar dados de ativação e gamificações
- [ ] T5: Garantir que `gamificacoes` é sempre array (nunca null)
- [ ] T6: Testar com ativação que tem gamificação e sem gamificação

**Notas técnicas:**
O payload atual pode usar `joinedload` ou query separada para carregar gamificações.
O modelo 1:1 (`Ativacao.gamificacao_id`) implica no máximo 1 gamificação, mas o
payload retorna array para antecipar o modelo futuro N:N sem breaking change.

---
### AFLPD-F2-02-002 — Retornar ativacao_lead_id no submit e criar endpoint de gamificação
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F2-02-001

**Descrição:**
Garantir que `POST /leads/` retorne `ativacao_lead_id` na response do submit.
Criar o endpoint `POST /ativacao-leads/{ativacao_lead_id}/gamificacao` que recebe
`gamificacao_id` e `gamificacao_completed`, persiste os campos em `AtivacaoLead` e
preenche `gamificacao_completed_at` com timestamp atual.

**Plano TDD:**
- **Red:** Escrever teste que submete lead via `POST /leads/` e asserta que response contém `ativacao_lead_id`. Escrever teste que chama `POST /ativacao-leads/{id}/gamificacao` e asserta persistência dos campos.
- **Green:** Atualizar schema de response do submit para incluir `ativacao_lead_id`. Criar handler, schema e rota para endpoint de gamificação.
- **Refactor:** Extrair lógica de atualização de gamificação para use case se o handler ultrapassar 20 linhas.

**Critérios de Aceitação:**
- Given submit de lead bem-sucedido, When response recebida, Then campo `ativacao_lead_id` está presente e é um inteiro válido
- Given `ativacao_lead_id` válido, When `POST /ativacao-leads/{id}/gamificacao` com `gamificacao_id=5` e `gamificacao_completed=true`, Then `AtivacaoLead` atualizado com `gamificacao_id=5`, `gamificacao_completed=true`, `gamificacao_completed_at` com timestamp
- Given `ativacao_lead_id` inexistente, When endpoint chamado, Then resposta 404
- Given `gamificacao_id` que não existe no banco, When endpoint chamado, Then resposta 400 com mensagem descritiva
- Given gamificação já concluída para aquele lead, When endpoint chamado novamente, Then atualização idempotente (não cria duplicata)

**Tarefas:**
- [ ] T1: Atualizar schema de response do `POST /leads/` para incluir `ativacao_lead_id: int`
- [ ] T2: Garantir que o handler de submit retorna o `ativacao_lead_id` do registro criado
- [ ] T3: Criar schema `GamificacaoCompleteRequest` com `gamificacao_id: int` e `gamificacao_completed: bool`
- [ ] T4: Criar schema `GamificacaoCompleteResponse` com `ativacao_lead_id`, `gamificacao_id`, `gamificacao_completed`, `gamificacao_completed_at`
- [ ] T5: Criar rota `POST /ativacao-leads/{ativacao_lead_id}/gamificacao` no router
- [ ] T6: Implementar handler: buscar `AtivacaoLead` por ID, validar existência de `gamificacao_id`, atualizar campos, preencher `gamificacao_completed_at = datetime.utcnow()`
- [ ] T7: Testar cenários: sucesso, 404, 400, idempotência

**Notas técnicas:**
O endpoint é público (sem JWT) — segurança por opacidade do `ativacao_lead_id` que
só é retornado ao frontend após submit bem-sucedido. Considerar rate limiting futuro
mas não implementar nesta fase. `gamificacao_completed_at` é sempre preenchido pelo
backend para garantir consistência temporal.

## 5. Notas de Implementação Globais
- Schemas novos devem ser criados em arquivo separado (ex: `backend/app/schemas/gamificacao_landing.py`) para não poluir schemas existentes
- O endpoint de gamificação deve ser idempotente — chamadas repetidas atualizam o mesmo registro
- `gamificacao_completed_at` nunca vem do frontend — sempre `datetime.utcnow()` no handler
- Testar retrocompatibilidade: payloads antigos (sem `ativacao` e `gamificacoes`) devem funcionar com fallback no frontend
