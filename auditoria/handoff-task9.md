# Handoff - Task 9 (validacao de upload: conteudo alem da extensao)

## Missao original

- Rejeitar cedo uploads `.csv` e `.xlsx` com conteudo incoerente, antes de parser pesado.
- Manter os limites de tamanho ja existentes.
- Devolver erro HTTP consistente (`INVALID_FILE_CONTENT`) sem stack trace exposto.
- Cobrir o comportamento com teste automatizado.

## Estado atual da implementacao

### Resolvido

- A validacao ficou centralizada em [`backend/app/services/imports/file_reader.py`](backend/app/services/imports/file_reader.py), via `inspect_upload`.
- `inspect_upload` e usado por:
  - [`backend/app/routers/leads.py`](backend/app/routers/leads.py) em `POST /leads/import/upload` e `POST /leads/batches`;
  - [`backend/app/routers/publicidade.py`](backend/app/routers/publicidade.py) em `POST /publicidade/import/upload`;
  - `read_file_sample`, o que cobre o preview de publicidade;
  - [`backend/app/modules/leads_publicidade/application/etl_import/extract.py`](backend/app/modules/leads_publicidade/application/etl_import/extract.py) via `read_upload_bytes`, sem diff direto nesse modulo.
- Regras atuais:
  - **`.xlsx`**: o probe inicial precisa comecar como ZIP valido (`PK...`) e o arquivo ZIP precisa conter a estrutura minima de workbook OOXML: `[Content_Types].xml`, `_rels/.rels` e `xl/workbook.xml`.
  - **`.csv`**: o probe rejeita byte NUL e rejeita assinatura ZIP no inicio.
- O stream volta para `seek(0)` ao final da validacao.
- Os erros continuam sendo devolvidos como 400 estruturado via `ImportFileError` -> `raise_http_error`.

### Parcialmente resolvido / limites conhecidos

- A validacao de `.csv` continua leve: ela barra binario obvio e ZIP/XLSX renomeado, mas nao tenta provar semanticamente que o arquivo e um CSV valido.
- `read_raw_file_preview` e `read_raw_file_rows` continuam assumindo que o blob recebido ja passou pela validacao de upload. Isso e suficiente para novos uploads, mas batches Bronze antigos gravados antes desta task ainda podem falhar tardiamente se o blob armazenado ja estiver corrompido.

## Ficheiros relevantes

| Caminho | Papel na solucao |
|---------|------------------|
| [backend/app/services/imports/file_reader.py](backend/app/services/imports/file_reader.py) | Validacao central: extensao, tamanho, vazio, probe inicial e estrutura minima de `.xlsx`. |
| [backend/app/routers/leads.py](backend/app/routers/leads.py) | Upload e criacao de batch usam `inspect_upload` e convertem `ImportFileError` em HTTP 400 estruturado. |
| [backend/tests/test_import_file_reader.py](backend/tests/test_import_file_reader.py) | Cobertura unitario para `.xlsx` invalido textual, ZIP arbitrario renomeado para `.xlsx`, CSV com NUL, CSV com assinatura ZIP, CSV valido e workbook `.xlsx` real. |
| [backend/tests/test_lead_batch_endpoints.py](backend/tests/test_lead_batch_endpoints.py) | Cobertura de integracao para rejeicao no `POST /leads/batches` tanto de bytes invalidos quanto de ZIP arbitrario renomeado para `.xlsx`. |

## O que foi corrigido nesta revisao

- O handoff anterior descrevia `.xlsx` como "qualquer ZIP com assinatura valida". Isso estava otimista demais.
- Antes deste ajuste, um ZIP arbitrario renomeado para `.xlsx` passava em `inspect_upload` e so quebrava depois no parser.
- Agora o upload so passa se o ZIP tiver estrutura minima de workbook OOXML.

## Compatibilidade

- **Continua aceito**:
  - CSV UTF-8/UTF-8 BOM/Latin-1 legivel como texto, sem NUL e sem assinatura ZIP.
  - XLSX real gerado por workbook OOXML.
- **Passa a ser rejeitado cedo**:
  - conteudo textual com nome `.xlsx`;
  - ZIP arbitrario ou `.docx` renomeado para `.xlsx`;
  - `.xlsx` truncado ou corrompido sem estrutura minima de workbook;
  - `.xlsx` / ZIP renomeado para `.csv`;
  - CSV com byte NUL no probe.

## Validacao executada

No Windows, a verificacao rodada nesta revisao foi:

```powershell
$env:PYTHONPATH='C:\Users\NPBB\npbb;C:\Users\NPBB\npbb\backend'
$env:SECRET_KEY='ci-secret-key'
$env:TESTING='true'
.\.venv\Scripts\python.exe -m pytest -q tests/test_import_file_reader.py tests/test_lead_batch_endpoints.py
```

Resultado: `39 passed`.

## Proximo passo recomendado

- Se a proxima task continuar na linha de endurecimento da superficie de upload, priorizar:
  - decidir se batches Bronze antigos precisam de revalidacao defensiva no preview;
  - decidir se o sniff de `.csv` deve subir um nivel (ex.: heuristica de texto/tabular mais forte), sem transformar a validacao inicial em parser completo.
