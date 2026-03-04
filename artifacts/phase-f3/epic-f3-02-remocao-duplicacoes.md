# EPIC-F3-02 — Remocao Duplicacoes

## Resumo da entrega

- `backend/app/utils/lead_import_normalize.py` foi removido.
- O router legado de importacao passou a consumir diretamente `core.leads_etl.models.coerce_lead_field`.
- Guards de arquitetura/higiene foram ajustados para bloquear reintroducao do helper legado.
- Testes de contrato do backend foram atualizados para validar coercao canonica e ausencia do helper removido.

## Mudancas aplicadas

### 1) Consumo direto do core no backend

- Arquivo alterado: `backend/app/routers/leads.py`
- Mudanca: troca de `from app.utils.lead_import_normalize import coerce_field` por `from core.leads_etl.models import coerce_lead_field`.
- Mudanca: `importar_leads_usecase(..., coerce_field=coerce_lead_field, ...)`.

### 2) Remocao do helper legado

- Arquivo removido: `backend/app/utils/lead_import_normalize.py`

### 3) Testes de contrato atualizados

- Arquivo alterado: `backend/tests/test_lead_constraints.py`
- Mudancas:
  - remove dependencia do helper legado.
  - valida coercoes canonicas com valores esperados (`email`, `cpf`, `telefone`, `cep`, datas, flags e campos textuais).
  - valida que o helper legado nao existe mais.
  - valida que `backend/app/routers/leads.py` usa coercao direta do core.

### 4) Guardrails para evitar regressao

- Arquivo alterado: `scripts/check_architecture_guards.sh`
- Mudancas:
  - falha se `backend/app/utils/lead_import_normalize.py` existir.
  - falha se houver qualquer import de `app.utils.lead_import_normalize` em `backend/` ou `tests/`.

- Arquivo alterado: `scripts/check_repo_hygiene.sh`
- Mudanca:
  - falha se `backend/app/utils/lead_import_normalize.py` existir.

## Evidencias de verificacao

### Comandos verdes

- `PYTHONPATH=. pytest -q tests/test_core_leads_etl_compat.py` -> `3 passed`
- `PYTHONPATH=backend:. pytest -q backend/tests/test_lead_constraints.py` -> `6 passed`
- `PYTHONPATH=backend:. pytest -q backend/tests/test_leads_import_csv_smoke.py backend/tests/test_lead_import_preview_xlsx.py` -> `2 passed`
- `bash scripts/check_architecture_guards.sh` -> `OK`
- `bash scripts/check_repo_hygiene.sh` -> `OK`

### Observacao de suite adjacente

- A suite `backend/tests/test_leads_import_etl_usecases.py` permanece com falhas de contrato na assinatura `strict` do commit ETL no workspace atual.
- Esse ponto foi mantido fora do escopo deste epic para nao misturar a limpeza de duplicacoes com mudanca comportamental do fluxo ETL commit.
