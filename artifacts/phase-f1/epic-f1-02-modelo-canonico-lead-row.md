# EPIC-F1-02 - Modelo Canonico Lead Row

## Status

- `status`: done
- `data`: 2026-03-03
- `contrato_canonico`: `core/leads_etl/models/lead_row.py`

## Campos Incluidos em `LeadRow`

| Campo | Observacao |
|---|---|
| `id_salesforce` | Identificador externo importavel. |
| `nome` | Texto trimado. |
| `sobrenome` | Texto trimado. |
| `email` | Lowercase + trim. |
| `telefone` | Digits-only. |
| `cpf` | Digits-only. |
| `data_nascimento` | Aceita `DD/MM/YYYY` e `YYYY-MM-DD`. |
| `evento_nome` | Nome canonico do evento no contrato de entrada. |
| `sessao` | Texto trimado. |
| `data_compra` | Aceita datetime atual do importador e fallback de data para meia-noite. |
| `opt_in` | Texto trimado. |
| `opt_in_id` | Texto trimado. |
| `opt_in_flag` | Coercao booleana compativel com helper legado. |
| `metodo_entrega` | Texto trimado. |
| `endereco_rua` | Texto trimado. |
| `endereco_numero` | Texto trimado. |
| `bairro` | Texto trimado. |
| `cep` | Digits-only. |
| `cidade` | Texto trimado. |
| `estado` | Uppercase + trim. |
| `genero` | Texto trimado. |
| `codigo_promocional` | Texto trimado. |
| `ingresso_tipo` | Texto trimado. |
| `ingresso_qtd` | Inteiro derivado do comportamento atual do importador. |
| `fonte_origem` | Texto trimado. |

## Exclusoes Intencionais

| Campo | Motivo |
|---|---|
| `id` | Chave primaria de persistencia; fora do contrato de entrada. |
| `data_criacao` | Timestamp de auditoria/persistencia; fora do contrato compartilhado. |
| `data_compra_data` | Campo derivado do backend; nao pertence ao contrato de entrada. |
| `data_compra_hora` | Campo derivado do backend; nao pertence ao contrato de entrada. |

## Adaptadores de Borda

- `backend_payload_to_lead_row`: aceita payload backend-orientado e falha se receber campos derivados/de persistencia fora do contrato.
- `etl_payload_to_lead_row`: aceita apenas aliases ETL explicitamente mapeados:
  - `evento -> evento_nome`
  - `sexo -> genero`
  - `dt_hr_compra -> data_compra`
  - `qtd_ingresso -> ingresso_qtd`
  - `dt_nascimento -> data_nascimento`
  - `ingresso -> ingresso_tipo`
- O adapter ETL rejeita payloads de staging/canonical com metadados como `source_id`, `ingestion_id`, `lineage_ref_id`, `cpf_hash`, `email_hash`, `person_key_hash`, `sheet_name`, `row_number` e campos `__*`.

## Matriz de Coercao

| Campo | Regra |
|---|---|
| `email` | `lower().strip()` |
| `cpf` | somente digitos |
| `telefone` | somente digitos |
| `cep` | somente digitos |
| `estado` | `upper().strip()` |
| `data_nascimento` | parse `DD/MM/YYYY` ou `YYYY-MM-DD` |
| `data_compra` | parse datetime atual do importador; data pura vira meia-noite |
| `ingresso_qtd` | extracao de digitos + `int` |
| `opt_in_flag` | `1/0`, `true/false`, `yes/no`, `sim/nao`, `s/n` |
| Demais strings | trim simples |

## Evidencias

### Testes executados

```bash
env PYTHONPATH=.:backend python3 -m pytest -q \
  core/leads_etl/models/tests/test_lead_row.py \
  core/leads_etl/models/tests/test_lead_row_adapters.py \
  backend/tests/test_lead_constraints.py \
  backend/tests/test_leads_import_csv_smoke.py \
  backend/tests/test_lead_import_preview_xlsx.py
```

Resultado:

- `14 passed in 2.06s`

### Guards executados

```bash
bash scripts/check_architecture_guards.sh
```

Resultado:

- `OK`
- `core/leads_etl/models` sem imports de `fastapi`, `sqlmodel`, `sqlalchemy`, `alembic` ou `app.`

## Compatibilidade Provada

- O helper legado `backend/app/utils/lead_import_normalize.py` agora delega para `core.leads_etl.models.coerce_lead_field`.
- `backend/tests/test_leads_import_csv_smoke.py` permaneceu verde, preservando o fluxo legado de preview/validate/import.
- `backend/tests/test_lead_import_preview_xlsx.py` permaneceu verde, preservando a interface publica de preview.
- `backend/tests/test_lead_constraints.py` agora congela:
  - cobertura do inventario de campos do `Lead`
  - alinhamento entre helper legado e coercao canonica
  - cobertura dos campos expostos pela UI de importacao
