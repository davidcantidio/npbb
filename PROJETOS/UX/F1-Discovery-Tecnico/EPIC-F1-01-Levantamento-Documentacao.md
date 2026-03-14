---
doc_id: "EPIC-F1-01-Levantamento-Documentacao.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-14"
---

# EPIC-F1-01 - Levantamento e Documentacao

## Objetivo

Resolver todas as lacunas `nao_definido` do intake e registrar decisoes de arquitetura necessarias para a implementacao segura do layout side-by-side, preview mobile, drag-and-drop e limpeza de redundancias nas 5 etapas do wizard.

## Resultado de Negocio Mensuravel

Documento consolidado com componentes mapeados, estrutura de layout, decisao sobre biblioteca dnd, breakpoint definido, conteudo das colunas direitas e confirmacao de cobertura Tema/Contexto — sem lacunas bloqueantes para F2.

## Contexto Arquitetural

O wizard de configuracao de evento possui 5 paginas: Evento (EventWizardPage), Formulario de Lead (EventLeadFormConfig), Gamificacao (EventGamificacao), Ativacoes (EventAtivacoes), Questionario (EventQuestionario). Cada pagina tem estrutura propria. O PRD exige layout de duas colunas em todas; a etapa Formulario de Lead ja possui PreviewSection e LandingPageView; as demais etapas precisam de mapeamento.

## Definition of Done do Epico
- [x] Componentes de preview (landing e ativacao) identificados
- [x] Estrutura de layout do wizard documentada
- [x] Biblioteca de drag-and-drop verificada e decisao registrada
- [x] Breakpoint definido
- [x] Conteudo da coluna direita Evento e Questionario definido
- [x] Cobertura Tema/Contexto confirmada

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Mapear Componentes e Layout | Identificar componentes de preview e estrutura de layout | 3 | done | [ISSUE-F1-01-001-Mapear-Componentes-Layout.md](./issues/ISSUE-F1-01-001-Mapear-Componentes-Layout.md) |
| ISSUE-F1-01-002 | Documentar Arquitetura e Validar Decisoes | Definir breakpoint, coluna direita, dnd e cobertura Tema | 2 | done | [ISSUE-F1-01-002-Documentar-Arquitetura-Validar-Decisoes.md](./issues/ISSUE-F1-01-002-Documentar-Arquitetura-Validar-Decisoes.md) |

## Artifact Minimo do Epico

Documento ou secao na issue com: lista de componentes, estrutura de layout, decisao dnd, breakpoint, conteudo coluna direita Evento/Questionario, confirmacao cobertura Tema/Contexto.

## Dependencias
- [Intake](../../INTAKE-UX.md)
- [PRD](../../PRD-UX.md)
- [Fase](./F1_UX_EPICS.md)
