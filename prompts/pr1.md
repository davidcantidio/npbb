# pr1 — Contexto global para o Codex (Fabrica + npbb)

## Quem és e o que vais fazer

És um agente de implementação (Codex) com acesso ao filesystem. O objetivo é **fechar semanticamente** o caminho **provider-backed** de `PRD -> Features` na **Fabrica**, de forma que o comando abaixo **convirja sem `--proposal-file`** para o projeto operacional **ATIVOS-INGRESSOS** no npbb, **sem enfraquecer** o validador lean.

Comando-alvo (Windows PowerShell, após código pronto e preflight ok):

`python .\scripts\fabrica.py --repo-root C:\Users\NPBB\npbb generate features --project ATIVOS-INGRESSOS`

## Dois repositórios (não confundir)

| Papel | Caminho | O que mudas |
|--------|---------|-------------|
| **Framework** | `C:\Users\NPBB\fabrica` | Hot path: `scripts\fabrica_core\prd_features_bundle.py`, `prd_features_provider.py`, `features_lean.py`, `cli.py`; testes em `tests\`. |
| **Projeto operacional** | `C:\Users\NPBB\npbb` | Apenas `PROJETOS\ATIVOS-INGRESSOS\features\FEATURE-*` quando fores **regenerar** para teste E2E; **não** editar PRD nem Intake. |

## Fonte de verdade de produto

- Canónico: `npbb\PROJETOS\**\*.md` (governança e artefatos).
- **Não** usar `PLAN1.md` nem `.cursor/plans` como fonte de requisitos; só contexto humano.

## Problema atual (finding)

- O **bundle** já expõe `coverage_contract` com `scope_in_items` completos (ex.: **10** bullets em ATIVOS-INGRESSOS).
- O **validador** em `features_lean.py` exige cobertura **total** de cada `scope_in_*`, **no máximo 2** itens por feature, **sem duplicar** o mesmo item entre features, e **pelo menos uma aresta** `depends_on` quando há múltiplas features.
- O **modelo** (OpenRouter) tende a **underdecomposition** (ex.: parar em 5 features) mesmo com prompt/repair — porque a **cardinalidade** ainda é inferida pelo LLM a partir de texto.
- **Structured JSON schema** sozinho garante formato, **não** garante o recorte de negócio certo.

## Direção da solução (acordada)

1. Adicionar ao bundle lean (`prd_features_lean/v1`) um campo **aditivo** `candidate_feature_plan`: lista de **candidatos finais** (não um candidato bruto por cada `scope_in_item` se houver merges permitidos).
2. Um **planner determinístico** no bundle constrói esse plano a partir de `coverage_contract.scope_in_items` + regras v1 de merge.
3. O **provider** deixa de usar âncoras como “minimum plausible feature count” / “uma feature por item” como meta; em vez disso deve **materializar uma feature por entrada do `candidate_feature_plan`**, preservando `seed_evidence` literal e **sem omitir** candidatos.
4. O **repair** passa a receber um `repair_context` **estruturado** (missing keys, duplicados, overmerge, edges, payload anterior), não só uma string de erro concatenada.
5. O **validador** continua a levantar as **mesmas mensagens** visíveis ao utilizador, mas expõe **internamente** um relatório estruturado para alimentar o repair.

## Regras v1 do planner (merge)

- Itens cujo `basis` **começa por** `regra de ` → tratar como `facet_rule`; tentar fundir com a capacidade primária **mais relacionada** (heurística v1), **sem** exceder `max_scope_in_items_per_feature` (hoje **2**).
- Itens cujo `basis` **começa por** `contratos de API` → `facet_contract`; tentar fundir com candidato de **persistência / integração** mais relacionado.
- Itens sem pareamento claro → candidato próprio.
- **Nenhum** merge pode violar o limite de 2 `scope_in` por feature.

## Oráculo de regressão para ATIVOS-INGRESSOS (10 → 8 candidatos)

O planner, para este PRD, deve produzir **8** candidatos finais com agrupamentos:

- `[scope_in_01]`
- `[scope_in_02]`
- `[scope_in_03, scope_in_04]`
- `[scope_in_05]`
- `[scope_in_06]`
- `[scope_in_07, scope_in_10]`
- `[scope_in_08]`
- `[scope_in_09]`

**Nota:** isto orienta testes e o comportamento esperado **neste** PRD; o código do planner deve permanecer **genérico** para outros projetos (degradação: sem merge → um candidato por item).

## Campos sugeridos por candidato final

Cada entrada de `candidate_feature_plan` deve ser **compacta** (chaves, listas curtas):

- `candidate_key` (estável, ex. `cand_01` … `cand_08`)
- `scope_in_keys` (lista de `scope_in_XX`)
- `seed_evidence` (lista de `{section, basis}` **literais** copiados dos itens do contrato)
- `kind` (`primary_capability` | `facet_rule` | `facet_contract` | …)
- `suggested_title_seed`, `suggested_slug_seed` (curtos; o modelo pode refinar título/texto)
- `depends_on_candidates` (lista de `candidate_key` ou vazio — depois mapear para `FEATURE-*` na proposal na **ordem** do plano)

## O que NÃO fazer

- **Não** editar [PRD-ATIVOS-INGRESSOS.md](c:/Users/NPBB/npbb/PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md) nem [INTAKE-ATIVOS-INGRESSOS.md](c:/Users/NPBB/npbb/PROJETOS/ATIVOS-INGRESSOS/INTAKE-ATIVOS-INGRESSOS.md).
- **Não** relaxar `coverage_contract`, mínimos de `behavior_expected` / `acceptance_criteria`, nem a regra de dependências em multi-feature.
- **Não** colocar `feature_proposal.py` no hot path do `generate features`.
- **Não** fazer `git reset` cego no npbb; respeitar alterações alheias.

## Preflight lean no npbb

`preflight_lean_prd_to_features` **bloqueia** se existirem pastas `PROJETOS\<PROJETO>\features\FEATURE-*`. Para rerodar E2E, remove **apenas** essas pastas do ATIVOS-INGRESSOS, não o resto do worktree.

## Variáveis e sync Postgres

- Canónica: `FABRICA_PROJECTS_DATABASE_URL`.
- `apply_repo_env_files` em [fabrica/scripts/fabrica_core/repo_env.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/repo_env.py) lê `npbb/.env` e `npbb/backend/.env` **sem sobrescrever** env já definido.
- Se a URL estiver ausente, o CLI **não** falha por isso — apenas **não** sincroniza o read model.

## Próximos prompts

- **pr2:** implementação fatia A (bundle + planner + testes).
- **pr3:** fatia B (provider + repair_context).
- **pr4:** fatia C (validator estruturado + CLI + testes integrados).
- **pr5:** validação manual npbb + pytest + Postgres opcional.
