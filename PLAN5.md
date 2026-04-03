# Builder Lean de Contexto para `PRD -> Features`

## Summary
- Adicionar uma API nova, apenas de biblioteca, para montar um bundle lean e serializável de contexto para `PRD -> Features`, sem tocar no fluxo atual de `generate_features` nem na CLI existente.
- O bundle vai carregar somente o PRD do projeto e os 4 docs nucleares de governança (`GOV-PRD`, `GOV-FEATURE`, `TEMPLATE-FEATURE`, `PROMPT-PRD-PARA-FEATURES`), e vai expor apenas evidências mínimas do PRD em vez de dumps integrais.
- `intake_path` entra só como referência de caminho quando existir; o corpo do intake não entra no hot path.
- A política lean de leitura de `SPEC-LEITURA-MINIMA-EVIDENCIA.md` será embutida em constantes/comportamento/documentação do código, sem ler esse doc no runtime do builder.
- Docs excluídos do hot path ficam fora tanto das leituras registradas quanto do payload serializado.

## Implementation Changes
- Criar `scripts/fabrica_core/prd_features_bundle.py` com a API pública `build_prd_features_lean_bundle(project_slug: str, *, repo_root: Path | None = None) -> PrdFeaturesLeanBundle`.
- Não alterar `scripts/fabrica_core/cli.py` nem substituir `generate_features`; o caminho determinístico atual continua intacto como fallback/manual.
- Não tocar em `scripts/fabrica_core/__init__.py`; o import explícito de `fabrica_core.prd_features_bundle` é suficiente nesta v1.

- Definir o contrato serializável com dataclasses pequenas e `to_dict()` JSON-safe:
  - `PrdFeaturesLeanBundle`
  - `PrdEvidenceSlice`
- Campos do bundle:
  - `schema_version`: `prd_features_lean/v1`
  - `stage`: `PRD_TO_FEATURES`
  - `project`
  - `project_root`
  - `prd_path`
  - `intake_path`
  - `project_metadata`
  - `runtime_inputs`
  - `read_policy`
  - `rules`
  - `prd_evidence`

- `project_metadata` virá de um allowlist do frontmatter do PRD:
  - `status`
  - `owner`
  - `intake_kind`
  - `source_mode`
  - `product_type`
  - `delivery_surface`
  - `business_domain`
  - `criticality`
  - `data_sensitivity`
  - `integrations`
  - `change_type`
  - `audit_rigor`

- `runtime_inputs` vai registrar exatamente os arquivos lidos pelo builder:
  - `governance_paths`: os 4 docs nucleares
  - `project_paths`: apenas o `prd_path`
- O builder deve ter um helper interno único de leitura de arquivo para permitir teste exato do allowlist do hot path.

- `read_policy` será explícita e curta:
  - `mode`: `lean_evidence_only`
  - `full_prd_in_bundle`: `false`
  - `load_intake_body`: `false`
  - `prd_targets`: `summary`, `problem`, `jobs`, `scope`, `metrics`, `restrictions`, `dependencies`, `hypotheses`, `architecture`, `rollout`, `risks`, `non_objectives`
- Não serializar lista de docs excluídos; a exclusão será garantida pelo allowlist de leitura e pelos testes.

- Implementar extração mínima de evidências do PRD com compatibilidade para as duas famílias de headings já presentes no repo:
  - legado/template: `### 2.4`, `### 2.5`, `### 2.6`, `### 2.7`, `## 3`, `## 4`, `## 5`, `## 8`
  - corpus atual: `## 5`, `## 6`, `## 7`, `## 8`, `## 9`, `## 10`, `## 13`
- `prd_evidence` será uma lista ordenada de slices com:
  - `key`
  - `section`
  - `items`
- Slices alvo:
  - `summary`
  - `problem`
  - `jobs`
  - `scope_in`
  - `scope_out`
  - `metrics`
  - `restrictions`
  - `dependencies`
  - `hypotheses`
  - `architecture`
  - `rollout`
  - `risks`
  - `non_objectives`
- Regras de extração:
  - usar bullets primeiro
  - cair para `sentence_candidates` se a seção for prosa
  - deduplicar
  - capar cada slice para um orçamento pequeno fixo
  - preservar a âncora real encontrada, por exemplo `5. Escopo > Dentro`

- Implementar síntese curta das regras dos 4 docs nucleares, sem transportar markdown bruto:
  - de `GOV-PRD`: elegibilidade do PRD e conteúdo proibido
  - de `GOV-FEATURE`: conteúdo obrigatório do manifesto e fronteiras com PRD/US/Tasks
  - de `TEMPLATE-FEATURE`: frontmatter obrigatório e seções obrigatórias do manifesto
  - de `PROMPT-PRD-PARA-FEATURES`: objetivo da etapa, contrato do hot path, constraints da proposta e campos obrigatórios da saída estruturada
- Não construir parser markdown genérico grande; usar extratores pequenos e direcionados para esses 4 documentos.

## Bundle Contract
```json
{
  "schema_version": "prd_features_lean/v1",
  "stage": "PRD_TO_FEATURES",
  "project": "<PROJETO>",
  "project_root": "PROJETOS/<PROJETO>",
  "prd_path": "PROJETOS/<PROJETO>/PRD-<PROJETO>.md",
  "intake_path": "PROJETOS/<PROJETO>/INTAKE-<PROJETO>.md",
  "project_metadata": {
    "status": "approved",
    "owner": "PM",
    "intake_kind": "new-capability",
    "source_mode": "original",
    "product_type": "internal-framework",
    "delivery_surface": "cli-deterministica",
    "business_domain": "engenharia",
    "criticality": "media",
    "data_sensitivity": "interna",
    "integrations": ["Postgres", "Markdown"],
    "change_type": "nova-capacidade",
    "audit_rigor": "standard"
  },
  "runtime_inputs": {
    "governance_paths": [
      "PROJETOS/COMUM/GOV-PRD.md",
      "PROJETOS/COMUM/GOV-FEATURE.md",
      "PROJETOS/COMUM/TEMPLATE-FEATURE.md",
      "PROJETOS/COMUM/PROMPT-PRD-PARA-FEATURES.md"
    ],
    "project_paths": [
      "PROJETOS/<PROJETO>/PRD-<PROJETO>.md"
    ]
  },
  "read_policy": {
    "mode": "lean_evidence_only",
    "full_prd_in_bundle": false,
    "load_intake_body": false,
    "prd_targets": [
      "summary",
      "problem",
      "jobs",
      "scope",
      "metrics",
      "restrictions",
      "dependencies",
      "hypotheses",
      "architecture",
      "rollout",
      "risks",
      "non_objectives"
    ]
  },
  "rules": {
    "stage_goal": "...",
    "hot_path_contract": ["..."],
    "prd_eligibility": ["..."],
    "prd_prohibited": ["..."],
    "feature_manifest_requirements": ["..."],
    "feature_frontmatter_fields": ["project", "feature_key", "feature_slug", "prd_path", "intake_path", "depende_de", "audit_gate"],
    "feature_sections": ["0. Rastreabilidade", "1. Objetivo de Negocio", "2. Comportamento Esperado", "3. Dependencias entre Features", "4. Criterios de Aceite", "5. Riscos Especificos", "7. Impactos por Camada"],
    "proposal_rules": ["..."],
    "proposal_output_fields": ["feature_key", "feature_slug", "title", "prd_evidence", "business_objective", "behavior_expected", "depends_on", "acceptance_criteria", "risks", "layer_impacts"]
  },
  "prd_evidence": [
    {
      "key": "scope_in",
      "section": "5. Escopo > Dentro",
      "items": ["..."]
    }
  ]
}
```

## Test Plan
- Criar `tests/test_prd_features_bundle.py` na raiz do repo para evitar o problema atual de descoberta/config do `pytest` ao mirar subpastas com `scripts/*/pyproject.toml`.
- Cobrir PRD válido com `json.dumps(bundle.to_dict())` bem-sucedido, `project_metadata` filtrado, `rules` preenchidas e slices mínimas presentes para `scope`, `metrics`, `restrictions`, `dependencies`, `rollout` e `risks`.
- Parametrizar o teste de PRD válido para os dois formatos de headings já existentes no corpus.
- Cobrir hot path estrito: fixture inclui os docs excluídos com conteúdo sentinela, mas o builder deve registrar leitura apenas de `PRD + 4 docs nucleares`; os docs excluídos e o corpo do intake não podem aparecer em `runtime_inputs` nem no JSON serializado.
- Comando de validação alvo:
  - `& '.\\.venv\\Scripts\\python.exe' -m pytest -q tests/test_prd_features_bundle.py`

## Assumptions and Defaults
- Esta v1 não decide `blocked=true`, não gera proposta JSON, não integra provider, não renderiza `FEATURE-*.md`, não faz merge com `features/` existentes e não adiciona CLI nova.
- O builder não inventa lacunas do PRD; ele expõe apenas as evidências encontradas. A decisão de elegibilidade/bloqueio fica para a camada seguinte.
- `intake_path` é referência opcional de rastreabilidade, não fonte de evidência do bundle lean.
- Os paths do bundle serão strings POSIX relativas ao repo para facilitar consumo externo.
- A política lean de `SPEC-LEITURA-MINIMA-EVIDENCIA.md` será materializada em código e comentários, não como doc carregado no runtime do builder.
