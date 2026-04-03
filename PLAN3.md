# Integrar trilha lean `PRD -> Features` sem tocar no fallback legado

## Resumo

Adicionar uma trilha explícita e pequena ao comando atual `generate features`, sem alterar o comportamento default. O legado continua em `fabrica generate features --project <SLUG>`. A nova trilha entra só com `--lean`, consome uma proposta JSON externa, valida contrato/preflight local e renderiza os `FEATURE-*.md` de forma determinística. Não haverá integração com Cursor, Composer, OpenRouter ou qualquer provider nesta iteração.

## Mudanças de implementação

- **CLI**
  - Alterar `scripts/fabrica_core/cli.py` para expor:
    - `fabrica generate features --project <SLUG>`: caminho legado, inalterado.
    - `fabrica generate features --project <SLUG> --lean --proposal-file <PATH|-> [--agent-id <OPAQUE>]`: trilha lean explícita.
  - `--proposal-file` só é válido com `--lean`.
  - `--agent-id` será aceito como metadata opaca; fora de `--lean`, não muda comportamento e não influencia o legado.
  - A ajuda da CLI deve deixar explícito:
    - `--lean` não invoca provider externo nesta iteração.
    - a proposta precisa vir de um JSON externo.
    - `agent_id` é apenas metadata/plumbing.

- **Novo runner lean**
  - Criar `scripts/fabrica_core/features_lean.py` como superfície isolada da nova trilha.
  - Implementar leitura de proposta JSON via arquivo ou stdin (`-`), com dataclasses/validação manual, sem dependências novas.
  - Validar o contrato mínimo do prompt:
    - `project` coerente com `--project`.
    - `prd_path` coerente com `PROJETOS/<PROJETO>/PRD-<PROJETO>.md`.
    - `blocked=true` exige `features=[]` e `blockers` não vazio.
    - `blocked=false` exige `blockers=[]` e `features` não vazio.
    - `feature_key`, `feature_slug`, `depends_on`, `acceptance_criteria`, `layer_impacts` e evidências obrigatórias consistentes.
    - se já existirem `features/FEATURE-*`, a trilha lean bloqueia e não escreve nada.
    - se o PRD contiver backlog explícito (`FEATURE-*`, `US-*`), a trilha lean bloqueia e não escreve nada.
  - Renderizar manifestos alinhados a `TEMPLATE-FEATURE.md`, sem mexer em `generate_stories`/`generate_tasks`.
  - Criar apenas a árvore mínima por feature:
    - `features/FEATURE-<N>-<SLUG>/FEATURE-<N>.md`
    - diretórios vazios `user-stories/` e `auditorias/` para compatibilidade downstream
  - Em proposta bloqueada ou preflight inválido, sair com erro claro e sem sync/escrita.

- **Preservação do legado**
  - Não alterar a lógica interna de `generate_features()` em `scripts/fabrica_core/generation.py`.
  - O branch default do CLI continua chamando exatamente o gerador atual.
  - O sync continua acontecendo apenas após geração bem-sucedida; erro/bloqueio na trilha lean não dispara sync.

- **`agent_id`**
  - Fonte suportada:
    - `--agent-id` na CLI
    - `agent_id` no JSON de proposta
  - Regra:
    - se apenas um vier preenchido, ele vira o `agent_id` efetivo.
    - se ambos vierem iguais, segue normalmente.
    - se ambos vierem diferentes, falha explícita por ambiguidade.
  - Tratamento:
    - metadata/plumbing apenas.
    - não altera validação semântica.
    - não seleciona modelo/provider.
    - não faz chamada externa.
  - Preservação:
    - incluir `agent_id` no frontmatter gerado como metadata operacional opcional, junto com `generated_by`/`generator_stage`, sem qualquer semântica de runtime.

## Interface pública exposta

- `fabrica generate features --project <SLUG>`
  - comportamento atual preservado.

- `fabrica generate features --project <SLUG> --lean --proposal-file <PATH|-> [--agent-id <OPAQUE>]`
  - valida proposta JSON externa.
  - renderiza Markdown final deterministicamente.
  - não chama provider externo.

## Plano de testes

- Criar `tests/test_fabrica_generate_features_cli.py` com testes black-box via subprocess contra um repo temporário em layout canônico `temp/fabrica/...`.
- Cenários obrigatórios:
  - legado continua funcionando com `generate features --project <SLUG>`.
  - trilha lean só entra quando `--lean` é usado explicitamente.
  - trilha lean com `--proposal-file` válido gera `FEATURE-*.md` alinhado ao template e não cria US/tasks.
  - `--agent-id` pode ser passado sem quebrar o comando.
  - `agent_id` fica preservado como metadata no frontmatter gerado e não altera a renderização.
  - fallback antigo permanece intacto mesmo após a introdução das novas flags.
- Cenários adicionais de proteção:
  - proposta `blocked=true` não escreve arquivos.
  - projeto com `features/FEATURE-*` preexistentes bloqueia a trilha lean.
  - mismatch entre `--agent-id` e `agent_id` do JSON falha explicitamente.
- Execução:
  - `.\scripts\run-pytest.ps1 tests/test_fabrica_generate_features_cli.py -q`

## Assunções e defaults

- Não mexer em `PROJETOS/COMUM/GOV-PRD.md`, `GOV-FEATURE.md`, `PROMPT-PRD-PARA-FEATURES.md` e `TEMPLATE-FEATURE.md` nesta tarefa.
  - Esses arquivos já estão modificados no worktree e já documentam a limitação de provider/runtime.
- A documentação obrigatória desta iteração ficará em:
  - help da CLI
  - docstring/comentários do novo módulo lean
- A trilha lean v1 aceita apenas proposta JSON externa; não tenta produzir a proposta localmente.
- Nenhuma mudança em `Feature -> User Stories`, `User Story -> Tasks` ou no pipeline legado fora do branch explícito `--lean`.
