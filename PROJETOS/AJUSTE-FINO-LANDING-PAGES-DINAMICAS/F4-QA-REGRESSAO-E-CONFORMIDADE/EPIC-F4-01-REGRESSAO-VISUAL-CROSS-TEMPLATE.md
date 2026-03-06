# EPIC-F4-01 — Regressão Visual Cross-Template e Acessibilidade
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F4 | **status:** 🔲

---
## 1. Resumo do Épico
Executar testes de regressão visual em todos os templates de landing page existentes,
verificar que `renderGraphicOverlay()` funciona corretamente após as alterações de
layout, validar responsividade do formulário above the fold em todos os breakpoints,
e executar checklist de acessibilidade básica (WCAG AA).

**Resultado de Negócio Mensurável:** Confirmação documentada de que nenhuma landing
page existente quebrou com as alterações das fases F1–F3, e que a acessibilidade
atende o mínimo para uso público do Banco do Brasil.

## 2. Contexto Arquitetural
- Templates existentes: `esporte_convencional`, `evento_cultural`, `tecnologia_inovacao`, `esporte_radical`, `show_musical`
- `renderGraphicOverlay()` aplica overlays visuais diferentes por template
- `buildLandingTheme()` gera tema MUI por template
- `getLayoutVisualSpec()` retorna specs de layout por template
- Breakpoints de teste: 375px (mobile), 768px (tablet), 1280px (desktop)
- Ferramenta de teste visual: screenshot manual ou Playwright/Cypress com comparação

## 3. Riscos e Armadilhas
- Templates pouco utilizados podem ter combinações de dados não testadas — testar com dados mock representativos
- `renderGraphicOverlay()` pode depender de posição DOM específica — validar com novo grid
- Acessibilidade: `aria-disabled` vs `disabled` em botões da gamificação — ambos necessários
- Hero image condicional pode gerar alturas diferentes entre templates — validar fallback visual

## 4. Definition of Done do Épico
- [ ] Cada template testado em 3 breakpoints (375px, 768px, 1280px) — screenshots capturados
- [ ] `renderGraphicOverlay()` renderiza corretamente em todos os templates
- [ ] Formulário above the fold confirmado em todos os breakpoints para todos os templates
- [ ] Chips `mood`/`categoria` ausentes na view pública em todos os templates
- [ ] Hero image condicional funcional (com e sem imagem) em todos os templates
- [ ] Checklist WCAG AA validado: contraste, labels, teclado, screen reader
- [ ] Fluxos UC-01 a UC-04 executados sem erro

---
## Issues

### AFLPD-F4-01-001 — Testar regressão visual por template e breakpoint
**tipo:** docs | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Para cada um dos 5 templates existentes, renderizar a landing em 3 breakpoints
(375px, 768px, 1280px) com dados mock representativos. Capturar screenshots e
verificar: formulário above the fold, `renderGraphicOverlay()` correto, hero image
condicional, ausência de chips internos e borderRadius 24px.

**Plano TDD:**
- **Red:** Definir matriz de teste (5 templates × 3 breakpoints × 2 estados hero = 30 cenários) e checklist esperado.
- **Green:** Executar cada cenário manualmente ou via ferramenta de automação, registrar resultado.
- **Refactor:** Se ferramenta de automação disponível, criar script reutilizável para futuras regressões.

**Critérios de Aceitação:**
- Given template `esporte_convencional` em viewport 375px, When renderizado, Then formulário acima da dobra e overlay gráfico correto
- Given template `show_musical` em viewport 1280px sem hero image, When renderizado, Then fallback visual presente e layout íntegro
- Given qualquer template em qualquer viewport, When renderizado em modo público, Then nenhum chip `mood`/`categoria` visível
- Given matriz de 30 cenários, When todos executados, Then todos passam sem regressão visual

**Tarefas:**
- [ ] T1: Preparar dados mock para cada template (com e sem hero image, com e sem gamificação)
- [ ] T2: Testar `esporte_convencional` em 375px, 768px, 1280px — registrar screenshots
- [ ] T3: Testar `evento_cultural` em 375px, 768px, 1280px — registrar screenshots
- [ ] T4: Testar `tecnologia_inovacao` em 375px, 768px, 1280px — registrar screenshots
- [ ] T5: Testar `esporte_radical` em 375px, 768px, 1280px — registrar screenshots
- [ ] T6: Testar `show_musical` em 375px, 768px, 1280px — registrar screenshots
- [ ] T7: Consolidar resultados em tabela com status pass/fail por cenário

**Notas técnicas:**
Screenshots devem ser salvos em `artifacts/phase-f4/screenshots/` com nomenclatura
`{template}_{breakpoint}_{hero|nohero}.png`. Se Playwright disponível, usar
`page.screenshot()` com viewport configurado.

---
### AFLPD-F4-01-002 — Validar fluxos UC-01 a UC-04 e acessibilidade
**tipo:** docs | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F4-01-001

**Descrição:**
Executar os 4 casos de uso definidos no PRD (seção 08) e validar checklist de
acessibilidade WCAG AA: contraste de cores, labels de formulário, navegação por
teclado e compatibilidade com screen reader.

**Plano TDD:**
- **Red:** Listar os 4 UCs e o checklist WCAG AA com critérios verificáveis.
- **Green:** Executar cada UC step-by-step e cada item do checklist, registrar resultado.
- **Refactor:** Documentar issues de acessibilidade encontradas como bugs futuros se não críticas.

**Critérios de Aceitação:**
- Given UC-01 (ativação sem gamificação), When executado step-by-step, Then todos os passos completam sem erro
- Given UC-03 (ativação com gamificação), When executado end-to-end, Then formulário → gamificação → conclusão → reset funciona
- Given landing page, When inspecionada com ferramenta de contraste, Then todos os textos atendem ratio mínimo WCAG AA (4.5:1 normal, 3:1 large)
- Given formulário, When navegado apenas com teclado (Tab/Enter), Then todos os campos e botões são acessíveis

**Tarefas:**
- [ ] T1: Executar UC-01 (ativação sem gamificação) — documentar resultado
- [ ] T2: Executar UC-02 (ativação com mensagem de orientação) — documentar resultado
- [ ] T3: Executar UC-03 (ativação com gamificação completa) — documentar resultado
- [ ] T4: Executar UC-04 (preview no backoffice) — documentar resultado
- [ ] T5: Validar contraste de cores com ferramenta (ex: axe, Lighthouse)
- [ ] T6: Validar navegação por teclado — Tab cycle completo no formulário
- [ ] T7: Verificar `aria-label` / `aria-disabled` nos botões da gamificação

**Notas técnicas:**
Ferramentas sugeridas: Lighthouse (acessibilidade), axe-core (contraste), screen
reader do OS (VoiceOver/NVDA). Issues de acessibilidade com severidade baixa devem
ser registradas mas não bloqueiam o gate.

## 5. Notas de Implementação Globais
- Esta fase é primariamente de validação e documentação — sem código novo
- Screenshots e resultados devem ser armazenados em `artifacts/phase-f4/`
- Issues de regressão encontradas devem ser reportadas como bugs e corrigidas antes do gate
- O gate de fase depende da evidência consolidada no EPIC-F4-02
