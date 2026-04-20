# Task 4 — Preview ETL: drilldown operacional (grade, export, duplicados)

**Prioridade:** P1

## Problema

O `EtlPreviewStep` resume o resultado sobretudo em **alerts** (`dq_report`), sem uma camada intermédia para o operador corrigir o ficheiro com eficiência: falta grade tabular de rejeições, filtros por regra, export CSV de erros e clareza em duplicidades (qual linha “vence” e porquê).

## Escopo

- [frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx](frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx) — componente `EtlPreviewStep` e dados expostos ao cliente
- Backend: garantir que o payload de preview expõe amostras/campos suficientes para a grade (`_RejectedRowsCheck`, `_DuplicateRowsCheck` e estruturas já existentes)
- Download CSV “rejeitadas + motivo” (endpoint ou geração client-side a partir do JSON já devolvido)

## Critérios de aceite

1. Tabela ou grade com **filtro por tipo de erro / regra**, linha física e coluna quando aplicável.
2. Acção de **export** (CSV ou Excel leve) com linhas rejeitadas e motivo.
3. Para warnings de duplicidade, texto ou UI que indique **qual ocorrência prevalece** e o critério.

## Plano de verificação

- Testes de componente do preview ETL (Vitest) com `dq_report` fixture.
- Teste manual com ficheiro de várias rejeições e duplicados.

## Skills recomendadas (acionar na execução)

- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md)
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md)
- [.claude/skills/api-designer/SKILL.md](.claude/skills/api-designer/SKILL.md) — contrato de dados do preview se for estendido.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task4.md`**.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Preview ETL é informativo, mas pouco operacional**; **Priorização final** (item 4).
