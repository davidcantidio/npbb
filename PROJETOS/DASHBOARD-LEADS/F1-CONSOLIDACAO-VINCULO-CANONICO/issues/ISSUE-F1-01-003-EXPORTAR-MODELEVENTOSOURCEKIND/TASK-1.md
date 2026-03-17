---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-003-EXPORTAR-MODELEVENTOSOURCEKIND"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# T1 - Exportar LeadEvento e LeadEventoSourceKind no agregado de modelos

## objetivo
Garantir que `LeadEvento` e `LeadEventoSourceKind` estejam disponíveis para importação via `app.models.models` adicionando os exports necessários em `backend/app/models/models.py`.

## precondicoes
- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar
- `backend/app/models/models.py` (arquivo a ser modificado para adicionar os exports)
- `backend/app/models/lead_public_models.py` (apenas para referência, não será alterado)

## testes_red
- testes_a_escrever_primeiro:
  - Verificar que `LeadEvento` pode ser importado de `app.models.models`
  - Verificar que `LeadEventoSourceKind` pode ser importado de `app.models.models`
  - Garantir que os testes de dashboard coletam sem erro de import
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- criterio_red:
  - os testes novos devem falhar antes da implementação; se ja passarem sem mudança de código, parar e revisar a task

## passos_atomicos
1. escrever ou ajustar primeiro os testes focados listados em `testes_red` (adicionar asserts de import nos testes existentes ou criar novos)
2. rodar o comando red e confirmar falha ligada ao `ImportError` de `LeadEventoSourceKind`
3. implementar o mínimo necessário em `backend/app/models/models.py` para exportar `LeadEvento` e `LeadEventoSourceKind` (adicionar as importações da `lead_public_models` e exportá-las)
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicações locais sem ampliar escopo (se necessário)

## comandos_permitidos
- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- `grep -n "LeadEvento\|LeadEventoSourceKind" backend/app/models/models.py backend/app/models/lead_public_models.py`

## resultado_esperado
Aplicação sobe sem `ImportError` e os módulos que dependem de `LeadEventoSourceKind` importam pelo agregado canonico (`app.models.models`).

## testes_ou_validacoes_obrigatorias
- coleta de `tests/test_dashboard_age_analysis_endpoint.py` sem erro de import
- coleta de `tests/test_dashboard_leads_endpoint.py` sem erro de import
- coleta de `tests/test_dashboard_leads_report_endpoint.py` sem erro de import
- teste específico que verifica `from app.models.models import LeadEvento, LeadEventoSourceKind`

## stop_conditions
- parar se surgir requisito novo não previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural não relacionado a escopo local (por exemplo, problemas de migração não relacionados à exportação de modelos)