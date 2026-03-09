---
doc_id: "ISSUE-F1-03-004-ALINHAR-COR-RODAPE-ESPORTE-RADICAL-E-CONTRATO.md"
version: "1.0"
status: "done"
owner: "PM"
task_instruction_mode: "required"
last_updated: "2026-03-08"
---

# ISSUE-F1-03-004 - Alinhar Cor de Rodape `esporte_radical` ao Contrato

## User Story

Como responsavel pelo gate de F1, quero que o token de cor do rodape para o template `esporte_radical` esteja alinhado com o contrato aprovado para eliminar divergencia entre codigo, teste e documentacao.

## Contexto Tecnico

A auditoria F1-R01 identificou divergencia no contrato de `footerTextColor`:

- implementacao atual em `landingStyle.tsx` retorna `rgba(255, 255, 255, 0.85)` para `esporte_radical`
- teste de contrato (`landingStyle.test.tsx`) valida `rgba(255, 255, 255, 0.85)`
- PRD da fase descreve `rgba(255, 255, 255, 0.85)` para `esporte_radical`

O gate da fase foi bloqueado por este desvio e agora está resolvido.

## Plano TDD

- Red: reproduzir a falha em `landingStyle.test.tsx` para `esporte_radical`.
- Green: alinhar token e contrato para um unico valor aprovado e zerar falha na suite alvo.
- Refactor: consolidar a fonte de verdade da expectativa para reduzir risco de nova divergencia.

## Criterios de Aceitacao

- Given o template `esporte_radical`, When `getTemplateFooterTextColor` e chamado, Then retorna o valor aprovado no contrato oficial da fase.
- Given a suite de testes de landing da F1, When executada, Then nao ha falhas em `landingStyle.test.tsx`.
- Given o PRD e os testes, When revisados apos ajuste, Then codigo, teste e especificacao estao consistentes.
- Given o `AUDIT-LOG` e o relatorio F1-R01, When consultados, Then o follow-up desta issue esta rastreavel.

## Definition of Done da Issue

- [x] token de cor do rodape `esporte_radical` alinhado ao contrato aprovado
- [x] teste de contrato alinhado para o valor único do contrato
- [x] suite alvo de landing executada e revalidada com sucesso
- [x] rastreabilidade documental preservada no audit-log/relatorio

## Tarefas Decupadas

- [x] T1: confirmar valor de contrato final com base em PRD + criterios de acessibilidade
- [x] T2: aplicar ajuste em `frontend/src/components/landing/landingStyle.tsx`
- [x] T3: ajustar expectativa em `frontend/src/components/landing/__tests__/landingStyle.test.tsx` apenas se a decisao de contrato exigir
- [x] T4: executar suite de testes alvo da landing e anexar evidencia no fechamento da issue

## Instructions por Task

### T1

- Validar se o valor final sera mantido como `rgba(255, 255, 255, 0.85)` (PRD atual) ou revisado com justificativa formal.
- Se houver mudanca de contrato, atualizar PRD no mesmo change set.

### T2

- Editar somente o mapeamento de `TEMPLATE_FOOTER_TEXT_COLORS.esporte_radical`.
- Nao alterar comportamento dos demais templates.

### T3

- Se o contrato final permanecer o do PRD, manter teste aderente a ele.
- Se o contrato final mudar, atualizar expectativa do teste e o PRD de forma sincronizada.

### T4

- Executar:
  - `npm run test -- --run src/components/landing/__tests__/LandingPageView.test.tsx src/components/landing/__tests__/LandingUCFlows.test.tsx src/components/landing/__tests__/LandingVisualRegression.test.tsx src/components/landing/__tests__/LandingAccessibility.test.tsx src/components/landing/__tests__/FullPageBackground.test.tsx src/components/landing/__tests__/FormCard.test.tsx src/components/landing/__tests__/MinimalFooter.test.tsx src/components/landing/__tests__/formOnlySurface.test.ts src/components/landing/__tests__/landingStyle.test.tsx`
- Registrar resultado no fechamento da issue e no audit-log de supersedencia da rodada.

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/landingStyle.tsx`
- `frontend/src/components/landing/__tests__/landingStyle.test.tsx`
- `PROJETOS/LANDING-PAGE-FORM-FIRST/PRD-LANDING-PAGE-FORM-FIRST.md` (se houver mudanca de contrato)

## Artifact Minimo

- token de rodape `esporte_radical` alinhado e suite de contrato passando

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Relatorio F1-R01](../auditorias/RELATORIO-AUDITORIA-F1-R01.md)

## Navegacao Rapida

- `[[../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
- `[[../auditorias/RELATORIO-AUDITORIA-F1-R01]]`
