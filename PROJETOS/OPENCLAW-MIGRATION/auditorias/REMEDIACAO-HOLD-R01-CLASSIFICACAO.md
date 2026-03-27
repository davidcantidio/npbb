---
doc_id: "REMEDIACAO-HOLD-R01-CLASSIFICACAO.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OPENCLAW-MIGRATION"
---

# Classificacao de follow-ups — remediacao hold MIGRATION-R01

Sessao alinhada a [PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md](../../COMUM/SESSION-REMEDIAR-HOLD.md) e parametros em [SESSION-REMEDIAR-HOLD.md](../SESSION-REMEDIAR-HOLD.md).

```text
CLASSIFICACAO DOS FOLLOW-UPS
─────────────────────────────────────────
Relatorio: PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md
Veredito:  hold
Destino padrao do relatorio: issue-local
DRIFT_INDICE: nenhuma (sync apos criacao de INTAKE/PRD/F1; Markdown canónico prevalece)
─────────────────────────────────────────

Follow-ups Bloqueantes:
| # | Resumo | Destino proposto | Feature/PRD afetado | Objetivo da fase | Epic candidato / motivo explicito | Alinhamento ou drift |
|---|---|---|---|---|---|---|
| B1 | Criar TEMPLATE-USER-STORY.md | issue-local | Feature 2 / PRD US-2.2; spec Task 2.2.1 | Remediar hold R01 em COMUM | EPIC-F1-01 | Alinhamento com ACHADO A-02 |
| B2 | Reescrever boot-prompt.md niveis 4-6 | issue-local | Feature 3 / PRD US-3.1; spec Task 3.1.1 | Idem | EPIC-F1-01 | Alinhamento com ACHADO A-01 |
| B3 | SESSION-REVISAR-US, MAPA, AUDITAR-FEATURE, GOV-SCRUM, depreciar legados | issue-local | Features 1 e 3; conformidade cruzada relatorio | Idem | EPIC-F1-01 | Alinhamento A-03, A-05, A-06 + SESSION-IMPLEMENTAR-US |
| B4 | Limpar GOV-FRAMEWORK-MASTER issue-first / fase fora deprecated | issue-local | Feature 1 / US-1.1 criterios | Idem | EPIC-F1-01 | Alinhamento A-04 |

Follow-ups Nao Bloqueantes:
| # | Resumo | Destino proposto | Feature/PRD afetado | Objetivo da fase | Epic candidato / motivo explicito | Alinhamento ou drift |
|---|---|---|---|---|---|---|
| — | nenhum no relatorio | — | — | — | — | — |

─────────────────────────────────────────
Resultado esperado do gate: APROVADO
Audit ID de Origem: MIGRATION-R01
─────────────────────────────────────────
```
