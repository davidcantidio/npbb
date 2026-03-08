# ISSUE-F3-01-001 - Relatorio de Validacao de Fundo Tematico

- issue: `ISSUE-F3-01-001`
- gerado_em: `2026-03-08T16:26:32.084Z`
- source_mode: `backend-real`
- event_id_base: `1`
- api_url: `http://127.0.0.1:8000`
- base_url: `http://127.0.0.1:5173`
- evidencia_json: `artifacts/phase-f3/evidence/issue-f3-01-001-results.json`

## Resumo

- matriz executada: `7 templates x 3 breakpoints = 21 cenarios`
- resultado: `21 PASS / 0 FAIL`
- gradientes: `100% aderentes ao PRD secao 05`
- overlay_variant: `100% aderente ao template esperado`
- viewport gap: `0`
- imagens externas carregadas para o fundo: `0`

## Achados Corrigidos

- A resolucao de overlay deixou de depender apenas de `graphics_style` e passou a usar variantes explicitas por template.
- O catalogo agora possui 7 overlays distintos no frontend: `corporativo`, `esporte_convencional`, `esporte_radical`, `evento_cultural`, `show_musical`, `tecnologia`, `generico`.
- O DOM do fundo e do overlay agora expoe metadata de QA via `data-template-category` e `data-overlay-variant`.
- A cobertura automatizada foi atualizada de uma regressao legada centrada em 5 templates para uma validacao F3 dedicada cobrindo os 7 templates com backend real e `template_override`.

## Matriz 7 x 3

| Template | 375px | 768px | 1280px | Overlay esperado | Status |
|---|---|---|---|---|---|
| `corporativo` | PASS ([mobile](./screenshots/corporativo_mobile.png)) | PASS ([tablet](./screenshots/corporativo_tablet.png)) | PASS ([desktop](./screenshots/corporativo_desktop.png)) | `corporativo` | PASS |
| `esporte_convencional` | PASS ([mobile](./screenshots/esporte_convencional_mobile.png)) | PASS ([tablet](./screenshots/esporte_convencional_tablet.png)) | PASS ([desktop](./screenshots/esporte_convencional_desktop.png)) | `esporte_convencional` | PASS |
| `esporte_radical` | PASS ([mobile](./screenshots/esporte_radical_mobile.png)) | PASS ([tablet](./screenshots/esporte_radical_tablet.png)) | PASS ([desktop](./screenshots/esporte_radical_desktop.png)) | `esporte_radical` | PASS |
| `evento_cultural` | PASS ([mobile](./screenshots/evento_cultural_mobile.png)) | PASS ([tablet](./screenshots/evento_cultural_tablet.png)) | PASS ([desktop](./screenshots/evento_cultural_desktop.png)) | `evento_cultural` | PASS |
| `show_musical` | PASS ([mobile](./screenshots/show_musical_mobile.png)) | PASS ([tablet](./screenshots/show_musical_tablet.png)) | PASS ([desktop](./screenshots/show_musical_desktop.png)) | `show_musical` | PASS |
| `tecnologia` | PASS ([mobile](./screenshots/tecnologia_mobile.png)) | PASS ([tablet](./screenshots/tecnologia_tablet.png)) | PASS ([desktop](./screenshots/tecnologia_desktop.png)) | `tecnologia` | PASS |
| `generico` | PASS ([mobile](./screenshots/generico_mobile.png)) | PASS ([tablet](./screenshots/generico_tablet.png)) | PASS ([desktop](./screenshots/generico_desktop.png)) | `generico` | PASS |

## Validacoes Executadas

- Gradiente computado do `full-page-background-layer` comparado contra o gradiente esperado do PRD para cada template.
- `data-template-category` e `data-overlay-variant` verificados no DOM para todos os 21 cenarios.
- Cobertura total da viewport validada pelo `getBoundingClientRect()` da camada fixa de fundo.
- Monitoramento de requests do tipo `image` com exigencia de `0` requests externos durante o carregamento da landing.
- Captura de screenshot `fullPage` para cada combinacao template x breakpoint.

## Desvios Residuais

- Nenhum desvio residual identificado no escopo desta issue.

## Artefatos

- screenshots: `artifacts/phase-f3/screenshots/`
- evidencia estruturada: `artifacts/phase-f3/evidence/issue-f3-01-001-results.json`
- comando de reproducao: `cd frontend && npm run test:e2e:f3-theme`
