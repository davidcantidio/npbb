# Arquivos Afetados - Migração para Fábrica Canônica

## npbb — Arquivos afetados (ainda carregam framework próprio)

| Arquivo | Papel hoje | Por que está afetado |
|---------|------------|----------------------|
| **AGENTS.md** | Contrato operacional do repo | Declara o índice `.openclaw/openclaw-projects.sqlite` como estado operacional do npbb, conflitando com a fábrica como framework canônico. |
| **bin/sync-openclaw-projects-db.sh** | Entrypoint de sync do produto | Aponta diretamente para a implementação local em `npbb/scripts/openclaw_projects_index/sync.py`. |
| **bin/apply-openclaw-projects-pg-schema.sh** | Aplicação de schema local | Continua tratando o schema do npbb como fonte aplicável, em vez de consumir apenas o schema canônico da fábrica. |
| **scripts/openclaw_projects_index/sync.py** | Implementação local do índice/sync | Principal arquivo com responsabilidade misturada: reimplementa o framework dentro do repo de produto. |
| **scripts/openclaw_projects_index/schema_postgres.sql** | Schema local do índice | Duplica a responsabilidade de modelagem estrutural, que deveria viver só na fábrica. |
| **scripts/openclaw_projects_index/domain.py** | Parser/classificação/utilitários do índice | Mantém lógica de framework embutida no produto; risco de divergência com a implementação canônica. |
| **scripts/openclaw_projects_index/mirror_sqlite_to_postgres.py** | Migração/compatibilidade local | Prolonga a posse local do pipeline de índice e reforça o acoplamento ao stack legado. |
| **tests/test_openclaw_projects_index.py** | Suite de teste do índice local | Legitima e protege uma segunda implementação ativa do framework. |
| **tests/test_criar_projeto.py** | Teste de integração local | Importa o sync local do npbb, amarrando o fluxo do produto ao framework duplicado. |
| **PROJETOS/COMUM/INVENTARIO-TECNICO-FRAMEWORK-OPENCLAW.md** | Inventário técnico ativo | Documenta `openclaw_projects_index` como núcleo obrigatório dentro do npbb. |
| **scripts/fabrica_domain/src/fabrica_domain/service.py** | Domínio local no repo de produto | Coloca regra de domínio/framework dentro do npbb (deveria ser consumido da fábrica). |
| **scripts/fabrica_domain/src/fabrica_domain/normative_chain.py** | Cadeia normativa local | Regra normativa vivendo no produto cria risco de drift. |
| **tests/test_fabrica_domain_gov_ids.py** | Testes do domínio local | Protege superfície de domínio mantida dentro do npbb. |

---

## fabrica — Arquivos afetados (definem a superfície canônica)

| Arquivo | Papel hoje | Por que está afetado |
|---------|------------|----------------------|
| **README.md** | Contrato do repo framework | Afirma a fábrica como fonte canônica, mas o npbb ainda mantém implementação paralela. |
| **scripts/fabrica_projects_index/sync.py** | Sync canônico do framework | Implementação que deveria concentrar toda evolução do índice (existe duplicidade com npbb). |
| **scripts/fabrica_projects_index/schema_postgres.sql** | Schema canônico | Fica em disputa enquanto o npbb carrega schema local próprio. |
| **scripts/fabrica_projects_index/README.md** | Manual operacional canônico | Documenta corte para `fabrica_*`, mas entra em conflito com documentação do npbb. |
| **tests/test_fabrica_projects_index_contract.py** | Teste de contrato canônico | Valida remoção de `openclaw_*`, mas npbb ainda usa essas superfícies. |
| **scripts/fabrica_core/cli.py** | CLI canônica da Fábrica | Deveria orquestrar o framework, mas perde autoridade por causa dos wrappers locais do npbb. |
| **scripts/fabrica_domain/src/fabrica_domain/service.py** | Serviço de domínio canônico | Divide responsabilidade com a cópia local do npbb. |
| **scripts/fabrica_domain/src/fabrica_domain/normative_chain.py** | Cadeia normativa canônica | Deveria ser a única regra normativa viva, mas coexistem duas. |

---

**Observação:** Este arquivo pode ser usado como base para um plano de refatoração ou para acompanhar o progresso da migração.