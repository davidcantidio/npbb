# EPIC-F1-01 — Extensão do Modelo Lead e Migração
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Adicionar ao modelo `Lead` os campos `is_cliente_bb` e `is_cliente_estilo` (boolean
nullable), criar a migration Alembic correspondente e atualizar os schemas de
leitura/escrita para expor os novos campos sem quebrar fluxos existentes.

**Contexto:** Os campos representam o resultado de cruzamento externo com a base do
Banco do Brasil. Ficam `NULL` até que o cruzamento seja realizado para o lote
correspondente. O dashboard usa esses campos para calcular percentuais de clientes BB
e cobertura de dados.

## 2. Contexto Arquitetural
- Modelo `Lead` em `backend/app/models/models.py` (SQLModel, table=True)
- Migrations Alembic em `backend/alembic/versions/`
- Schemas Pydantic em `backend/app/schemas/`
- PYTHONPATH: `/workspace:/workspace/backend`
- Ambos os campos são indexados para performance de queries do dashboard

## 3. Riscos e Armadilhas
- Migration em tabela com muitos registros pode ser lenta — campos nullable mitigam isso
- Schemas de leitura existentes que fazem `model_validate` podem falhar se não atualizados
- Índice composto `(evento_nome, is_cliente_bb, data_nascimento)` deve ser avaliado após
  medir performance, não criado prematuramente

## 4. Definition of Done do Épico
- [ ] Model `Lead` possui `is_cliente_bb` e `is_cliente_estilo` (Optional[bool], default=None, indexed)
- [ ] Migration Alembic criada e aplicável em banco limpo e com dados existentes
- [ ] Rollback da migration remove os campos sem efeito colateral
- [ ] Schemas de leitura do Lead atualizados para incluir os novos campos
- [ ] Testes de criação/leitura de lead com e sem os novos campos passam

---
## Issues

### DLE-F1-01-001 — Adicionar campos `is_cliente_bb` e `is_cliente_estilo` ao modelo Lead
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Estender o SQLModel `Lead` com dois campos boolean nullable para armazenar o resultado
do cruzamento com a base de dados do Banco do Brasil. Ambos os campos recebem índice
individual para otimizar queries do dashboard.

**Critérios de Aceitação:**
- [ ] Classe `Lead` possui campo `is_cliente_bb: Optional[bool] = Field(default=None, index=True)`
- [ ] Classe `Lead` possui campo `is_cliente_estilo: Optional[bool] = Field(default=None, index=True)`
- [ ] Campos têm description explicativa no Field
- [ ] Leads existentes continuam válidos (default NULL)
- [ ] Testes de criação de lead com e sem os novos campos passam

**Tarefas:**
- [ ] T1: Adicionar campos ao modelo `Lead` em `backend/app/models/models.py`
- [ ] T2: Verificar que imports e tipagem estão corretos (Optional, Field)
- [ ] T3: Executar testes existentes do modelo Lead para garantir retrocompatibilidade

**Notas técnicas:**
Os campos seguem o mesmo padrão de campos nullable já existentes no modelo. A description
do Field deve explicar a semântica: "True = cliente BB confirmado; NULL = cruzamento pendente".

---
### DLE-F1-01-002 — Criar migration Alembic para novos campos do Lead
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F1-01-001

**Descrição:**
Gerar e validar migration Alembic que adiciona as colunas `is_cliente_bb` e
`is_cliente_estilo` à tabela `lead`. Ambos os campos são incluídos na mesma migration
por afinidade semântica.

**Critérios de Aceitação:**
- [ ] Arquivo de migration em `backend/alembic/versions/` com revision ID único
- [ ] `alembic upgrade head` aplica sem erro em banco limpo
- [ ] `alembic upgrade head` aplica sem erro em banco com dados existentes
- [ ] `alembic downgrade -1` remove as colunas sem efeito colateral
- [ ] Índices `ix_lead_is_cliente_bb` e `ix_lead_is_cliente_estilo` criados

**Tarefas:**
- [ ] T1: Gerar migration com `alembic revision --autogenerate -m "add_is_cliente_bb_estilo_to_lead"`
- [ ] T2: Revisar migration gerada — verificar que apenas os campos esperados aparecem
- [ ] T3: Testar upgrade em banco limpo
- [ ] T4: Testar upgrade em banco com leads existentes (verificar NULLs)
- [ ] T5: Testar downgrade

---
### DLE-F1-01-003 — Atualizar schemas de leitura do Lead
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F1-01-001

**Descrição:**
Atualizar os schemas Pydantic de leitura do Lead (`LeadListItemRead` e similares) para
incluir os novos campos `is_cliente_bb` e `is_cliente_estilo`, garantindo que a
serialização JSON não quebre fluxos existentes.

**Critérios de Aceitação:**
- [ ] `LeadListItemRead` inclui `is_cliente_bb: Optional[bool]` e `is_cliente_estilo: Optional[bool]`
- [ ] Outros schemas de leitura do Lead que exponham dados atualizados conforme necessário
- [ ] Serialização de leads antigos (campos NULL) funciona sem erro
- [ ] Endpoints existentes que retornam leads continuam funcionais

**Tarefas:**
- [ ] T1: Localizar todos os schemas de leitura do Lead em `backend/app/schemas/`
- [ ] T2: Adicionar campos opcionais aos schemas relevantes
- [ ] T3: Executar testes existentes de endpoints que retornam leads
- [ ] T4: Verificar que a documentação OpenAPI reflete os novos campos

## 5. Notas de Implementação Globais
- Os dois campos devem ser tratados como par semântico — sempre adicionados juntos
- Não criar índice composto nesta fase; avaliar após medição de performance em produção
- Manter retrocompatibilidade total: nenhum endpoint existente deve quebrar
