# Task 8 — Shell `/leads/importar`: jornadas separadas e menos estado na query string

**Prioridade:** P2

## Problema

O mesmo shell concentra Bronze simples, Bronze batch, ETL e navegação por `step`, `batch_id`, `context`, `mapping_mode`. A **carga cognitiva** e a reidratação por URL tornam o fluxo difícil de ensinar e fácil de usar no “modo errado”.

## Escopo

- [frontend/src/pages/leads/ImportacaoPage.tsx](frontend/src/pages/leads/ImportacaoPage.tsx) — `importFlow`, `bronzeMode`, `activeStep`, leitura de query params
- Rotas: avaliar rotas distintas ou landing de escolha (“Bronze” vs “ETL”) antes do wizard
- Copies e onboarding contextual por modo; reduzir dependência de query string como **única** fonte de verdade (estado persistido ou session store conforme desenho)

## Critérios de aceite

1. Entrada clara com **dois caminhos** perceptíveis (Bronze vs ETL), sem obrigar o utilizador a adivinhar o submodo.
2. Batch Bronze apresentado como **subproduto** explícito do caminho Bronze.
3. Testes de navegação / reidratação actualizados para as novas rotas ou estado persistido.

## Plano de verificação

- Percursos manuais documentados (3 personas: só ETL, só Bronze single, batch).
- Regressão dos testes em [ImportacaoPage.test.tsx](frontend/src/pages/__tests__/ImportacaoPage.test.tsx).

## Skills recomendadas (acionar na execução)

- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md)
- [.claude/skills/feature-forge/SKILL.md](.claude/skills/feature-forge/SKILL.md)
- [.claude/skills/architecture-designer/SKILL.md](.claude/skills/architecture-designer/SKILL.md)
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task8.md`**.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Shell único com complexidade cognitiva alta**; **Priorização final** (item 8).
