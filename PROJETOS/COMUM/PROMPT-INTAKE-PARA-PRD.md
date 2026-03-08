---
doc_id: "PROMPT-INTAKE-PARA-PRD.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# Prompt Canonico - Intake para PRD

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e informe o caminho do arquivo `INTAKE-*.md`.

## Prompt

Voce e um engenheiro de produto responsavel por transformar um intake estruturado em um PRD implementavel e auditavel.

### Leitura obrigatoria

1. `AGENTS.md`
2. `PROJETOS/COMUM/scrum-framework-master.md`
3. `PROJETOS/COMUM/SCRUM-GOV.md`
4. `PROJETOS/COMUM/WORK-ORDER-SPEC.md`
5. `PROJETOS/COMUM/ISSUE-FIRST-TEMPLATES.md`
6. `PROJETOS/COMUM/INTAKE-FRAMEWORK.md`
7. `PROJETOS/<PROJETO>/INTAKE-*.md`
8. `PROJETOS/<PROJETO>/DECISION-PROTOCOL.md`, se existir

### Passagem 1 - Validacao do intake

Antes de escrever o PRD, valide se o intake tem informacao suficiente.

- liste lacunas criticas que impedem um PRD confiavel
- nao invente regra de negocio ausente
- diferencie claramente fato, inferencia e hipotese
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, valide explicitamente sintoma, impacto, evidencia tecnica e escopo da remediacao
- se o intake vier de auditoria, valide a rastreabilidade para `origin_audit_id` e `origin_report_path`

Se houver lacunas criticas, pare apos a validacao e devolva apenas:

- resumo do que esta claro
- lacunas criticas
- perguntas objetivas que precisam ser respondidas
- decisao: `BLOQUEADO`

### Passagem 2 - Geracao do PRD

So execute esta passagem se o intake estiver pronto.

- gere um PRD claro, modular e sem ingenuidade de escopo
- preserve restricoes, nao-objetivos e riscos do intake
- traduza o contexto em fases, epicos e criterios de fatiamento coerentes
- inclua referencia explicita ao arquivo `INTAKE-*.md` usado como origem
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, produza um PRD de remediacao controlada, com escopo minimo necessario, riscos, rollback e criterios de validacao
- nao reclassifique remediation como novo produto sem justificativa documentada

### Requisitos minimos do PRD gerado

O PRD precisa sair com:

- objetivo e contexto
- escopo dentro/fora
- restricoes e riscos
- arquitetura afetada
- fatiamento por fases coerente
- indicadores de sucesso
- referencia explicita ao arquivo de intake

### Regra final

Se uma dependencia essencial estiver ausente, declare a lacuna. Nao complete silenciosamente o que o intake nao suporta.
