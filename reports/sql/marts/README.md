# TMJ 2025 Mart Views (`mart_report_*`)

Esta pasta concentra as views SQL consumidas pelo gerador de Word.

## Estrutura

- `*.sql`: scripts versionados de criacao/atualizacao de views `mart_report_*`
- `contracts.yml`: contrato esperado de saida por view (nome + colunas + tipos)
- `../run_views.py`: runner local para aplicar e validar views

## Fluxo local (dev/test)

1. Aplicar SQL + validar contratos:

```powershell
python reports/sql/run_views.py `
  --db-url "sqlite:///reports/tmj2025/tmj_marts_dev.db" `
  --sql-dir "reports/sql/marts" `
  --contracts "reports/sql/marts/contracts.yml"
```

2. Validar sem reaplicar SQL:

```powershell
python reports/sql/run_views.py `
  --db-url "sqlite:///reports/tmj2025/tmj_marts_dev.db" `
  --contracts "reports/sql/marts/contracts.yml" `
  --validate-only
```

3. Validar apenas uma view:

```powershell
python reports/sql/run_views.py `
  --db-url "sqlite:///reports/tmj2025/tmj_marts_dev.db" `
  --contracts "reports/sql/marts/contracts.yml" `
  --view mart_report_healthcheck `
  --validate-only
```

## Convencoes

- Toda view de relatorio deve comecar com `mart_report_`.
- Toda view deve possuir contrato no `contracts.yml`.
- Alteracao de colunas/tipos exige update simultaneo do SQL e do contrato.
