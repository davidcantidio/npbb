# Handoff: Verificacao Independente do Harness de Features

Data: `2026-04-05`
Repo alvo: `C:\Users\NPBB\fabrica`
Objetivo da proxima sessao: verificar, de forma independente, se a implementacao do plano "Harness Enterprise para Manifestos de Feature 10/10" esta correta, consistente e funcionando ponta a ponta.

## Escopo do que foi implementado

O trabalho foi feito no caminho lean `PRD -> Features`, evoluindo o fluxo para um contrato semantico mais forte.

Principais entregas:

- bundle `prd_features_lean/v2` com `source_bundle_v2`, `capability_atoms` e `derived_obligations`
- `FeatureSpecDraft` com `operational_policies`, `acceptance_trace_matrix`, `derived_obligation_keys` e `feature_candidate`
- gates semanticos para:
  - rastreabilidade/evidencia
  - ambiguidade
  - claims tecnicos nao sustentados
  - prontidao para decomposicao
  - mutation policy
  - audit/compliance obligations
- renderer da feature com secao `Politicas Operacionais Relevantes`
- secao de US sem placeholders falsos, mas com marcador explicito do ponto de inicio da decomposicao
- provider/CLI com suporte a repair semantico e `repair_model`

## Arquivos alterados

Arquivos diretamente alterados por esta implementacao:

- `scripts/fabrica_core/prd_features_bundle.py`
- `scripts/fabrica_core/features_lean.py`
- `scripts/fabrica_core/prd_features_provider.py`
- `scripts/fabrica_core/cli.py`
- `scripts/fabrica_core/generation.py`
- `scripts/fabrica_core/prd_features.py`
- `tests/test_features_lean_contract.py`
- `tests/test_fabrica_cli.py`
- `tests/test_prd_features_provider.py`

## Resultado conhecido no momento do handoff

Testes executados com sucesso:

- `python -m pytest tests/test_features_lean_contract.py tests/test_fabrica_cli.py tests/test_prd_features_provider.py -q`
- `python -m pytest tests/test_candidate_feature_plan.py -q`
- `python -m pytest tests/test_prd_features.py tests/test_pipeline_prd_feature_us_task_separation.py -q`

Resultado observado:

- `49 passed`
- `5 passed`
- `6 passed`

Total validado diretamente: `60 testes passados`

## Pontos que exigem verificacao independente

1. Confirmar que o `mutation_policy` agora dispara apenas quando o escopo canonico coberto realmente indica mutacao operacional, e nao por texto generico do manifesto.
2. Confirmar que `acceptance_trace_matrix` esta sendo exigido e validado de forma coerente com o bundle.
3. Confirmar que o provider prompt/schema refletem corretamente os novos campos e que o fluxo de repair usa `repair_model` apenas para falhas semanticas/cobertura.
4. Confirmar que o manifesto renderizado ficou aderente ao objetivo:
   - ha `Politicas Operacionais Relevantes`
   - nao ha linhas falsas de US
   - ainda existe um marcador textual claro para onde a decomposicao em US comeca
5. Confirmar que o bundle `v2` nao quebrou a compatibilidade operacional do fluxo lean.

## Como verificar

### 1. Ler o diff relevante

Rodar:

```powershell
git diff -- scripts/fabrica_core/prd_features_bundle.py scripts/fabrica_core/features_lean.py scripts/fabrica_core/prd_features_provider.py scripts/fabrica_core/cli.py scripts/fabrica_core/generation.py scripts/fabrica_core/prd_features.py tests/test_features_lean_contract.py tests/test_fabrica_cli.py tests/test_prd_features_provider.py
```

### 2. Rodar a bateria focal

```powershell
python -m pytest tests/test_features_lean_contract.py tests/test_fabrica_cli.py tests/test_prd_features_provider.py tests/test_candidate_feature_plan.py tests/test_prd_features.py tests/test_pipeline_prd_feature_us_task_separation.py -q
```

### 3. Fazer revisao tecnica de comportamento

Checar especialmente estes pontos em `scripts/fabrica_core/features_lean.py`:

- `_feature_requires_mutation_policy`
- `_applicable_derived_obligations`
- `_validate_acceptance_trace_matrix_semantics`
- `_analyze_semantic_quality`
- `validate_lean_proposal`
- `render_feature_manifest`

Checar estes pontos em `scripts/fabrica_core/prd_features_bundle.py`:

- `SCHEMA_VERSION = "prd_features_lean/v2"`
- `_build_source_bundle_v2`
- `_build_derived_obligations`
- `_build_capability_atoms`
- `_FEATURE_SECTIONS`

Checar estes pontos em `scripts/fabrica_core/prd_features_provider.py`:

- prompt do provider
- JSON schema dos features
- `FeaturesProviderConfig.repair_model`
- `request_proposal_repair_text(..., use_repair_model=...)`

### 4. Fazer smoke mental ou manual do fluxo

Verificar se o fluxo abaixo faz sentido de ponta a ponta:

`PRD/intake -> bundle v2 -> provider -> validate_lean_proposal -> render_feature_manifest`

## Criterios de aceite da verificacao

A proxima sessao deve considerar o trabalho ok somente se:

- a bateria focal acima continuar verde
- nao houver bug claro de precedencia entre gates estruturais e gates semanticos
- nao houver falso positivo evidente do `mutation_policy`
- nao houver claims tecnicos inventados passando sem gate
- o manifesto final continuar pronto para servir de ponto de partida para `Feature -> User Stories`

## Contexto importante do worktree

O repo ja estava sujo antes deste trabalho. Existem mudancas nao relacionadas que nao devem ser revertidas durante a verificacao.

Estado observado no momento do handoff:

- alterados preexistentes em docs/governanca/README/tests nao relacionados a este trabalho
- arquivo untracked preexistente: `scripts/fabrica_core/logging_setup.py`

A verificacao deve focar no diff listado em "Arquivos alterados" e evitar conclusoes baseadas em arquivos fora desse recorte.

## Pedido para o proximo agente

Fazer uma verificacao independente em modo review, priorizando:

- bugs
- regressao comportamental
- falhas de contrato
- inconsistencias entre bundle, provider, validador e renderer
- lacunas de teste

Se encontrar problema real, apontar com arquivo/linha e descrever o impacto. Se nao encontrar problema, registrar explicitamente que nao foram encontrados findings e mencionar apenas riscos residuais.
