# Handoff — Task 8 (Política única de merge: Gold vs legado/ETL)

## Resumo

- **Política acordada:** merge **não destrutivo** (“só preenche lacunas”) para **todos** os campos do payload, com a mesma semântica de “valor presente” em todo o sistema: `None` e strings só com espaços contam como vazio; valores já presentes no `Lead` **não** são substituídos por valores novos do ficheiro (nem `nome`, nem `evento_nome`, nem email/CPF/`fonte_origem` tratados de forma especial face ao resto).
- **Implementação:** função única `merge_lead_payload_fill_missing` + `lead_field_has_value` em [`backend/app/modules/leads_publicidade/application/lead_merge_policy.py`](backend/app/modules/leads_publicidade/application/lead_merge_policy.py). O Gold chama-a via `_merge_lead_payload_if_missing`; o ETL e o legado via `merge_lead` em [`persistence.py`](backend/app/modules/leads_publicidade/application/etl_import/persistence.py).
- **Documentação:** [ADR-0001](docs/adr/0001-lead-import-merge-policy.md) (matriz vazio/preenchido, consequências) e secção Upsert actualizada em [`docs/leads_importacao.md`](docs/leads_importacao.md).
- **Consequência operacional:** reimportar para “corrigir” nome ou `evento_nome` já gravados **não** altera o registo; edição manual ou outro fluxo explícito é necessário.

## Ficheiros tocados

| Caminho | Alteração |
|---------|-----------|
| [backend/app/modules/leads_publicidade/application/lead_merge_policy.py](backend/app/modules/leads_publicidade/application/lead_merge_policy.py) | Novo: política de merge partilhada. |
| [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](backend/app/modules/leads_publicidade/application/etl_import/persistence.py) | `merge_lead` delega na função partilhada. |
| [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) | `_merge_lead_payload_if_missing` delega na mesma função; import. |
| [docs/adr/0001-lead-import-merge-policy.md](docs/adr/0001-lead-import-merge-policy.md) | ADR. |
| [docs/adr/README.md](docs/adr/README.md) | Índice de ADRs. |
| [docs/leads_importacao.md](docs/leads_importacao.md) | Secção Upsert + fluxo ETL alinhados ao ADR. |
| [backend/tests/test_lead_merge_policy.py](backend/tests/test_lead_merge_policy.py) | Testes unitários da política e dois passes sucessivos. |
| [backend/tests/test_etl_import_persistence.py](backend/tests/test_etl_import_persistence.py) | Cenário rename: expectativas de preservação de `nome` / `evento_nome`. |
| [backend/tests/test_leads_import_etl_endpoint.py](backend/tests/test_leads_import_etl_endpoint.py) | Teste de commit ETL após rename de evento: preserva `nome` existente. |

## Trecho crítico (merge)

Função pura sobre o modelo `Lead` (sem I/O):

```python
def merge_lead_payload_fill_missing(lead: Lead, payload: dict[str, object]) -> None:
    for field, value in payload.items():
        if not lead_field_has_value(value):
            continue
        current = getattr(lead, field, None)
        if lead_field_has_value(current):
            continue
        setattr(lead, field, value)
```

## Diffs / revisão (comandos sugeridos)

```bash
git diff -- backend/app/modules/leads_publicidade/application/lead_merge_policy.py backend/app/modules/leads_publicidade/application/etl_import/persistence.py backend/app/services/lead_pipeline_service.py
git diff -- docs/adr/ docs/leads_importacao.md
git diff -- backend/tests/test_lead_merge_policy.py backend/tests/test_etl_import_persistence.py backend/tests/test_leads_import_etl_endpoint.py
```

## Testes executados

```powershell
cd backend
$env:PYTHONPATH="<repo>;<repo>/backend"
$env:SECRET_KEY="ci-secret-key"
python -m pytest tests/test_lead_merge_policy.py tests/test_etl_import_persistence.py tests/test_leads_import_etl_usecases.py -q
python -m pytest tests/test_leads_import_etl_endpoint.py::test_commit_etl_preserves_existing_lead_fields_after_event_rename -q
```

## Referência

- Pedido: [auditoria/task8.md](task8.md)
- Contexto: [auditoria/deep-research-report.md](deep-research-report.md)
- Task 7 (parser ETL): [auditoria/handoff-task7.md](handoff-task7.md)
