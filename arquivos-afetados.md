# Arquivos Afetados - Boundary NPBB -> Fabrica Canonica

## npbb - estado atual

| Arquivo ou superficie | Papel hoje | Estado atual |
|-----------------------|------------|--------------|
| **AGENTS.md** | Contrato operacional do repo | Alinhado. O indice derivado pertence ao runtime da Fabrica e usa `FABRICA_PROJECTS_DATABASE_URL`. |
| **README.MD** | Manual operacional do produto | Alinhado. A CLI canonica para sync e operacao do framework e a do clone irmao `C:\\Users\\NPBB\\fabrica`. |
| **tests/test_criar_projeto.py** | Guarda do scaffold local | Alinhado. Nao importa sync/schema local nem referencia `openclaw_*`. |
| **tests/test_fabrica_boundary.py** | Guarda de regressao do boundary | Ativo. Faz guarda de ausencia das superficies locais removidas e bloqueia referencias ativas a wrappers/tokens legados. |
| **.gitignore** | Higiene de artefatos locais | Mantem `.openclaw/openclaw-projects.sqlite` apenas como artefato local ignorado. |
| **.openclaw/.gitkeep** | Ancora da pasta local | Mantido. A pasta pode existir para artefatos locais, mas nao e fonte de verdade nem read model canonico. |

## npbb - superficies removidas do boundary

| Superficie | Estado |
|------------|--------|
| **bin/apply-openclaw-projects-pg-schema.sh** | Removido do repo de produto; nao deve voltar. |
| **bin/ensure-openclaw-projects-index-runtime.sh** | Removido do repo de produto; nao deve voltar. |
| **bin/mirror-openclaw-projects-sqlite-to-pg.sh** | Removido do repo de produto; nao deve voltar. |
| **bin/sync-openclaw-projects-db.sh** | Removido do repo de produto; nao deve voltar. |
| **scripts/openclaw_projects_index/*** | Removido do repo de produto; schema e sync pertencem a `..\\fabrica`. |
| **tests/test_openclaw_projects_index.py** | Removido; o `npbb` nao valida mais um indice proprio. |
| **.openclaw/openclaw-projects.sqlite** | Artefato derivado local. Pode existir no disco, mas apenas ignorado; nao pode aparecer em `git ls-files`. |

## fabrica - superficie canonica

| Arquivo ou superficie | Papel hoje |
|-----------------------|------------|
| **C:\\Users\\NPBB\\fabrica\\scripts\\fabrica_projects_index\\schema_postgres.sql** | Schema canonico unico do indice. |
| **C:\\Users\\NPBB\\fabrica\\scripts\\fabrica_projects_index\\sync.py** | Sync canonico Markdown -> Postgres. |
| **C:\\Users\\NPBB\\fabrica\\scripts\\fabrica_projects_index\\README.md** | Manual operacional canonico do indice. |
| **C:\\Users\\NPBB\\fabrica\\tests\\test_fabrica_projects_index_contract.py** | Guarda do boundary canonico no framework. |
| **C:\\Users\\NPBB\\fabrica\\scripts\\fabrica_core\\cli.py** | Entrypoint canonico para operar o framework a partir do `npbb`. |

## Conclusao

- Disputa de schema resolvida no `npbb`: o produto nao carrega mais schema proprio do indice.
- O contrato operacional local e:
  - `PROJETOS/**/*.md` e a fonte de verdade.
  - schema e sync do indice pertencem ao clone irmao `fabrica`.
  - `FABRICA_PROJECTS_DATABASE_URL` e a variavel operacional do read model.
- O boundary fica protegido por guards de ausencia de superficie e por varredura de referencias ativas nos docs do produto.
- Fora de escopo desta rodada: shims legados ainda existentes dentro do repo `fabrica`.
