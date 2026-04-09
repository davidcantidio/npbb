# pr5 — Validação E2E no npbb + Postgres opcional + higiene git

## Pré-requisitos

- Código das fatias A–C integrado e `python -m pytest tests\ -q` verde na Fabrica.
- Chaves OpenRouter disponíveis no processo (ex. `OPENROUTER_API_KEY` + modelo se necessário). O CLI carrega `npbb\.env` / `npbb\backend\.env` se existirem.

## Passo 1 — Limpar só features para preflight

No **npbb**:

```powershell
Get-ChildItem -LiteralPath 'C:\Users\NPBB\npbb\PROJETOS\ATIVOS-INGRESSOS\features' -Directory -Filter 'FEATURE-*' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
```

**Não** apagar outras alterações pendentes no repositório.

## Passo 2 — Bundle-only (sanidade)

```powershell
cd C:\Users\NPBB\fabrica
python .\scripts\fabrica.py --repo-root C:\Users\NPBB\npbb generate features --project ATIVOS-INGRESSOS --bundle-only
```

Confirmar no JSON: `coverage_contract.scope_in_items` tem **10** entradas; `candidate_feature_plan` tem **8** candidatos com agrupamentos do pr1.

## Passo 3 — Generate features real (provider-backed)

```powershell
python .\scripts\fabrica.py --repo-root C:\Users\NPBB\npbb generate features --project ATIVOS-INGRESSOS
```

**Sucesso mínimo:**

- Exit code 0.
- Pastas `PROJETOS\ATIVOS-INGRESSOS\features\FEATURE-*` recriadas.
- Cobertura: cada `scope_in_01`…`scope_in_10` coberto **exatamente uma vez** em `prd_evidence` (via match ao contrato).
- Nenhuma feature com mais de **2** itens canónicos de scope_in.
- Proposta multi-feature com **pelo menos uma** dependência explícita (regra atual do validador).

Slugs/títulos podem diferir ligeiramente da decomposição “referência” humana; o contrato importa.

## Passo 4 — Postgres (opcional)

Se `FABRICA_PROJECTS_DATABASE_URL` **não** estiver definida no ambiente nem nos `.env` carregados: **registar explicitamente** que a sync foi ignorada.

Se estiver definida:

```powershell
python C:\Users\NPBB\fabrica\scripts\fabrica_projects_index\sync.py --repo-root C:\Users\NPBB\npbb --preflight --json
python C:\Users\NPBB\fabrica\scripts\fabrica_projects_index\sync.py --repo-root C:\Users\NPBB\npbb --sync-trigger handoff-prd-features
```

Validar `sync_runs` (status `success` ou `partial` aceite), `repo_root` coerente com o clone usado.

## Passo 5 — Git

- Revisar `git status` em **fabrica** e **npbb** separadamente.
- Um ou dois commits focados (fabrica vs npbb), **sem** reset cego.
- Não incluir em commit ficheiros de sessão tipo `PLAN1.md` ou `.cursor/plans` salvo pedido explícito.

## Se falhar

- Guardar stderr completo e o último JSON de proposta (se possível logar em ficheiro temporário) para depuração.
- Verificar se o modelo ignorou `candidate_feature_plan` ou reordenou features (quebra `depends_on`).
