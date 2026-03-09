# EPIC-F2-01 — Migration AtivacaoLead — Campos de Gamificação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Adicionar ao modelo `AtivacaoLead` os campos `gamificacao_id` (FK para `gamificacao.id`),
`gamificacao_completed` (boolean, default FALSE) e `gamificacao_completed_at` (timestamp
nullable), criar a migration Alembic correspondente e atualizar schemas Pydantic de
leitura.

**Resultado de Negócio Mensurável:** O sistema registra qual gamificação cada lead
completou, permitindo consultas como "quantos leads completaram a gamificação X na
ativação Y".

## 2. Contexto Arquitetural
- Modelo `AtivacaoLead` em `backend/app/models/models.py` (SQLModel, table=True)
- FK para `Gamificacao.id` — modelo já existente no sistema
- Migrations Alembic em `backend/alembic/versions/`
- Schemas em `backend/app/schemas/`
- PYTHONPATH: `/workspace:/workspace/backend`
- Tabela pode ter volume considerável — campos nullable evitam `ALTER TABLE ... NOT NULL` com lock

## 3. Riscos e Armadilhas
- FK `gamificacao_id` deve ser nullable — nem todo lead participa de gamificação
- `gamificacao_completed` default FALSE (não NULL) para facilitar queries sem coalesce
- Migration deve ser testada com dados existentes para garantir que registros antigos ficam intactos
- Se modelo `Gamificacao` não existir ainda, a FK deve apontar para a tabela correta

## 4. Definition of Done do Épico
- [ ] Modelo `AtivacaoLead` possui campo `gamificacao_id: Optional[int] = Field(default=None, foreign_key="gamificacao.id")`
- [ ] Modelo `AtivacaoLead` possui campo `gamificacao_completed: Optional[bool] = Field(default=False)`
- [ ] Modelo `AtivacaoLead` possui campo `gamificacao_completed_at: Optional[datetime] = Field(default=None)`
- [ ] Migration Alembic criada e aplicável em banco limpo e com dados existentes
- [ ] Rollback remove os 3 campos sem efeito colateral
- [ ] Schemas de leitura de `AtivacaoLead` atualizados com os novos campos
- [ ] Registros existentes preservados com valores default

---
## Issues

### AFLPD-F2-01-001 — Adicionar campos de gamificação ao modelo AtivacaoLead
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Estender o SQLModel `AtivacaoLead` com três campos: `gamificacao_id` (FK nullable
para `gamificacao.id`), `gamificacao_completed` (boolean, default FALSE) e
`gamificacao_completed_at` (timestamp nullable). Atualizar o relationship se
necessário.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_models.py` que cria um `AtivacaoLead` com `gamificacao_id=5` e verifica persistência e leitura.
- **Green:** Adicionar os 3 campos ao modelo com tipos, defaults e FK corretos.
- **Refactor:** Verificar se relationship bidirecional `Gamificacao.ativacao_leads` é necessário; adicionar se sim.

**Critérios de Aceitação:**
- Given modelo `AtivacaoLead`, When inspecionado, Then possui campo `gamificacao_id: Optional[int]` com FK para `gamificacao.id`
- Given criação de `AtivacaoLead` sem gamificação, When salvo, Then `gamificacao_completed = False` e `gamificacao_completed_at = None`
- Given `AtivacaoLead` existente sem os novos campos, When migration aplicada, Then registros mantidos com defaults

**Tarefas:**
- [ ] T1: Adicionar `gamificacao_id: Optional[int] = Field(default=None, foreign_key="gamificacao.id")` ao modelo
- [ ] T2: Adicionar `gamificacao_completed: Optional[bool] = Field(default=False)`
- [ ] T3: Adicionar `gamificacao_completed_at: Optional[datetime] = Field(default=None)`
- [ ] T4: Verificar imports necessários (datetime, Optional, Field)
- [ ] T5: Executar testes existentes para garantir retrocompatibilidade

**Notas técnicas:**
O campo `gamificacao_completed` usa `Optional[bool]` com default `False` para que
queries de contagem de participação não precisem de `COALESCE`. O `gamificacao_completed_at`
é populado pelo backend no momento da chamada ao endpoint de conclusão.

---
### AFLPD-F2-01-002 — Criar migration Alembic e atualizar schemas
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F2-01-001

**Descrição:**
Gerar migration Alembic para os 3 novos campos de `AtivacaoLead`, testar upgrade e
downgrade, e atualizar schemas Pydantic de leitura para expor os campos na API.

**Plano TDD:**
- **Red:** Escrever teste que aplica migration em banco de teste e verifica existência das 3 colunas via introspection SQL.
- **Green:** Gerar migration com `alembic revision --autogenerate`, revisar e testar upgrade/downgrade.
- **Refactor:** Consolidar schemas se houver duplicação entre create/read de `AtivacaoLead`.

**Critérios de Aceitação:**
- Given banco limpo, When `alembic upgrade head` executado, Then colunas `gamificacao_id`, `gamificacao_completed`, `gamificacao_completed_at` existem na tabela `ativacao_lead`
- Given banco com dados, When `alembic upgrade head` executado, Then registros existentes mantidos com `gamificacao_id=NULL`, `gamificacao_completed=FALSE`, `gamificacao_completed_at=NULL`
- Given migration aplicada, When `alembic downgrade -1` executado, Then colunas removidas sem erro
- Given endpoint que retorna `AtivacaoLead`, When chamado, Then response inclui os 3 novos campos

**Tarefas:**
- [ ] T1: Gerar migration com `alembic revision --autogenerate -m "add_gamificacao_fields_to_ativacao_lead"`
- [ ] T2: Revisar migration — verificar FK constraint, defaults e nullability
- [ ] T3: Testar upgrade em banco limpo
- [ ] T4: Testar upgrade em banco com registros existentes
- [ ] T5: Testar downgrade
- [ ] T6: Atualizar schemas de leitura de `AtivacaoLead` em `backend/app/schemas/`

**Notas técnicas:**
A migration deve criar a FK com `ON DELETE SET NULL` para que a deleção de uma
gamificação não cascade para os leads. Verificar que o índice na FK é criado
automaticamente pelo Alembic ou adicioná-lo manualmente.

## 5. Notas de Implementação Globais
- Os 3 campos formam um grupo semântico — sempre testados e documentados juntos
- `gamificacao_completed_at` é preenchido exclusivamente pelo backend (nunca pelo frontend)
- FK com `ON DELETE SET NULL` — deleção de gamificação não apaga dados de leads
- Manter retrocompatibilidade total: nenhum endpoint existente deve quebrar
