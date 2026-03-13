# Tabela de Arquivos e Funções Monolíticas — Landing Page de Eventos e Ativações

**Projeto:** LP – QR por Ativação  
**Referência:** `SPEC-ANTI-MONOLITO.md`  
**Thresholds:** arquivo `warn >400` / `block >600` | função `warn >60` / `block >100`  
**Data:** Março/2026

---

## 1. Arquivos Monolíticos

| Nome do arquivo                     | Linhas | Caminho                                                      | Status           |
| ----------------------------------- | ------ | ------------------------------------------------------------ | ---------------- |
| `eventos.py`                        | 1500   | `backend/app/routers/eventos.py`                             | **BLOCK** (>600) |
| `EventLeadFormConfig.tsx`           | 879    | `frontend/src/pages/EventLeadFormConfig.tsx`                 | **BLOCK** (>600) |
| `EventAtivacoes.tsx`                | 808    | `frontend/src/pages/EventAtivacoes.tsx`                      | **BLOCK** (>600) |
| `landingStyle.tsx`                  | 716    | `frontend/src/components/landing/landingStyle.tsx`           | **BLOCK** (>600) |
| `EventGamificacao.tsx`              | 583    | `frontend/src/pages/EventGamificacao.tsx`                    | **WARN** (>400)  |
| `EventLandingPage.tsx`              | 431    | `frontend/src/pages/EventLandingPage.tsx`                    | **WARN** (>400)  |
| `ativacao.py`                       | 394    | `backend/app/routers/ativacao.py`                             | OK               |
| `landing_public.py`                 | 361    | `backend/app/routers/landing_public.py`                       | OK               |
| `landing_page_submission.py`       | 352    | `backend/app/services/landing_page_submission.py`            | OK               |
| `landing_public.ts`                 | 331    | `frontend/src/services/landing_public.ts`                   | OK               |
| `FormCard.tsx`                     | 221    | `frontend/src/components/landing/FormCard.tsx`              | OK               |
| `landing_public.py` (schemas)       | 197    | `backend/app/schemas/landing_public.py`                       | OK               |
| `LandingPageView.tsx`               | 161    | `frontend/src/components/landing/LandingPageView.tsx`        | OK               |
| `ativacao.py` (schemas)             | 156    | `backend/app/schemas/ativacao.py`                             | OK               |
| `GamificacaoBlock.views.tsx`        | 151    | `frontend/src/components/landing/GamificacaoBlock.views.tsx` | OK               |
| `landing_gamificacao_completion.py`| 122    | `backend/app/services/landing_gamificacao_completion.py`     | OK               |
| `urls.py`                           | 106    | `backend/app/utils/urls.py`                                  | OK               |
| `AtivacaoQrPreview.tsx`             | 119    | `frontend/src/components/eventos/AtivacaoQrPreview.tsx`      | OK               |
| `models.py`                         | 549    | `backend/app/models/models.py`                                | OK               |
| `landing.py` (schemas)              | 29     | `backend/app/schemas/landing.py`                              | OK               |
| `gamificacao_landing.py`            | 19     | `backend/app/schemas/gamificacao_landing.py`                 | OK               |
| `landing_experiments.ts`            | 32     | `frontend/src/services/landing_experiments.ts`               | OK               |
| `workflow.ts`                       | 267    | `frontend/src/services/eventos/workflow.ts`                  | OK               |

---

## 2. Funções Monolíticas

| Nome da função                     | Linhas | Caminho                                                          | Status           |
| ----------------------------------- | ------ | ---------------------------------------------------------------- | ---------------- |
| `EventLeadFormConfig`               | 820    | `frontend/src/pages/EventLeadFormConfig.tsx:60-879`               | **BLOCK** (>100) |
| `EventAtivacoes`                    | 704    | `frontend/src/pages/EventAtivacoes.tsx:105-808`                  | **BLOCK** (>100) |
| `EventGamificacao`                  | 508    | `frontend/src/pages/EventGamificacao.tsx:76-583`                 | **BLOCK** (>100) |
| `EventLandingPage`                  | 393    | `frontend/src/pages/EventLandingPage.tsx:39-431`                 | **BLOCK** (>100) |
| `LandingPageView`                   | 109    | `frontend/src/components/landing/LandingPageView.tsx:53-161`     | **BLOCK** (>100) |
| `listar_eventos`                    | 141    | `backend/app/routers/eventos.py:125-265`                         | **BLOCK** (>100) |
| `_build_evento_payload_from_row`    | 100    | `backend/app/routers/eventos.py:410-509`                         | **BLOCK** (>100) |
| `upsert_formulario_lead_config`     | 91     | `backend/app/routers/eventos.py:1059-1149`                        | **WARN** (>60)   |
| `submit_public_lead`                | 83     | `backend/app/services/landing_page_submission.py:253-335`        | **WARN** (>60)   |
| `renderMusicalOverlay`              | 65     | `frontend/src/components/landing/landingStyle.tsx:530-594`        | **WARN** (>60)   |
| `obter_formulario_lead_config`      | 60     | `backend/app/routers/eventos.py:940-999`                         | OK (limite)      |

---

## 3. Resumo por Status

| Status | Arquivos | Funções |
| ------ | -------- | ------- |
| **BLOCK** | 4 | 7 |
| **WARN** | 2 | 3 |
| OK | 18 | — |

---

## 4. Observações

- **Arquivos BLOCK:** `eventos.py`, `EventLeadFormConfig.tsx`, `EventAtivacoes.tsx`, `landingStyle.tsx` excedem o threshold bloqueante de 600 linhas.
- **Funções BLOCK:** Componentes React `EventLeadFormConfig`, `EventAtivacoes`, `EventGamificacao`, `EventLandingPage` e `LandingPageView` concentram lógica e JSX extenso; `listar_eventos` e `_build_evento_payload_from_row` no backend também excedem 100 linhas.
- **SPEC-ANTI-MONOLITO:** Para componentes React, o spec orienta priorizar a lógica imperativa; JSX declarativo extenso, por si só, não deve classificar `monolithic-function`. Ainda assim, os componentes listados apresentam concentração significativa de estado e handlers.
- **Recomendação:** Particionar `eventos.py` em módulos por domínio (CRUD, CSV, formulário, gamificação, ativações, questionário); extrair hooks e subcomponentes das páginas React.
