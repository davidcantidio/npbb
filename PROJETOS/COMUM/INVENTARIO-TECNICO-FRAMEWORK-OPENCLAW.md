# Inventário Técnico do Framework OpenClaw

Este documento descreve, em linguagem simples, o que compõe o framework OpenClaw neste repositório. O foco aqui é o framework em si: regras, modelos de documento, scripts, skills, wrappers de operação, runtime de apoio, testes e meta-projetos usados para desenhar, provar e migrar o próprio framework.

Não entram no escopo deste inventário os projetos consumidores do framework, arquivos temporários, caches, diretórios de revisão local e artefatos soltos que não fazem parte da superfície operacional oficial.

## Como ler este inventário

- `Obrigatório`: deve ir junto quando você clonar o framework para outro repositório.
- `Opcional`: ajuda em operação, validação, automação, host ou prova do framework, mas não é o miolo mínimo.
- `Excluir`: existe no repositório por histórico, referência ou compatibilidade, mas não deve entrar no pacote extraído do framework.

## Fonte usada para montar a lista

- A lista oficial deste documento foi fechada a partir de `git ls-files`.
- Em outras palavras: só entram aqui os arquivos que estão versionados no Git dentro do escopo combinado.
- Pastas locais não versionadas podem existir no worktree, mas não entram como parte oficial do pacote extraível.

## 1. PROJETOS/COMUM

Esta pasta é o coração documental do framework. Ela guarda as regras comuns, os roteiros de conversa, os modelos de arquivo e os textos que explicam como o fluxo deve funcionar.

| Arquivo                                      | Classificação | O que faz                                                                                                             | Quando você olha para ele                                                                  | Do que ele depende ou com o que conversa                                                                              |
| -------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `boot-prompt.md`                             | Obrigatório   | É o ponto de partida do fluxo autônomo do framework. Ele orienta como descobrir o próximo passo sem inventar atalhos. | Você lê quando quer iniciar a operação do framework sem escolher manualmente a etapa.      | Conversa com `GOV-FRAMEWORK-MASTER.md`, `SESSION-MAPA.md` e os artefatos do projeto ativo.                            |
| `GOV-AUDITORIA-FEATURE.md`                   | Obrigatório   | Define as regras para auditar uma feature inteira.                                                                    | Você usa quando precisa saber como a auditoria de feature deve acontecer.                  | Conversa com `SESSION-AUDITAR-FEATURE.md`, `TEMPLATE-AUDITORIA-FEATURE.md` e `AUDIT-LOG.md` dos projetos.             |
| `GOV-AUDITORIA.md`                           | Obrigatório   | Define as regras gerais de auditoria no framework.                                                                    | Você lê quando quer entender o padrão comum de auditoria.                                  | Conversa com os templates e sessões de auditoria.                                                                     |
| `GOV-BRANCH-STRATEGY.md`                     | Obrigatório   | Explica como o framework espera o uso de branches.                                                                    | Você consulta quando vai alinhar trabalho em Git com o processo documental.                | Conversa com `GOV-COMMIT-POR-TASK.md` e com a disciplina de execução por task.                                        |
| `GOV-COMMIT-POR-TASK.md`                     | Obrigatório   | Define a regra de registrar trabalho em commits pequenos e ligados a tasks.                                           | Você olha quando vai executar ou revisar uma task.                                         | Conversa com `TEMPLATE-TASK.md`, `SESSION-IMPLEMENTAR-US.md` e a estratégia de branch.                                |
| `GOV-DECISOES.md`                            | Obrigatório   | Define como decisões relevantes devem ser registradas.                                                                | Você usa quando uma escolha muda rumo, escopo ou interpretação.                            | Conversa com `AUDIT-LOG.md`, PRD, feature e outros artefatos de governança.                                           |
| `GOV-FEATURE.md`                             | Obrigatório   | Explica o que uma feature precisa conter e como ela se comporta no fluxo.                                             | Você lê quando vai decompor PRD em features ou revisar uma feature.                        | Conversa com `TEMPLATE-FEATURE.md`, `SESSION-DECOMPOR-PRD-EM-FEATURES.md` e `SESSION-AUDITAR-FEATURE.md`.             |
| `GOV-FRAMEWORK-MASTER.md`                    | Obrigatório   | É a regra-mãe do framework. Diz qual é a estrutura canônica, quais artefatos existem e como eles se relacionam.       | Você abre quando precisa resolver dúvida estrutural sobre o framework.                     | Conversa com praticamente toda a pasta `PROJETOS/COMUM`, com `scripts/criar_projeto.py` e com as skills `openclaw-*`. |
| `GOV-INTAKE.md`                              | Obrigatório   | Define como um intake deve ser escrito e aprovado.                                                                    | Você consulta quando vai criar ou revisar a entrada inicial de um projeto.                 | Conversa com `TEMPLATE-INTAKE.md` e `SESSION-CRIAR-INTAKE.md`.                                                        |
| `GOV-ISSUE-FIRST.md`                         | Obrigatório   | Registra as regras do fluxo legado baseado em issue-first.                                                            | Você olha quando precisa entender compatibilidade com material mais antigo.                | Conversa com `LEGADO/` e com projetos que ainda carregam histórico issue-first.                                       |
| `GOV-PRD.md`                                 | Obrigatório   | Define o que um PRD pode e não pode fazer.                                                                            | Você lê quando vai criar, revisar ou corrigir um PRD.                                      | Conversa com `TEMPLATE-PRD.md`, `PROMPT-INTAKE-PARA-PRD.md` e `SPEC-PIPELINE-PRD-SEM-FEATURES.md`.                    |
| `GOV-SCRUM.md`                               | Obrigatório   | Consolida limites de cadência, handoff e disciplina de execução.                                                      | Você consulta quando precisa alinhar o trabalho diário com o método do framework.          | Conversa com sessões, tarefas, auditorias e regras de sprint.                                                         |
| `GOV-SPRINT-LIMITES.md`                      | Obrigatório   | Registra os limites usados para sprints no material legado.                                                           | Você usa quando precisa ler ou migrar conteúdo antigo.                                     | Conversa com `LEGADO/` e com histórico anterior ao formato atual.                                                     |
| `GOV-USER-STORY.md`                          | Obrigatório   | Define como uma user story deve ser escrita, quebrada e encerrada.                                                    | Você lê quando vai decompor feature em user stories ou revisar execução.                   | Conversa com `TEMPLATE-USER-STORY.md`, `TEMPLATE-TASK.md` e `SESSION-DECOMPOR-FEATURE-EM-US.md`.                      |
| `GOV-WORK-ORDER.md`                          | Obrigatório   | Explica a ordem prática do trabalho no framework.                                                                     | Você usa quando quer confirmar qual artefato vem antes de qual outro.                      | Conversa com `boot-prompt.md` e com as sessões `SESSION-*`.                                                           |
| `PRD-ADAPTACAO-FEATURE-FIRST.md`             | Obrigatório   | Registra o racional da mudança para o fluxo feature-first.                                                            | Você lê quando quer entender a intenção por trás da estrutura atual.                       | Conversa com `GOV-FRAMEWORK-MASTER.md` e com os meta-projetos de migração.                                            |
| `PROMPT-AUDITORIA-FRAMEWORK.md`              | Obrigatório   | Dá o texto-base para auditar o próprio framework.                                                                     | Você consulta quando a auditoria recai sobre o framework e não sobre um produto.           | Conversa com `GOV-AUDITORIA.md` e com meta-projetos como `OPENCLAW-MIGRATION`.                                        |
| `PROMPT-AUDITORIA.md`                        | Obrigatório   | Dá o texto-base para uma auditoria comum.                                                                             | Você usa para manter consistência de tom e cobertura na auditoria.                         | Conversa com `SESSION-AUDITAR-FEATURE.md` e templates de auditoria.                                                   |
| `PROMPT-FEATURE-PARA-USER-STORIES.md`        | Obrigatório   | Ensina como transformar uma feature em user stories.                                                                  | Você abre na etapa de decomposição da feature.                                             | Conversa com `SESSION-DECOMPOR-FEATURE-EM-US.md` e `GOV-USER-STORY.md`.                                               |
| `PROMPT-INTAKE-PARA-PRD.md`                  | Obrigatório   | Ensina como transformar um intake em PRD.                                                                             | Você usa logo após a etapa de intake.                                                      | Conversa com `SESSION-CRIAR-PRD.md` e `GOV-PRD.md`.                                                                   |
| `PROMPT-MONOLITO-PARA-INTAKE.md`             | Obrigatório   | Ensina como reduzir um problema grande demais até virar um intake tratável.                                           | Você usa quando o contexto está grande, confuso ou espalhado.                              | Conversa com `SPEC-ANTI-MONOLITO.md` e `SESSION-REFATORAR-MONOLITO.md`.                                               |
| `PROMPT-PRD-PARA-FEATURES.md`                | Obrigatório   | Ensina como quebrar um PRD em features.                                                                               | Você consulta na passagem de PRD para backlog estruturado.                                 | Conversa com `SESSION-DECOMPOR-PRD-EM-FEATURES.md` e `GOV-FEATURE.md`.                                                |
| `PROMPT-US-PARA-TASKS.md`                    | Obrigatório   | Ensina como transformar uma user story em tasks.                                                                      | Você usa quando precisa sair de planejamento para execução concreta.                       | Conversa com `SESSION-DECOMPOR-US-EM-TASKS.md` e `TEMPLATE-TASK.md`.                                                  |
| `RESUMO-ADEQUACAO-FRAMEWORK.md`              | Obrigatório   | Resume o ajuste do framework para o modelo atual.                                                                     | Você lê quando quer uma visão curta da adaptação sem entrar em todo o histórico.           | Conversa com os documentos de governança e migração.                                                                  |
| `RUNTIME-WINDOWS.md`                         | Opcional      | Explica como preparar e usar o framework no Windows.                                                                  | Você consulta quando o ambiente local de trabalho é Windows.                               | Conversa com `requirements.txt`, scripts de teste e operação com Postgres local.                                      |
| `SESSION-AUDITAR-FEATURE.md`                 | Obrigatório   | É o roteiro de conversa para auditar uma feature.                                                                     | Você abre quando chega a hora de decidir se a feature passou, segurou ou precisa correção. | Conversa com `GOV-AUDITORIA-FEATURE.md`, templates de auditoria e `AUDIT-LOG.md`.                                     |
| `SESSION-CLARIFICAR-INTAKE.md`               | Obrigatório   | É o roteiro para limpar dúvidas antes de congelar o entendimento do intake.                                           | Você usa quando o intake ainda está ambíguo.                                               | Conversa com `GOV-INTAKE.md`, `TEMPLATE-INTAKE.md` e PRD futuro.                                                      |
| `SESSION-CRIAR-INTAKE.md`                    | Obrigatório   | É o roteiro de conversa para criar ou revisar intake.                                                                 | Você abre no começo de um projeto novo.                                                    | Conversa com `GOV-INTAKE.md` e `TEMPLATE-INTAKE.md`.                                                                  |
| `SESSION-CRIAR-PRD.md`                       | Obrigatório   | É o roteiro de conversa para criar ou revisar PRD.                                                                    | Você usa depois do intake aprovado.                                                        | Conversa com `GOV-PRD.md` e `TEMPLATE-PRD.md`.                                                                        |
| `SESSION-DECOMPOR-FEATURE-EM-US.md`          | Obrigatório   | É o roteiro para quebrar uma feature em user stories.                                                                 | Você abre no planejamento intermediário.                                                   | Conversa com `PROMPT-FEATURE-PARA-USER-STORIES.md` e `GOV-USER-STORY.md`.                                             |
| `SESSION-DECOMPOR-PRD-EM-FEATURES.md`        | Obrigatório   | É o roteiro para quebrar o PRD em features.                                                                           | Você usa quando o PRD já está maduro e precisa virar backlog.                              | Conversa com `PROMPT-PRD-PARA-FEATURES.md` e `GOV-FEATURE.md`.                                                        |
| `SESSION-DECOMPOR-US-EM-TASKS.md`            | Obrigatório   | É o roteiro para quebrar uma user story em tasks executáveis.                                                         | Você abre na preparação da execução.                                                       | Conversa com `PROMPT-US-PARA-TASKS.md` e `TEMPLATE-TASK.md`.                                                          |
| `SESSION-IMPLEMENTAR-US.md`                  | Obrigatório   | É o roteiro de execução de user story.                                                                                | Você usa durante o trabalho prático da task e do fechamento da story.                      | Conversa com `GOV-USER-STORY.md`, `TEMPLATE-IMP-SESSAO.md`, feature, user story e tasks.                              |
| `SESSION-MAPA.md`                            | Obrigatório   | É o índice interativo das sessões do framework.                                                                       | Você abre quando quer descobrir qual wrapper usar em seguida.                              | Conversa com `boot-prompt.md` e com todas as outras `SESSION-*`.                                                      |
| `SESSION-PLANEJAR-PROJETO.md`                | Obrigatório   | É o roteiro para planejar o projeto inteiro ou um pedaço dele.                                                        | Você usa quando o projeto já tem base suficiente para virar backlog estruturado.           | Conversa com PRD, `GOV-FEATURE.md`, `GOV-USER-STORY.md` e sessões de decomposição.                                    |
| `SESSION-REFATORAR-MONOLITO.md`              | Obrigatório   | É o roteiro para cortar escopo grande demais em partes menores.                                                       | Você abre quando o material ficou grande, confuso ou travado.                              | Conversa com `SPEC-ANTI-MONOLITO.md` e `PROMPT-MONOLITO-PARA-INTAKE.md`.                                              |
| `SESSION-REMEDIAR-HOLD.md`                   | Obrigatório   | É o roteiro para tratar um hold decidido em revisão ou auditoria.                                                     | Você usa quando algo foi bloqueado e precisa voltar com correção orientada.                | Conversa com relatórios de auditoria, `AUDIT-LOG.md` e sessões de execução/revisão.                                   |
| `SESSION-REVISAR-US.md`                      | Obrigatório   | É o roteiro para revisão pós-execução de user story.                                                                  | Você abre quando a story chegou em `ready_for_review`.                                     | Conversa com `SESSION-IMPLEMENTAR-US.md`, `GOV-USER-STORY.md` e os relatórios de revisão.                             |
| `SPEC-ANTI-MONOLITO.md`                      | Obrigatório   | Explica como identificar e tratar documentos ou escopos grandes demais.                                               | Você consulta quando a estrutura começa a ficar pesada ou ambígua.                         | Conversa com `SESSION-REFATORAR-MONOLITO.md`.                                                                         |
| `SPEC-EDITOR-ARTEFACTOS.md`                  | Obrigatório   | Explica como editar artefatos do framework sem quebrar o padrão.                                                      | Você lê quando vai atualizar documentos de governança ou backlog.                          | Conversa com templates e regras `GOV-*`.                                                                              |
| `SPEC-INDICE-PROJETOS-POSTGRES.md`           | Obrigatório   | Descreve o modelo derivado em Postgres que espelha os documentos em Markdown.                                         | Você consulta quando trabalha com sync, leitura operacional ou consultas estruturadas.     | Conversa com `scripts/fabrica_projects_index/`, `scripts/fabrica_domain/` e `bin/sync-fabrica-projects-db.sh`.        |
| `SPEC-PIPELINE-PRD-SEM-FEATURES.md`          | Obrigatório   | Deixa explícito que o PRD não é backlog e não deve misturar etapas posteriores.                                       | Você usa quando precisa evitar drift entre PRD e planejamento.                             | Conversa com `GOV-PRD.md` e com os prompts de decomposição.                                                           |
| `SPEC-RUNTIME-POSTGRES-MATRIX.md`            | Obrigatório   | Diz quando o sync com Postgres é obrigatório e o que fazer quando ele falha.                                          | Você abre quando o runtime do índice está ausente, quebrado ou defasado.                   | Conversa com `SPEC-INDICE-PROJETOS-POSTGRES.md` e `bin/ensure-fabrica-projects-index-runtime.sh`.                    |
| `SPEC-T1-ESTADO-ATUAL-FRAMEWORK-OPENCLAW.md` | Obrigatório   | Registra uma fotografia do estado atual esperado do framework.                                                        | Você consulta quando quer conferir o ponto de referência do framework.                     | Conversa com meta-projetos de migração e adequação.                                                                   |
| `SPEC-TASK-INSTRUCTIONS.md`                  | Obrigatório   | Explica como uma task deve virar instrução prática de execução.                                                       | Você lê quando quer manter tasks pequenas, claras e auditáveis.                            | Conversa com `TEMPLATE-TASK.md`, `SESSION-IMPLEMENTAR-US.md` e `GOV-COMMIT-POR-TASK.md`.                              |
| `TEMPLATE-AUDITORIA-FEATURE.md`              | Obrigatório   | É o molde para escrever um relatório de auditoria de feature.                                                         | Você usa ao formalizar o resultado da auditoria.                                           | Conversa com `GOV-AUDITORIA-FEATURE.md` e `SESSION-AUDITAR-FEATURE.md`.                                               |
| `TEMPLATE-AUDITORIA-LOG.md`                  | Obrigatório   | É o molde do log de auditoria do projeto.                                                                             | Você usa ao criar ou padronizar `AUDIT-LOG.md`.                                            | Conversa com relatórios, revisões e decisões.                                                                         |
| `TEMPLATE-AUDITORIA-RELATORIO.md`            | Obrigatório   | É o molde para relatórios formais de auditoria.                                                                       | Você consulta quando precisa escrever um parecer estruturado.                              | Conversa com `GOV-AUDITORIA.md` e sessões de auditoria.                                                               |
| `TEMPLATE-ENCERRAMENTO.md`                   | Obrigatório   | É o molde para registrar o fechamento de um ciclo ou projeto.                                                         | Você usa no encerramento de uma frente de trabalho.                                        | Conversa com `SESSION-PLANEJAR-PROJETO.md` e com auditorias finais.                                                   |
| `TEMPLATE-FEATURE.md`                        | Obrigatório   | É o molde de uma feature.                                                                                             | Você usa ao criar uma nova feature a partir do PRD.                                        | Conversa com `GOV-FEATURE.md`.                                                                                        |
| `TEMPLATE-IMP-SESSAO.md`                     | Obrigatório   | É o molde do cabeçalho usado na sessão de implementação.                                                              | Você consulta quando vai executar uma task com rastreabilidade.                            | Conversa com `SESSION-IMPLEMENTAR-US.md` e com o gerador `generate_openclaw_framework_v4_imp_headers.py`.             |
| `TEMPLATE-INTAKE.md`                         | Obrigatório   | É o molde de intake.                                                                                                  | Você usa no nascimento de um projeto.                                                      | Conversa com `GOV-INTAKE.md` e `SESSION-CRIAR-INTAKE.md`.                                                             |
| `TEMPLATE-PRD.md`                            | Obrigatório   | É o molde de PRD.                                                                                                     | Você usa quando o intake já foi compreendido.                                              | Conversa com `GOV-PRD.md` e `SESSION-CRIAR-PRD.md`.                                                                   |
| `TEMPLATE-SCOPE-LEARN.md`                    | Obrigatório   | É o molde para registrar aprendizado de escopo sem bagunçar o backlog principal.                                      | Você usa quando descobre algo novo durante execução ou revisão.                            | Conversa com PRD, feature, user story e remediação.                                                                   |
| `TEMPLATE-TASK.md`                           | Obrigatório   | É o molde de task.                                                                                                    | Você usa na etapa final da decomposição antes da execução.                                 | Conversa com `GOV-USER-STORY.md`, `SPEC-TASK-INSTRUCTIONS.md` e `SESSION-DECOMPOR-US-EM-TASKS.md`.                    |
| `TEMPLATE-USER-STORY.md`                     | Obrigatório   | É o molde de user story.                                                                                              | Você usa ao quebrar uma feature em unidades menores de entrega.                            | Conversa com `GOV-USER-STORY.md` e `SESSION-DECOMPOR-FEATURE-EM-US.md`.                                               |


## 2. scripts/

Esta seção reúne o que gera projeto, materializa o índice derivado, expõe o domínio compartilhado e ajuda em validação local.

### 2.1 Itens centrais na raiz de `scripts/`

| Arquivo                                                 | Classificação | O que faz                                                                               | Quando você olha para ele                                                                  | Do que ele depende ou com o que conversa                                                               |
| ------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `scripts/criar_projeto.py`                              | Obrigatório   | Cria um novo projeto dentro de `PROJETOS/` já com o scaffold canônico preenchido.       | Você usa quando quer nascer um projeto novo sem montar tudo à mão.                         | Conversa com `PROJETOS/COMUM/`, especialmente `GOV-FRAMEWORK-MASTER.md`, templates e sessões.          |
| `scripts/generate_openclaw_framework_v4_imp_headers.py` | Opcional      | Gera arquivos `imp-N.md` prontos para uso ao lado das tasks do projeto de framework v4. | Você olha quando quer automatizar cabeçalhos de execução para o meta-projeto do framework. | Conversa com `TEMPLATE-IMP-SESSAO.md`, `SESSION-IMPLEMENTAR-US.md` e `PROJETOS/OPENCLAW-FRAMEWORK-V4`. |
| `scripts/run-pytest.ps1`                                | Opcional      | Roda os testes no Windows usando o ambiente esperado do repositório.                    | Você usa quando quer executar a suíte Python no Windows sem tropeçar em PATH errado.       | Conversa com `.venv`, `requirements.txt` e a pasta `tests/`.                                           |
| `scripts/run-pytest.sh`                                 | Opcional      | Roda os testes em Linux e macOS com a mesma ideia do script PowerShell.                 | Você usa para validar o repositório em ambiente Unix.                                      | Conversa com `requirements.txt` e `tests/`.                                                            |

### 2.2 `scripts/fabrica_projects_index/`

Esta pasta transforma os arquivos Markdown do framework e dos projetos em um espelho consultável em Postgres.

| Arquivo                                                                   | Classificação | O que faz                                                                                      | Quando você olha para ele                                                             | Do que ele depende ou com o que conversa                                                                                               |
| ------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `fabrica_projects_index/README.md`                                        | Obrigatório   | Explica como o índice funciona, como sincronizar e quais variáveis de ambiente ele usa.        | Você lê quando vai operar ou depurar o sync para Postgres.                            | Conversa com `SPEC-INDICE-PROJETOS-POSTGRES.md`, `bin/ensure-fabrica-projects-index-runtime.sh` e `bin/sync-fabrica-projects-db.sh`. |
| `fabrica_projects_index/build_local_pyyaml_wheel.py`                      | Opcional      | Monta um pacote local do `PyYAML` para deploys e smokes remotos.                               | Você usa quando precisa preparar dependência de forma reprodutível no runtime remoto. | Conversa com deploy remoto e com o bootstrap do índice.                                                                                |
| `fabrica_projects_index/chunk_documents.py`                               | Obrigatório   | Quebra documentos grandes em pedaços menores para busca e uso posterior com embeddings.        | Você olha quando quer preparar a camada de chunks do índice.                          | Conversa com `schema_postgres.sql` e com o banco Postgres.                                                                             |
| `fabrica_projects_index/domain.py`                                        | Obrigatório   | Reúne a leitura de frontmatter, classificação de caminhos e utilidades compartilhadas do sync. | Você usa quando precisa entender como o parser enxerga os arquivos Markdown.          | Conversa com `sync.py` e com a estrutura de `PROJETOS/`.                                                                               |
| `fabrica_projects_index/postgres_schema_util.py`                          | Obrigatório   | Centraliza a aplicação e o controle do schema Postgres.                                        | Você olha quando precisa aplicar ou validar o schema do índice.                       | Conversa com `schema_postgres.sql`, `sync.py` e `bin/apply-fabrica-projects-pg-schema.sh`.                                            |
| `fabrica_projects_index/requirements.txt`                                 | Obrigatório   | Mantém compatibilidade com chamadas antigas apontando para as dependências Python da raiz.     | Você consulta quando algum script ou automação pede esse caminho específico.          | Conversa com `requirements.txt` da raiz.                                                                                               |
| `fabrica_projects_index/requirements-postgres.txt`                        | Obrigatório   | Faz o mesmo papel do arquivo acima, mas com nome legado ligado ao Postgres.                    | Você usa quando uma automação antiga ainda aponta para esse nome.                     | Conversa com `requirements.txt` da raiz.                                                                                               |
| `fabrica_projects_index/__init__.py`                                      | Opcional      | Marca o pacote Python do índice e estabiliza imports internos.                                 | Você olha quando quer entender a superfície de import do pacote.                      | Conversa com `sync.py`, `domain.py` e `postgres_schema_util.py`.                                                                       |
| `fabrica_projects_index/schema_postgres.sql`                              | Obrigatório   | Define as tabelas, índices e extensões do índice operacional em Postgres.                      | Você abre quando precisa entender ou aplicar a estrutura do banco.                    | Conversa com `SPEC-INDICE-PROJETOS-POSTGRES.md`, `sync.py` e `bin/apply-fabrica-projects-pg-schema.sh`.                               |
| `fabrica_projects_index/sync.py`                                          | Obrigatório   | Varre `PROJETOS/**/*.md` e reconstrói o espelho operacional em Postgres.                       | Você usa quando precisa sincronizar a verdade em Markdown com o banco.                | Conversa com `domain.py`, `postgres_schema_util.py`, `schema_postgres.sql` e `FABRICA_PROJECTS_DATABASE_URL`.                         |
| `fabrica_projects_index/legacy/migrate_sqlite_embeddings_to_postgres.py`  | Opcional      | Migra embeddings antigos que ficaram em SQLite para o formato novo em Postgres.                | Você usa só em cenário de migração de legado.                                         | Conversa com `schema_postgres.sql` e o banco de destino.                                                                               |

### 2.3 `scripts/fabrica_domain/`

Esta pasta contém o pacote Python de domínio compartilhado, usado para ler o estado do framework e dos projetos sem acoplar tudo à camada do banco.

| Arquivo                                                          | Classificação | O que faz                                                                                  | Quando você olha para ele                                                          | Do que ele depende ou com o que conversa                                                               |
| ---------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `fabrica_domain/README.md`                                       | Obrigatório   | Explica a API pública do pacote, os erros esperados e o jeito certo de consumir o domínio. | Você lê quando quer integrar CLI, skill ou serviço ao domínio compartilhado.       | Conversa com `service.py`, `ports.py`, `persistence/postgres.py` e `SPEC-INDICE-PROJETOS-POSTGRES.md`. |
| `fabrica_domain/pyproject.toml`                                  | Obrigatório   | Define como empacotar e instalar o domínio como pacote Python.                             | Você usa quando vai instalar ou publicar o pacote localmente.                      | Conversa com `requirements.txt` da raiz e com `pip install -e`.                                        |
| `fabrica_domain/examples/minimal_consumer.py`                    | Opcional      | Mostra um consumidor mínimo do domínio em funcionamento.                                   | Você abre quando quer ver um exemplo direto, sem muita camada em volta.            | Conversa com o pacote `fabrica_domain` e com o repositório de leitura em memória ou Postgres.          |
| `fabrica_domain/src/fabrica_domain/__init__.py`                  | Obrigatório   | Expõe a superfície pública do pacote em um ponto de importação estável.                    | Você olha quando quer saber o que o pacote promete para fora.                      | Conversa com `service.py`, DTOs e erros.                                                               |
| `fabrica_domain/src/fabrica_domain/errors.py`                    | Obrigatório   | Define erros de domínio e persistência que o consumidor deve tratar.                       | Você consulta quando quer entender falhas esperadas do pacote.                     | Conversa com `service.py` e adaptadores de persistência.                                               |
| `fabrica_domain/src/fabrica_domain/gov_ids.py`                   | Obrigatório   | Normaliza identificadores `FEATURE-*` e `US-*` para comparar escopo sem depender de slugs. | Você usa quando precisa alinhar manifesto, pasta e rastreabilidade canônica.       | Conversa com `service.py`, `normative_chain.py` e validadores de rastreabilidade.                      |
| `fabrica_domain/src/fabrica_domain/normative_chain.py`           | Obrigatório   | Implementa a leitura da cadeia normativa e decide em que fase um projeto está.             | Você usa quando precisa bloquear ou liberar operações com base na fase documental. | Conversa com `PROJETOS/COMUM/`, com o repositório de leitura e com `normative_errors.py`.              |
| `fabrica_domain/src/fabrica_domain/normative_errors.py`          | Obrigatório   | Define o erro que representa bloqueio por regra normativa.                                 | Você olha quando quer tratar recusas do domínio de maneira clara.                  | Conversa com `normative_chain.py` e `service.py`.                                                      |
| `fabrica_domain/src/fabrica_domain/ports.py`                     | Obrigatório   | Define os contratos de leitura que um repositório precisa cumprir.                         | Você usa quando quer trocar a fonte de dados sem quebrar a API do domínio.         | Conversa com `service.py`, `persistence/postgres.py` e `persistence/memory_stub.py`.                   |
| `fabrica_domain/src/fabrica_domain/py.typed`                     | Obrigatório   | Marca o pacote como tipado para ferramentas Python.                                        | Você raramente olha diretamente para ele; ele existe para tooling.                 | Conversa com instaladores e verificadores de tipo.                                                     |
| `fabrica_domain/src/fabrica_domain/service.py`                   | Obrigatório   | Reúne a fachada principal do domínio e as operações públicas consumidas por fora.          | Você abre quando quer saber quais consultas o domínio oferece.                     | Conversa com `ports.py`, `normative_chain.py` e os adaptadores de persistência.                        |
| `fabrica_domain/src/fabrica_domain/persistence/__init__.py`      | Obrigatório   | Organiza a saída pública dos adaptadores de persistência.                                  | Você olha quando quer importar os adaptadores de forma estável.                    | Conversa com `postgres.py` e `memory_stub.py`.                                                         |
| `fabrica_domain/src/fabrica_domain/persistence/memory_stub.py`   | Obrigatório   | Fornece um repositório em memória para demonstração e testes simples.                      | Você usa quando quer exercitar o domínio sem Postgres.                             | Conversa com `ports.py` e exemplos locais.                                                             |
| `fabrica_domain/src/fabrica_domain/persistence/postgres.py`      | Obrigatório   | Implementa a leitura real a partir do índice operacional em Postgres.                      | Você usa quando quer consultar o estado materializado de verdade.                  | Conversa com `FABRICA_PROJECTS_DATABASE_URL`, `schema_postgres.sql` e `service.py`.                    |
| `fabrica_domain/tests/test_normative_chain.py`                   | Opcional      | Confere se a leitura da cadeia normativa funciona como esperado.                           | Você roda quando muda regra de fase ou gate.                                       | Conversa com `normative_chain.py`.                                                                     |
| `fabrica_domain/tests/test_postgres_repository.py`               | Opcional      | Confere se o adaptador Postgres lê o que promete ler.                                      | Você roda quando muda consulta ou contrato relacional.                             | Conversa com `persistence/postgres.py`.                                                                |
| `fabrica_domain/tests/test_service.py`                           | Opcional      | Confere a fachada pública do domínio.                                                      | Você roda quando muda o serviço ou a forma de montar resultados.                   | Conversa com `service.py` e `ports.py`.                                                                |
|                                                                  |               |                                                                                            |                                                                                    |                                                                                                        |
|                                                                  |               |                                                                                            |                                                                                    |                                                                                                        |

### 2.4 `scripts/session_logs/`

Esta pasta guarda o pipeline que transforma logs de sessão em JSON auditável.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `session_logs/README.md` | Opcional | Explica o pipeline de captura, geração e validação de traces de sessão. | Você lê quando quer registrar sessões de forma reprodutível. | Conversa com os schemas JSON e com os scripts desta mesma pasta. |
| `session_logs/build_trace.py` | Opcional | Constrói um trace final a partir de um capture manifest e, opcionalmente, de um transcript. | Você usa quando quer materializar uma sessão em arquivo auditável. | Conversa com `session_capture.schema.json`, `session_trace.schema.json` e `core.py`. |
| `session_logs/collect_traces.py` | Opcional | Processa vários captures de uma vez. | Você usa quando a coleta é feita em lote. | Conversa com `build_trace.py` e a pasta de inbox. |
| `session_logs/core.py` | Opcional | Centraliza a lógica compartilhada do pipeline de logs. | Você olha quando precisa entender a base comum usada pelos demais scripts. | Conversa com todos os outros arquivos de `session_logs/`. |
| `session_logs/session_capture.schema.json` | Opcional | Define o formato aceito para entrada de captura. | Você usa quando vai gerar captures válidos. | Conversa com `build_trace.py` e `collect_traces.py`. |
| `session_logs/session_trace.schema.json` | Opcional | Define o formato final do trace gerado. | Você consulta quando quer validar ou consumir o resultado. | Conversa com `build_trace.py` e `validate_trace.py`. |
| `session_logs/validate_trace.py` | Opcional | Valida se um trace gerado está no formato certo. | Você usa depois de gerar ou coletar traces. | Conversa com `session_trace.schema.json`. |

### 2.5 `scripts/framework_governance/`

Esta pasta reúne gates automáticos de rastreabilidade documental. Ela entra como parte oficial do framework porque já é citada como caminho canônico em governança, sessões, prompts, meta-projeto e testes.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `framework_governance/validate_us_traceability.py` | Obrigatório | Valida se uma user story fechou do jeito certo: tasks, commits e handoff de revisão precisam estar coerentes. | Você usa antes de marcar uma user story como pronta para revisão ou ao depurar por que ela falhou no gate. | Conversa com `PROJETOS/COMUM/`, com o histórico Git da cópia de trabalho e com `scripts/fabrica_projects_index/domain.py`. |
| `framework_governance/scan_us_traceability.py` | Obrigatório | Varre o repositório e roda o validador em todas as user stories que estão em `ready_for_review`. | Você usa em checagem mais ampla, CI ou revisão de lote. | Conversa com `validate_us_traceability.py`, com `PROJETOS/**/*.md` e com `scripts/fabrica_projects_index/domain.py`. |

### 2.6 `scripts/session_tools/`

Esta pasta reúne ferramentas pequenas usadas para apoiar a leitura mínima de artefatos grandes durante uma sessão.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `session_tools/read_file.py` | Obrigatório | Lê só o trecho relevante de um arquivo: começo, fim, faixa de linhas ou trecho perto de uma âncora. | Você usa quando quer inspecionar um artefato grande sem abrir o arquivo inteiro. | Conversa com `boot-prompt.md`, `SPEC-LEITURA-MINIMA-EVIDENCIA.md`, prompts de decomposição e sessões operacionais do framework. |

## 3. `.codex/skills/fabrica-*`

Estas skills traduzem as regras do framework para o ambiente do agente. Em cada skill há dois arquivos: o texto da skill e o arquivo de metadados do agente.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `.codex/skills/fabrica-autonomous/SKILL.md` | Obrigatório | Ensina o agente a operar de forma autônoma dentro das regras do framework. | Você lê quando quer entender o fluxo automático completo. | Conversa com `boot-prompt.md`, `SESSION-MAPA.md`, `GOV-FRAMEWORK-MASTER.md` e o índice de projetos. |
| `.codex/skills/fabrica-autonomous/agents/openai.yaml` | Obrigatório | Guarda os metadados que conectam a skill ao runtime do agente. | Você usa quando vai instalar, sincronizar ou validar a skill. | Conversa com scripts de instalação e verificação de skills. |
| `.codex/skills/fabrica-projects-index/SKILL.md` | Obrigatório | Ensina o agente a sincronizar e consultar o espelho de projetos em Postgres. | Você lê quando quer usar o read model operacional. | Conversa com `scripts/fabrica_projects_index/`, `scripts/fabrica_domain/` e `FABRICA_PROJECTS_DATABASE_URL`. |
| `.codex/skills/fabrica-projects-index/agents/openai.yaml` | Obrigatório | Guarda os metadados dessa skill de índice. | Você olha quando valida instalação e disponibilidade da skill. | Conversa com `install-codex-skills.sh`, `sync-openclaw-skills.sh` e testes de skill. |
| `.codex/skills/fabrica-router/SKILL.md` | Obrigatório | Ensina o agente a escolher o fluxo certo com base no estado do projeto. | Você usa quando quer roteamento determinístico de sessão. | Conversa com `SESSION-MAPA.md`, `GOV-FRAMEWORK-MASTER.md` e o domínio compartilhado. |
| `.codex/skills/fabrica-router/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de roteamento. | Você olha quando instala ou valida a suite de skills. | Conversa com os scripts de skill e com a própria skill. |
| `.codex/skills/fabrica-sandbox-external-repo/SKILL.md` | Opcional | Ensina o agente a trabalhar com um repositório externo dentro do sandbox. | Você usa quando o framework vai operar sobre um repositório de aplicação separado. | Conversa com `bootstrap-sandbox-git-project.sh` e com o deploy para sandbox. |
| `.codex/skills/fabrica-sandbox-external-repo/agents/openai.yaml` | Opcional | Guarda os metadados dessa skill opcional de repositório externo. | Você consulta quando instala ou sincroniza essa skill específica. | Conversa com scripts de instalação de skills. |
| `.codex/skills/fabrica-session-hold-remediation/SKILL.md` | Obrigatório | Ensina o agente a tratar situações de hold. | Você lê quando quer seguir o fluxo de remediação sem drift. | Conversa com `SESSION-REMEDIAR-HOLD.md`, auditorias e estado do índice. |
| `.codex/skills/fabrica-session-hold-remediation/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de remediação de hold. | Você usa em instalação e validação da suite. | Conversa com scripts e testes de skill. |
| `.codex/skills/fabrica-session-intake/SKILL.md` | Obrigatório | Ensina o agente a conduzir intake seguindo o padrão do framework. | Você usa no início do projeto. | Conversa com `SESSION-CRIAR-INTAKE.md`, `GOV-INTAKE.md` e `TEMPLATE-INTAKE.md`. |
| `.codex/skills/fabrica-session-intake/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de intake. | Você consulta quando instala ou depura a skill. | Conversa com scripts de skill. |
| `.codex/skills/fabrica-session-issue-execution/SKILL.md` | Obrigatório | Ensina o agente a executar o fluxo de implementação compatível com material legado de issue/review. | Você usa quando o projeto ainda depende desse wrapper legado. | Conversa com sessões locais antigas e com o índice de projetos. |
| `.codex/skills/fabrica-session-issue-execution/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de execução compatível. | Você consulta em instalação e checagem de paridade. | Conversa com os scripts de skill. |
| `.codex/skills/fabrica-session-issue-review/SKILL.md` | Obrigatório | Ensina o agente a revisar uma unidade no fluxo compatível com issue/review legado. | Você usa quando precisa revisar material ainda preso a esse fluxo. | Conversa com wrappers locais e com o domínio compartilhado. |
| `.codex/skills/fabrica-session-issue-review/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de revisão compatível. | Você usa na instalação e validação da skill. | Conversa com os scripts de skill. |
| `.codex/skills/fabrica-session-monolith-refactor/SKILL.md` | Obrigatório | Ensina o agente a reduzir contexto grande demais em partes menores. | Você usa quando o material ficou monolítico. | Conversa com `SESSION-REFATORAR-MONOLITO.md` e `SPEC-ANTI-MONOLITO.md`. |
| `.codex/skills/fabrica-session-monolith-refactor/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de refatoração de monolito. | Você consulta em instalação e validação. | Conversa com scripts de skill. |
| `.codex/skills/fabrica-session-phase-audit/SKILL.md` | Obrigatório | Ensina o agente a auditar uma fase ou feature. | Você usa quando quer aplicar o fluxo de auditoria no runtime do agente. | Conversa com `SESSION-AUDITAR-FEATURE.md`, templates de auditoria e índice. |
| `.codex/skills/fabrica-session-phase-audit/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de auditoria. | Você usa em instalação e testes de disponibilidade. | Conversa com scripts de skill. |
| `.codex/skills/fabrica-session-prd/SKILL.md` | Obrigatório | Ensina o agente a criar ou revisar PRD segundo o padrão do framework. | Você usa na passagem de intake para PRD. | Conversa com `SESSION-CRIAR-PRD.md`, `GOV-PRD.md` e `TEMPLATE-PRD.md`. |
| `.codex/skills/fabrica-session-prd/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de PRD. | Você consulta quando instala ou sincroniza a suite. | Conversa com scripts de skill. |
| `.codex/skills/fabrica-session-project-planning/SKILL.md` | Obrigatório | Ensina o agente a planejar projeto, features, user stories e tasks. | Você usa quando o projeto precisa virar backlog executável. | Conversa com `SESSION-PLANEJAR-PROJETO.md`, sessões de decomposição e o índice. |
| `.codex/skills/fabrica-session-project-planning/agents/openai.yaml` | Obrigatório | Guarda os metadados da skill de planejamento. | Você usa em instalação, sync e checagem da suite. | Conversa com scripts de skill e testes de paridade. |

## 4. `bin/`

Esta pasta concentra os wrappers de linha de comando usados para instalar, sincronizar, validar e operar o framework.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `bin/apply-fabrica-projects-pg-schema.sh` | Obrigatório | Aplica o schema Postgres do índice de projetos. | Você usa quando o banco ainda não recebeu a estrutura esperada. | Conversa com `schema_postgres.sql`, `FABRICA_PROJECTS_DATABASE_URL` e `psql`. |
| `bin/bootstrap-openclaw-projects-postgres.sh` | Obrigatório | Faz o bootstrap do runtime do índice em Postgres de ponta a ponta. | Você usa quando quer preparar o ambiente do índice com menos passos manuais. | Conversa com o preflight, aplicação de schema, sync e geração de chunks. |
| `bin/bootstrap-sandbox-git-project.sh` | Opcional | Clona ou atualiza um repositório de aplicação dentro do sandbox. | Você usa quando o runtime precisa atuar em um repo externo. | Conversa com variáveis de sandbox da aplicação e com deploy remoto. |
| `bin/check-openclaw-smoke.sh` | Opcional | Faz uma checagem rápida para provar que a superfície mínima do framework está funcionando. | Você usa quando quer um teste curto de sanidade do ambiente. | Conversa com `PROJETOS/OC-SMOKE-SKILLS`, skills e runtime remoto. |
| `bin/codex-skills-common.sh` | Opcional | Reúne funções compartilhadas pelos scripts que instalam e validam skills. | Você olha quando precisa entender a base comum dos scripts de skill. | Conversa com `.codex/skills/` e os scripts de instalação/sync. |
| `bin/deploy-openclaw-gateway-project.sh` | Opcional | Publica este repositório dentro do sandbox e atualiza a superfície operacional remota. | Você usa quando quer sincronizar o framework inteiro para o ambiente remoto. | Conversa com `src/nemoclaw-host/`, `fabrica-workspace/`, skills e índice Postgres. |
| `bin/ensure-fabrica-projects-index-runtime.sh` | Obrigatório | Faz um preflight barato do runtime do índice: repo root, URL, conectividade e dependências. | Você usa antes de rodar operações que dependem do índice em Postgres. | Conversa com `FABRICA_PROJECTS_DATABASE_URL`, `FABRICA_REPO_ROOT` e `sync.py`. |
| `bin/install-codex-skills.sh` | Opcional | Instala as skills no ambiente local do Codex usando links simbólicos. | Você usa quando prepara uma máquina nova para trabalhar com o framework. | Conversa com `.codex/skills/`. |
| `bin/install-git-hooks.sh` | Opcional | Instala os hooks versionados do repositório. | Você usa quando quer automatizar ações após merge ou rewrite. | Conversa com `.githooks/`. |
| `bin/install-host-linux.sh` | Opcional | Instala o toolkit host-side no Linux. | Você usa ao preparar o host Linux que sustenta a operação remota. | Conversa com `src/nemoclaw-host/`, `templates/`, `config/host.env.example` e `systemd --user`. |
| `bin/install-host.sh` | Opcional | Instala o toolkit host-side no macOS. | Você usa ao preparar o host macOS. | Conversa com `src/nemoclaw-host/`, `templates/`, `config/host.env.example` e `launchd`. |
| `bin/install-openclaw-skills.sh` | Opcional | Instala a suite `openclaw-*` no destino esperado. | Você usa quando quer disponibilizar a suite de skills do framework. | Conversa com `.codex/skills/` e scripts de skill. |
| `bin/migrate-host-env-legacy.sh` | Opcional | Ajuda a migrar um `host.env` antigo para o formato atual. | Você usa quando reaproveita uma instalação mais velha. | Conversa com `config/host.env.example`. |
| `bin/bootstrap-fabrica-projects-postgres.sh` | Obrigatório | Faz o bootstrap do runtime do índice em Postgres de ponta a ponta. | Você usa quando quer preparar o ambiente do índice com menos passos manuais. | Conversa com o preflight, aplicação de schema, sync e geração de chunks. |
| `bin/nemoclaw-progress-notify.sh` | Opcional | Envia notificações curtas de progresso usando o lado host. | Você usa quando quer avisos rápidos sem expor credencial ao sandbox. | Conversa com `src/nemoclaw-host/nemoclaw-progress-notify`, `progress-feed.js` e credenciais locais. |
| `bin/fabrica-projects-db-host-env.sh` | Obrigatório | Carrega a URL do banco e variáveis relacionadas a partir do `host.env`. | Você usa quando o shell atual ainda não tem a configuração carregada. | Conversa com `config/host.env.example` e os wrappers do índice. |
| `bin/refresh-host-sync-source.sh` | Opcional | Atualiza a base usada pelo host para sincronização remota. | Você usa quando quer garantir que o host esteja empurrando a versão certa do repositório. | Conversa com hooks de Git e deploy remoto. |
| `bin/regenerate-openclaw-skill-openai-yaml.sh` | Opcional | Regenera arquivos `openai.yaml` das skills a partir do tooling disponível. | Você usa quando muda a estrutura das skills e quer recompor metadados. | Conversa com `.codex/skills/` e `codex-skills-common.sh`. |
| `bin/sync-codex-skills.sh` | Opcional | Copia as skills para o diretório local do Codex, em vez de usar links simbólicos. | Você usa quando prefere cópia real. | Conversa com `.codex/skills/`. |
| `bin/sync-fabrica-projects-db.sh` | Obrigatório | É o comando oficial para sincronizar `PROJETOS/` com o índice operacional em Postgres. | Você usa toda vez que o estado documental muda e o espelho precisa ser atualizado. | Conversa com `ensure-fabrica-projects-index-runtime.sh`, `sync.py` e `FABRICA_PROJECTS_DATABASE_URL`. |
| `bin/sync-openclaw-skills.sh` | Opcional | Sincroniza a suite `openclaw-*` para o destino operacional. | Você usa quando quer atualizar as skills já instaladas. | Conversa com `.codex/skills/`. |
| `bin/sync-fabrica-workspace.sh` | Opcional | Sincroniza o workspace versionado para o runtime vivo no sandbox. | Você usa quando atualiza o “cérebro” versionado do agente. | Conversa com `fabrica-workspace/` e com o runtime remoto. |
| `bin/uninstall-host.sh` | Opcional | Remove o toolkit host-side instalado por este repositório. | Você usa quando quer desmontar a instalação do host com segurança. | Conversa com os caminhos criados por `install-host*.sh`. |
| `bin/validate-host.sh` | Opcional | Valida se o host e o runtime remoto estão com a base esperada. | Você usa depois da instalação ou quando suspeita de drift operacional. | Conversa com skills, deploy remoto, índice Postgres e serviços do host. |
| `bin/verify-fabrica-skill-parity.sh` | Obrigatório | Confere se o domínio e as skills continuam alinhados nas regras-chave do framework. | Você usa quando altera governança, skills ou pacote de domínio. | Conversa com `.codex/skills/`, `scripts/fabrica_domain/` e testes de paridade. |

## 5. Runtime de apoio

Este bloco reúne arquivos úteis para rodar o framework completo no host e no sandbox. Eles ajudam muito na operação, mas não são o miolo mínimo para clonar a governança e o motor documental.

### 5.1 Arquivos de raiz do repositório

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `README.md` | Obrigatório | Dá a visão geral do repositório e do runtime operacional. | Você lê primeiro para entender o que o repositório entrega. | Conversa com `bin/`, `fabrica-workspace/`, skills e host runtime. |
| `AGENTS.md` | Obrigatório | Resume as regras operacionais e normativas para agentes que atuam neste repositório. | Você consulta quando quer um resumo forte das regras em vigor. | Conversa com `PROJETOS/COMUM/` e com o fluxo do agente. |
| `requirements.txt` | Obrigatório | Lista as dependências Python compartilhadas pelo repositório. | Você usa ao preparar o ambiente local. | Conversa com testes, domínio e índice de projetos. |

### 5.2 `config/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `config/host.env.example` | Opcional | Mostra quais variáveis o host precisa para operar o runtime e o índice. | Você usa ao criar o `host.env` real da máquina. | Conversa com `install-host*.sh`, `validate-host.sh`, deploy remoto e wrappers do índice. |

### 5.3 `docs/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `docs/host-bootstrap-macos-to-linux.md` | Opcional | Explica o contrato de bootstrap entre macOS e Linux. | Você consulta quando está montando ou comparando ambientes host-side. | Conversa com `install-host.sh`, `install-host-linux.sh` e `validate-host.sh`. |
| `docs/restore.md` | Opcional | Explica como restaurar partes importantes do ambiente. | Você usa em recuperação, reinstalação ou continuidade de operação. | Conversa com host runtime, credenciais e workspace. |

### 5.4 `fabrica-workspace/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `fabrica-workspace/AGENTS.md` | Opcional | Resume as regras locais do workspace versionado. | Você lê quando quer saber como o runtime vivo deve se comportar dentro do workspace. | Conversa com `PROJETOS/COMUM/` e com o agente no sandbox. |
| `fabrica-workspace/BOOTSTRAP.md` | Opcional | Guarda instruções de arranque do workspace versionado. | Você usa ao entender como o workspace é iniciado. | Conversa com `sync-fabrica-workspace.sh`. |
| `fabrica-workspace/HEARTBEAT.md` | Opcional | Registra sinais simples de acompanhamento do workspace. | Você olha quando quer entender o pulso operacional esperado do workspace. | Conversa com o runtime do agente. |
| `fabrica-workspace/IDENTITY.md` | Opcional | Explica a identidade assumida pelo runtime versionado. | Você usa quando quer alinhar tom e papel do agente. | Conversa com `SOUL.md`, `USER.md` e `AGENTS.md` do workspace. |
| `fabrica-workspace/MEMORY.md` | Opcional | Guarda memória tática versionada, sem virar fonte de verdade acima de `PROJETOS/`. | Você consulta quando quer contexto operacional curto do workspace. | Conversa com `PROJETOS/COMUM/` e com o runtime do agente. |
| `fabrica-workspace/README.md` | Opcional | Explica o que é o workspace versionado e como ele deve ser usado. | Você lê quando quer entender o papel desta pasta. | Conversa com `sync-fabrica-workspace.sh`. |
| `fabrica-workspace/SOUL.md` | Opcional | Registra a “alma” intencional do workspace, isto é, a postura e direção do agente. | Você lê quando quer alinhar comportamento e propósito do runtime. | Conversa com `IDENTITY.md` e `AGENTS.md` do workspace. |
| `fabrica-workspace/TOOLS.md` | Opcional | Resume ferramentas e superfícies que o runtime do workspace usa. | Você consulta quando quer ver a caixa de ferramentas do agente. | Conversa com o runtime remoto e com os wrappers do host. |
| `fabrica-workspace/USER.md` | Opcional | Resume o perfil do usuário do runtime versionado. | Você lê quando quer ajustar respostas e contexto à pessoa operadora. | Conversa com `IDENTITY.md` e `SOUL.md`. |
| `fabrica-workspace/memory/.gitkeep` | Opcional | Mantém a pasta de memória versionada viva mesmo quando ela está vazia. | Você quase nunca olha para ele diretamente. | Conversa só com Git e com a estrutura da pasta. |

### 5.5 `src/nemoclaw-host/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `src/nemoclaw-host/colima-autostart.sh` | Opcional | Liga ou prepara o Colima no macOS como parte do host runtime. | Você usa ao operar host macOS com Colima. | Conversa com `install-host.sh` e templates `launchd`. |
| `src/nemoclaw-host/common.sh` | Opcional | Reúne funções shell compartilhadas do toolkit host-side. | Você abre quando precisa entender o comportamento comum dos scripts do host. | Conversa com quase todos os scripts de `src/nemoclaw-host/`. |
| `src/nemoclaw-host/dashboard-tunnel.sh` | Opcional | Abre e mantém o túnel do dashboard. | Você usa quando o runtime precisa expor ou alcançar o dashboard. | Conversa com instalação do host e templates `launchd`. |
| `src/nemoclaw-host/helper.js` | Opcional | Fornece utilidades Node compartilhadas para o runtime host-side. | Você olha quando precisa entender a base comum dos scripts JavaScript do host. | Conversa com `progress-feed.js`, `telegram-client.js` e outros utilitários Node. |
| `src/nemoclaw-host/nemoclaw-hostctl` | Opcional | É o comando de controle do host-side runtime. | Você usa no dia a dia para status, logs e restart. | Conversa com serviços do host e demais scripts desta pasta. |
| `src/nemoclaw-host/nemoclaw-progress-notify` | Opcional | É o executável host-side usado para publicar notificações curtas de progresso. | Você usa quando quer avisos de execução sem expor segredos ao sandbox. | Conversa com `progress-feed.js` e `bin/nemoclaw-progress-notify.sh`. |
| `src/nemoclaw-host/progress-feed-cli.js` | Opcional | É a interface de linha de comando do feed de progresso. | Você usa quando precisa interagir com o feed via Node. | Conversa com `progress-feed.js`. |
| `src/nemoclaw-host/progress-feed.js` | Opcional | Implementa a lógica do feed de progresso e sua persistência local. | Você olha quando quer entender como o host registra e evita duplicidade de notificações. | Conversa com `helper.js`, `nemoclaw-progress-notify` e testes Node. |
| `src/nemoclaw-host/remote-project-sync.sh` | Opcional | Sincroniza o projeto OpenClaw para o sandbox. | Você usa quando o host precisa empurrar a versão nova do framework para o runtime remoto. | Conversa com deploy remoto, workspace e skills. |
| `src/nemoclaw-host/runtime-singleton.sh` | Opcional | Garante que exista uma única superfície operacional do runtime. | Você usa quando quer evitar runtimes duplicados no host ou no sandbox. | Conversa com deploy, validação e testes de singleton. |
| `src/nemoclaw-host/telegram-bridge-host.js` | Opcional | Implementa o lado host da ponte com Telegram. | Você olha quando quer entender a camada de integração do host com Telegram. | Conversa com `telegram-client.js` e `telegram-bridge.sh`. |
| `src/nemoclaw-host/telegram-bridge.sh` | Opcional | É o wrapper shell da ponte com Telegram. | Você usa para iniciar ou gerenciar a ponte. | Conversa com scripts de instalação e templates `launchd`. |
| `src/nemoclaw-host/telegram-client.js` | Opcional | Implementa o cliente que fala com Telegram do lado host. | Você olha quando quer entender envio e recebimento nessa ponte. | Conversa com `telegram-bridge-host.js` e testes Node. |

### 5.6 `templates/launchd/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `templates/launchd/colima-autostart.plist.template` | Opcional | É o molde do serviço `launchd` que sobe o Colima no macOS. | Você usa na instalação do host macOS. | Conversa com `install-host.sh` e `colima-autostart.sh`. |
| `templates/launchd/dashboard-tunnel.plist.template` | Opcional | É o molde do serviço `launchd` do túnel do dashboard. | Você usa quando instala o host no macOS. | Conversa com `dashboard-tunnel.sh`. |
| `templates/launchd/remote-project-sync.plist.template` | Opcional | É o molde do serviço `launchd` que sincroniza o projeto remoto. | Você usa quando quer sync automático após login ou reboot no macOS. | Conversa com `remote-project-sync.sh` e deploy remoto. |
| `templates/launchd/telegram-bridge.plist.template` | Opcional | É o molde do serviço `launchd` da ponte com Telegram. | Você usa na operação macOS com Telegram bridge. | Conversa com `telegram-bridge.sh`. |

### 5.7 `.githooks/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `.githooks/_run-refresh-host-sync.sh` | Opcional | É a rotina compartilhada usada pelos hooks para atualizar a base de sync do host. | Você usa quando quer entender o que o hook realmente dispara. | Conversa com `refresh-host-sync-source.sh`. |
| `.githooks/post-merge` | Opcional | Roda após merge para manter a base do host alinhada. | Você olha quando um merge dispara automação inesperada. | Conversa com `_run-refresh-host-sync.sh`. |
| `.githooks/post-rewrite` | Opcional | Roda após rewrite para manter a base do host alinhada. | Você usa ao depurar comportamento após rebase ou amend. | Conversa com `_run-refresh-host-sync.sh`. |

### 5.8 `.github/`

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `.github/workflows/ci.yml` | Opcional | Define a automação de CI do repositório. | Você usa quando quer ver o que é validado em pipeline. | Conversa com `tests/`, scripts shell e dependências do projeto. |

## 6. `tests/`

Os testes protegem a estrutura documental, o domínio compartilhado, o índice de projetos, a instalação host-side e a suite de skills.

| Arquivo | Classificação | O que faz | Quando você olha para ele | Do que ele depende ou com o que conversa |
|---|---|---|---|---|
| `tests/README.md` | Opcional | Explica como a suíte de testes está organizada e como executá-la. | Você lê antes de rodar os testes pela primeira vez. | Conversa com `scripts/run-pytest.*` e `.github/workflows/ci.yml`. |
| `tests/node/progress-feed.test.js` | Opcional | Confere o comportamento do feed de progresso no runtime host-side. | Você roda quando muda `progress-feed.js`. | Conversa com `src/nemoclaw-host/progress-feed.js`. |
| `tests/node/telegram-bridge.test.js` | Opcional | Confere a ponte com Telegram do lado Node. | Você roda quando muda cliente ou bridge de Telegram. | Conversa com `src/nemoclaw-host/telegram-client.js` e `telegram-bridge-host.js`. |
| `tests/test_criar_projeto.py` | Opcional | Confere se o gerador de projeto cria o scaffold esperado. | Você roda quando muda `scripts/criar_projeto.py` ou templates centrais. | Conversa com `scripts/criar_projeto.py` e `PROJETOS/COMUM/`. |
| `tests/test_framework_normative_separation.py` | Opcional | Confere se a separação normativa do framework continua íntegra. | Você roda quando muda governança, schema ou contrato documental. | Conversa com `PROJETOS/COMUM/` e o índice de projetos. |
| `tests/test_generate_openclaw_framework_v4_imp_headers.py` | Opcional | Confere o gerador de cabeçalhos `imp-N.md` do meta-projeto v4. | Você roda quando muda o script gerador ou o formato dos `imp`. | Conversa com `scripts/generate_openclaw_framework_v4_imp_headers.py` e `PROJETOS/OPENCLAW-FRAMEWORK-V4`. |
| `tests/test_governance_docs.py` | Opcional | Confere alinhamento geral da documentação de governança. | Você roda quando altera `PROJETOS/COMUM/` ou skills. | Conversa com governança, skills e roteiros. |
| `tests/test_nemoclaw_host_linux_bootstrap.py` | Opcional | Confere o contrato de bootstrap host-side no Linux. | Você roda quando muda scripts ou premissas do host Linux. | Conversa com `install-host-linux.sh` e `src/nemoclaw-host/`. |
| `tests/test_nemoclaw_host_linux_install_execution.py` | Opcional | Exercita a instalação Linux em ambiente controlado. | Você roda quando altera o instalador Linux. | Conversa com `install-host-linux.sh` e wrappers do host. |
| `tests/test_nemoclaw_host_scripts.py` | Opcional | Confere contratos importantes dos scripts host-side. | Você roda quando mexe em `bin/` e `src/nemoclaw-host/`. | Conversa com os scripts de host e a README. |
| `tests/test_nemoclaw_progress_feed.py` | Opcional | Confere a camada de notificação de progresso. | Você roda quando muda feed, CLI ou integração de notificação. | Conversa com `src/nemoclaw-host/progress-feed.js` e `bin/nemoclaw-progress-notify.sh`. |
| `tests/test_nemoclaw_runtime_singleton.py` | Opcional | Confere a regra de runtime único. | Você roda quando muda deploy, workspace ou runtime singleton. | Conversa com `runtime-singleton.sh`, deploy e arquivos sincronizados. |
| `tests/test_governance_docs.py` | Opcional | Confere se os documentos ativos continuam alinhados com o contrato normativo do framework. | Você roda quando muda `PROJETOS/COMUM/` ou a documentação operacional. | Conversa com os documentos ativos e com os wrappers principais. |
| `tests/test_fabrica_projects_index_contract.py` | Opcional | Confere o boundary do índice canônico e a ausência de superfícies legadas nas áreas ativas. | Você roda quando muda schema, sync, wrappers ou docs operacionais do índice. | Conversa com `scripts/fabrica_projects_index/`, `bin/sync-fabrica-projects-db.sh` e `PROJETOS/COMUM/`. |
| `tests/test_fabrica_domain_gov_ids.py` | Opcional | Confere a normalização canônica de identificadores `FEATURE-*` e `US-*`. | Você roda quando muda o domínio compartilhado ou a rastreabilidade de identificadores. | Conversa com `scripts/fabrica_domain/` e validadores do framework. |
| `tests/test_openclaw_skill_scripts.py` | Opcional | Confere scripts que instalam, sincronizam e validam skills. | Você roda quando muda `bin/` ligado a skills. | Conversa com `.codex/skills/` e scripts de skill. |
| `tests/test_pipeline_prd_feature_us_task_separation.py` | Opcional | Confere se o pipeline documental continua separado em intake, PRD, feature, user story e task. | Você roda quando muda governança ou templates. | Conversa com `PROJETOS/COMUM/`. |
| `tests/test_review_same_issue_flow_docs.py` | Opcional | Confere a consistência do fluxo de revisão documentado para a mesma unidade. | Você roda quando muda sessões de revisão ou execução. | Conversa com `PROJETOS/COMUM/` e wrappers locais. |
| `tests/test_session_logs.py` | Opcional | Confere o pipeline de logs de sessão. | Você roda quando muda `scripts/session_logs/`. | Conversa com schemas e scripts de trace. |

## 7. `PROJETOS` de contexto do framework

Os projetos abaixo não são consumidores do framework. Eles existem para descrever o próprio framework, migrá-lo, testá-lo em escala controlada ou guardar memória de decisões da migração. Por isso, entram aqui como `Opcional`: ajudam muito a entender e provar o framework, mas não são a base mínima para clonagem.

Para evitar repetir o mesmo texto dezenas de vezes, os arquivos deste bloco usam a legenda de tipos abaixo. Cada linha da listagem aponta o arquivo, a classificação e o tipo ao qual ele pertence.

### Legenda dos tipos usados neste bloco

| Tipo | O que faz | Quando você olha para ele | Com o que conversa |
|---|---|---|---|
| `INTAKE de meta-projeto` | Explica por que o meta-projeto foi aberto e qual problema do framework ele quer atacar. | Você lê no começo ou ao revisar a origem da iniciativa. | Conversa com PRD, sessões locais e audit log. |
| `PRD de meta-projeto` | Descreve o resultado esperado do meta-projeto. | Você usa quando quer entender a entrega-alvo. | Conversa com intake, features e auditorias. |
| `AUDIT-LOG` | Guarda histórico de andamento, decisões e vereditos. | Você lê ao revisar status ou sequência de eventos. | Conversa com relatórios, sessões e features. |
| `Prompt local` | É um prompt ou preset específico daquele meta-projeto. | Você usa quando o projeto precisa de um texto-base próprio. | Conversa com governança comum e sessões locais. |
| `Sessão local` | É um wrapper local que aplica o framework a um projeto específico. | Você usa durante a execução daquele projeto. | Conversa com `PROJETOS/COMUM/` e com os documentos do próprio projeto. |
| `Feature` | Resume uma frente de trabalho do meta-projeto. | Você lê ao revisar escopo ou progresso daquela frente. | Conversa com user stories, auditorias e PRD do meta-projeto. |
| `Auditoria de feature` | Guarda o parecer final de uma feature. | Você consulta ao revisar aceitação, hold ou evidências. | Conversa com a feature correspondente e o audit log. |
| `README de user story ou issue` | Consolida contexto, objetivo e evidência da unidade local. | Você usa antes de executar ou revisar a unidade. | Conversa com tasks, revisão e documento pai. |
| `Revisão de user story` | Registra o parecer de revisão de uma user story. | Você lê ao decidir se a unidade fechou ou voltou para ajuste. | Conversa com `README.md`, `TASK-*.md` e `imp-*.md`. |
| `Task` | Define um passo executável daquela unidade. | Você usa durante execução ou revisão fina. | Conversa com o `README.md` da unidade e com o documento pai. |
| `Cabeçalho de execução` | É um `imp-N.md` pronto para abrir a sessão de execução da task correspondente. | Você usa para começar uma rodada de implementação com menos atrito. | Conversa com a task do mesmo número e com `SESSION-IMPLEMENTAR-US.md`. |
| `Spec local` | Registra um contrato técnico mais detalhado que ficou específico daquele meta-projeto. | Você lê quando precisa de detalhe técnico além do README ou da feature. | Conversa com feature, PRD e código alvo. |
| `Checklist de paridade` | Lista verificações para conferir alinhamento entre partes do framework. | Você usa ao validar paridade. | Conversa com inventário de regras, exceções e testes. |
| `Exceções de paridade` | Registra waivers ou exceções temporárias. | Você lê quando uma regra de paridade não pôde ser aplicada. | Conversa com checklist e inventário de regras. |
| `Inventário de regras` | Lista as regras que precisam permanecer alinhadas. | Você usa para revisar drift entre partes do framework. | Conversa com skills, domínio e checklist. |
| `Epic` | Resume um agrupador maior de trabalho dentro de uma fase. | Você lê para entender o tema principal da fase. | Conversa com sprints, issues e auditorias da fase. |
| `Índice de épicos` | Lista os épicos de uma fase. | Você usa para navegar rapidamente pela fase. | Conversa com os arquivos `EPIC-*.md`. |
| `Sprint` | Registra o recorte operacional de uma fase. | Você consulta quando quer ver a organização prática da fase. | Conversa com épicos e issues daquela fase. |
| `Relatório de auditoria` | Guarda o parecer formal de uma fase ou rodada. | Você lê quando quer o veredito estruturado. | Conversa com audit log e artefatos auditados. |
| `Classificação de remediação` | Registra a triagem de itens que saíram em hold ou pedem correção. | Você usa quando precisa organizar a remediação. | Conversa com relatórios de auditoria e issues de correção. |
| `Registro de revisão local` | Guarda o texto de uma rodada local de revisão. | Você lê quando precisa reconstruir a sequência de revisão. | Conversa com a issue correspondente. |
| `Guia de teste` | Explica como provar o framework em um projeto-canário. | Você usa quando quer rodar uma prova controlada do framework. | Conversa com skills, smoke test e projeto-canário. |
| `Memória de migração` | Guarda inventário, decisão ou auditoria sobre a migração do framework. | Você usa quando quer entender por que a migração foi feita de certo jeito. | Conversa com `OPENCLAW-MIGRATION` e governança comum. |

### 7.1 `_WORK-MIGRACAO-OPENCLAW`

| Arquivo | Classificação | Tipo | Nota curta |
|---|---|---|---|
| `AUDITORIA-PROJETOS-ATUAIS.md` | Opcional | Memória de migração | Resume o estado encontrado nos projetos durante a migração. |
| `DECISAO-PROJETOS.md` | Opcional | Memória de migração | Registra decisões sobre o que migrar, corrigir ou manter. |
| `INVENTARIO-LEGADO.md` | Opcional | Memória de migração | Lista o legado que precisou ser lido antes da mudança. |

### 7.2 `OC-SMOKE-SKILLS`

| Arquivo | Classificação | Tipo | Nota curta |
|---|---|---|---|
| `AUDIT-LOG.md` | Opcional | AUDIT-LOG | Histórico do projeto-canário usado para provar o framework. |
| `GUIA-TESTE-SKILLS.md` | Opcional | Guia de teste | Passo a passo para provar a suite `openclaw-*` em ambiente controlado. |
| `INTAKE-OC-SMOKE-SKILLS.md` | Opcional | INTAKE de meta-projeto | Explica por que o projeto-canário existe. |
| `PRD-OC-SMOKE-SKILLS.md` | Opcional | PRD de meta-projeto | Define o resultado esperado do canário do framework. |
| `SESSION-AUDITAR-FASE.md` | Opcional | Sessão local | Wrapper local para auditoria do projeto-canário. |
| `SESSION-CRIAR-INTAKE.md` | Opcional | Sessão local | Wrapper local para intake do projeto-canário. |
| `SESSION-CRIAR-PRD.md` | Opcional | Sessão local | Wrapper local para PRD do projeto-canário. |
| `SESSION-IMPLEMENTAR-ISSUE.md` | Opcional | Sessão local | Wrapper local de execução no fluxo compatível legado. |
| `SESSION-MAPA.md` | Opcional | Sessão local | Índice local das sessões do projeto-canário. |
| `SESSION-PLANEJAR-PROJETO.md` | Opcional | Sessão local | Wrapper local de planejamento do projeto-canário. |
| `SESSION-REFATORAR-MONOLITO.md` | Opcional | Sessão local | Wrapper local para redução de escopo grande demais. |
| `SESSION-REMEDIAR-HOLD.md` | Opcional | Sessão local | Wrapper local de remediação de hold. |
| `SESSION-REVISAR-ISSUE.md` | Opcional | Sessão local | Wrapper local de revisão compatível legado. |
| `F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md` | Opcional | Epic | Resume o épico de fundação do projeto-canário. |
| `F1-FUNDACAO/F1_OC-SMOKE-SKILLS_EPICS.md` | Opcional | Índice de épicos | Lista os épicos da fase F1 do canário. |
| `F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md` | Opcional | Relatório de auditoria | Registra o parecer formal da rodada F1-R01. |
| `F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md` | Opcional | README de user story ou issue | Consolida a issue bootstrap do canário. |
| `F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md` | Opcional | Task | Define a task da issue bootstrap do canário. |
| `F1-FUNDACAO/sprints/SPRINT-F1-01.md` | Opcional | Sprint | Registra o sprint inicial do canário. |

### 7.3 `TESTE-FW`

| Arquivo | Classificação | Tipo | Nota curta |
|---|---|---|---|
| `AUDIT-LOG.md` | Opcional | AUDIT-LOG | Histórico do projeto de teste do framework. |
| `INTAKE-TESTE-FW.md` | Opcional | INTAKE de meta-projeto | Explica por que o projeto de teste foi criado. |
| `PRD-TESTE-FW.md` | Opcional | PRD de meta-projeto | Define o resultado esperado do projeto de teste. |
| `SESSION-AUDITAR-FASE.md` | Opcional | Sessão local | Wrapper local para auditoria. |
| `SESSION-CRIAR-INTAKE.md` | Opcional | Sessão local | Wrapper local para intake. |
| `SESSION-CRIAR-PRD.md` | Opcional | Sessão local | Wrapper local para PRD. |
| `SESSION-IMPLEMENTAR-ISSUE.md` | Opcional | Sessão local | Wrapper local de execução no fluxo legado compatível. |
| `SESSION-MAPA.md` | Opcional | Sessão local | Índice local das sessões do projeto de teste. |
| `SESSION-PLANEJAR-PROJETO.md` | Opcional | Sessão local | Wrapper local de planejamento. |
| `SESSION-REFATORAR-MONOLITO.md` | Opcional | Sessão local | Wrapper local de redução de monolito. |
| `SESSION-REMEDIAR-HOLD.md` | Opcional | Sessão local | Wrapper local de remediação. |
| `SESSION-REVISAR-ISSUE.md` | Opcional | Sessão local | Wrapper local de revisão no fluxo legado compatível. |
| `F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md` | Opcional | Epic | Resume o épico de fundação do projeto de teste. |
| `F1-FUNDACAO/F1_TESTE-FW_EPICS.md` | Opcional | Índice de épicos | Lista os épicos da fase F1 do projeto de teste. |
| `F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md` | Opcional | Relatório de auditoria | Parecer formal da rodada F1-R01 do projeto de teste. |
| `F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md` | Opcional | README de user story ou issue | Consolida a issue bootstrap do projeto de teste. |
| `F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md` | Opcional | Task | Define a task da issue bootstrap do projeto de teste. |
| `F1-FUNDACAO/sprints/SPRINT-F1-01.md` | Opcional | Sprint | Registra o sprint inicial do projeto de teste. |

### 7.4 `OPENCLAW-MIGRATION`

| Arquivo | Classificação | Tipo | Nota curta |
|---|---|---|---|
| `AUDIT-LOG.md` | Opcional | AUDIT-LOG | Histórico da migração do framework. |
| `INTAKE-OPENCLAW-MIGRATION.md` | Opcional | INTAKE de meta-projeto | Explica por que a migração do framework foi aberta. |
| `PRD-OPENCLAW-MIGRATION.md` | Opcional | PRD de meta-projeto | Define a entrega-alvo da migração. |
| `SESSION-AUDITAR-FEATURE.md` | Opcional | Sessão local | Wrapper local de auditoria para a migração. |
| `SESSION-IMPLEMENTAR-US.md` | Opcional | Sessão local | Wrapper local de execução de user story. |
| `SESSION-MAPA.md` | Opcional | Sessão local | Índice local das sessões da migração. |
| `SESSION-REMEDIAR-HOLD.md` | Opcional | Sessão local | Wrapper local de remediação de hold. |
| `SESSION-REVISAR-US.md` | Opcional | Sessão local | Wrapper local de revisão de user story. |
| `auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md` | Opcional | Relatório de auditoria | Parecer formal da primeira rodada da migração. |
| `auditorias/RELATORIO-AUDITORIA-MIGRATION-R02.md` | Opcional | Relatório de auditoria | Parecer formal da segunda rodada da migração. |
| `auditorias/REMEDIACAO-HOLD-R01-CLASSIFICACAO.md` | Opcional | Classificação de remediação | Organiza o que entrou em remediação após hold. |
| `openclaw-alignment-spec.md` | Opcional | Spec local | Desenha o alinhamento técnico esperado da migração. |
| `openclaw-migration-spec.md` | Opcional | Spec local | Detalha a especificação principal da migração. |
| `features/FEATURE-1-DOCUMENTOS-DE-GOVERNANCA-CENTRAIS/FEATURE-1.md` | Opcional | Feature | Frente dedicada aos documentos centrais de governança. |
| `features/FEATURE-1-DOCUMENTOS-DE-GOVERNANCA-CENTRAIS/zAudit_FEATURE_1.md` | Opcional | Auditoria de feature | Parecer final da feature 1 da migração. |
| `features/FEATURE-2-TEMPLATES-DE-ARTEFATO/FEATURE-2.md` | Opcional | Feature | Frente dedicada aos templates de artefato. |
| `features/FEATURE-2-TEMPLATES-DE-ARTEFATO/zAudit_FEATURE_2.md` | Opcional | Auditoria de feature | Parecer final da feature 2 da migração. |
| `features/FEATURE-3-DOCUMENTOS-OPERACIONAIS-E-SKILLS/FEATURE-3.md` | Opcional | Feature | Frente dedicada a documentos operacionais e skills. |
| `features/FEATURE-3-DOCUMENTOS-OPERACIONAIS-E-SKILLS/zAudit_FEATURE_3.md` | Opcional | Auditoria de feature | Parecer final da feature 3 da migração. |
| `features/FEATURE-4-SCAFFOLD-CANONICO-DE-PROJETO/FEATURE-4.md` | Opcional | Feature | Frente dedicada ao scaffold canônico de projeto. |
| `features/FEATURE-4-SCAFFOLD-CANONICO-DE-PROJETO/zAudit_FEATURE_4.md` | Opcional | Auditoria de feature | Parecer final da feature 4 da migração. |
| `features/FEATURE-5-SMOKE-TEST-E-PROJETO-DE-REFERENCIA-CANONICOS/FEATURE-5.md` | Opcional | Feature | Frente dedicada ao smoke test e projeto-canário. |
| `features/FEATURE-5-SMOKE-TEST-E-PROJETO-DE-REFERENCIA-CANONICOS/zAudit_FEATURE_5.md` | Opcional | Auditoria de feature | Parecer final da feature 5 da migração. |
| `features/FEATURE-6-FLUXO-COMPLETO-DE-EXECUCAO-REVISAO-AUDITORIA-E-REMEDIACAO/FEATURE-6.md` | Opcional | Feature | Frente dedicada ao fluxo completo de execução, revisão, auditoria e remediação. |
| `features/FEATURE-6-FLUXO-COMPLETO-DE-EXECUCAO-REVISAO-AUDITORIA-E-REMEDIACAO/zAudit_FEATURE_6.md` | Opcional | Auditoria de feature | Parecer final da feature 6 da migração. |
| `features/FEATURE-7-BANCO-DE-DADOS-E-QUERIES-ESTRUTURADAS-REAIS/FEATURE-7.md` | Opcional | Feature | Frente dedicada ao banco de dados e consultas estruturadas reais. |
| `features/FEATURE-7-BANCO-DE-DADOS-E-QUERIES-ESTRUTURADAS-REAIS/zAudit_FEATURE_7.md` | Opcional | Auditoria de feature | Parecer final da feature 7 da migração. |
| `features/FEATURE-8-TOOLCHAIN-DE-METADATA-DAS-SKILLS/FEATURE-8.md` | Opcional | Feature | Frente dedicada à toolchain de metadados das skills. |
| `features/FEATURE-8-TOOLCHAIN-DE-METADATA-DAS-SKILLS/zAudit_FEATURE_8.md` | Opcional | Auditoria de feature | Parecer final da feature 8 da migração. |
| `F1-REMEDIACAO-HOLD-R01/EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md` | Opcional | Epic | Resume o épico de remediação após hold da migração. |
| `F1-REMEDIACAO-HOLD-R01/F1_OPENCLAW-MIGRATION_EPICS.md` | Opcional | Índice de épicos | Lista os épicos da fase de remediação R01. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/README.md` | Opcional | README de user story ou issue | Consolida a issue local sobre o template de user story. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/TASK-1.md` | Opcional | Task | Define a task da issue sobre o template de user story. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK/README.md` | Opcional | README de user story ou issue | Consolida a issue local sobre o boot prompt novo. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK/TASK-1.md` | Opcional | Task | Define a task da issue do boot prompt. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/README.md` | Opcional | README de user story ou issue | Consolida a issue local sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-1.md` | Opcional | Task | Primeira task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-2.md` | Opcional | Task | Segunda task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-3.md` | Opcional | Task | Terceira task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-4.md` | Opcional | Task | Quarta task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-5.md` | Opcional | Task | Quinta task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/TASK-6.md` | Opcional | Task | Sexta task da issue sobre sessions e `GOV-SCRUM`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/README.md` | Opcional | README de user story ou issue | Consolida a issue local de limpeza do `GOV-FRAMEWORK-MASTER`. |
| `F1-REMEDIACAO-HOLD-R01/issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/TASK-1.md` | Opcional | Task | Define a task da issue de limpeza do `GOV-FRAMEWORK-MASTER`. |
| `F1-REMEDIACAO-HOLD-R01/issues/session-revisar-issue/session-revisar-issue-f1-01-001.md` | Opcional | Registro de revisão local | Guarda uma rodada local de revisão da issue 001. |
| `F1-REMEDIACAO-HOLD-R01/issues/session-revisar-issue/session-revisar-issue-f1-01-002.md` | Opcional | Registro de revisão local | Guarda uma rodada local de revisão da issue 002. |
| `F1-REMEDIACAO-HOLD-R01/issues/session-revisar-issue/session-revisar-issue-f1-01-003.md` | Opcional | Registro de revisão local | Guarda uma rodada local de revisão da issue 003. |
| `F1-REMEDIACAO-HOLD-R01/issues/session-revisar-issue/session-revisar-issue-f1-01-004.md` | Opcional | Registro de revisão local | Guarda uma rodada local de revisão da issue 004. |

### 7.5 `OPENCLAW-FRAMEWORK-V4`

| Arquivo | Classificacao | Tipo | Nota curta |
|---|---|---|---|
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/AUDIT-LOG.md` | Opcional | AUDIT-LOG | Historico do desenho e da validacao do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/INTAKE-OPENCLAW-FRAMEWORK-V4.md` | Opcional | INTAKE de meta-projeto | Explica por que o framework v4 foi aberto como iniciativa. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/PRD-OPENCLAW-FRAMEWORK-V4.md` | Opcional | PRD de meta-projeto | Define o resultado esperado do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/PROMPT-INTAKE-PARA-PRD.md` | Opcional | Prompt local | Texto-base local usado para transformar intake em PRD neste meta-projeto. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/SESSION-DECOMPOR-FEATURE-EM-US.md` | Opcional | Sessao local | Wrapper local para decompor feature em us no framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/SESSION-DECOMPOR-PRD-EM-FEATURES.md` | Opcional | Sessao local | Wrapper local para decompor prd em features no framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/SESSION-DECOMPOR-US-EM-TASKS.md` | Opcional | Sessao local | Wrapper local para decompor us em tasks no framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/SESSION-IMPLEMENTAR-US.md` | Opcional | Sessao local | Wrapper local para implementar us no framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/FEATURE-1.md` | Opcional | Feature | Resume a frente DOMINIO COMPARTILHADO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/auditorias/RELATORIO-AUDITORIA-F1-R01.md` | Opcional | Relatorio de auditoria | Parecer formal da rodada de auditoria desta feature. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/README.md` | Opcional | README de user story ou issue | Consolida a US-1-01 sobre API DOMINIO CONSUMIDOR MINIMO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/REV-US-1-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/TASK-1.md` | Opcional | Task | Define a task 1 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/TASK-2.md` | Opcional | Task | Define a task 2 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/TASK-3.md` | Opcional | Task | Define a task 3 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/TASK-4.md` | Opcional | Task | Define a task 4 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/TASK-5.md` | Opcional | Task | Define a task 5 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-01-API-DOMINIO-CONSUMIDOR-MINIMO/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-1-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/NORMATIVE-GATES-SPEC.md` | Opcional | Spec local | Detalha os gates normativos da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/README.md` | Opcional | README de user story ou issue | Consolida a US-1-02 sobre CADEIA NORMATIVA DOMINIO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/REV-US-1-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/TASK-1.md` | Opcional | Task | Define a task 1 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/TASK-2.md` | Opcional | Task | Define a task 2 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/TASK-3.md` | Opcional | Task | Define a task 3 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/TASK-4.md` | Opcional | Task | Define a task 4 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-02-CADEIA-NORMATIVA-DOMINIO/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-1-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/PARITY-CHECKLIST.md` | Opcional | Checklist de paridade | Lista as verificacoes de paridade da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/PARITY-EXCEPTIONS.md` | Opcional | Excecoes de paridade | Registra excecoes aceitas na US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/PARITY-RULES-INVENTORY.md` | Opcional | Inventario de regras | Lista as regras que precisam ficar alinhadas na US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/README.md` | Opcional | README de user story ou issue | Consolida a US-1-03 sobre PARIDADE DOMINIO SKILLS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/REV-US-1-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/TASK-1.md` | Opcional | Task | Define a task 1 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/TASK-2.md` | Opcional | Task | Define a task 2 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/TASK-3.md` | Opcional | Task | Define a task 3 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/TASK-4.md` | Opcional | Task | Define a task 4 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/TASK-5.md` | Opcional | Task | Define a task 5 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/user-stories/US-1-03-PARIDADE-DOMINIO-SKILLS/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-1-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-1-DOMINIO-COMPARTILHADO/zAudit_FEATURE_1.md` | Opcional | Auditoria de feature | Parecer final da feature 1 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/FEATURE-2.md` | Opcional | Feature | Resume a frente SYNC E MATERIALIZACAO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/README.md` | Opcional | README de user story ou issue | Consolida a US-2-01 sobre SYNC DETERMINISTICO MD PG. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/REV-US-2-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/TASK-1.md` | Opcional | Task | Define a task 1 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/TASK-2.md` | Opcional | Task | Define a task 2 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/TASK-3.md` | Opcional | Task | Define a task 3 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/TASK-4.md` | Opcional | Task | Define a task 4 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-01-SYNC-DETERMINISTICO-MD-PG/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-2-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/README.md` | Opcional | README de user story ou issue | Consolida a US-2-02 sobre REGISTO SYNC RUNS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/REV-US-2-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/TASK-1.md` | Opcional | Task | Define a task 1 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/TASK-2.md` | Opcional | Task | Define a task 2 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/TASK-3.md` | Opcional | Task | Define a task 3 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/TASK-4.md` | Opcional | Task | Define a task 4 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-02-REGISTO-SYNC-RUNS/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-2-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/README.md` | Opcional | README de user story ou issue | Consolida a US-2-03 sobre POLITICA EXPORT MARKDOWN. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/REV-US-2-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/TASK-1.md` | Opcional | Task | Define a task 1 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/TASK-2.md` | Opcional | Task | Define a task 2 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/TASK-3.md` | Opcional | Task | Define a task 3 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/TASK-4.md` | Opcional | Task | Define a task 4 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/user-stories/US-2-03-POLITICA-EXPORT-MARKDOWN/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-2-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-2-SYNC-E-MATERIALIZACAO/zAudit_FEATURE_2.md` | Opcional | Auditoria de feature | Parecer final da feature 2 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/FEATURE-3.md` | Opcional | Feature | Resume a frente CARGA BATCH ARVORE. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/README.md` | Opcional | README de user story ou issue | Consolida a US-3-01 sobre CONTRATO JSON CARGA ARVORE. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/REV-US-3-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/TASK-1.md` | Opcional | Task | Define a task 1 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/TASK-2.md` | Opcional | Task | Define a task 2 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/TASK-3.md` | Opcional | Task | Define a task 3 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/TASK-4.md` | Opcional | Task | Define a task 4 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-01-CONTRATO-JSON-CARGA-ARVORE/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-3-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/README.md` | Opcional | README de user story ou issue | Consolida a US-3-02 sobre VALIDACAO GRAFO DEPENDENCIAS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/REV-US-3-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/TASK-1.md` | Opcional | Task | Define a task 1 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/TASK-2.md` | Opcional | Task | Define a task 2 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/TASK-3.md` | Opcional | Task | Define a task 3 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/TASK-4.md` | Opcional | Task | Define a task 4 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-02-VALIDACAO-GRAFO-DEPENDENCIAS/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-3-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/README.md` | Opcional | README de user story ou issue | Consolida a US-3-03 sobre CARGA IDEMPOTENTE TRANSACIONAL. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/REV-US-3-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/TASK-1.md` | Opcional | Task | Define a task 1 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/TASK-2.md` | Opcional | Task | Define a task 2 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/TASK-3.md` | Opcional | Task | Define a task 3 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/TASK-4.md` | Opcional | Task | Define a task 4 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/TASK-5.md` | Opcional | Task | Define a task 5 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/user-stories/US-3-03-CARGA-IDEMPOTENTE-TRANSACIONAL/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-3-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-3-CARGA-BATCH-ARVORE/zAudit_FEATURE_3.md` | Opcional | Auditoria de feature | Parecer final da feature 3 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/FEATURE-4.md` | Opcional | Feature | Resume a frente MOTOR ONDAS E ELEGIBILIDADE. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/README.md` | Opcional | README de user story ou issue | Consolida a US-4-01 sobre ELEGIBILIDADE E GRAFOS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/REV-US-4-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/TASK-1.md` | Opcional | Task | Define a task 1 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/TASK-2.md` | Opcional | Task | Define a task 2 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/TASK-3.md` | Opcional | Task | Define a task 3 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/TASK-4.md` | Opcional | Task | Define a task 4 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-01-ELEGIBILIDADE-E-GRAFOS/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-4-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/README.md` | Opcional | README de user story ou issue | Consolida a US-4-02 sobre ONDAS PARALELIZAVEIS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/REV-US-4-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/TASK-1.md` | Opcional | Task | Define a task 1 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/TASK-2.md` | Opcional | Task | Define a task 2 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/TASK-3.md` | Opcional | Task | Define a task 3 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/TASK-4.md` | Opcional | Task | Define a task 4 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-02-ONDAS-PARALELIZAVEIS/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-4-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/README.md` | Opcional | README de user story ou issue | Consolida a US-4-03 sobre INTEGRACAO ESTADO E PARALELO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/REV-US-4-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/TASK-1.md` | Opcional | Task | Define a task 1 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/TASK-2.md` | Opcional | Task | Define a task 2 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/TASK-3.md` | Opcional | Task | Define a task 3 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/TASK-4.md` | Opcional | Task | Define a task 4 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/TASK-5.md` | Opcional | Task | Define a task 5 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/user-stories/US-4-03-INTEGRACAO-ESTADO-E-PARALELO/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-4-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-4-MOTOR-ONDAS-E-ELEGIBILIDADE/zAudit_FEATURE_4.md` | Opcional | Auditoria de feature | Parecer final da feature 4 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/FEATURE-5.md` | Opcional | Feature | Resume a frente CLI CICLO DE VIDA TUI. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/README.md` | Opcional | README de user story ou issue | Consolida a US-5-01 sobre CLI ENTRYPOINT DOMINIO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/REV-US-5-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/TASK-1.md` | Opcional | Task | Define a task 1 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/TASK-2.md` | Opcional | Task | Define a task 2 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/TASK-3.md` | Opcional | Task | Define a task 3 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/TASK-4.md` | Opcional | Task | Define a task 4 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-01-CLI-ENTRYPOINT-DOMINIO/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-5-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/README.md` | Opcional | README de user story ou issue | Consolida a US-5-02 sobre TUI PROJETO INTAKE PRD. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/REV-US-5-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/TASK-1.md` | Opcional | Task | Define a task 1 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/TASK-2.md` | Opcional | Task | Define a task 2 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/TASK-3.md` | Opcional | Task | Define a task 3 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/TASK-4.md` | Opcional | Task | Define a task 4 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/TASK-5.md` | Opcional | Task | Define a task 5 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-02-TUI-PROJETO-INTAKE-PRD/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-5-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/README.md` | Opcional | README de user story ou issue | Consolida a US-5-03 sobre PRE SYNC E VISIBILIDADE SYNC. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/REV-US-5-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/TASK-1.md` | Opcional | Task | Define a task 1 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/TASK-2.md` | Opcional | Task | Define a task 2 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/TASK-3.md` | Opcional | Task | Define a task 3 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/TASK-4.md` | Opcional | Task | Define a task 4 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-03-PRE-SYNC-E-VISIBILIDADE-SYNC/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-5-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/README.md` | Opcional | README de user story ou issue | Consolida a US-5-04 sobre ACESSIBILIDADE E ERROS CLI. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/REV-US-5-04.md` | Opcional | Revisao de user story | Registra a revisao da user story US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/TASK-1.md` | Opcional | Task | Define a task 1 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/TASK-2.md` | Opcional | Task | Define a task 2 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/TASK-3.md` | Opcional | Task | Define a task 3 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/TASK-4.md` | Opcional | Task | Define a task 4 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/TASK-5.md` | Opcional | Task | Define a task 5 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/user-stories/US-5-04-ACESSIBILIDADE-E-ERROS-CLI/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-5-04. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-5-CLI-CICLO-DE-VIDA-TUI/zAudit_FEATURE_5.md` | Opcional | Auditoria de feature | Parecer final da feature 5 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/FEATURE-6.md` | Opcional | Feature | Resume a frente ORQUESTRACAO E POLITICA DE MODELOS. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/README.md` | Opcional | README de user story ou issue | Consolida a US-6-01 sobre FLUXO AGNO REFERENCIA. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/REV-US-6-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/TASK-1.md` | Opcional | Task | Define a task 1 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/TASK-2.md` | Opcional | Task | Define a task 2 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/TASK-3.md` | Opcional | Task | Define a task 3 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/TASK-4.md` | Opcional | Task | Define a task 4 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-01-FLUXO-AGNO-REFERENCIA/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-6-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/README.md` | Opcional | README de user story ou issue | Consolida a US-6-02 sobre CONFIG MODELOS E OAUTH. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/REV-US-6-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/TASK-1.md` | Opcional | Task | Define a task 1 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/TASK-2.md` | Opcional | Task | Define a task 2 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/TASK-3.md` | Opcional | Task | Define a task 3 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/TASK-4.md` | Opcional | Task | Define a task 4 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/TASK-5.md` | Opcional | Task | Define a task 5 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-02-CONFIG-MODELOS-E-OAUTH/imp-5.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 5 da US-6-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/README.md` | Opcional | README de user story ou issue | Consolida a US-6-03 sobre ROTACAO OAUTH E EVIDENCIA. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/REV-US-6-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/TASK-1.md` | Opcional | Task | Define a task 1 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/TASK-2.md` | Opcional | Task | Define a task 2 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/TASK-3.md` | Opcional | Task | Define a task 3 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/TASK-4.md` | Opcional | Task | Define a task 4 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/user-stories/US-6-03-ROTACAO-OAUTH-E-EVIDENCIA/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-6-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-6-ORQUESTRACAO-E-POLITICA-DE-MODELOS/zAudit_FEATURE_6.md` | Opcional | Auditoria de feature | Parecer final da feature 6 do framework v4. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/FEATURE-7.md` | Opcional | Feature | Resume a frente EXTENSAO GOVERNANCA COMUM DB. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/README.md` | Opcional | README de user story ou issue | Consolida a US-7-01 sobre ADR RFC GOVERNANCA COMUM DB. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/REV-US-7-01.md` | Opcional | Revisao de user story | Registra a revisao da user story US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/TASK-1.md` | Opcional | Task | Define a task 1 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/TASK-2.md` | Opcional | Task | Define a task 2 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/TASK-3.md` | Opcional | Task | Define a task 3 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/TASK-4.md` | Opcional | Task | Define a task 4 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/imp-1.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 1 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/imp-2.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 2 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/imp-3.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 3 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-01-ADR-RFC-GOVERNANCA-COMUM-DB/imp-4.md` | Opcional | Cabecalho de execucao | Cabecalho pronto da task 4 da US-7-01. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-02-SCHEMA-E-LEITURA-ESPELHO/README.md` | Opcional | README de user story ou issue | Consolida a US-7-02 sobre SCHEMA E LEITURA ESPELHO. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-02-SCHEMA-E-LEITURA-ESPELHO/REV-US-7-02.md` | Opcional | Revisao de user story | Registra a revisao da user story US-7-02. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-03-EXPORT-MARKDOWN-ROUND-TRIP/README.md` | Opcional | README de user story ou issue | Consolida a US-7-03 sobre EXPORT MARKDOWN ROUND TRIP. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/user-stories/US-7-03-EXPORT-MARKDOWN-ROUND-TRIP/REV-US-7-03.md` | Opcional | Revisao de user story | Registra a revisao da user story US-7-03. |
| `PROJETOS/OPENCLAW-FRAMEWORK-V4/features/FEATURE-7-EXTENSAO-GOVERNANCA-COMUM-DB/zAudit_FEATURE_7.md` | Opcional | Auditoria de feature | Parecer final da feature 7 do framework v4. |

## Recorte para clonagem

Leve como `Obrigatorio` o que forma o nucleo reutilizavel do framework: `PROJETOS/COMUM/`, `scripts/criar_projeto.py`, `scripts/generate_openclaw_framework_v4_imp_headers.py`, `scripts/framework_governance/`, `scripts/session_tools/`, `scripts/fabrica_projects_index/`, `scripts/fabrica_domain/`, `scripts/session_logs/`, `.codex/skills/fabrica-*`, `README.md`, `AGENTS.md` e `requirements.txt`. Esse bloco cobre norma, scaffold, gates de rastreabilidade, leitura minima, materializacao em banco, dominio compartilhado, suite de skills e documentacao-base.

Leve como `Opcional` o runtime de apoio e a prova operacional: `bin/`, `config/host.env.example`, `docs/`, `fabrica-workspace/`, `src/nemoclaw-host/`, `templates/launchd/`, `.githooks/`, `.github/workflows/ci.yml`, `tests/`, `PROJETOS/OPENCLAW-FRAMEWORK-V4`, `PROJETOS/OPENCLAW-MIGRATION`, `PROJETOS/_WORK-MIGRACAO-OPENCLAW`, `PROJETOS/OC-SMOKE-SKILLS` e `PROJETOS/TESTE-FW`. Eles ajudam a operar, validar, instalar e explicar o framework, mas nao sao o pacote minimo.

Deixe em `Excluir` o que nao deve entrar no clone do framework: `PROJETOS/COMUM/LEGADO/`, projetos consumidores, `PROJETOS/v4`, pastas `_review_*`, `.venv`, `.pytest_cache`, `__pycache__` e artefatos soltos como `files.zip`, `simposio*.html` e `mneme*.html`.
