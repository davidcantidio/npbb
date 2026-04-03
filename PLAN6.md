# Lean PRD -> Features Acceptance Coverage

## Summary

- Tratar `C:\Users\NPBB\fabrica` como repo primário e criar a suíte root `tests/`, porque o wrapper `scripts/run-pytest.ps1` já aponta para `tests/` e hoje ela não existe.
- Introduzir um harness lean mínimo e interno em `scripts/fabrica_core/` só para viabilizar bundle/preflight/validator/renderer testáveis; não fazer cutover da CLI para esse hot path nesta mudança.
- Preservar o caminho determinístico antigo em `generate_features` para projetos limpos, adicionando apenas guardrails não destrutivos compartilhados.

## Implementation Changes

- Criar `scripts/fabrica_core/prd_features_lean.py` com quatro seams puras:
  - `build_prd_features_bundle(...)`: monta o contexto lean usando apenas `PRD-<PROJETO>.md`, `GOV-PRD.md`, `GOV-FEATURE.md` e `TEMPLATE-FEATURE.md`; do PRD, extrai só as seções lean (`Escopo`, `Resultado de Negocio e Metricas`, `Restricoes e Guardrails`, `Dependencias e Integracoes`, `Rollout e Comunicacao`, `Riscos Globais`).
  - `preflight_prd_features_bundle(...)`: retorna resultado estruturado com `blocked`/`blockers`; bloqueia PRD com backlog estruturado (`FEATURE-*`, `US-*`, headings/tabelas equivalentes) e bloqueia projetos que já tenham `features/FEATURE-*`.
  - `validate_prd_features_proposal_json(raw_json, ...)`: faz `json.loads`, valida campos obrigatórios e regras mínimas pedidas nesta iteração.
  - `render_prd_features_proposal(...)`: gera apenas manifestos `FEATURE-*.md` e pastas `features/FEATURE-<N>-<SLUG>/`; não cria US, TASK nem integração com provider.
- Ajustar `scripts/fabrica_core/generation.py` só no necessário:
  - extrair um helper pequeno de guardrails reaproveitável;
  - aplicar no caminho legado apenas os bloqueios seguros desta iteração: `features/FEATURE-*` já existentes e backlog estruturado dentro do PRD;
  - não aplicar ao legado a elegibilidade lean mais rica, para não quebrar o fluxo determinístico atual em projetos válidos.
- Não mexer em `cli.py` além do estritamente necessário para expor/importar o helper novo, se isso simplificar os testes.
- Criar `tests/conftest.py` com fixture de repo temporário:
  - cria `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` para `resolve_framework_root`;
  - copia os docs canônicos atuais de `PROJETOS/COMUM/` usados pelos testes;
  - materializa projeto mínimo com `INTAKE`, `PRD`, `AUDIT-LOG` e, conforme o caso, `features/` preexistente.
- Criar `tests/test_prd_to_features_lean.py` para o harness lean.
- Criar `tests/test_fabrica_cli.py` para a compatibilidade do caminho antigo via `fabrica_core.cli.main(..., sync_runner=noop)`.
- Criar `tests/test_governance_docs.py` para travar a parte “explícita e documentada” dos guardrails em `GOV-PRD.md` e `PROMPT-PRD-PARA-FEATURES.md`.

## Test Plan

- `PRD válido, sem features existentes`
  - bundle lean inclui só os 4 docs permitidos e só os trechos whitelisted do PRD;
  - `validate_prd_features_proposal_json` aceita um payload válido;
  - `render_prd_features_proposal` cria `FEATURE-1.md`/`FEATURE-2.md` com `feature_key`, `feature_slug`, `prd_path`, `intake_path`, `depende_de`, bloco `Evidencia no PRD`, 3 critérios de aceite e tabela de impactos por camada;
  - assert explícito de que não surgem `README.md` de US nem `TASK-*.md`.
- `PRD inválido por listar backlog no próprio PRD`
  - fixture com `FEATURE-1`, `US-1-01` e/ou heading `Feature 1`;
  - `preflight_prd_features_bundle` retorna `blocked=True` e blocker contendo “PRD”, “backlog estruturado” e “PRD -> Features”.
- `JSON inválido da IA`
  - `feature_key` duplicado entre features;
  - `acceptance_criteria` com menos de 3 itens não vazios;
  - `depends_on` apontando para `FEATURE-*` ausente na própria proposta;
  - campo obrigatório ausente, usando `feature_slug` como caso mecânico;
  - cada caso deve falhar com mensagem assertada por substring clara e estável.
- `Hot path lean`
  - fixture inclui também `boot-prompt.md`, `GOV-FRAMEWORK-MASTER.md`, `SESSION-DECOMPOR-PRD-EM-FEATURES.md` e `SPEC-PIPELINE-PRD-SEM-FEATURES.md`;
  - assert de que o bundle final não carrega nenhum desses docs excluídos.
- `Compatibilidade com fluxo antigo`
  - teste via `cli.main(["--repo-root", tmp_repo, "generate", "features", "--project", ...], sync_runner=noop)` em projeto válido e limpo;
  - assert de saída zero e presença dos manifestos do caminho determinístico antigo.
- `Projeto com features/ preexistentes`
  - fixture com `features/FEATURE-9-LEGADO/FEATURE-9.md`;
  - lean preflight bloqueia com mensagem explícita sobre v1 não renumerar nem fazer merge;
  - teste documental confirma que `PROMPT-PRD-PARA-FEATURES.md` continua registrando esse bloqueio.

## Verification

- Rodar:
  - `.\scripts\run-pytest.ps1 tests/test_prd_to_features_lean.py -q`
  - `.\scripts\run-pytest.ps1 tests/test_fabrica_cli.py -q`
  - `.\scripts\run-pytest.ps1 tests/test_governance_docs.py -q`
  - `.\scripts\run-pytest.ps1 tests/ -q`
- Não tentar “`pytest -q` na raiz” como meta desta entrega; os conflitos atuais entre `scripts/fabrica_domain/tests` e `scripts/openclaw_domain/tests` permanecem fora de escopo.

## Assumptions

- “Acceptance criteria insuficientes” nesta iteração significa menos de 3 critérios não vazios, alinhado ao shape de `TEMPLATE-FEATURE.md`.
- O harness lean será usado diretamente pelos testes e por helpers internos; o hot path da CLI não será promovido por padrão nesta mudança.
- Não haverá provider integration, nem extensão para `Feature -> User Stories`, nem reescrita ampla de `generation.py`/`markdown.py`.
