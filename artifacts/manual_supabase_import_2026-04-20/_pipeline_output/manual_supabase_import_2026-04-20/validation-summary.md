# Validation Summary

Lote: manual_supabase_import_2026-04-20
Status: PASS_WITH_WARNINGS
Decision: promote
Source profiles: {'silver_input.csv': ['modelo_canonico']}
Mapping version: multieventos_v1

## Inputs
- input_files_scanned: 15
- input_files_processed: 15
- input_files_skipped: 0

## Totals
- raw_rows: 54911
- valid_rows: 47703
- discarded_rows: 7208

## Quality Metrics
- cpf_invalid_discarded: 5902
- telefone_invalid: 257
- data_evento_invalid: 0
- data_nascimento_invalid: 3226
- data_nascimento_missing: 11759
- duplicidades_cpf_evento: 1051
- cidade_fora_mapeamento: 0
- localidade_invalida: 0
- localidade_nao_resolvida: 0
- localidade_fora_brasil: 0
- localidade_cidade_uf_inconsistente: 0

## Skips
- []

## Gate
- fail_reasons: []
- warnings: ['CPF_INVALIDO_DESCARTADO', 'TELEFONE_INVALIDO', 'DATA_NASCIMENTO_INVALIDA', 'DATA_NASCIMENTO_AUSENTE', 'DUPLICIDADE_CPF_EVENTO']
- localidade_controle: 0
