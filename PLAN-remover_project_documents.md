# Remover `project_documents` e canonizar intake/PRD no read model Fabrica

## Summary
- Eliminar `project_documents` do runtime Postgres e da migração legada para que o índice pare de persistir um resumo duplicado de documentos de projeto.
- Substituir o consumo genérico de “project document summaries” por entidades canônicas de domínio: `intakes`, `prds` e `documents`.
- Fazer corte seco: sem tabela compatível, sem `VIEW` temporária e sem API de domínio baseada em `project_documents`.

## Implementation Changes
- No `scripts/openclaw_projects_index/schema_postgres.sql`, remover o DDL e índices de `project_documents`.
- Adicionar tabelas canônicas `intakes` e `prds` ao read model Postgres.
  - `intakes`: `project_id`, `document_id` FK único para `documents(id)`, `doc_id`, `status`, `intake_kind`, `source_mode`, `intake_slug`, `path_relative`, timestamps.
  - `prds`: `project_id`, `document_id` FK único para `documents(id)`, `doc_id`, `status`, `intake_kind`, `source_mode`, `path_relative`, timestamps.
- Manter `audit_log` e `closing_report` apenas em `documents` com `kind` canônico; não criar nova tabela-resumo para eles nesta mudança.
- No `scripts/openclaw_projects_index/sync.py`, parar de inserir em `project_documents`.
  - `project_intake` passa a gerar uma linha em `documents` e uma linha em `intakes`.
  - `project_prd` passa a gerar uma linha em `documents` e uma linha em `prds`.
  - `project_audit_log` e `project_closing_report` ficam só em `documents`.
  - Rotinas de limpeza/truncate deixam de citar `project_documents` e passam a incluir `intakes`/`prds`.
- No `scripts/openclaw_projects_index/mirror_sqlite_to_postgres.py`, remover `_copy_project_documents`.
  - A migração legada deve reconstruir `intakes` e `prds` a partir de `documents.kind` + `front_matter_json` do SQLite.
  - Não usar `project_documents` nem como tabela de destino nem como etapa intermediária do fluxo legado.
- No pacote de domínio citado pelo usuário (`postgres.py`, `service.py`, `normative_chain.py`), trocar a abstração de “documento resumido do projeto” por contrato canônico.
  - Repositório Postgres passa a carregar `intakes`, `prds` e `documents`.
  - `service.py` deixa de expor/listar `ProjectDocument*` e passa a expor snapshot normativo do projeto com intake atual, PRD atual e documentos relevantes.
  - `normative_chain.py` decide fase e gates com base em presença/estado de intake e PRD canônicos, consultando `documents` só para artefatos não canonizados.
- Atualizar docs operacionais e exemplos SQL para consultar `intakes`, `prds` e `documents`, removendo qualquer referência a `project_documents`.
  - `scripts/openclaw_projects_index/README.md`
  - `PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md`
  - `PROJETOS/COMUM/MANUAL-FABRICA-CLI-PASSO-A-PASSO.md`

## Public Interfaces / Types
- SQL público do índice muda de:
  - `project_documents`
- Para:
  - `intakes`
  - `prds`
  - `documents`
- O contrato do domínio muda de DTO/repositório genérico de documento de projeto para tipos canônicos equivalentes a `Intake`, `PRD` e `NormativeSnapshot`.
- Consultas operacionais e documentação de suporte devem considerar `audit_log` e `closing_report` como documentos canônicos em `documents`, não como entidade-resumo separada.

## Test Plan
- Atualizar `tests/test_openclaw_projects_index.py` para:
  - validar que sync popula `intakes` e `prds`;
  - validar que `audit_log` e `closing_report` aparecem apenas em `documents`;
  - validar ausência total de `project_documents` no schema/queries do fluxo Postgres.
- Adicionar regressão no mirror SQLite -> Postgres garantindo que snapshots legados geram `intakes`/`prds` sem copiar `project_documents`.
- Atualizar testes/documentação que hoje usam query em `project_documents`.
- No pacote de domínio externo, adicionar ou ajustar testes de `normative_chain` para garantir que os gates continuam corretos usando entidades canônicas.

## Assumptions
- `schema.sql` do SQLite pode permanecer como artefato histórico de snapshot; a remoção é do runtime Postgres e da camada de migração, não da representação fiel de bancos antigos.
- Não haverá `VIEW` de compatibilidade nem fallback em `project_documents`.
- Os arquivos `postgres.py`, `service.py` e `normative_chain.py` referidos pelo usuário estão fora deste workspace atual; a implementação deve aplicar o mesmo contrato canônico nesses módulos em paralelo ao ajuste do índice.
