# Handoff - Task 8 (politica unica de merge: Gold vs legado/ETL)

## Resumo executivo

- **Missao da task 8:** eliminar a divergencia de merge entre Gold e ETL/legado, deixando uma unica politica documentada e testada.
- **Politica implementada:** merge **nao destrutivo** para todos os campos do payload. O import **so preenche lacunas** no `Lead` existente.
- **Semantica de valor presente:** `None` e string vazia ou so com espacos contam como vazio. Valores ja presentes no `Lead` nao sao substituidos por valores novos do arquivo.
- **Estado real da implementacao:** a logica de producao esta correta e centralizada; a lacuna encontrada nesta revisao era de **cobertura automatizada do fluxo Gold**, nao de comportamento de merge.

## O que esta resolvido

- Existe uma funcao unica de merge em [backend/app/modules/leads_publicidade/application/lead_merge_policy.py](backend/app/modules/leads_publicidade/application/lead_merge_policy.py):
  - `lead_field_has_value`
  - `merge_lead_payload_fill_missing`
- O **Gold** usa essa politica via `_merge_lead_payload_if_missing` em [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py).
- O **ETL/legado** usam a mesma politica via `merge_lead` em [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](backend/app/modules/leads_publicidade/application/etl_import/persistence.py).
- A documentacao de produto/arquitetura esta alinhada:
  - [docs/adr/0001-lead-import-merge-policy.md](docs/adr/0001-lead-import-merge-policy.md)
  - [docs/leads_importacao.md](docs/leads_importacao.md)

## Cobertura de testes

- **Coberto e validado no helper compartilhado:** [backend/tests/test_lead_merge_policy.py](backend/tests/test_lead_merge_policy.py)
  - valor presente vs vazio
  - dois passes sucessivos preservando valor ja preenchido
- **Coberto e validado em ETL/legado:** [backend/tests/test_etl_import_persistence.py](backend/tests/test_etl_import_persistence.py) e [backend/tests/test_leads_import_etl_endpoint.py](backend/tests/test_leads_import_etl_endpoint.py)
  - reimport com rename de evento
  - preservacao de `nome` e `evento_nome`
- **Coberto nesta revisao no fluxo Gold real:** [backend/tests/test_lead_gold_pipeline.py](backend/tests/test_lead_gold_pipeline.py)
  - dois lotes Gold ancorados para o mesmo lead/evento
  - primeiro lote grava `nome="Alice Original"`
  - segundo lote traz `nome="Alice Corrigida"`
  - o mesmo `Lead` e reutilizado e o valor preenchido e preservado
  - `LeadEvento` continua unico

## Ficheiros tocados pela task 8

| Caminho | Alteracao |
|---------|-----------|
| [backend/app/modules/leads_publicidade/application/lead_merge_policy.py](backend/app/modules/leads_publicidade/application/lead_merge_policy.py) | Modulo compartilhado da politica de merge. |
| [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](backend/app/modules/leads_publicidade/application/etl_import/persistence.py) | `merge_lead` delega para a politica compartilhada. |
| [backend/app/services/lead_pipeline_service.py](backend/app/services/lead_pipeline_service.py) | Gold delega para a mesma politica via `_merge_lead_payload_if_missing`. |
| [docs/adr/0001-lead-import-merge-policy.md](docs/adr/0001-lead-import-merge-policy.md) | ADR da decisao. |
| [docs/adr/README.md](docs/adr/README.md) | Indice de ADRs. |
| [docs/leads_importacao.md](docs/leads_importacao.md) | Secao de upsert alinhada ao ADR. |
| [backend/tests/test_lead_merge_policy.py](backend/tests/test_lead_merge_policy.py) | Testes unitarios da politica. |
| [backend/tests/test_etl_import_persistence.py](backend/tests/test_etl_import_persistence.py) | Cenarios ETL/legado preservando campos preenchidos. |
| [backend/tests/test_leads_import_etl_endpoint.py](backend/tests/test_leads_import_etl_endpoint.py) | Endpoint ETL preserva campos preenchidos apos rename de evento. |
| [backend/tests/test_lead_gold_pipeline.py](backend/tests/test_lead_gold_pipeline.py) | Regressao Gold end-to-end adicionada nesta revisao. |

## Trecho critico

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

## Diffs / revisao

```bash
git diff -- backend/app/modules/leads_publicidade/application/lead_merge_policy.py backend/app/modules/leads_publicidade/application/etl_import/persistence.py backend/app/services/lead_pipeline_service.py
git diff -- backend/tests/test_lead_merge_policy.py backend/tests/test_etl_import_persistence.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_gold_pipeline.py
git diff -- docs/adr/ docs/leads_importacao.md
```

## Pontos sensiveis e limites

- **Resolvido nesta task:** a divergencia de politica de merge entre Gold e ETL/legado.
- **Nao e parte desta task:** outros achados do [auditoria/deep-research-report.md](auditoria/deep-research-report.md), como `partial_failure` do commit ETL, dedupe robusto em banco, durabilidade do pipeline Gold, parser multiaba e rastreabilidade de linha original. Esses pontos so devem ser tratados aqui se outra task os tiver assumido explicitamente.
- **Consequence operacional:** reimportar arquivo para "corrigir" `nome`, `evento_nome` ou qualquer outro campo ja preenchido **nao** altera o registro existente. Correcao exige edicao manual ou fluxo explicito de overwrite.

## Proximo passo recomendado

- Considerar a task 8 encerrada se a suite alvo estiver verde.
- Se surgir nova discussao de produto sobre overwrite seletivo, abrir isso como **nova decisao de politica**, e nao como ajuste pontual em um dos fluxos.

## Referencias

- Pedido: [auditoria/task8.md](task8.md)
- Contexto: [auditoria/deep-research-report.md](deep-research-report.md)
- Contexto anterior: [auditoria/handoff-task7.md](handoff-task7.md)
