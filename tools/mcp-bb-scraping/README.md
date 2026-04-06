# MCP - Pipeline de scraping e indicadores BB

Projeto para coletar posts de Instagram/X/TikTok com Playwright, gerar indicadores tabulados e produzir texto executivo sobre mencoes ao Banco do Brasil.

## Visao geral
- Scrape multi-plataforma (IG/X/TikTok) com login manual quando necessario.
- Instagram: gera posts enriquecidos, indicadores tabulados e relatorio deterministico automaticamente (Python).
- Interpretacao opcional via IA usando o indicadores.json.
- Saidas em CSV com separador ";" e BOM (Excel pt-BR).

## Requisitos
- Node.js + npm
- Python 3 (para scripts em `report/` e `generate_report.py`)
- Playwright browsers: `npx playwright install`

## Instalacao
```bash
npm install
npx playwright install
```

Dependencias Python (scripts em `report/` e `generate_report.py`):
```bash
pip install -r requirements.txt
```

## Python venv (opcional)
Dentro do monorepo NPBB, o `.venv` desta pasta fica **gitignored**. Crie e ative localmente:

PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Desativar:
```powershell
deactivate
```

Para criar o venv do zero (se precisar):
```powershell
python -m venv .venv
```

Depois de ativar o venv, instale as dependencias:
```powershell
pip install -r requirements.txt
```

## Autenticacao (opcional)
Quando a plataforma exigir login, gere o `storageState`:

```bash
npm run auth:ig
npm run auth:x
npm run auth:tiktok
```

Opcoes extras:
- CDP (Chrome ja aberto): `npm run auth:tiktok -- --cdp http://127.0.0.1:9222`
- Perfil local do Chrome: `npm run auth:tiktok -- --chrome-user-data-dir "C:\\Users\\SEU_USUARIO\\AppData\\Local\\Google\\Chrome\\User Data" --chrome-profile-dir Default`

Os arquivos ficam em `auth/*.json` e nao fazem parte dos dados coletados.

## TikTok: captcha e transferencia de cookies
O TikTok pode exigir captcha. Nesses casos, o scraping precisa rodar em modo visivel (`--headful`) para um humano resolver o desafio.

Fluxo recomendado quando voce ja esta logado no Chrome comum e quer transferir cookies para o Playwright:

1) Feche todas as janelas do Chrome.
2) Copie o perfil local e gere o storageState:
```powershell
npm run auth:tiktok -- --chrome-user-data-dir "C:\\Users\\SEU_USUARIO\\AppData\\Local\\Google\\Chrome\\User Data" --chrome-profile-dir Default
```
3) O browser vai abrir em modo visivel. Se aparecer captcha, resolva manualmente.
4) Volte ao terminal e pressione ENTER para salvar em `auth/tiktok_state.json`.
5) Rode o scrape:
```powershell
npm run scrape -- --profile italotferreira --no-x --no-ig --max 400 --out out
```

Se o captcha aparecer durante o scrape (ou os videos nao carregarem), rode o scraping em modo headful:
```powershell
npm run scrape -- --profile italotferreira --no-x --no-ig --max 400 --out out --headful
```
Resolva o captcha na janela aberta e aguarde o processo terminar.

## Uso rapido (scrape)
```bash
npm run scrape -- --profile <handle> --max 150 --since 2024-01-01 --until 2024-01-31 --out out
```

Exemplos:
```bash
npm run scrape -- --profile tainahinckel --no-x --no-tiktok --max 400 --out out
npm run scrape -- --no-ig --max 50 --out out
npm run scrape -- --all-athletes --no-x --no-tiktok --since 2026-02-01 --until 2026-02-15 --out out
```

## Execucao em lote (todos os atletas)
Comando recomendado para Instagram (todos os handles do `config/instagram_handles.csv`):
```bash
npm run scrape -- --all-athletes --no-x --no-tiktok --since 2026-02-01 --until 2026-02-15 --out out
```

Filtro opcional de status no lote:
```bash
npm run scrape -- --all-athletes --all-status confirmed,needs_confirmation --no-x --no-tiktok --since 2026-02-01 --until 2026-02-15 --out out
```

Regras do lote:
- `--until` e inclusivo (considera ate `23:59:59.999` da data informada).
- Sem `--all-status`, o lote ignora apenas linhas com status `alias` e `missing_handle`.
- Cada atleta roda em sequencia e grava os artefatos na respectiva pasta `out/<dir>/`.

## Saidas e pastas
- `--out` define a pasta base.
- O app cria `out/<dir>/`, onde `<dir>` = nome do atleta (quando existe em `config/instagram_handles.csv`) ou o handle.
- Ex: `--profile ronygomes` -> `out/rony_gomes/` (nome do atleta).
- Para controlar a pasta final, passe `--out out/<dir>` com o nome exato.

## Pipeline completo
Nota: `<dir>` = nome do atleta (quando existe em `config/instagram_handles.csv`) ou o handle.

1) Scrape (gera CSVs em `out/<dir>/`):
```bash
npm run scrape -- --profile <handle> --since 2024-01-01 --until 2024-01-31 --out out
```

2) Indicadores tabulados:
- Executa automaticamente no fim do scraping do Instagram (requer Python no PATH).
- Para rodar manualmente:
```bash
python report/append_indicator.py --handle <handle> --csv "out/<dir>/<arquivo_posts>.csv" --out "out/<dir>/indicadores_<handle>.csv"
```

3) Relatorio deterministico:
- Executa automaticamente no fim do scraping do Instagram (requer Python + pandas).
- Para rodar manualmente:
```bash
python generate_report.py --file "out/<dir>/<arquivo_posts>.csv" --user "<handle>" --out "out/<dir>"
```
Opcional: `--since "YYYY-MM-DD"` para forcar recorte. Se omitido, usa o inicio da base.

4) Interpretacao por IA (opcional):
```bash
python report/interpret_indicators.py --input "out/<dir>/indicadores.json" --out "out/<dir>" --provider openai --user "@<handle>"
```

Sem IA (mock):
```bash
python report/interpret_indicators.py --input "out/<dir>/indicadores.json" --out "out/<dir>" --provider mock --user "@<handle>"
```
Observacao: se voce passar `out/<handle>/indicadores.json` e a pasta real for `out/<dir>`, o script tenta resolver automaticamente.

5) Consolidacao para BI (opcional):
```bash
python report/consolidate_indicators.py
```

## Principais saidas
- `out/<dir>/posts_<handle>.csv`: consolidado multi-plataforma.
- `out/<dir>/instagram_posts_<handle>.csv`: posts IG basicos.
- `out/<dir>/<nome>_<handle>_posts.csv`: posts IG enriquecidos (ou `out/<dir>/<handle>_posts.csv`).
- `out/<dir>/indicadores_<handle>.csv`: 1 linha com indicadores.
- `out/<dir>/indicadores_bb_por_mes_<handle>.csv`: serie mensal de mencoes BB.
- `out/<dir>/summary_<handle>.csv`, `out/<dir>/top_hashtags_bb_<handle>.csv`, `out/<dir>/top_mentions_bb_<handle>.csv`.
- `out/<dir>/run_<handle>.csv` e `out/<dir>/run_<handle>.log`: log da execucao.
- `out/<dir>/texto_relatorio.md`, `out/<dir>/indicadores.json` e `out/<dir>/tabelas.md` (quando o relatorio deterministico roda).

## Flags principais (scrape)
- `--profile <handle>` / `--perfil <handle>`
- `--max <n>` | `--since YYYY-MM-DD` | `--until YYYY-MM-DD` | `--out <dir>`
- `--all-athletes` (roda um perfil por linha em `config/instagram_handles.csv`, ignorando `alias` e `missing_handle`)
- `--all-status <csv>` (opcional no batch; ex: `confirmed,needs_confirmation`)
- `--headful` | `--debug` | `--cdp <url>`
- `--no-ig` | `--no-x` | `--no-tiktok`
- `--ig-url` | `--x-url` | `--tiktok-url`
- `--auth-ig` | `--auth-x` | `--auth-tiktok`
- `--bb-aliases <lista>` (ex: `#squadbb,#tamojuntobb`)

## Timeouts
- Nao existe timeout global de execucao no pipeline (um lote pode durar varias horas).
- `--timeout <ms>` controla apenas timeout por acao/navegacao do Playwright (default: `30000`).
- Se a rede/plataforma estiver lenta, aumente `--timeout` (ex: `--timeout 120000`).
- Se voce viu timeout de ~2 horas em uma ferramenta externa, isso e limite do runner externo, nao da CLI do projeto.

## Variaveis de ambiente
- `PIPELINE_ROOT` ou `MCP_ROOT`: sobrescreve a raiz do projeto (subtree/submodule).
- `OPENAI_API_KEY` (obrigatorio para `--provider openai`)
- `OPENAI_MODEL`, `OPENAI_BASE_URL`, `OPENAI_ENDPOINT` (opcionais)
- `OPENAI_TIMEOUT`, `OPENAI_RETRIES`, `OPENAI_RETRY_BACKOFF`, `OPENAI_MAX_OUTPUT_TOKENS` (opcionais)

## Estrutura do repo
- `src/`: scraper Playwright e writers CSV.
- `report/`: indicadores e interpretacao.
- `generate_report.py`: relatorio deterministico.
- `config/instagram_handles.csv`: mapeia handle -> nome (usado no nome do arquivo enriquecido).
- `docs/`: schemas de QA.

## Compliance
- Nao contorna login/captcha/anti-bot.
- Login sempre manual; `auth/*.json` guarda apenas storageState.
