# Épicos — NPBB-LEADS / F3 — Gold: Pipeline
**version:** 1.0.0 | **last_updated:** 2026-03-03
**projeto:** NPBB-LEADS | **fase:** F3

## Objetivo da Fase
Executar o lead_pipeline (PROJETOS/lead_pipeline/) sobre os dados Silver de um lote,
normalizar e validar os dados, promover os leads aprovados para a tabela `leads`
(Gold) e disponibilizar o relatório de qualidade na UI.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Pipeline Tratamento Gold | Integrar lead_pipeline + promoção Gold + relatório | F2 concluída | ✅ | `EPIC-F3-01-PIPELINE-TRATAMENTO-GOLD.md` |

## Definition of Done da Fase
- [ ] `run_pipeline()` integrado como background task FastAPI
- [ ] Leads aprovados (PASS/PASS_WITH_WARNINGS) promovidos para tabela `leads`
- [ ] Lotes com FAIL: nenhum lead promovido, erros visíveis na UI
- [ ] `lead_batches.pipeline_report` preenchido com report.json
- [ ] Stage do lote atualizado para `gold`
- [ ] Fluxo E2E (upload → mapeamento → pipeline → leads na tabela) funcional
- [ ] CI verde