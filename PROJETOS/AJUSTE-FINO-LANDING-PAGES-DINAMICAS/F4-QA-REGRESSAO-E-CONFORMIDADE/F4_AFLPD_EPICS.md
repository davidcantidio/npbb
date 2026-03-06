# Épicos — Ajuste Fino Landing Pages Dinâmicas / F4 — QA, Regressão e Conformidade
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F4
**prd:** ../PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md
**status:** aprovado

---
## Objetivo da Fase
Executar validação de regressão visual cross-template, verificar acessibilidade
básica, confirmar conformidade com identidade visual BB, e consolidar evidência
de entrega com decisão go/no-go documentada.

Ao final da fase, todas as landing pages existentes renderizam corretamente com o
novo layout, sem regressão em `renderGraphicOverlay()`, e a evidência consolidada
permite decisão informada sobre promoção a produção.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F4-01 | Regressão Visual Cross-Template e Acessibilidade | Validar ausência de regressão visual em todos os templates, testar responsividade e acessibilidade básica. | nenhuma | 🔲 | `EPIC-F4-01-REGRESSAO-VISUAL-CROSS-TEMPLATE.md` |
| EPIC-F4-02 | Coerência Normativa e Gate de Fase | Validar consistência entre implementação e contrato do PRD, cobertura de testes e consolidar evidência de entrega. | EPIC-F4-01 | 🔲 | `EPIC-F4-02-COERENCIA-NORMATIVA-E-GATE.md` |

## Dependências entre Épicos
`EPIC-F4-01` → `EPIC-F4-02`

O EPIC-F4-02 depende dos resultados de regressão do EPIC-F4-01 para consolidar a
evidência final.

## Definition of Done da Fase
- [ ] Todos os templates existentes renderizam sem regressão visual
- [ ] `renderGraphicOverlay()` funcional em todos os templates
- [ ] Formulário above the fold em 375px, 768px e 1280px para todos os templates
- [ ] Acessibilidade: todos os botões com labels, contraste mínimo WCAG AA, formulário navegável por teclado
- [ ] Fluxos UC-01 a UC-04 testados e funcionais
- [ ] Testes de contrato de API passando
- [ ] Evidência consolidada em `artifacts/phase-f4/validation-summary.md`
- [ ] Decisão `promote | hold` documentada com justificativa

## Notas e Restrições
- Regressão visual pode ser validada manualmente ou via screenshot comparison
- Templates a testar: `esporte_convencional`, `evento_cultural`, `tecnologia_inovacao`, `esporte_radical`, `show_musical`
- Acessibilidade WCAG AA é o nível mínimo — AAA é desejável mas não obrigatório
- A fase não introduz código novo — apenas testes, validação e documentação
