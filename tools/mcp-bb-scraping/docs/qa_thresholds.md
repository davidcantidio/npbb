# QA thresholds

Arquivo de configuracao:
- `config/qa_thresholds.json`

Campos:
- `min_posts`: minimo de posts para considerar a base suficiente.
- `coverage_min_pct`: thresholds minimos por metrica (`likes`, `comments`, `views`).

Overrides via CLI (interpretador):
- `--qa-config <path>`: caminho do arquivo de thresholds.
- `--min-posts <n>`: override do minimo de posts.
- `--min-coverage-likes <pct>`: override da cobertura minima de likes.
- `--min-coverage-comments <pct>`: override da cobertura minima de comments.
- `--min-coverage-views <pct>`: override da cobertura minima de views.

Exemplo:
python report/interpret_indicators.py --input out/indicadores.json --user @exemplo --min-posts 20 --min-coverage-likes 50
