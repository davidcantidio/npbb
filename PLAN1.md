# Renderer Deterministico de Features

## Resumo
- Implementar um renderer interno novo que recebe o JSON ja validado da proposta e materializa manifestos canonicos de feature em Markdown.
- Manter a CLI e o caminho legado intactos nesta etapa: sem provider integration, sem novo comando, sem renomear `generate features`, sem mexer em `Feature -> User Stories`.
- O renderer faz preflight completo antes de escrever qualquer ficheiro; se houver bloqueio, aborta sem side effects.

## Mudancas de Implementacao
- Adicionar um modulo novo em [features_renderer.py](C:/Users/NPBB/fabrica/scripts/fabrica_core/features_renderer.py) com a API interna `render_feature_proposal(proposal, *, repo_root=None) -> list[Path]`.
- Fazer ajuste minimo em [generation.py](C:/Users/NPBB/fabrica/scripts/fabrica_core/generation.py) apenas para exportar/importar o renderer novo para uso futuro. `generate_features(project_slug, *, repo_root=None)` permanece sem mudanca funcional nesta iteracao.
- Reusar `resolve_project_paths`, `render_frontmatter`, `markdown_href`, `markdown_table`, `today_iso` e `write_generated_markdown`; manter `generated_by: fabrica-cli` e `generator_stage: feature` porque o overwrite seguro atual depende disso.
- Preflight do renderer:
  - validar que `project` e `prd_path` batem com o path canonico `PROJETOS/<PROJETO>/PRD-<PROJETO>.md`
  - tratar `blocked=true` como bloqueio operacional e levantar `ValueError` com mensagem estavel no formato `Proposta de features bloqueada: ...`
  - bloquear se existir qualquer `features/FEATURE-*` no projeto; pasta `features/` vazia continua permitida
  - a mensagem desse bloqueio deve ser explicita: `Projeto <PROJETO> ja possui features existentes em PROJETOS/<PROJETO>/features; v1 nao faz merge nem renumeracao.`
  - validar que `features` vem em ordem crescente de `FEATURE-1..FEATURE-N`; se a lista vier fora de ordem ou com buracos, bloquear em vez de reordenar ou renumerar silenciosamente
  - validar que cada `depends_on` referencia apenas `FEATURE-*` presente na propria proposta e nunca a propria feature
- Renderizacao por feature:
  - criar `PROJETOS/<PROJETO>/features/FEATURE-<N>-<SLUG>/`
  - criar tambem `user-stories/` e `auditorias/` vazios, porque a estrutura canonica ativa exige esses subdiretorios
  - criar o manifesto `FEATURE-<N>.md` com frontmatter e secoes na ordem exata de `TEMPLATE-FEATURE.md`
  - preencher `### Evidencia no PRD` a partir de `prd_evidence`, preservando a ordem de entrada
  - usar `business_objective` nos dois bullets de `Objetivo de Negocio`, sem inferencia adicional
  - renderizar `depends_on` como `depende_de` no frontmatter e no corpo; vazio vira `[]`, nao vazio vira lista inline estavel como ``[`FEATURE-1`, `FEATURE-2`]``
  - renderizar `behavior_expected`, `acceptance_criteria` e `risks` na ordem recebida, sem inventar texto
  - manter a secao `Estrategia de Implementacao` com o texto fixo do template
  - renderizar `Impactos por Camada` em ordem fixa `Banco`, `Backend`, `Frontend`, `Testes`, `Observabilidade`; usar o mesmo valor do JSON nas colunas `Impacto` e `Detalhamento`
  - derivar `intake_path` do projeto como `../../INTAKE-<PROJETO>.md`, seguindo o padrao canonico atual
  - manter `status: todo` e `audit_gate: not_ready`
  - em `User Stories (rastreabilidade)`, manter apenas a nota do template e a tabela com cabecalho vazio, sem linhas fake de US
  - em `Referencias e Anexos`, usar apenas os bullets fixos do template

## Testes
- Criar a suite em [test_fabrica_features_renderer.py](C:/Users/NPBB/fabrica/tests/test_fabrica_features_renderer.py), com imports a partir de `scripts/`, para ficar compativel com o runner padrao do repo.
- Montar fixtures com `tmp_path` para um repo minimo contendo `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`, `PRD-<PROJETO>.md`, `INTAKE-<PROJETO>.md` e `features/` vazio.
- Fixar a data via monkeypatch do `today_iso` do modulo do renderer para garantir snapshot textual estavel.
- Cobrir obrigatoriamente:
  - JSON valido gera manifestos aderentes ao template, incluindo `Evidencia no PRD`, `depende_de`, duplicacao de `business_objective` e tabela de impactos
  - estrutura de pastas sai correta, incluindo `FEATURE-<N>-<SLUG>/`, `user-stories/`, `auditorias/` e `FEATURE-<N>.md`
  - ordem e naming sao deterministas, inclusive ordem de paths retornados
  - projeto com `features/FEATURE-*` preexistente bloqueia com erro claro e nao cria novos artefatos
  - `blocked=true` nao renderiza ficheiros e expõe os blockers na mensagem
- Comando de validacao previsto: `.\scripts\run-pytest.ps1 tests/test_fabrica_features_renderer.py -q`

## Assumptions e Defaults
- O contrato de entrada continua exatamente o JSON enviado por voce; esta etapa nao adiciona `agent_id`, `intake_path` nem provider payloads.
- `intake_path` nao vem no JSON e sera derivado do projeto, porque o padrao atual do repo sempre usa `INTAKE-<PROJETO>.md`.
- O renderer nao faz merge, nao renumera e nao atualiza backlog existente em v1.
- Nenhuma mudanca de docs, prompts ou fluxo `Feature -> User Stories` entra neste escopo.
