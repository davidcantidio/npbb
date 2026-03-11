---
doc_id: "EPIC-F2-01-USECASE-ETL-IMPORT"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F2-01 - Use Case ETL Import

## Objetivo

Criar `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py` com a assinatura publica `async def import_leads_with_etl(file, evento_id, db, strict) -> ImportEtlResult`, orquestrando extract, transform, validate e persistencia.

## Resultado de Negocio Mensuravel

Arquivos XLSX fora do padrao passam a ter um caminho HTTP canonico ate o banco, com preview auditavel de qualidade e persistencia consistente com o modelo atual de leads.

## Definition of Done

- O use case ETL recebe arquivo, `evento_id`, sessao de banco e `strict`, devolvendo um contrato consistente para preview e commit.
- O fluxo passa por extract, transform, validate e persistencia com contagens e evidencias rastreaveis.
- `strict=true` bloqueia persistencia quando houver erro de validacao.
- O comportamento de deduplicacao e merge continua coerente com o importador atual.

## Issues

### ISSUE-F2-01-01 - Orquestrar extract, transform e validate no use case ETL
Status: todo

**User story**
Como pessoa usuaria da importacao avancada, quero que o backend execute extract, transform e validate no mesmo use case para ter preview tecnico completo antes de persistir.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_leads_import_csv_smoke.py` para falhar quando `backend/app/modules/leads_publicidade/application/leads_import_usecases.py` nao conseguir reproduzir o fluxo extract, transform e validate usando `etl/extract/xlsx_utils.py` e `etl/validate/framework.py`.
2. `Green`: criar `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py` e implementar a sequencia extract, `core/leads_etl/transform/*`, `core/leads_etl/validate/*`, retornando contagens e `dq_report`.
3. `Refactor`: separar responsabilidade de leitura, transformacao, validacao e serializacao para manter o use case pequeno e pronto para ser reutilizado por preview e commit.

**Criterios de aceitacao**
- Given um XLSX fora do padrao, When `import_leads_with_etl` e chamado, Then a sequencia extract, transform e validate acontece e retorna contagens com `dq_report`.
- Given arquivo vazio ou extensao invalida, When o use case roda, Then o erro segue o contrato HTTP ja usado pelo fluxo legado de importacao.

### ISSUE-F2-01-02 - Persistir sessao de preview e resultado canonico do lote
Status: todo

**User story**
Como pessoa que revisa o preview, quero que o backend gere um `session_token` para reaproveitar as linhas validadas no commit sem recalculo ambigoo.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_import_preview_xlsx.py` para falhar quando o preview nao produzir um `session_token` capaz de referenciar linhas aprovadas, rejeitadas e metadados de DQ.
2. `Green`: implementar persistencia de estado de preview em `backend/app/modules/leads_publicidade/application/leads_import_etl_usecases.py`, incluindo linhas aprovadas, linhas rejeitadas e resumo tecnico do lote.
3. `Refactor`: consolidar o contrato da sessao para suportar idempotencia, reutilizacao controlada e futura expiracao sem vazamento de detalhes do parser.

**Criterios de aceitacao**
- Given preview bem-sucedido, When o use case termina, Then um `session_token` referencia linhas aprovadas, rejeitadas e metadados de DQ.
- Given reutilizacao do mesmo token, When o commit e repetido, Then o comportamento e idempotente ou explicitamente rejeitado pelo contrato do use case.

### ISSUE-F2-01-03 - Aplicar persistencia com strict e deduplicacao
Status: todo

**User story**
Como pessoa dona da carga de leads, quero que o commit respeite `strict` e a deduplicacao atual para evitar carga parcial indevida ou regressao de merge.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_constraints.py` e `backend/tests/test_leads_import_csv_smoke.py` para falhar quando `strict=true` ainda persistir linhas com erro ou quando a deduplicacao divergir do importador atual em `backend/app/routers/leads.py`.
2. `Green`: implementar a persistencia do use case ETL reutilizando as regras atuais de merge, contagem e deduplicacao por `email|cpf|evento_nome|sessao`.
3. `Refactor`: separar as regras de gate de validacao das regras de merge para tornar o comportamento previsivel em preview, commit e retries.

**Criterios de aceitacao**
- Given `strict=true` e qualquer erro de validacao, When o lote e processado, Then zero linhas sao persistidas.
- Given duplicidade por `email|cpf|evento_nome|sessao`, When o commit roda, Then `created`, `updated` e `skipped` seguem a semantica atual do importador.

## Artifact Minimo do Epico

- `artifacts/phase-f2/epic-f2-01-usecase-etl-import.md` com evidencias do fluxo unificado, persistencia de preview e comportamento de `strict`.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
