---
doc_id: "EPIC-F1-01-MIGRACAO-LEAD-CLIENTE-BB"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F1-01 - Migracao Lead Cliente BB

## Objetivo

Adicionar ao modelo `Lead` os campos nullable `is_cliente_bb` e `is_cliente_estilo`, com migration unica e indices suficientes para sustentar a analise etaria sem quebrar dados legados.

## Resultado de Negocio Mensuravel

O sistema passa a distinguir "nao cliente" de "dado indisponivel", permitindo que o dashboard exponha cobertura real do cruzamento BB em vez de inferir valores incorretos.

## Definition of Done

- Existe uma migration em `backend/alembic/versions/` que cria e remove os dois campos com upgrade e downgrade validos.
- `backend/app/models/models.py` expone os novos campos como `Optional[bool]`, com default `None` e indexacao coerente.
- Registros antigos continuam legiveis sem backfill obrigatorio.
- Os cenarios de teste que semeiam `Lead` seguem passando com e sem preenchimento dos novos campos.

## Issues

### DLE-F1-01-001 - Criar migration unica para BB e Estilo
Status: todo

**User story**
Como pessoa responsavel pelo banco, quero uma migration unica para os dois campos de cruzamento para aplicar e reverter a mudanca sem ambiguidade operacional.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_lead_constraints.py` usando as fixtures de `backend/tests/conftest.py` para falhar quando a tabela `lead` nao expuser `is_cliente_bb` e `is_cliente_estilo` como colunas nullable.
2. `Green`: criar a revision em `backend/alembic/versions/` adicionando as duas colunas e os indices recomendados na mesma migration.
3. `Refactor`: padronizar nomes de indice e comandos de downgrade para manter compatibilidade entre SQLite de teste e Postgres de producao.

**Criterios de aceitacao**
- Given um banco limpo, When a migration roda, Then a tabela `lead` passa a ter `is_cliente_bb` e `is_cliente_estilo` com default `NULL`.
- Given a revision aplicada, When o downgrade roda, Then as duas colunas e seus indices sao removidos sem deixar objeto residual.

### DLE-F1-01-002 - Atualizar o modelo `Lead` para refletir a migration
Status: todo

**User story**
Como pessoa desenvolvedora do backend, quero que o SQLModel `Lead` reflita os novos campos para que querys, seeds e schemas usem a tipagem correta.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_dashboard_leads_endpoint.py` e `backend/tests/test_dashboard_leads_report_endpoint.py` para semear leads com `is_cliente_bb=True`, `False` e `None`, falhando enquanto `backend/app/models/models.py` nao aceitar essas variacoes.
2. `Green`: atualizar `backend/app/models/models.py` com os dois campos opcionais, descricoes e indexacao coerente com a migration.
3. `Refactor`: centralizar comentarios e descricoes dos campos no modelo para evitar divergencia entre schema ORM e documentacao da API.

**Criterios de aceitacao**
- Given um `Lead` novo criado pelos testes, When `is_cliente_bb` e `is_cliente_estilo` nao sao informados, Then ambos persistem como `NULL`.
- Given um `Lead` com `is_cliente_bb=True`, When o objeto e relido pelo ORM, Then o valor permanece acessivel sem coercao incorreta para string ou inteiro.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f1/epic-f1-01-migracao-lead-cliente-bb.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
