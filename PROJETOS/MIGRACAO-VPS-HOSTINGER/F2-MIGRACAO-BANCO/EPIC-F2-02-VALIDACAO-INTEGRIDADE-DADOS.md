---
doc_id: "EPIC-F2-02-VALIDACAO-INTEGRIDADE-DADOS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F2-02 - Validacao Integridade Dados

## Objetivo

Validar que o banco restaurado preserva contagens e integridade suficiente para prosseguir para o deploy, com evidencia auditavel de `promote | hold`.

## Resultado de Negocio Mensuravel

A aprovacao da migracao deixa de depender de validacao informal e passa a exigir equivalencia minima de dados e sinais objetivos de prontidao.

## Definition of Done

- Existe comparacao objetiva de contagem entre origem e destino para `lead`, `evento` e `usuario`.
- Existe uma validacao minima de integridade e leitura do schema restaurado com suite ancorada no backend.
- Divergencia de contagem, constraint ou leitura gera bloqueio explicito da fase.
- `artifacts/phase-f2/epic-f2-02-validacao-integridade-dados.md` e `artifacts/phase-f2/validation-summary.md` registram a decisao final.

## Issues

### ISSUE-F2-02-01 - Comparar contagens de tabelas criticas entre origem e destino
Status: todo

**User story**
Como pessoa responsavel pelos dados, quero comparar as contagens de tabelas criticas para provar que a migracao nao perdeu registros essenciais.

**Plano TDD**
1. `Red`: usar `backend/app/models/models.py` e `backend/alembic/versions/289b4605dc23_init.py` para fixar o conjunto minimo `lead`, `evento` e `usuario` e fazer falhar um comparador sempre que a contagem diferir.
2. `Green`: criar `scripts/compare_restore_counts.py` com CLI `--source-url`, `--target-url`, `--tables lead evento usuario` e `--output`, gerando `artifacts/phase-f2/table-counts.md`.
3. `Refactor`: externalizar lista de tabelas e formato de saida para permitir reuso do comparador em ensaio e cutover final sem duplicacao.

**Criterios de aceitacao**
- Given conexao valida com origem e destino, When o comparador roda, Then as contagens de `lead`, `evento` e `usuario` ficam identicas e a evidencia e gravada.
- Given qualquer divergencia de contagem, When o comparador termina, Then o gate da fase fica em `hold` e a tabela divergente aparece no artifact.

### ISSUE-F2-02-02 - Validar integridade relacional e leituras essenciais
Status: todo

**User story**
Como pessoa mantenedora do backend, quero validar constraints e leituras essenciais no banco restaurado para evitar seguir para o deploy com um schema inutilizavel.

**Plano TDD**
1. `Red`: apontar `backend/tests/test_lead_constraints.py`, `backend/tests/test_leads_list_endpoint.py` e `backend/tests/test_dashboard_leads_endpoint.py` para um perfil de Postgres restaurado e fazer a suite falhar quando constraints, queries ou joins essenciais quebrarem.
2. `Green`: definir um perfil de validacao do restore para executar essa suite contra o banco local restaurado e registrar o resultado no artifact do epico.
3. `Refactor`: isolar fixtures de restore para que a validacao pos-migracao nao contamine a suite diaria baseada em SQLite ou ambientes locais padrao.

**Criterios de aceitacao**
- Given banco restaurado em `head`, When a suite de validacao roda, Then leituras essenciais de leads e eventos concluem sem erro e as constraints permanecem validas.
- Given linhas orfas, constraints quebradas ou regressao de leitura, When a suite roda, Then a fase e bloqueada com evidencia objetiva do teste falho.

### ISSUE-F2-02-03 - Consolidar evidencia de fase e decisao promote ou hold
Status: todo

**User story**
Como pessoa que aprova a migracao, quero um resumo unico com comparacao de dados, alembic, validacao e rollback para decidir `promote | hold` de forma auditavel.

**Plano TDD**
1. `Red`: usar `PROJETOS/SCRUM-GOV.md`, `PROJETOS/DECISION-PROTOCOL.md` e `artifacts/phase-f2/validation-summary.md` para tratar como falha qualquer fase sem um resumo unico de gate, evidencias, decisao e rollback.
2. `Green`: gerar `artifacts/phase-f2/validation-summary.md` com status dos dois epicos, resultado de contagens, resultado do `alembic upgrade head`, resultado da suite de integridade e decisao `promote | hold`.
3. `Refactor`: padronizar o formato do resumo para que as fases seguintes possam consumir o mesmo modelo de aprovacao operacional.

**Criterios de aceitacao**
- Given evidencias completas dos dois epicos, When a revisao de fase ocorre, Then `validation-summary.md` registra gate, status dos epicos, decisao final e rollback referenciado.
- Given evidencia ausente ou qualquer falha de contagem, migration ou integridade, When a revisao ocorre, Then a decisao registrada e `hold` com motivo objetivo.

## Artifact Minimo do Epico

- `artifacts/phase-f2/epic-f2-02-validacao-integridade-dados.md` com relatorio de contagens, resultado da suite de integridade, analise de bloqueios e ponteiro para `artifacts/phase-f2/validation-summary.md`.

## Dependencias

- [PRD](../prd_vps_migration.md)
- [SCRUM-GOV](../SCRUM-GOV.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
