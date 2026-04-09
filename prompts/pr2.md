# pr2 - Fatia A: bundle lean + planner deterministico + testes

> Estado atual do workspace: esta fatia ja foi implementada no repo `fabrica`.
> Usa este ficheiro como handoff historico da parte `bundle + planner`,
> nao como instrucao assumindo um repo ainda sem alteracoes posteriores.

## Escopo desta fatia

Alterar **apenas** o repositorio Fabrica: [c:\Users\NPBB\fabrica](c:\Users\NPBB\fabrica).

Ficheiro principal: [scripts/fabrica_core/prd_features_bundle.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/prd_features_bundle.py).

## Objetivo

1. Manter `schema_version: prd_features_lean/v1` e todos os campos atuais do bundle.
2. Adicionar **`candidate_feature_plan`** ao dict serializado por `PrdFeaturesLeanBundle.to_dict()` como campo **aditivo**.
3. Implementar funcao(oes) puras que, dado `CoverageContract` (ou `scope_in_items + max_scope_in_items_per_feature`), produzam `candidate_feature_plan` conforme regras em **pr1**.

## Forma dos dados

- `candidate_feature_plan`: lista ordenada de objetos JSON-serializaveis, cada um com pelo menos:
  - `candidate_key: str`
  - `scope_in_keys: list[str]`
  - `seed_evidence: list[{"section": str, "basis": str}]` com copia literal de `section` e `basis`
  - `kind: str`
  - `suggested_title_seed: str`
  - `suggested_slug_seed: str` em `MAIUSCULAS-COM-HIFEN`
  - `depends_on_candidates: list[str]`

## Resultado observado no estado atual

- O bundle `prd_features_lean/v1` ja serializa `candidate_feature_plan`.
- O planner deterministico ja existe em [scripts/fabrica_core/prd_features_bundle.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/prd_features_bundle.py).
- Os testes relacionados hoje vivem em:
  - [tests/test_lean_preflight.py](c:/Users/NPBB/fabrica/tests/test_lean_preflight.py)
  - [tests/test_candidate_feature_plan.py](c:/Users/NPBB/fabrica/tests/test_candidate_feature_plan.py)
- No caso real `ATIVOS-INGRESSOS`, o estado validado hoje e:
  - `coverage_contract.scope_in_items = 10`
  - `candidate_feature_plan = 8`
  - agrupamentos:
    - `[scope_in_01]`
    - `[scope_in_02]`
    - `[scope_in_03, scope_in_04]`
    - `[scope_in_05]`
    - `[scope_in_06]`
    - `[scope_in_07, scope_in_10]`
    - `[scope_in_08]`
    - `[scope_in_09]`

## Oraculo ATIVOS

Criar teste que constroi o bundle para projeto **ATIVOS-INGRESSOS** com `--repo-root` apontando para **npbb** ou fixture equivalente.

**Assert:** `len(candidate_feature_plan) == 8` e os agrupamentos de `scope_in_keys` sao **exatamente** os de `pr1`.

## Teste generico

Fixture minima (`temp_repo`) com 2-3 `scope_in` sem merge -> numero de candidatos = numero de itens.

## Comandos

```powershell
cd C:\Users\NPBB\fabrica
Remove-Item -LiteralPath 'C:\Users\NPBB\fabrica\.tmp-pytest' -Recurse -Force -ErrorAction SilentlyContinue
python -m pytest tests\test_lean_preflight.py tests\test_candidate_feature_plan.py tests\ -q
```

## Criterio de conclusao da fatia A

- `python -m pytest tests\ -q` verde.
- `generate features --bundle-only --repo-root npbb --project ATIVOS-INGRESSOS` mostra `candidate_feature_plan` no JSON com 8 entradas e chaves coerentes.

No estado atual, este criterio ja foi observado com sucesso.

## Nao fazer nesta fatia

- Historicamente, esta fatia nao exigia alterar ainda `prd_features_provider.py` nem o loop de repair em `cli.py`.
- No estado atual do repo, essas mudancas ja existem porque `pr1` foi implementado ponta a ponta.
