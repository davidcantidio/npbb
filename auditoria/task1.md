# Task 1 — Bronze: pré-revisão antes de persistir o `LeadBatch`

**Prioridade:** P0

## Problema

No fluxo Bronze, o utilizador confirma metadados e o sistema chama `createLeadBatch` antes de uma validação operacional rica do ficheiro. O preview só vem depois, por `batch_id`, o que cria assimetria face ao ETL (`preview → commit`) e aumenta risco de lotes errados já gravados e difíceis de “desfazer” na percepção do operador.

## Escopo

- [frontend/src/pages/leads/ImportacaoPage.tsx](frontend/src/pages/leads/ImportacaoPage.tsx) — `handleSubmitStep1`, fluxo Bronze antes de `createLeadBatch`
- Serviços [frontend/src/services/leads_import.ts](frontend/src/services/leads_import.ts) — `createLeadBatch`, `getLeadBatchPreview` (ou equivalentes)
- Backend: endpoints de lote Bronze / preview se for necessário expor pré-análise sem persistir o binário
- Copy de UI: botão “Enviar para Bronze” vs mensagem explícita de que o lote será criado (mitigação mínima se o preview sem persistência for faseada)

## Critérios de aceite

1. O operador vê **cabeçalho detectado, amostra de linhas e validações básicas** antes da criação definitiva do `LeadBatch`, **ou** a UI deixa inequívoco que o lote é criado imediatamente e porquê (mitigação documentada + testes).
2. O caminho Bronze aproxima-se semanticamente de `preview → confirmação → persistência` (mesmo que a persistência continue a ser `LeadBatch` numa segunda chamada).
3. Testes de front (e/ou integração) cobrem o novo passo e regressão do fluxo ETL não é quebrada.

## Plano de verificação

- Testes existentes em [frontend/src/pages/__tests__/ImportacaoPage.test.tsx](frontend/src/pages/__tests__/ImportacaoPage.test.tsx) actualizados ou novos casos para o passo intermédio.
- Repro manual: `/leads/importar` modo Bronze — confirmar ordem percebida preview vs criação de lote.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — estado do wizard, steps e formulários complexos.
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md) — tipos dos serviços e props.
- [.claude/skills/fullstack-guardian/SKILL.md](.claude/skills/fullstack-guardian/SKILL.md) — contrato API + UX coerente com o backend.
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — se for necessário novo endpoint de pré-preview.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — Vitest/React Testing Library.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task1.md`** com resumo, lista de ficheiros tocados e indicações de `git diff` / riscos de deploy.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Bronze persiste antes de validar de verdade**; **Priorização final** (item 1).
