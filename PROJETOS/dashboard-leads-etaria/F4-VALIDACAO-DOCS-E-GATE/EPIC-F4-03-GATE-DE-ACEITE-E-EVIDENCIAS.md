---
doc_id: "EPIC-F4-03-GATE-DE-ACEITE-E-EVIDENCIAS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F4-03 - Gate de Aceite e Evidencias

## Objetivo

Consolidar a validacao final da entrega v1.0, cruzando criterios de aceite do PRD com evidencias de backend, frontend e documentacao antes de promover a fase para `feito/`.

## Resultado de Negocio Mensuravel

A entrega deixa de depender de memoria oral e passa a ter uma decisao objetiva de promocao, apoiada em artefatos verificaveis e alinhada ao protocolo de decisao do framework.

## Definition of Done

- Existe um resumo unico de validacao em `artifacts/dashboard-leads-etaria/phase-f4/validation-summary.md`.
- Os criterios 9.1, 9.2, 9.3 e 9.4 do PRD aparecem mapeados para evidencias objetivas.
- A decisao final de promover ou segurar a entrega informa justificativa e rollback operacional.
- A equipe sabe exatamente quando mover a fase para `feito/` sem inventar criterio adicional.

## Issues

### DLE-F4-03-001 - Validar criterios de aceite do PRD contra backend e frontend
Status: todo

**User story**
Como pessoa revisora de release, quero uma matriz objetiva ligando cada criterio do PRD a uma evidencia para saber se a entrega esta pronta ou nao.

**Plano TDD**
1. `Red`: revisar `PROJETOS/dashboard-leads-etaria/PRD_Dashboard_Portfolio.md` e falhar o gate enquanto os criterios 9.1 a 9.4 nao estiverem mapeados para comandos, testes ou verificacoes manuais objetivas.
2. `Green`: montar a matriz de aceite com referencias para suites backend, suites frontend e verificacoes de OpenAPI.
3. `Refactor`: agrupar a matriz por arquitetura, dados, migracao e UX para facilitar auditoria futura.

**Criterios de aceitacao**
- Given os criterios de aceite do PRD, When a matriz e preenchida, Then cada item aponta para uma evidencia objetiva e repetivel.
- Given um criterio sem evidencia, When o gate e revisado, Then a decisao final nao pode ser `promote`.

### DLE-F4-03-002 - Consolidar evidencia final e decisao operacional
Status: todo

**User story**
Como pessoa PM, quero um resumo de validacao com status final para comunicar com clareza se a entrega v1.0 pode avancar.

**Plano TDD**
1. `Red`: falhar a revisao final enquanto `artifacts/dashboard-leads-etaria/phase-f4/validation-summary.md` nao registrar status de cada epic e decisao final.
2. `Green`: gerar o resumo consolidado com status dos epicos F1-F4, riscos remanescentes, comando de validacao executado e decisao `promote` ou `hold`.
3. `Refactor`: padronizar o template do resumo para reaproveitamento em outros projetos de `PROJETOS/`.

**Criterios de aceitacao**
- Given todos os epicos avaliados, When o resumo final e gerado, Then o documento lista F1, F2, F3 e F4 com status individual e observacoes.
- Given risco residual relevante, When a decisao final e registrada, Then o documento traz justificativa clara e proximo passo explicito.

### DLE-F4-03-003 - Preparar a promocao da fase para `feito/`
Status: todo

**User story**
Como pessoa responsavel pela governanca do projeto, quero um passo final claro para mover a fase para `feito/` somente quando o gate estiver realmente concluido.

**Plano TDD**
1. `Red`: usar `PROJETOS/COMUM/SCRUM-GOV.md` e `PROJETOS/COMUM/DECISION-PROTOCOL.md` como referencia e falhar a execucao enquanto o plano de movimentacao nao indicar pre-condicoes, rollback e atualizacao de links.
2. `Green`: documentar no resumo final as pre-condicoes para mover a pasta da fase e os caminhos que precisam ser atualizados no mesmo change set.
3. `Refactor`: manter a instrucao de promocao enxuta e reutilizavel para futuras fases do portfolio.

**Criterios de aceitacao**
- Given a decisao final `promote`, When a movimentacao para `feito/` for autorizada, Then o plano descreve de forma objetiva o que mover e o que atualizar junto.
- Given a decisao final `hold`, When a fase ainda estiver ativa, Then a pasta permanece fora de `feito/` e o bloqueio fica registrado no resumo.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/phase-f4/validation-summary.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
