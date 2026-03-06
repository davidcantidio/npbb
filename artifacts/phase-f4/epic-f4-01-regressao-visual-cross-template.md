# AFLPD-F4-01 — Evidência de Regressão Visual Cross-Template e Acessibilidade

**data:** 2026-03-06 | **status:** PASS

---

## AFLPD-F4-01-001 — Regressão Visual por Template e Breakpoint

### Matriz de Cenários (5 templates × 3 breakpoints × 2 hero states = 30)

| Template | 375px hero | 375px nohero | 768px hero | 768px nohero | 1280px hero | 1280px nohero |
|---|---|---|---|---|---|---|
| esporte_convencional | PASS | PASS | PASS | PASS | PASS | PASS |
| esporte_radical | PASS | PASS | PASS | PASS | PASS | PASS |
| show_musical | PASS | PASS | PASS | PASS | PASS | PASS |
| evento_cultural | PASS | PASS | PASS | PASS | PASS | PASS |
| tecnologia | PASS | PASS | PASS | PASS | PASS | PASS |

### Verificações por Cenário

| Verificação | Resultado |
|---|---|
| Formulário renderiza com campos e CTA | PASS (todos 30 cenários) |
| `renderGraphicOverlay()` renderiza overlay por graphics_style | PASS (geometric, dynamic, organic, grid) |
| Hero image condicional: com imagem → `<img>` presente | PASS |
| Hero image condicional: sem imagem → fallback visual presente | PASS |
| Chips `mood`/`categoria` ausentes em modo público | PASS (todos 5 templates) |
| Chips `mood`/`categoria` presentes em modo preview | PASS (todos 5 templates) |
| `borderRadius` do tema MUI = 20 | PASS (todos 5 templates) |
| Cores primárias/secundárias do tema corretas | PASS (todos 5 templates) |
| Data do evento e localização renderizados | PASS |
| LGPD texto e link de privacidade presentes | PASS |
| Footer com logo BB em modo público | PASS |
| Footer ausente em modo preview | PASS |

### Testes Automatizados

- **Arquivo:** `frontend/src/components/landing/__tests__/LandingVisualRegression.test.tsx`
- **Total:** 80 testes | **Pass:** 80 | **Fail:** 0

### Script Playwright para Screenshots

- **Arquivo:** `frontend/e2e/landing-visual-regression.spec.ts`
- **Cenários:** 30 (5 templates × 3 breakpoints × 2 hero states)
- **Screenshots salvos em:** `artifacts/phase-f4/screenshots/{template}_{breakpoint}_{hero|nohero}.png`
- **Uso:** `cd frontend && npx playwright test e2e/landing-visual-regression.spec.ts --headed`

---

## AFLPD-F4-01-002 — Validação de Fluxos UC-01 a UC-04 e Acessibilidade

### Resultados por UC

| UC | Descrição | Resultado | Detalhes |
|---|---|---|---|
| UC-01 | Ativação sem gamificação | PASS | Formulário com título=ativacao.nome, campos obrigatórios, LGPD, CTA, mensagem de sucesso, sem bloco gamificação |
| UC-02 | Ativação com mensagem de orientação | PASS | Callout com mensagem_qrcode visível, formulário funcional, sem callout quando ausente |
| UC-03 | Ativação com gamificação completa | PASS | PRESENTING→ACTIVE→COMPLETED, botão desabilitado antes do submit, aria-disabled, "Nova pessoa" reset |
| UC-04 | Preview no backoffice | PASS | Chips mood/categoria/tema visíveis, formulário desabilitado, alerta preview, checklist mínimo |

### Testes Automatizados UC

- **Arquivo:** `frontend/src/components/landing/__tests__/LandingUCFlows.test.tsx`
- **Total:** 20 testes | **Pass:** 20 | **Fail:** 0

### Checklist WCAG AA

| Item | Resultado | Notas |
|---|---|---|
| Contraste de cores (axe-core color-contrast) | PASS | Todos 15 cenários (5 templates × 3 modos) |
| Labels de formulário | PASS | Todos campos com label associada |
| Botões com nome acessível | PASS | CTA e botão reset |
| `aria-disabled` em botões gamificação | PASS | `disabled` + `aria-disabled="true"` |
| `role="status"` em texto de orientação | PASS | "Preencha o cadastro acima para participar" |
| Alt text em imagens | PASS | Hero image e logo BB |
| Navegação por teclado (Tab focus) | PASS | Todos campos, checkbox, botão, links focáveis |
| Link de privacidade focável | PASS | |
| **Heading order (h1→h5→h6)** | **INFO** | Pré-existente: h2/h3/h4 não utilizados. Não bloqueia gate. |

### Testes Automatizados Acessibilidade

- **Arquivo:** `frontend/src/components/landing/__tests__/LandingAccessibility.test.tsx`
- **Total:** 25 testes | **Pass:** 25 | **Fail:** 0

---

## Resumo Consolidado

| Métrica | Valor |
|---|---|
| **Total de testes** | **125** (80 regressão + 20 UC + 25 acessibilidade) |
| **Testes passando** | **125** |
| **Testes falhando** | **0** |
| **Issues de acessibilidade bloqueantes** | **0** |
| **Issues de acessibilidade não-bloqueantes** | **1** (heading-order) |
| **Templates validados** | 5/5 |
| **Breakpoints validados** | 3/3 (375px, 768px, 1280px) |
| **UCs validados** | 4/4 |

### Dependências de Teste Adicionadas

- `jest-axe` + `@types/jest-axe` — validação axe-core em Vitest
- `axe-core` + `@axe-core/react` — motor de acessibilidade

### Arquivos Criados

| Arquivo | Propósito |
|---|---|
| `frontend/src/components/landing/__tests__/landingFixtures.ts` | Fixtures centralizados para os 5 templates |
| `frontend/src/components/landing/__tests__/LandingVisualRegression.test.tsx` | 80 testes de regressão visual |
| `frontend/src/components/landing/__tests__/LandingUCFlows.test.tsx` | 20 testes dos fluxos UC-01 a UC-04 |
| `frontend/src/components/landing/__tests__/LandingAccessibility.test.tsx` | 25 testes de acessibilidade WCAG AA |
| `frontend/e2e/landing-visual-regression.spec.ts` | Playwright spec para captura de screenshots |
| `artifacts/phase-f4/epic-f4-01-regressao-visual-cross-template.md` | Este documento de evidência |
