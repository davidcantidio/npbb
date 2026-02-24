# Spec Snapshot Goldens

Este diretorio guarda snapshots (golden files) dos artefatos gerados pelo fluxo
DOCX-as-spec.

Arquivos esperados:
- `00_docx_as_spec.md`
- `03_requirements_to_schema_mapping.md`

Como validar snapshots:
```bash
python -m pytest tests/test_spec_snapshots.py
```

Como atualizar snapshots (comando explicito com flag):
```bash
python scripts/run_spec_checks.py --docx tests/fixtures/docx/min_template.docx --mapping tests/fixtures/spec/mapping_min.yml --out-dir tests/golden/spec --required-section "Contexto do evento" --required-section "Publico por sessao" --update-snapshots
```

Observacao:
- Atualize snapshots somente quando a mudanca no output for intencional e revisada.
