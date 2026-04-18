# Import de leads — limites recomendados (operadores)

Até migrações futuras (Bronze em object storage, snapshots ETL compactados), o sistema continua a:

- Aceitar ficheiros até **50 MB** por defeito (`DEFAULT_IMPORT_MAX_BYTES` em `backend/app/services/imports/file_reader.py`).
- Guardar o ficheiro Bronze como **blob** na tabela `lead_batches` (crescimento de base e backups).
- Manter snapshots ETL completos em **JSON** em `lead_import_etl_preview_session`.

## Recomendações

1. **CSV/XLSX:** preferir ficheiros **< 20 MB** e **< 50 000 linhas** por lote em produção; acima disso, esperar tempos longos no preview ETL e na pipeline Gold, e maior pressão de RAM no servidor.
2. **Concorrência:** evitar vários lotes enormes em paralelo no mesmo nó API.
3. **Gold:** após o insert por janelas (`NPBB_LEAD_GOLD_INSERT_LOOKUP_CHUNK_SIZE`), o pico de RAM por lote desce, mas o CSV consolidado e o Silver ainda podem ser pesados — manter a mesma prudência de linhas.
4. **Timeouts UI:** o frontend usa timeouts longos (até 120 s) para operações de ficheiro; se ocorrer timeout, reduzir o ficheiro ou repetir fora de horas de pico.

Para métricas objectivas, usar o plano em [task5-measurement-plan.md](task5-measurement-plan.md).
