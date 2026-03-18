---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-03-002-Entregar-navegacao-hierarquica-e-edicao-de-artefatos"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Entregar detalhe e edicao de artefatos persistidos

## objetivo

permitir abrir o artefato selecionado e editar seus dados persistidos

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/framework/FrameworkDetailPage.tsx`
- `frontend/src/components/framework/ArtifactEditor.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkArtifactEditor.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir exibicao e edicao dos dados persistidos do artefato selecionado
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkArtifactEditor.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkArtifactEditor.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue abrir e editar o artefato persistido.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkArtifactEditor.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a edicao exigir conflict resolution ainda nao definida
