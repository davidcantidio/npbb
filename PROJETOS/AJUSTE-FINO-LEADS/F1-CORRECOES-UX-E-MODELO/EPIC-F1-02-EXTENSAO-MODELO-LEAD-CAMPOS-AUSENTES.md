---
doc_id: "EPIC-F1-02-EXTENSAO-MODELO-LEAD-CAMPOS-AUSENTES"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F1-02 — Extensão do Modelo Lead — Campos Ausentes
**projeto:** AJUSTE-FINO-LEADS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico

Restaurar ao modelo de dados `Lead` os 8 campos identificados como ausentes no PRD (seção 3.3): `sobrenome`, `rg`, `genero`, `logradouro`, `numero`, `complemento`, `bairro` e `cep`. Criar a migration Alembic, atualizar schemas de resposta no backend e estender o tipo `LeadListItem` no frontend, mantendo retrocompatibilidade total com importações e endpoints existentes.

## 2. Contexto Arquitetural

- Modelo `Lead` em `backend/app/models/models.py` (SQLModel, table=True)
- Migrations Alembic em `backend/alembic/versions/`
- Schemas Pydantic em `backend/app/schemas/`
- Tipo `LeadListItem` em `frontend/src/services/leads_import.ts`
- Campos `cidade` e `estado` já existem — foco nos 8 campos completamente ausentes
- Todos os novos campos são `Optional[str]` com default `None` (nullable)
- CSV de importação existente (`leads-import-smoke.csv`) usa `nome,email,cpf,evento_nome` — novos campos são opcionais

## 3. Riscos e Armadilhas

- **Risco médio-alto:** Necessidade de auditar se colunas já existem no banco mas estão ausentes apenas da serialização, ou se precisam ser criadas via migration
- Migration em tabela com muitos registros pode ser lenta — campos nullable mitigam lock
- Schemas de leitura que fazem `model_validate` podem falhar se não atualizados simultaneamente
- O campo `nome` pode armazenar nome completo — `sobrenome` pode redundar; manter ambos para flexibilidade
- Importação de CSV sem os novos campos deve continuar funcionando (NULL por padrão)

## 4. Definition of Done do Épico

- [ ] Modelo `Lead` possui os 8 campos: `sobrenome`, `rg`, `genero`, `logradouro`, `numero`, `complemento`, `bairro`, `cep` (todos `Optional[str]`, default=None)
- [ ] Migration Alembic criada e aplicável em banco limpo e com dados existentes
- [ ] Rollback da migration remove as colunas sem efeito colateral
- [ ] Schemas de leitura do Lead atualizados para incluir os novos campos
- [ ] Tipo `LeadListItem` no frontend atualizado com os 8 campos
- [ ] Importação de CSV existente não quebra (retrocompatibilidade confirmada por teste)
- [ ] Testes de criação/leitura de lead com e sem os novos campos passam
- [ ] CI verde sem regressão

---
## Issues

### AFL-F1-02-001 — Adição de Colunas ao Modelo Lead e Migration Alembic
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**User Story:**
Como engenheiro de backend, quero que o modelo `Lead` tenha todos os campos de dados pessoais e endereço disponíveis, para que o sistema possa armazenar informações completas dos leads sem perda de dados na importação.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_lead_model.py` que cria um `Lead` com os novos campos (`sobrenome="Silva"`, `rg="12345"`, `genero="M"`, `logradouro="Rua A"`, `numero="100"`, `complemento="Sala 1"`, `bairro="Centro"`, `cep="01001000"`) e verifica que os valores são persistidos e recuperáveis. O teste falha porque os campos não existem no modelo.
- **Green:** Adicionar os 8 campos ao modelo `Lead` em `backend/app/models/models.py` como `Optional[str] = Field(default=None)`. Gerar migration Alembic com `alembic revision --autogenerate`.
- **Refactor:** Agrupar os campos de endereço com comentário semântico no modelo para facilitar manutenção futura.

**Critérios de Aceitação:**

- **Given** o modelo `Lead` atualizado com os 8 novos campos
  **When** `alembic upgrade head` é executado em banco com leads existentes
  **Then** a migration aplica sem erro e leads existentes têm os novos campos como `NULL`

- **Given** um lead é criado com todos os novos campos preenchidos
  **When** o lead é recuperado do banco
  **Then** todos os 8 campos retornam os valores salvos corretamente

- **Given** a migration foi aplicada
  **When** `alembic downgrade -1` é executado
  **Then** as 8 colunas são removidas sem efeito colateral nos dados restantes

**Tarefas:**
- [ ] T1: Auditar tabela `lead` no banco para verificar se colunas já existem mas não estão no modelo
- [ ] T2: Adicionar os 8 campos ao modelo `Lead` em `backend/app/models/models.py`
- [ ] T3: Gerar migration: `alembic revision --autogenerate -m "add_campos_ausentes_lead"`
- [ ] T4: Revisar migration gerada — verificar que apenas os campos esperados aparecem
- [ ] T5: Testar `alembic upgrade head` em banco limpo e com dados existentes
- [ ] T6: Testar `alembic downgrade -1`
- [ ] T7: Escrever pytest de criação e leitura de lead com novos campos

**Notas técnicas:**
Campos seguem o padrão de nullable já usado no modelo. Para `genero`, usar `Optional[str]` (valores livres como `"M"`, `"F"`, `"Outro"`) sem enum no banco — validação por schema se necessário.

---

### AFL-F1-02-002 — Atualização de Schemas de Resposta e Tipo Frontend
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** AFL-F1-02-001

**User Story:**
Como consumidor da API de leads, quero que os endpoints de listagem e detalhamento retornem os campos restaurados (`sobrenome`, `rg`, `genero`, endereço), para que o frontend e futuros consumidores tenham acesso completo às informações cadastrais.

**Plano TDD:**
- **Red:** Escrever teste em `backend/tests/test_leads_api.py` que cria um lead com `sobrenome="Silva"` e chama `GET /leads` verificando que o campo aparece na resposta JSON. Escrever teste frontend que valida que `LeadListItem` aceita os novos campos.
- **Green:** Atualizar schemas Pydantic de leitura do Lead em `backend/app/schemas/` para incluir os 8 campos como `Optional[str]`. Atualizar tipo `LeadListItem` em `frontend/src/services/leads_import.ts`.
- **Refactor:** Verificar se há schemas duplicados de Lead e consolidar se necessário.

**Critérios de Aceitação:**

- **Given** um lead com `sobrenome`, `rg`, `genero` e campos de endereço preenchidos
  **When** `GET /leads` é chamado
  **Then** a resposta JSON contém todos os 8 novos campos com seus valores

- **Given** um lead antigo sem os novos campos (todos `NULL`)
  **When** `GET /leads` é chamado
  **Then** a resposta JSON contém os 8 campos como `null` sem erro de serialização

- **Given** o tipo `LeadListItem` atualizado no frontend
  **When** a listagem de leads é renderizada
  **Then** nenhum erro de TypeScript é gerado e campos estão acessíveis

**Tarefas:**
- [ ] T1: Localizar todos os schemas de leitura do Lead em `backend/app/schemas/`
- [ ] T2: Adicionar os 8 campos opcionais aos schemas relevantes
- [ ] T3: Atualizar tipo `LeadListItem` em `frontend/src/services/leads_import.ts`
- [ ] T4: Executar testes existentes de endpoints que retornam leads
- [ ] T5: Verificar que a documentação OpenAPI reflete os novos campos
- [ ] T6: Escrever teste de importação de CSV antigo (sem novos campos) para confirmar retrocompatibilidade

## 5. Artifact Mínimo do Épico

`artifacts/ajuste-fino-leads/phase-f1/epic-f1-02-migration-evidence.md` — log de `alembic upgrade head` e output de teste pytest demonstrando campos persistidos e recuperáveis.

## 6. Dependências

- [PRD Refino Leads v2](../PRD_Refino_Leads_v2.md) — Seção 3.3
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
