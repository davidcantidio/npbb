---
doc_id: "EPIC-F1-02-MODELO-CANONICO-LEAD-ROW"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F1-02 - Modelo Canonico Lead Row

## Objetivo

Criar `core/leads_etl/models/lead_row.py` como modelo Pydantic canonico de uma linha de lead, independente de FastAPI, SQLModel e ORM, cobrindo os campos importaveis usados por ETL e backend.

## Resultado de Negocio Mensuravel

Backend e ETL passam a falar o mesmo contrato de dados para leads, diminuindo risco de perda de campos, coercoes divergentes e bugs de integracao entre preview, validacao e persistencia.

## Definition of Done

- `lead_row.py` cobre os campos importaveis observados no modelo `Lead` e nas coercoes do importador atual.
- O contrato canonico explicita tipos, coercao esperada e falhas validaveis para campos criticos.
- O modelo pode ser consumido tanto por ETL quanto por backend sem dependencia de camada web ou de banco.
- Testes de contrato detectam drift de campos ou coercao entre camadas.

## Issues

### ISSUE-F1-02-01 - Inventariar o contrato canonico de campos do lead
Status: todo

**User story**
Como pessoa dona do contrato de dados, quero inventariar todos os campos importaveis de lead para consolidar um modelo canonico unico e auditavel.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_constraints.py` para falhar quando um campo usado por `backend/app/models/models.py` ou por `backend/app/utils/lead_import_normalize.py` nao estiver refletido no inventario canonico.
2. `Green`: criar `core/leads_etl/models/lead_row.py` com os campos importaveis do modelo `Lead` e documentar exclusoes intencionais quando um campo nao fizer parte do contrato de entrada.
3. `Refactor`: consolidar nomes e obrigatoriedades para que o inventario vire a referencia unica entre backend, ETL e documentacao tecnica.

**Criterios de aceitacao**
- Given o modelo `Lead` e as coercoes atuais, When `LeadRow` e definido, Then todo campo importavel tem contraparte explicita ou exclusao documentada.
- Given o modelo canonico no core, When carregado isoladamente, Then ele nao depende de web, ORM ou imports do backend.

### ISSUE-F1-02-02 - Modelar validacoes de tipos e coercoes em Pydantic
Status: todo

**User story**
Como pessoa que importa leads, quero que o modelo canonico aplique coercoes previsiveis para email, cpf, telefone, cep e datas para reduzir inconsistencias entre preview e commit.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_leads_import_csv_smoke.py` e `backend/tests/test_lead_import_preview_xlsx.py` para capturar divergencias nas coercoes hoje centralizadas em `backend/app/utils/lead_import_normalize.py`.
2. `Green`: implementar validadores em `core/leads_etl/models/lead_row.py` que reproduzam a semantica atual para email, cpf, telefone, cep, `data_nascimento` e `data_compra`.
3. `Refactor`: reduzir regras duplicadas de coercao, documentar os defaults do modelo e explicitar os erros validaveis para entradas invalidas.

**Criterios de aceitacao**
- Given email, cpf, telefone, cep e datas validos, When o dado entra em `LeadRow`, Then o comportamento de coercao segue o contrato atual do importador.
- Given valor invalido em campo critico, When o modelo valida, Then a falha e explicita, automatizavel e rastreavel por teste.

### ISSUE-F1-02-03 - Provar compatibilidade do modelo com ETL e backend
Status: todo

**User story**
Como pessoa mantenedora da integracao, quero provar que o mesmo `LeadRow` serve ao ETL e ao backend para evitar drift silencioso entre transformacao e persistencia.

**Plano TDD**
1. `Red`: ampliar `tests/test_xlsx_utils.py`, `tests/test_etl_orchestrator_s1.py` e `backend/tests/test_leads_import_csv_smoke.py` para expor diferencas de shape entre linhas normalizadas do ETL e payloads usados pelo backend.
2. `Green`: adaptar os pontos de fronteira necessarios para materializar `LeadRow` tanto a partir de linhas normalizadas do ETL quanto dos payloads do importador HTTP.
3. `Refactor`: consolidar testes contratuais para que qualquer drift de campo, tipo ou coercao falhe cedo na suite.

**Criterios de aceitacao**
- Given linhas normalizadas do ETL e payloads do backend, When adaptadas para `LeadRow`, Then a mesma estrutura serve aos dois fluxos sem campos divergentes.
- Given drift de campo entre camadas, When a suite contratual roda, Then a divergencia falha antes da integracao seguir para F2.

## Artifact Minimo do Epico

- `artifacts/phase-f1/epic-f1-02-modelo-canonico-lead-row.md` com inventario de campos, regras de coercao e evidencias de compatibilidade cross-camada.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
