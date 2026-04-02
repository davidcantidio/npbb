---
doc_id: "SESSION-REFATORAR-MONOLITO.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# SESSION-REFATORAR-MONOLITO - Mini-Projeto de Refatoracao Estrutural

## Parametros obrigatorios

```
PROJETO:      <nome do projeto>
INTAKE_PATH:  <caminho completo do intake de remediacao>
ARQUIVO_ALVO: <arquivo ou funcao alvo>
AUDIT_REF:    <ID da auditoria de origem ou "nao_aplicavel">
```

## Prompt

Voce e um engenheiro senior operando em sessao de chat interativa.

Conduza o fluxo abaixo:

1. validar o intake de remediacao
2. gerar PRD de refatoracao com escopo minimo e rollback; esta e a unica etapa
   que continua exigindo aprovacao humana explicita
3. apos o PRD aprovado, decompor em features, user stories e tasks de extracao com
   gate do agente senior
4. executar user story a user story no loop do agente local ate `ready_for_review`
5. revisar e auditar compatibilidade de interface com o agente senior no fim

Nao introduza confirmacoes humanas adicionais apos a aprovacao do PRD.

Use, conforme a etapa:

- `SESSION-CRIAR-PRD.md`
- `SESSION-DECOMPOR-PRD-EM-FEATURES.md`
- `SESSION-DECOMPOR-FEATURE-EM-US.md`
- `SESSION-DECOMPOR-US-EM-TASKS.md`
- `SESSION-IMPLEMENTAR-US.md`
- `SESSION-AUDITAR-FEATURE.md`
- `SPEC-ANTI-MONOLITO.md`

Se o intake nao sustentar a decomposicao com rastreabilidade suficiente, responda `BLOQUEADO`.
