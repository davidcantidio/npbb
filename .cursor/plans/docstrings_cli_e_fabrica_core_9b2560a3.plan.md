---
name: Docstrings CLI e fabrica_core
overview: Docstrings (módulo + `__all__` real + `to_dict` onde aplicável) em npbb `lead_pipeline/cli.py` e em três módulos `fabrica_core` no fabrica, com bloco `Monólito:`. Critério de conclusão travado em fechamento verde — os três comandos de verificação devem passar (ver secção de baseline e done).
todos:
  - id: cli-npbb
    content: Docstrings módulo + build_parser + main em lead_pipeline/cli.py (npbb) com bloco Monólito
    status: pending
  - id: features-lean-fabrica
    content: Docstrings conforme __all__ real; canónico em SemanticValidationReportV2 e FeatureSpecDraft; alias só comentário curto na linha de atribuição
    status: pending
  - id: prd-bundle-fabrica
    content: Docstrings para os 13 exports de prd_features_bundle.py + to_dict(); build_candidate_feature_plan em PT completo
    status: pending
  - id: prd-provider-fabrica
    content: Docstrings para __all__ de prd_features_provider.py + módulo
    status: pending
  - id: verify-green
    content: Correr os 3 comandos fixos; done só com os três verdes (incl. corrigir F401 em features_lean se necessário)
    status: pending
isProject: false
---

# Docstrings com nota de monolithicidade

## Contexto importante

- **[npbb](c:\Users\NPBB\npbb):** [lead_pipeline/cli.py](c:\Users\NPBB\npbb\lead_pipeline\cli.py). Não há `scripts/fabrica_core/` no npbb.
- **[fabrica](c:\Users\NPBB\fabrica):** [features_lean.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\features_lean.py), [prd_features_bundle.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\prd_features_bundle.py), [prd_features_provider.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\prd_features_provider.py).

**Referência de uso:** [cli.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\cli.py) e testes sob `tests/` consomem estas APIs; este plano não obriga docstrings na CLI fabrica.

## Convenção de docstring

- **Estilo:** Google (resumo, `Args` / `Returns`, `Raises` quando fizer sentido).
- **Idioma:** português.
- **Bloco obrigatório:** `Monólito:` (frase curta).

---

## Escopo obrigatório — `__all__` real (working tree fabrica)

As listas abaixo reflectem o `__all__` obtido de `scripts/fabrica_core/features_lean.py` e `prd_features_bundle.py` no ramo actual. Se `__all__` mudar antes da implementação, **actualizar a lista no diff** ou repetir `rg "__all__" -A 30` no ficheiro.

### 1. [lead_pipeline/cli.py](c:\Users\NPBB\npbb\lead_pipeline\cli.py) (npbb)

Módulo, `build_parser`, `main` — cada um com `Monólito:` (ambos **não** monolíticos neste desenho).

### 2. [features_lean.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\features_lean.py) — **todas** as entradas de `__all__`

Lista canónica (23 símbolos):

`AcceptanceTraceItem`, `BlockingGap`, `CoverageContractValidationError`, `FeatureCandidate`, `FeatureSpecDraft`, `LayerImpact`, `LeanFeature`, `LeanProposal`, `PrdEvidence`, `RepairContextV2`, `SemanticValidationReport`, `SemanticValidationReportV2`, `normalize_provider_lean_payload`, `parse_proposal_text_to_dict`, `preflight_lean_bundle_inputs`, `preflight_lean_prd_to_features`, `read_proposal_text`, `generate_features_lean`, `load_proposal_json`, `render_feature_manifest`, `validate_and_render_lean_from_dict`, `validate_lean_proposal`, `write_feature_artifacts`.

**Aliases por atribuição (regra travada para implementação):**

- Em `features_lean.py` (linhas ~152 e ~206 no tree actual): `SemanticValidationReport = SemanticValidationReportV2` e `LeanFeature = FeatureSpecDraft`.

**O que fazer:**

- Docstring **canónica** (narrativa completa + `Monólito:`) apenas nas **classes base:** `SemanticValidationReportV2` e `FeatureSpecDraft`.
- Os nomes `SemanticValidationReport` e `LeanFeature` **não** são classes próprias: **não** leva docstring Python separada nesses identificadores (atribuição não suporta docstring de classe de forma útil sem criar ambiguidade para leitores e ferramentas).
- No máximo um **comentário curto** na mesma linha ou imediatamente acima da atribuição do alias (ex.: referência ao tipo canónico), **não** uma “docstring de remissão” como se fossem tipos documentáveis independentes.

`SemanticValidationReportV2` está em `__all__` e recebe a documentação principal; `SemanticValidationReport` em `__all__` continua a apontar para o mesmo objeto — a descoberta documental é via tipo base.

**Funções privadas** de estágio interno: docstring curta + `Monólito:` onde ajude leitura do módulo.

### 3. [prd_features_bundle.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\prd_features_bundle.py) — **todas** as entradas de `__all__` (13 símbolos)

`BlockingGap`, `CapabilityAtom`, `CandidateFeaturePlanItem`, `CandidateSeedEvidence`, `CoverageContract`, `CoverageContractItem`, `DerivedObligation`, `LiteralEvidenceSpan`, `PrdEvidenceSlice`, `PrdFeaturesLeanBundle`, `SourceBundleV2`, `build_candidate_feature_plan`, `build_prd_features_lean_bundle`.

- **Métodos `to_dict`:** docstring em cada um exposto no contrato JSON (payload estável / semântica dos campos), com `Monólito: não` salvo excepção justificada.
- **`build_candidate_feature_plan`:** docstring **completa em português** (entrada/saída, heurísticas, `Raises` se aplicável, `Monólito: sim` se o corpo for planner heurístico com funções aninhadas). Substituir/ampliar qualquer resquício de uma única linha em inglês.
- **`build_prd_features_lean_bundle`:** idem critério de completude + `Monólito:`.

### 4. [prd_features_provider.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\prd_features_provider.py) — `__all__`

`FABRICA_FEATURES_DEFAULT_OPENROUTER_MODEL`, `FeaturesProviderConfig`, `extract_json_object_from_model_output`, `load_features_provider_config`, `normalize_provider_model_ref`, `request_proposal_repair_text`, `request_proposal_text`.

Helpers privados críticos (`_request_text_with_fallback`, `_build_provider_payload`, …): docstring + `Monólito:`.

---

## Baseline de verificação (2026-04-05, revalidado) e critério de conclusão

**Baseline registado** na revalidação do aprovador (5 de abril de 2026):

| Comando | Resultado no baseline |
|--------|------------------------|
| `ruff check lead_pipeline/cli.py` (npbb) | **Verde** |
| Ruff fabrica nos três ficheiros `fabrica_core` abaixo | **Vermelho** com **2** achados **F401** (imports não usados) em [features_lean.py](c:\Users\NPBB\fabrica\scripts\fabrica_core\features_lean.py) nas linhas **21** e **26** |
| Pytest no alvo de quatro ficheiros | **Verde** — **41 passed** |

**Comandos (referência única):**

1. npbb:

```bash
cd C:\Users\NPBB\npbb && ruff check lead_pipeline/cli.py
```

2. fabrica:

```bash
cd C:\Users\NPBB\fabrica && ruff check scripts/fabrica_core/features_lean.py scripts/fabrica_core/prd_features_bundle.py scripts/fabrica_core/prd_features_provider.py
```

3. fabrica:

```bash
cd C:\Users\NPBB\fabrica && .venv\Scripts\python.exe -m pytest -q tests/test_prd_features_provider.py tests/test_candidate_feature_plan.py tests/test_lean_preflight.py tests/test_features_lean_contract.py
```

**Critério de done (travado — fechamento verde):**

- O trabalho só está **fechado** quando os **três** comandos acima terminam **sem falha** (Ruff npbb verde, Ruff fabrica verde, pytest verde).
- Isto implica, no mínimo, **corrigir os dois F401** em `features_lean.py` (por exemplo removendo ou usando os imports nas linhas indicadas pelo Ruff) **sem** alterar semântica observável pelos testes.
- Não há opções A/B nem “alternativa mínima”: o plano aprovado para execução segue **sempre** este fechamento verde.

---

## Alteração de comportamento

- **Docstrings** (e formatação compatível com o formatter) são o núcleo do trabalho.
- **Correcções mínimas para cumprir Ruff** (ex.: F401) são **permitidas e esperadas** para satisfazer o critério de done; devem ser mudanças triviais (imports / formatação) sem mudar contratos.
- Se algum teste regressar após edições, tratar antes do merge (ainda dentro do critério verde).
