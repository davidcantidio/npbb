---
doc_id: "AUDIT-LOG.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# AUDIT-LOG - LP

## Politica

- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
- toda rodada deve registrar commit base, veredito e categoria dos achados materiais
- auditoria `hold` abre follow-ups rastreaveis
- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
- auditoria `go` e pre-requisito para mover fase a `feito/`
- cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada
  `hold` que gerou o item

## Gate Atual por Fase

| Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
|---|---|---|---|---|
| F1 | hold | auditoria_fluxo_ativacao.md | [auditoria_fluxo_ativacao.md](./auditoria_fluxo_ativacao.md) | Hold provisional regularizado a partir da auditoria de marco/2026; remediacao aberta via intake derivado |
| F2 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |
| F3 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |
| F4 | not_ready | nao_aplicavel | nao_aplicavel | Aguardando primeira auditoria formal |

## Resolucoes de Follow-ups

| Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
|---|---|---|---|---|---|---|---|
| 2026-03-13 | auditoria_fluxo_ativacao.md | F1 | F1-NAO01 + F1-NAO02 + F1-NAO03 + F1-NAO04 | new-intake | Remediacao controlada para contrato publico, paridade de submit e refatoracao estrutural exigida pelo hold | [INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md](./INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md) | Inclui o PRD sibling de remediacao e prepara reauditoria independente |
| 2026-03-13 | auditoria_fluxo_ativacao.md | F1 | F1-NAO08 | issue-local | Adicionada exigencia explicita de validacao automatizada de metadata/migracao para tabelas e indice da fundacao | [PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md](./PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md) | Cobertura fica acoplada ao sibling de remediacao porque o contrato e a estrutura mudam juntos |
| 2026-03-13 | auditoria_fluxo_ativacao.md | F1 | F1-RISCO01 | planned-separate | Risco LGPD de CPF em claro fica fora deste sibling para nao inflar a saida do hold | n/a | Abrir intake proprio se a PM priorizar a remediacao de dados em repouso |

## Rodadas

| Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| auditoria_fluxo_ativacao.md | F1 | 2026-03-13 | auditoria externa regularizada em chat | nao_informado | nao_aplicavel | hold | provisional | [auditoria_fluxo_ativacao.md](./auditoria_fluxo_ativacao.md) | drift de contrato no submit publico, campo obrigatorio ausente, monolitismo em `models.py`, cobertura de migracao/paridade insuficiente | new-intake | [INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md](./INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md) | nenhum |
