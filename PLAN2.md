# Consolidar Harness Lean `PRD -> Features`

## Summary

- O estado atual está desalinhado com os 4 docs nucleares já atualizados: o código ainda faz geração direta de Markdown a partir do PRD, sem bundle lean explícito, sem contrato JSON, sem validador determinístico e sem renderer separado.
- Há inconsistências concretas a corrigir:
  - `generate_features()` exige `AUDIT-LOG.md`, embora isso não faça parte do hot path lean.
  - O gerador atual sintetiza features por heurística de bullets/sentenças do PRD e já materializa conteúdo downstream implícito.
  - O manifesto renderizado não preenche `Evidencia no PRD`.
  - Não existe bloqueio claro para backlog canônico já existente sob `features/`.
  - Não existe plumbing de `agent_id`.
  - Os testes citados pela própria iteração (`tests/test_fabrica_cli.py`, `tests/test_pipeline_prd_feature_us_task_separation.py`, `tests/test_governance_docs.py`) não existem no clone atual.
- A consolidação deve manter o comando atual `fabrica generate features --project ...` funcionando, mas reencaminhá-lo para um pipeline interno único: `bundle -> proposal JSON -> validação -> render`.

## Key Changes

- Criar um módulo único novo em `scripts/fabrica_core/prd_features.py` para concentrar o harness lean da etapa, com quatro responsabilidades explícitas:
  - `build_prd_feature_bundle(project, repo_root)`:
    - lê apenas `PRD-<PROJETO>.md`, `PROJETOS/COMUM/GOV-PRD.md`, `PROJETOS/COMUM/GOV-FEATURE.md` e `PROJETOS/COMUM/TEMPLATE-FEATURE.md`;
    - extrai do PRD só as evidências mínimas desta etapa: escopo, métricas, restrições/guardrails, dependências/integrações, rollout e riscos globais;
    - carrega `intake_path` apenas como metadata opcional;
    - não lê nem inclui `boot-prompt`, `GOV-FRAMEWORK-MASTER`, `SESSION-DECOMPOR-PRD-EM-FEATURES`, `SPEC-PIPELINE-PRD-SEM-FEATURES` nem `AUDIT-LOG`.
  - `validate_prd_feature_proposal(payload, bundle)`:
    - valida deterministicamente o JSON esperado pelo prompt;
    - aceita `agent_id` apenas como string opcional opaca;
    - exige coerência entre `project`/`prd_path` do payload e o bundle;
    - aplica as regras mecânicas de `blocked`/`blockers`/`features`;
    - valida `feature_key` sequencial (`FEATURE-1..N`), `feature_slug` em maiúsculas com hífen, `depends_on` referindo apenas features da mesma proposta, sem autorreferência e sem ciclo;
    - exige `prd_evidence`, `business_objective`, `behavior_expected`, `acceptance_criteria`, `risks` e `layer_impacts` com as cinco chaves esperadas;
    - produz erros claros com caminho de campo, por exemplo `features[0].layer_impacts.testes: required`.
  - `render_prd_feature_proposal(validated, bundle)`:
    - escreve apenas o que o contrato validado contém;
    - gera `FEATURE-<N>.md` aderente a `GOV-FEATURE.md` e `TEMPLATE-FEATURE.md`;
    - preenche `## 0. Rastreabilidade`, `### Evidencia no PRD`, objetivo, comportamento, dependências, critérios, riscos e impactos por camada a partir do JSON;
    - mantém `status`, `audit_gate`, `generated_by` e `generator_stage` como scaffold operacional;
    - não persiste `agent_id` no manifesto;
    - não inventa User Stories nem Tasks; a seção `## 9. User Stories` fica no estado de placeholder do template, sem linhas concretas.
  - `proposal_from_legacy_prd(bundle)`:
    - reutiliza a heurística atual apenas como fallback/manual do comando legado;
    - gera um payload já no contrato JSON novo;
    - fica isolado do validador para não contaminar regras com heurística.

- Atualizar `scripts/fabrica_core/generation.py`:
  - `generate_features()` deixa de renderizar Markdown diretamente;
  - remove a dependência de `AUDIT-LOG.md` do hot path;
  - faz preflight explícito para bloquear quando já existir backlog canônico sob `features/`:
    - bloquear se houver `features/FEATURE-*` ou conteúdo canônico de backlog sob `features/`;
    - não bloquear por `features/` vazio criado pelo scaffold;
  - usa `proposal_from_legacy_prd()` quando nenhum payload externo for fornecido;
  - sempre passa por `validate_prd_feature_proposal()` antes de renderizar.
- Atualizar `scripts/fabrica_core/cli.py`:
  - manter `fabrica generate features --project ...` como caminho atual;
  - adicionar `--proposal-file <json>` opcional para integração mínima com runtime externo, sem provider integration;
  - quando `--proposal-file` existir, ler o JSON local e usar o mesmo pipeline de validação/render.
- Ajustar a compatibilidade mínima com o caminho legado downstream:
  - adaptar `generate_stories()` para não depender de linhas fictícias em `## 9. User Stories`;
  - se a tabela estiver vazia/placeholder, derivar um seed mínimo determinístico da própria feature (título ou primeiro item de comportamento) só para manter `generate stories` operacional;
  - esse fallback fica fora do hot path `PRD -> Features`.

## Public Interfaces

- `fabrica generate features` ganha `--proposal-file` opcional.
- Novo seam interno estável para a etapa:
  - `build_prd_feature_bundle(...)`
  - `validate_prd_feature_proposal(...)`
  - `render_prd_feature_proposal(...)`
- `agent_id` entra apenas no contrato JSON e no transporte interno; não vira campo de frontmatter, não entra no renderer e não acopla provider.

## Test Plan

- Criar `tests/test_fabrica_cli.py`:
  - sucesso: `generate features` com payload JSON válido renderiza manifestos corretos;
  - sucesso legado: `generate features` sem `--proposal-file` continua funcionando via fallback/manual;
  - bloqueio: projeto com backlog canônico já existente sob `features/` falha com mensagem clara;
  - falha estrutural: JSON inválido falha sem escrever arquivos.
- Criar `tests/test_pipeline_prd_feature_us_task_separation.py`:
  - garante que `PRD -> Features` não exige `AUDIT-LOG` nem lê docs fora do hot path;
  - garante que o manifesto de feature contém `Evidencia no PRD`;
  - garante que o renderer não inventa US/tasks;
  - garante que `generate stories` continua operando após o novo renderer.
- Criar `tests/test_governance_docs.py`:
  - trava o alinhamento entre `GOV-PRD.md`, `GOV-FEATURE.md`, `TEMPLATE-FEATURE.md` e `PROMPT-PRD-PARA-FEATURES.md`;
  - verifica a allowlist do bundle lean e a denylist dos docs fora do hot path;
  - verifica que o contrato JSON esperado pelos testes é o mesmo descrito no prompt.
- Executar pelo menos:
  - `.\scripts\run-pytest.ps1 tests/test_fabrica_cli.py -q`
  - `.\scripts\run-pytest.ps1 tests/test_pipeline_prd_feature_us_task_separation.py -q`
  - `.\scripts\run-pytest.ps1 tests/test_governance_docs.py -q`

## Assumptions

- Apenas `C:\Users\NPBB\fabrica` entra nesta rodada; `C:\Users\NPBB\npbb` não será tocado.
- A regra de bloqueio confirmada para v1 é: bloquear quando já houver backlog canônico sob `features/`; diretório `features/` vazio do scaffold continua permitido.
- O validador será custom Python, sem nova dependência como `jsonschema` ou `pydantic`.
- `SPEC-LEITURA-MINIMA-EVIDENCIA.md` orienta a implementação, mas não entra no bundle lean carregado.
- Próxima etapa natural para `agent_id`, fora desta iteração: um runtime externo gerar o JSON e passá-lo via `--proposal-file`, preservando `agent_id` só como metadata de rastreio no transporte.
