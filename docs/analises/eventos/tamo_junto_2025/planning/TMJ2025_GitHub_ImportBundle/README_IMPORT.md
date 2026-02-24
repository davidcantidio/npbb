# Importador TMJ 2025 -> GitHub Issues + GitHub Project

Arquivos:
- `TMJ2025_GitHub_Issues.csv`: lista de épicos + tasks, com labels simplificadas (inclui `sprint-1..5`).
- `import_tmj_to_github.py`: script que cria labels e issues via `gh`, e opcionalmente adiciona tudo ao Project.

## Passo a passo (Windows / PowerShell)

1) Escolha o repo onde as issues vão morar (recomendado: o repo do seu código).
   Ex: `davidcantidio/npbb`

2) Instale/abra o GitHub CLI e autentique:
```powershell
gh auth login
```

3) Se você quiser que já caia no Project (recomendado), habilite o escopo `project`:
```powershell
gh auth refresh -s project
```

4) Rodar em **dry-run** (só para validar):
```powershell
python .\import_tmj_to_github.py --repo davidcantidio/npbb --project "Fechamento de Eventos" --csv .\TMJ2025_GitHub_Issues.csv --dry-run
```

5) Rodar pra valer:
```powershell
python .\import_tmj_to_github.py --repo davidcantidio/npbb --project "Fechamento de Eventos" --csv .\TMJ2025_GitHub_Issues.csv
```

## Como filtrar no GitHub

- Por sprint: `label:sprint-1`
- Por épico: `label:docx-como-spec-de-dados`
- Só épicos: `label:epic`
