---
doc_id: "ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-03-002 - Reposicionar GamificacaoBlock

## User Story

Como participante de evento com gamificacao, quero ver o bloco de gamificacao logo abaixo do formulario para participar do sorteio apos preencher o cadastro.

## Contexto Tecnico

O `GamificacaoBlock` continua funcionando exatamente como especificado no PRD v1.2, mas precisa ser reposicionado:
- Abaixo do FormCard, dentro do mesmo container de rolagem
- Mesma largura maxima do FormCard (440px mobile, 480px tablet, 520px desktop)
- Mesmo estilo de card (borderRadius 24px, elevacao, fundo semelhante ao FormCard)
- O fundo tematico continua visivel por tras do GamificacaoBlock
- Os estados PRESENTING → ACTIVE → COMPLETED devem funcionar sem regressao

## Plano TDD

- Red: GamificacaoBlock no layout antigo — posicionado no grid lateral.
- Green: mover GamificacaoBlock para abaixo do FormCard com mesma largura e estilo de card.
- Refactor: extrair constantes de largura maxima compartilhadas entre FormCard e GamificacaoBlock.

## Criterios de Aceitacao

- Given uma ativacao com gamificacoes, When a landing carrega, Then o GamificacaoBlock aparece abaixo do FormCard
- Given o GamificacaoBlock reposicionado, When medido, Then a largura maxima e identica a do FormCard
- Given o GamificacaoBlock reposicionado, When observado, Then o fundo tematico e visivel por tras do bloco
- Given o GamificacaoBlock em estado PRESENTING, When o lead e submetido, Then o botao "Quero participar" habilita
- Given o GamificacaoBlock em estado COMPLETED, When reset e acionado, Then o bloco volta a PRESENTING

## Definition of Done da Issue

- [x] GamificacaoBlock posicionado abaixo do FormCard
- [x] mesma largura maxima do FormCard em todos os breakpoints
- [x] borderRadius 24px e elevacao consistente com o FormCard
- [x] fundo tematico visivel por tras do GamificacaoBlock
- [x] fluxo PRESENTING → ACTIVE → COMPLETED sem regressao

## Tarefas Decupadas

- [x] T1: mover renderizacao do GamificacaoBlock para logo abaixo do FormCard no container
- [x] T2: aplicar mesma largura maxima e centralizacao do FormCard
- [x] T3: aplicar borderRadius 24px e elevacao ao wrapper do GamificacaoBlock
- [x] T4: garantir fundo semitransparente para que o tema vaze
- [x] T5: testar fluxo completo de estados da gamificacao no novo posicionamento

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/GamificacaoBlock.tsx` (ou equivalente)

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado)

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Issue FormCard](./ISSUE-F1-02-001-CRIAR-FORMCARD.md)

## Navegacao Rapida

- `[[../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
- `[[./ISSUE-F1-02-001-CRIAR-FORMCARD]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
