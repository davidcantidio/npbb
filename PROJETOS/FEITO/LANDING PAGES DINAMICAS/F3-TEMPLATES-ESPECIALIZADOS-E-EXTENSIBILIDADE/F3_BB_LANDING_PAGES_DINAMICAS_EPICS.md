# Épicos — BB Landing Pages Dinâmicas / F3 — Templates Especializados e Extensibilidade
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3
**prd:** ../PRD-BB-Landing-Pages-Dinamicas.md
**status:** aprovado

---
## Objetivo da Fase
Concluir a cobertura dos templates mais expressivos do portfólio, habilitar camadas de
customização controlada no backoffice e medir impacto de captação por template e CTA.

Ao final da fase, o sistema deve suportar os templates `esporte_radical` e
`show_musical`, permitir customizações governadas e gerar dados de analytics para
evolução contínua da taxa de captação no contexto das ativações.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Template Esporte Radical | Entregar a experiência visual mais dinâmica para skate, surfe e modalidades em ascensão. | F2 concluída | 🔲 | `EPIC-F3-01-TEMPLATE-ESPORTE-RADICAL.md` |
| EPIC-F3-02 | Template Show Musical | Entregar o template noturno e vibrante para shows, concertos e festivais. | EPIC-F3-01 | 🔲 | `EPIC-F3-02-TEMPLATE-SHOW-MUSICAL.md` |
| EPIC-F3-03 | Customização Controlada no Backoffice | Permitir ajustes seguros de conteúdo/hero/CTA sem romper a governança de marca. | EPIC-F3-02 | 🔲 | `EPIC-F3-03-CUSTOMIZACAO-CONTROLADA-NO-BACKOFFICE.md` |
| EPIC-F3-04 | Analytics de Captação por Template | Instrumentar métricas de visualizações, envios e captação por categoria/template. | EPIC-F3-03 | 🔲 | `EPIC-F3-04-ANALYTICS-DE-CONVERSAO-POR-TEMPLATE.md` |
| EPIC-F3-05 | Experimentos A/B de CTA | Habilitar experimentos controlados de CTA por categoria com leitura de desempenho. | EPIC-F3-04 | 🔲 | `EPIC-F3-05-EXPERIMENTOS-A-B-DE-CTA.md` |

## Dependências entre Épicos
`EPIC-F3-01` -> `EPIC-F3-02` -> `EPIC-F3-03` -> `EPIC-F3-04` -> `EPIC-F3-05`

## Definition of Done da Fase
- [ ] Templates `esporte_radical` e `show_musical` aprovados funcional e visualmente
- [ ] Backoffice permite customização governada sem romper identidade BB
- [ ] Métricas de captação por template estão disponíveis para análise
- [ ] Experimentos A/B de CTA conseguem ser executados e comparados por categoria

## Notas e Restrições
- Qualquer customização visual livre fora do catálogo precisa de decisão formal
- Analytics deve respeitar LGPD e não capturar dados sensíveis desnecessários
- Experimentos A/B não podem comprometer acessibilidade nem conformidade de marca
