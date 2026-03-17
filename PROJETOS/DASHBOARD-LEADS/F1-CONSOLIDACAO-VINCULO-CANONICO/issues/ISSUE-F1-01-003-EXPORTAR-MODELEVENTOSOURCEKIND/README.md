---
doc_id: "ISSUE-F1-01-003-EXPORTAR-MODELEVENTOSOURCEKIND.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-003 - Exportar LeadEvento e LeadEventoSourceKind no agregado de modelos

## User Story
Como mantenedor do modulo de leads e dashboards, quero garantir que `LeadEvento` e `LeadEventoSourceKind` sejam exportados pelo agregado de modelos (`app.models.models`) para que a aplicacao suba sem `ImportError` e os modulos que dependem desses tipos possam importar pelo caminho canonico.

## Contexto Tecnico
- A issue original (ISSUE-F1-01-001) tinha como objetivo corrigir surface de modelo e boot da app, mas o commit de evidencia (e129279) apenas adicionou testes de regressao sem implementar a correcao.
- O erro ocorre porque `LeadEventoSourceKind` nao e exportado em `backend/app/models/models.py`, apesar de ser definido em `backend/app/models/lead_public_models.py` e importado lá.
- Os arquivos que dependem desses tipos (como `backend/app/services/landing_page_submission.py`) quebram com `ImportError: cannot import name 'LeadEventoSourceKind' from 'app.models.models'`.
- O artefato minimo esperado e que a aplicacao suba sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importem pelo agregado canonico.

## Plano TDD
- Red: escrever ou ajustar testes focados nos contratos diretamente afetados pela exportacao correta, usando o comando alvo da issue original: `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- Green: implementar o minimo necessario para fazer os testes novos passarem sem ampliar escopo fora da issue.
- Refactor: remover drift local, nomes confusos ou duplicacoes mantendo a suite alvo green.

## Criterios de Aceitacao
- Given os arquivos alvo desta issue, When a issue for concluida, Then a aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.
- Given a dependencia das issues anteriores, When a validacao final rodar, Then a entrega nao reintroduz o paradigma antigo de `Lead -> AtivacaoLead -> Evento` como obrigatorio
- Given o modo `required`, When outro agente ler a issue, Then `README.md` e `TASK-1.md` bastam para executar a entrega sem improvisar escopo

## Definition of Done da Issue
- [ ] A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.
- [ ] validacao final obrigatoria executada ou preparada no comando alvo da issue
- [ ] dependencias e links canonicos da issue mantidos coerentes com fase e epic

## Tasks
- [T1: Exportar LeadEvento e LeadEventoSourceKind no agregado de modelos](./TASK-1.md)

## Arquivos Reais Envolvidos
- `backend/app/models/models.py`
- `backend/app/models/lead_public_models.py` (para referência, nao sera alterado)

## Artifact Minimo
A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico.

## Dependencias
- [Intake](../../../INTAKE-DASHBOARD-LEADS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS.md)
- [Fase](../../F1_DASHBOARD_LEADS_EPICS.md)
- [Epic](../../EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md)
- [Issue de origem](../ISSUE-F1-01-001-CORRIGIR-SURFACE-DE-MODELO-E-BOOT-DA-APP/README.md)