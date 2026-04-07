# Plano Faseado para Eliminar Redundâncias no Processo da Fábrica

## Summary
- Atacar primeiro a duplicação que afeta comportamento (`sync.py`), depois a duplicação de superfície (`cli`/`scaffold`), depois a duplicação arquitetural (`project_layout` via `generation`), e por fim a duplicação semântica do domínio e dos aliases `OpenClaw*`.
- O objetivo é deixar uma única implementação por responsabilidade: um pipeline de sync, uma CLI, uma fonte de layout, uma fonte de canonização de IDs e uma única identidade pública `Fabrica*`.
- A limpeza inclui código, testes, exemplos, scripts auxiliares e documentação ativa. Material histórico pode permanecer apenas em áreas explicitamente históricas.

## Implementation Changes
### P1. Unificar o pipeline de indexação em `sync.py`
- Manter uma única rotina de indexação por arquivo e uma única rotina de aplicação do estado indexado.
- Eliminar a duplicação entre `_run_index_pass_single_transaction` e o fluxo `_build_index_state` + `_index_markdown_file`; o comportamento de indexação deve existir uma vez só.
- `run_index_pass` continua sendo o único ponto de entrada e escolhe apenas a estratégia transacional:
  - transação única quando não houver `partial_errors`
  - savepoints/erros parciais quando houver `partial_errors`
- Não mudar schema nem contrato externo do sync nesta fase.
- Critério de aceite:
  - toda classificação/materialização de Markdown ocorre em uma única função compartilhada;
  - não resta caminho paralelo de indexação com regras próprias.

### P2. Remover a mini-CLI de `scaffold.py`
- `scripts/fabrica_core/cli.py` vira a única superfície de linha de comando.
- `scripts/fabrica_core/scaffold.py` fica restrito a funções puras de scaffolding e criação de estrutura.
- Remover de `scaffold.py` qualquer `main`, parser, `parse_args`, `build_argument_parser` e `_run_sync`.
- A decisão de executar sync após criação de projeto fica exclusivamente na CLI canônica.
- Critério de aceite:
  - só existe um entrypoint CLI para criação de projeto;
  - `scaffold.py` pode ser importado sem carregar lógica de CLI/orquestração.

### P3. Centralizar a execução de sync
- Extrair a lógica compartilhada de execução de sync para um helper único de runtime no `fabrica_core`.
- `cli.py` usa esse helper; nenhum outro módulo mantém sua própria versão de `_run_sync`.
- O helper recebe explicitamente `repo_root`, ambiente e modo de erro, sem depender de parsing local.
- Critério de aceite:
  - `_run_sync` existe em um único lugar;
  - criação de projeto e sync usam o mesmo mecanismo operacional.

### P4. Tornar `project_layout.py` a única fonte de layout
- `scripts/fabrica_core/project_layout.py` passa a ser a fonte exclusiva de `ArtifactPaths`, `ProjectPaths`, `resolve_project_paths` e helpers correlatos.
- Atualizar consumidores ativos para importar layout diretamente de `project_layout.py`, não via `generation.py`.
- Em especial, alinhar os consumidores já identificados:
  - `features_lean.py`
  - `features_renderer.py`
  - `prd_features_bundle.py`
- `generation.py` deixa de servir como fachada acidental de utilitários de layout.
- Critério de aceite:
  - não restam imports de layout vindos de `generation.py`;
  - `generation.py` mantém apenas responsabilidades de geração/orquestração do fluxo.

### P5. Extrair canonização e normalização do domínio
- Criar um módulo utilitário único no `fabrica_domain` para:
  - normalização textual
  - resolução canônica de `FEATURE-*`
  - resolução canônica de `US-*`
  - normalização de status quando hoje estiver duplicada
- `service.py` e `normative_chain.py` passam a depender só desse utilitário compartilhado.
- O comportamento deve permanecer equivalente ao atual; a fase é refatoração, não mudança de regra de negócio.
- Critério de aceite:
  - regexes e helpers de canonização não ficam mais duplicados nesses dois módulos;
  - os testes de domínio seguem verdes sem alteração semântica inesperada.

### P6. Remover aliases e superfície ativa `OpenClaw*`
- Tratar `OpenClaw*` como legado ativo e removê-lo da superfície canônica do pacote `fabrica_domain`.
- Atualizar código ativo para usar só `Fabrica*`, inclusive:
  - exports públicos do pacote
  - tipos/protocolos
  - erros
  - exemplos
  - testes
- Atualizar também scripts e docs ativas que ainda apontem para a identidade antiga ou para paths já removidos, incluindo:
  - `scripts/run-pytest.ps1`
  - exemplos sob `scripts/fabrica_domain/examples/`
  - docs operacionais em `PROJETOS/COMUM/**`
  - allowlists e inventários ativos fora de histórico
- Não reescrever material em `PROJETOS/HISTORICO/**`; ele permanece como registro histórico.
- Critério de aceite:
  - não há referência operacional ativa a `OpenClaw*`;
  - o pacote público expõe apenas `Fabrica*`;
  - qualquer menção remanescente fica restrita a histórico.

## Public Interfaces
- CLI pública:
  - permanece em `scripts/fabrica.py` -> `fabrica_core.cli`
  - nenhuma CLI paralela em `scaffold.py`
- `fabrica_core.project_layout`:
  - vira o único módulo público para convenções de path/layout
- `fabrica_domain`:
  - expõe apenas símbolos `Fabrica*`
  - remove aliases `OpenClaw*` da superfície pública
- O comportamento funcional do fluxo `project -> intake -> prd -> features -> user stories -> tasks -> sync` deve permanecer o mesmo.

## Test Plan
- Atualizar testes de sync para garantir que existe um único caminho de materialização e que os dois modos transacionais exercitam a mesma lógica.
- Atualizar testes da CLI/scaffold para refletir `scaffold.py` como biblioteca pura e `cli.py` como única entrada de comando.
- Adicionar regressão para impedir imports de layout via `generation.py` nos consumidores ativos.
- Atualizar testes do domínio para usar apenas `Fabrica*` e validar que a extração dos helpers de canonização preserva comportamento.
- Ajustar exemplos e scripts auxiliares para o novo naming e garantir que continuam executáveis.
- Validar documentação ativa com busca estática para garantir ausência de referências operacionais a `OpenClaw*` e a entrypoints removidos.

## Assumptions
- É aceitável fazer breaking change interno e de naming público no `fabrica_domain`, porque a diretriz é eliminar legado, não mantê-lo por compatibilidade.
- Referências históricas podem permanecer apenas em áreas explicitamente históricas.
- Esta refatoração não introduz nova modelagem de domínio nem muda o fluxo funcional; ela reduz redundância e consolida superfícies canônicas.
- A ordem recomendada de execução é P1 -> P2/P3 -> P4 -> P5 -> P6.
