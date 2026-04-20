# Task 2 — Hint por hash Bronze: explícito, revisável e confirmável

**Prioridade:** P1

## Problema

O SHA-256 do ficheiro é calculado no browser (`arrayBuffer`), seguido de `getLeadImportMetadataHint` e `applyBronzeImportHint`, que podem preencher plataforma, data, evento, origem e ativação com pouca fricção. O risco é **associar o ficheiro ao contexto errado** (evento/ativação) sem o operador perceber; além disso, ficheiros grandes pressionam memória só pelo hash.

## Escopo

- [frontend/src/pages/leads/ImportacaoPage.tsx](frontend/src/pages/leads/ImportacaoPage.tsx) — `handleSelectFile`, `applyBronzeImportHint`
- [frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts](frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts) — mesmo padrão de hint/hash por linha batch
- [frontend/src/services/leads_import.ts](frontend/src/services/leads_import.ts) — `computeFileSha256Hex`, `getLeadImportMetadataHint`
- UI: bloco “Metadados sugeridos” com diff antes/depois e confirmação explícita (opt-in), não autofill silencioso

## Critérios de aceite

1. Nenhum campo crítico (evento, ativação, origem do lote) é aplicado a partir do hint **sem** confirmação explícita do utilizador (ou equivalente com checkbox “Aplicar sugestões”).
2. A UI mostra **o que mudou** em relação aos valores já preenchidos.
3. (Opcional fase 2) Plano ou spike documentado para hashing no backend ou streaming quando o volume justificar.

## Plano de verificação

- Testes que hoje cobrem hint em [ImportacaoPage.test.tsx](frontend/src/pages/__tests__/ImportacaoPage.test.tsx) ajustados para o fluxo de confirmação.
- Caso manual: ficheiro com hash coincidente com import anterior — verificar que metadados não saltam para o contexto antigo sem aceite.

## Skills recomendadas (acionar na execução)

- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md)
- [.claude/skills/feature-forge/SKILL.md](.claude/skills/feature-forge/SKILL.md) — critérios de aceite e copy de produto.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task2.md`** com resumo, ficheiros tocados e diffs sugeridos.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Autofill por hash ajuda, mas está opaco e pode induzir erro**; **Priorização final** (item 2).
