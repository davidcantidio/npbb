# Handoff — Task 1 (pivô: CPF obrigatório)

## Resumo

A [auditoria/task1.md](task1.md) pedia alinhar o validador ETL com a regra documentada “email ou CPF”. A decisão de produto foi **revertida**: **CPF é sempre obrigatório** para leads importáveis; dados sem CPF válido não entram.

Implementação:

1. **Contratos de mapeamento legado** — `POST /leads/import/validate` passa a exigir que o campo canónico **`cpf` esteja mapeado** (não basta mapear só email). Mensagem HTTP: *“O mapeamento deve incluir a coluna CPF.”* (código `MAPPING_MISSING_ESSENTIAL` mantido).
2. **Documentação** — [docs/leads_importacao.md](../docs/leads_importacao.md) e [docs/leads_conversoes.md](../docs/leads_conversoes.md) atualizados para refletir CPF obrigatório e email recomendado.
3. **Contrato canónico** — [core/leads_etl/models/lead_row.py](../core/leads_etl/models/lead_row.py): docstring do `LeadRow` explica que `cpf`/`email` permanecem opcionais no modelo por compatibilidade, mas **importações** exigem CPF válido na validação a jusante.
4. **Validador ETL** — [backend/app/modules/leads_publicidade/application/etl_import/validators.py](../backend/app/modules/leads_publicidade/application/etl_import/validators.py): constante `MISSING_CPF_REASON` (**“CPF ausente”**) para `cpf` vazio/`None`; **“CPF inválido”** quando há valor presente mas inválido. A regra de rejeição (sempre exigir CPF válido) não mudou.

## Ficheiros tocados

| Ficheiro | Alteração |
|----------|-----------|
| [docs/leads_importacao.md](../docs/leads_importacao.md) | Regras e endpoint validate alinhados a CPF obrigatório; dedupe. |
| [docs/leads_conversoes.md](../docs/leads_conversoes.md) | Mapeamento essencial: CPF obrigatório. |
| [backend/app/routers/leads.py](../backend/app/routers/leads.py) | `_ensure_mapping_has_essential` exige `cpf` mapeado. |
| [backend/app/modules/leads_publicidade/application/etl_import/validators.py](../backend/app/modules/leads_publicidade/application/etl_import/validators.py) | `MISSING_CPF_REASON` + lógica de mensagem. |
| [core/leads_etl/models/lead_row.py](../core/leads_etl/models/lead_row.py) | Docstring `LeadRow`. |
| [backend/tests/test_etl_import_validators.py](../backend/tests/test_etl_import_validators.py) | Testes ausente vs inválido. |
| [backend/tests/test_leads_import_csv_smoke.py](../backend/tests/test_leads_import_csv_smoke.py) | CPF válido no CSV de smoke; novo teste `test_leads_import_validate_rejects_mapping_without_cpf_column`. |
| [auditoria/handoff-task1.md](handoff-task1.md) | Este ficheiro. |

## Revisão / diffs

Comandos úteis (na raiz do repositório):

```bash
git diff -- docs/leads_importacao.md docs/leads_conversoes.md
git diff -- backend/app/routers/leads.py backend/app/modules/leads_publicidade/application/etl_import/validators.py
git diff -- core/leads_etl/models/lead_row.py backend/tests/test_etl_import_validators.py backend/tests/test_leads_import_csv_smoke.py
```

Testes executados (com `PYTHONPATH=<repo>;<repo>/backend` e cwd `backend`):

```bash
python -m pytest tests/test_etl_import_validators.py tests/test_etl_import_persistence.py tests/test_leads_import_csv_smoke.py -q
python -m pytest tests/test_leads_import_etl_endpoint.py::test_preview_etl_reports_invalid_email_and_cpf_validation_errors -q
```

## Notas

- Relatórios em `auditoria/deep-research-report.md` / `task1.md` que descrevem o achado “email ou CPF” ficam **historicamente desatualizados** face a esta decisão; não foram editados neste trabalho.
- Migrações ou contratos OpenAPI gerados automaticamente: **nenhuma** alteração.
