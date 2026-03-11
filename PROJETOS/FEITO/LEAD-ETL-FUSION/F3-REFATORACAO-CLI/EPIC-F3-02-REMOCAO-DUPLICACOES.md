---
doc_id: "EPIC-F3-02-REMOCAO-DUPLICACOES"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# EPIC-F3-02 - Remocao Duplicacoes

## Objetivo

Reduzir `etl/transform/` e `etl/validate/` a reexports compativeis e preparar a remocao definitiva de `backend/app/utils/lead_import_normalize.py` apos cobertura de testes suficiente.

## Resultado de Negocio Mensuravel

O repositorio passa a ter um unico ponto de verdade para transformacao e validacao de leads, diminuindo custo de manutencao, divergencia entre fluxos e risco de correcoes aplicadas em apenas um caminho.

## Definition of Done

- A logica real de transformacao e validacao vive apenas em `core/leads_etl/`.
- `etl/transform/` e `etl/validate/` permanecem apenas como camadas de compatibilidade enquanto necessario.
- A remocao do normalize legado do backend fica condicionada a cobertura comprovada.
- Os guards de arquitetura e higiene detectam reintroducao de duplicacao funcional.

## Issues

### ISSUE-F3-02-01 - Reduzir etl/transform/ a reexports compativeis
Status: todo

**User story**
Como pessoa que mantem transformacoes do ETL, quero que `etl/transform/` vire somente uma fachada para o core para evitar bifurcacao de logica.

**Plano TDD**
1. `Red`: ampliar `tests/test_xlsx_utils.py` e `tests/test_segment_mapper.py` para falhar quando `etl/transform/__init__.py`, `etl/transform/column_normalize.py` ou `etl/transform/segment_mapper.py` mantiverem comportamento divergente do core.
2. `Green`: transformar `etl/transform/column_normalize.py` e `etl/transform/segment_mapper.py` em reexports compativeis apontando para `core/leads_etl/transform/`.
3. `Refactor`: simplificar `etl/transform/__init__.py` para reexportar apenas a superficie publica necessaria, deixando o core como implementacao real.

**Criterios de aceitacao**
- Given imports existentes de `etl.transform`, When o codigo roda, Then o comportamento permanece e a logica real vive so no core.
- Given alteracao futura no core, When os reexports sao usados, Then nao ha duplicacao funcional local em `etl/transform/`.

### ISSUE-F3-02-02 - Reduzir etl/validate/ a reexports compativeis
Status: todo

**User story**
Como pessoa responsavel pelos checks do ETL, quero que `etl/validate/` vire uma camada de compatibilidade para manter uma unica implementacao de validacao.

**Plano TDD**
1. `Red`: ampliar `tests/test_dq_checks_schema_not_null.py`, `tests/test_dq_advanced_checks.py` e `tests/test_render_dq_report.py` para falhar quando `etl/validate/framework.py` e os checks divergirem do core compartilhado.
2. `Green`: transformar `etl/validate/__init__.py`, `etl/validate/framework.py` e os modulos de checks em reexports ou fachadas que apontem para `core/leads_etl/validate/`.
3. `Refactor`: consolidar a superficie publica de validacao para reduzir espalhamento de contratos e facilitar os guards de duplicacao.

**Criterios de aceitacao**
- Given checks e renderer atuais, When carregados do caminho legado, Then o codigo resolve para o core compartilhado.
- Given divergencia de implementacao entre legado e core, When a suite roda, Then a duplicacao e exposta antes da liberacao da fase.

### ISSUE-F3-02-03 - Remover o normalize legado do backend apos cobertura
Status: todo

**User story**
Como pessoa que mantem o backend, quero remover `backend/app/utils/lead_import_normalize.py` quando a cobertura permitir para eliminar a ultima duplicacao relevante de normalizacao.

**Plano TDD**
1. `Red`: ampliar `backend/tests/test_leads_import_csv_smoke.py`, `backend/tests/test_lead_import_preview_xlsx.py`, `scripts/check_architecture_guards.sh` e `scripts/check_repo_hygiene.sh` para falhar se o helper legado ainda for necessario ou se voltar a ser reintroduzido apos a remocao.
2. `Green`: substituir o helper legado pelas chamadas ao core, remover o arquivo quando a cobertura estiver comprovada e ajustar os consumidores remanescentes.
3. `Refactor`: consolidar guardrails para impedir recriacao de logica duplicada no backend depois da limpeza final.

**Criterios de aceitacao**
- Given cobertura de testes ja migrada para o core, When a remocao final do helper legado ocorre, Then o backend continua green.
- Given tentativa futura de reintroduzir logica duplicada, When os guards rodam, Then a violacao e sinalizada de forma objetiva.

## Artifact Minimo do Epico

- `artifacts/phase-f3/epic-f3-02-remocao-duplicacoes.md` com evidencias de reexports, eliminacao de duplicacao e prontidao para remocao do helper legado.

## Dependencias

- [PRD](../PRD-LEAD-ETL-FUSION.md)
- [GOV-SCRUM](../../../../COMUM/GOV-SCRUM.md)
- [DECISION-PROTOCOL](../DECISION-PROTOCOL.md)
