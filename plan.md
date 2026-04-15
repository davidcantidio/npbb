## Summary

Evolve the NPBB assets/tickets domain from its current aggregated-quota model (`CotaCortesia` + `SolicitacaoIngresso`) into a full operational system that supports per-event ticket type configuration, two mutually exclusive supply modes (internal QR emission vs external ticketeer receipt), planned-vs-received reconciliation with automatic blocking, recipient-level distribution with lifecycle tracking, internal QR PDF generation, operational adjustments (reallocation, increase, reduction, incidents), email notifications, an analytics dashboard, and a minimal write API for OpenClaw integration. The system must coexist with the current model during a controlled rollout.

## Relevant Files

- `backend/app/models/event_support_models.py` - Current CotaCortesia, SolicitacaoIngresso, Convidado, Convite models
- `backend/app/models/models.py` - Core models including Evento, Diretoria, Usuario, enums (SolicitacaoIngressoStatus, SolicitacaoIngressoTipo)
- `backend/app/routers/ativos.py` - Current ativos CRUD router (list, assign, delete, CSV export)
- `backend/app/routers/ingressos.py` - Current ingressos router (list ativos for BB users, solicitations, create solicitation)
- `backend/app/schemas/ativos.py` - AtivoAssignPayload, AtivoListItem schemas
- `backend/app/schemas/ingressos.py` - SolicitacaoIngressoCreate/Read, IngressoAtivoListItem, AdminListItem schemas
- `backend/app/routers/dashboard_leads.py` - Dashboard leads pattern to follow for dashboard ativos
- `backend/app/schemas/dashboard_leads.py` - Dashboard query/response schema pattern
- `backend/app/services/email.py` - Existing email service (console/SMTP backends)
- `backend/app/main.py` - App entry point where routers are mounted
- `frontend/src/pages/AtivosList.tsx` - Current ativos list page
- `frontend/src/pages/IngressosPortal.tsx` - Current ingressos portal (BB + admin views)
- `frontend/src/config/dashboardManifest.ts` - Dashboard manifest for registering new dashboard pages
- `frontend/src/services/ativos.ts` - Frontend ativos API client
- `frontend/src/services/ingressos.ts` - Frontend ingressos API client

## Relevant Documentation

- [PRD-ATIVOS-INGRESSOS](https://github.com/davidcantidio/npbb/blob/main/PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md) - Full PRD with domain rules
- [ATIVOS_STATE_NOW](https://github.com/davidcantidio/npbb/blob/main/backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md) - Baseline audit of current state
- [RESTORE_ATIVOS_SUMMARY](https://github.com/davidcantidio/npbb/blob/main/docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md) - Previous restore audit

## Open Questions

- Final storage/retention strategy for ticket artifacts (files, QR PDFs, links) — use local/S3 with configurable backend for v1
- SMTP SLA for retry/bounce/resend — v1 uses fire-and-forget with logging; retry is future scope
- Detailed dashboard drill-downs and incident panel UX — v1 delivers summary views; drill-downs are future
- PDF layout for internal tickets — v1 uses a simple layout with event name, ticket type, recipient name/email, QR code (UUID), and date

## Risks

- **Coexistence complexity**: New models must coexist with `CotaCortesia`/`SolicitacaoIngresso` during transition; migrations must not break existing data
- **Heterogeneous ticketeer formats**: External receipt ingestion varies; v1 focuses on manual confirmation, not automated parsing
- **Scope creep**: PRD covers operations + analytics + automation prep; plan prioritizes operational core first

---

# Task 1: Create Domain Models and Migrations

Establish the new data model that supports ticket types per event, supply modes, reconciliation, recipient lifecycle, adjustments, and operational incidents — all coexisting with the current `CotaCortesia`/`SolicitacaoIngresso` tables.

## Implemented State

- Create new enums: `TipoIngresso` (pista, pista_premium, camarote), `ModoFornecimento` (interno_emitido_com_qr, externo_recebido), `StatusInventario` (planejado, recebido_confirmado, bloqueado_por_recebimento, disponivel, distribuido), `StatusDestinatario` (enviado, confirmado, utilizado, cancelado), `TipoOcorrencia` (entrega_errada, quantidade_divergente, destinatario_invalido, outro), `TipoAjuste` (aumento, reducao, remanejamento)
- Create `ConfiguracaoIngressoEvento` model — links evento to its active ticket types and supply mode, with `modo_fornecimento` field and audit trail for mode changes
- Create `PrevisaoIngresso` model — planned quantity per evento + diretoria + tipo_ingresso
- Create `RecebimentoIngresso` model — received confirmation records for external mode with quantity, artifacts (file path/link/instructions), and `correlation_id`
- Create `InventarioIngresso` model — computed stock per evento + diretoria + tipo_ingresso tracking planejado, recebido_confirmado, bloqueado, disponivel, distribuido counts
- Create `DistribuicaoIngresso` model — individual ticket assigned to a recipient (nome, email), with `status_destinatario`, UUID for QR, timestamps for each lifecycle transition, cancellation reason
- Create `AjusteIngresso` model — records for aumento, reducao, remanejamento with source/target diretoria+tipo, quantity, optional reason, user, timestamp
- Create `OcorrenciaIngresso` model — operational incidents with tipo_canonico, description, evento+diretoria+tipo, user, timestamp
- Create `AuditoriaIngressoEvento` model — audit log for supply mode changes with old/new mode, user, timestamp
- Write Alembic migration that creates all new tables without altering existing `cota_cortesia` or `solicitacao_ingresso` tables

## Details

- All new models go in a new file `backend/app/models/ingressos_v2_models.py` to keep separation from the legacy models
- Use SQLModel with the same patterns as `event_support_models.py`
- Every model includes `created_at` and `updated_at` using `now_utc`
- `DistribuicaoIngresso.qr_uuid` is a UUID4 string field, unique, generated at creation time — this is the value encoded in the QR
- `ConfiguracaoIngressoEvento` has a unique constraint on `evento_id` (one config per event)
- `PrevisaoIngresso` has a unique constraint on `(evento_id, diretoria_id, tipo_ingresso)`
- `correlation_id` (UUID string) on `RecebimentoIngresso`, `DistribuicaoIngresso`, `AjusteIngresso` for cross-entity traceability
- Enums should be added to `backend/app/models/models.py` alongside existing enums, or in a new `backend/app/models/enums.py` if cleaner

## Verification

- Migration runs forward and backward without errors on a database that has existing `cota_cortesia` and `solicitacao_ingresso` data
- All new tables are created with correct constraints and indexes
- Existing endpoints (`GET /ativos`, `GET /ingressos/ativos`, `POST /ingressos/solicitacoes`) continue working unchanged

---

# Task 2: Implement Event Ticket Configuration and Supply Mode Endpoints

Build the API for configuring which ticket types are active per event and setting the supply mode, including audited mode changes.

## Implemented State

- Schemas created in `backend/app/schemas/ingressos_v2.py`: `ConfiguracaoIngressoEventoCreate`, `ConfiguracaoIngressoEventoRead`, `ConfiguracaoIngressoEventoUpdate`, `PrevisaoIngressoCreate`, `PrevisaoIngressoRead`
- Router created in `backend/app/routers/ingressos_v2.py` with prefix `/ingressos/v2`
- Configuration and forecast endpoints are implemented in the router and covered by dedicated endpoint tests
- Implement `POST /ingressos/v2/eventos/{evento_id}/configuracao` — set active ticket types and supply mode for an event
- Implement `GET /ingressos/v2/eventos/{evento_id}/configuracao` — read current config
- Implement `PATCH /ingressos/v2/eventos/{evento_id}/configuracao` — update config (mode change creates audit record, requires admin role)
- Implement `POST /ingressos/v2/eventos/{evento_id}/previsoes` — create/update planned quantities per diretoria + tipo_ingresso
- Implement `GET /ingressos/v2/eventos/{evento_id}/previsoes` — list planned quantities with filters
- Router registered in `backend/app/main.py`
- Test coverage implemented in `backend/tests/test_ingressos_v2_endpoints.py`, with isolated app bootstrap for `auth` + `ingressos_v2`

## Details

- Only ticket types declared in the event config are valid for that event (e.g., an event might only use `pista` and `camarote`)
- Mode change via PATCH writes a row to `AuditoriaIngressoEvento` with the acting user, old mode, new mode
- RBAC: write operations use `require_npbb_user`; read operations use `get_current_user` plus `_check_evento_visible_or_404`
- Event visibility is enforced through `backend/app/routers/eventos/_shared.py`
- Previsao upserts: if a row for `(evento_id, diretoria_id, tipo_ingresso)` already exists, update the quantity

## Verification

- Can create a configuration for an event with a subset of ticket types
- Cannot create a duplicate configuration for the same event
- Mode change produces an audit record with correct old/new values
- Planned quantities can be created and updated per diretoria + tipo
- Target verification command: `cd backend && python -m pytest tests/test_ingressos_v2_endpoints.py -q`

---

# Task 3: Implement Reconciliation and Inventory Blocking Service

Build the reconciliation engine that tracks received quantities against planned quantities, manages automatic blocking/unblocking, and handles ticketeer surplus.

## TODOs

- Create service `backend/app/services/inventario_ingressos.py` with reconciliation logic
- Implement `registrar_recebimento()` — records a `RecebimentoIngresso`, updates inventory, triggers auto-unblock if sufficient
- Implement `calcular_inventario()` — computes current stock state (planejado, recebido, bloqueado, disponivel, distribuido) for a given evento + diretoria + tipo
- Implement automatic blocking: when `recebido_confirmado < planejado`, the difference is `bloqueado_por_recebimento`
- Implement automatic unblocking: when new `recebido_confirmado` is registered and total received >= planned, blocked amount is released
- Implement surplus blocking: when `recebido_confirmado > planejado`, excess is blocked until admin explicitly increases planned
- Implement `desbloqueio_manual()` — admin override to unblock with audit trail
- Add endpoints to router: `POST /ingressos/v2/eventos/{evento_id}/recebimentos`, `GET /ingressos/v2/eventos/{evento_id}/inventario`
- Write tests covering: normal receipt, partial receipt with blocking, surplus blocking, auto-unblock, manual unblock

## Details

- For `modo = interno_emitido_com_qr`, there is no reconciliation — `disponivel = planejado - distribuido`
- For `modo = externo_recebido`, `disponivel = min(recebido_confirmado, planejado) - distribuido`; surplus `max(recebido_confirmado - planejado, 0)` is blocked
- `RecebimentoIngresso` stores artifact references: file path, drive link, or text instructions (all optional, at least one recommended)
- `desbloqueio_manual` requires admin role and creates an audit record
- **Design decision (Task 1 review)**: `InventarioIngresso` is stored as a **materialized snapshot** row per (evento, diretoria, tipo_ingresso). The `calcular_inventario()` function **updates this snapshot** by aggregating from previsao + recebimentos + distribuicoes + ajustes. This avoids expensive JOINs on every inventory read and simplifies dashboard queries (Task 7). The reconciliation service (this task) is the sole writer of the snapshot.
- `correlation_id` links recebimento records to downstream operations

## Verification

- Registering a receipt for 50 when planned is 100 shows 50 blocked
- Registering another receipt of 50 auto-unblocks (total received = planned)
- Receiving 120 when planned is 100 shows 20 surplus blocked
- Admin increasing planned to 120 releases the surplus
- Manual unblock by admin creates audit trail
- Internal mode returns `disponivel = planejado - distribuido` without reconciliation

---

# Task 4: Implement Distribution and Recipient Lifecycle

Build the distribution flow where available tickets are assigned to recipients with full lifecycle tracking (enviado → confirmado → utilizado → cancelado).

## TODOs

- Add distribution schemas: `DistribuicaoIngressoCreate` (nome, email, evento_id, diretoria_id, tipo_ingresso), `DistribuicaoIngressoRead`, `DistribuicaoIngressoUpdate`
- Implement `POST /ingressos/v2/eventos/{evento_id}/distribuicoes` — assign a ticket to a recipient; validate availability from inventory; generate `qr_uuid`; set status to `enviado`; trigger email
- Implement `GET /ingressos/v2/eventos/{evento_id}/distribuicoes` — list distributions with filters (diretoria, tipo, status)
- Implement `PATCH /ingressos/v2/distribuicoes/{id}/confirmar` — recipient confirms receipt, status → `confirmado`
- Implement `PATCH /ingressos/v2/distribuicoes/{id}/utilizar` — mark as used, status → `utilizado`
- Implement `POST /ingressos/v2/distribuicoes/{id}/cancelar` — cancel distribution, status → `cancelado`, return ticket to available pool, trigger cancellation email, record reason
- Implement recipient selection endpoint: `GET /ingressos/v2/eventos/{evento_id}/disponiveis` — list available tickets for selection by recipient
- Write tests for full lifecycle and edge cases (cancel+redistribute, double-confirm, distribute beyond availability)

## Details

- Distribution checks inventory availability before creating; rejects if `disponivel <= 0`
- Cancellation returns the ticket to the available pool by decrementing the distributed count (computed from active distributions)
- Email on `enviado`: uses `send_email()` from existing service with ticket details
- Email on `cancelado`: notifies recipient that their ticket was cancelled
- `qr_uuid` is generated via `uuid.uuid4()` and stored on the `DistribuicaoIngresso` record
- Lifecycle timestamps: `enviado_em`, `confirmado_em`, `utilizado_em`, `cancelado_em` — each set when the corresponding transition occurs
- A cancelled ticket can be redistributed to a new recipient (creates a new `DistribuicaoIngresso`)

## Verification

- Distributing a ticket sends email and sets status to `enviado`
- Confirming updates status and sets `confirmado_em`
- Cancelling returns ticket to available pool and sends cancellation email
- Cannot distribute when no tickets are available
- Full lifecycle works: enviado → confirmado → utilizado
- Cancelled ticket's slot can be redistributed

---

# Task 5: Implement Internal QR Ticket PDF Generation

Build the PDF generation for internally emitted tickets (mode `interno_emitido_com_qr`) containing a unique QR code linked to the recipient.

## TODOs

- Add `qrcode` and `reportlab` (or `fpdf2`) to backend dependencies
- Create service `backend/app/services/ticket_pdf.py` with `gerar_pdf_ingresso()` function
- Generate QR code image from the `qr_uuid` of the distribution record
- Build PDF with: event name, ticket type, recipient name, recipient email, QR code image, date of issuance
- Implement `GET /ingressos/v2/distribuicoes/{id}/pdf` — returns the generated PDF as a downloadable response
- Store or cache the generated PDF path/bytes (configurable: local filesystem or S3-compatible via env var)
- Write tests that verify PDF generation produces a valid file with correct content

## Details

- v1 uses a simple layout — no branded design, just structured information
- QR encodes only the UUID string (not a URL) — future validator will look up the UUID
- PDF is generated on-demand or at distribution time and cached
- Only available for events with `modo = interno_emitido_com_qr`
- Endpoint returns 404 if the event mode is `externo_recebido`
- LGPD: PDFs contain PII (name, email) — access requires authentication and event visibility

## Verification

- PDF is generated with readable QR code containing the correct UUID
- PDF includes event name, ticket type, recipient name, email, and date
- Endpoint returns PDF with correct content-type (`application/pdf`)
- Returns 404 for external-mode events

---

# Task 6: Implement Operational Adjustments and Incidents

Build the endpoints for reallocation (between types and diretorias), increase, reduction, and operational incident reporting.

## TODOs

- Add schemas: `AjusteIngressoCreate` (tipo_ajuste, source/target diretoria+tipo, quantidade, motivo optional), `AjusteIngressoRead`, `OcorrenciaIngressoCreate`, `OcorrenciaIngressoRead`
- Implement `POST /ingressos/v2/eventos/{evento_id}/ajustes` — create an adjustment; validate that source has sufficient availability for remanejamento; update inventory accordingly
- Implement `GET /ingressos/v2/eventos/{evento_id}/ajustes` — list adjustments with filters
- Implement `POST /ingressos/v2/eventos/{evento_id}/ocorrencias` — report an operational incident with canonical type and description
- Implement `GET /ingressos/v2/eventos/{evento_id}/ocorrencias` — list incidents with filters
- Validate reallocation: source diretoria+tipo must have `disponivel >= quantidade`
- Aumento increases planned quantity; reducao decreases it (with guard against going below distributed)
- Write tests for each adjustment type and incident creation

## Details

- `remanejamento` is immediate reallocation: decrements source `disponivel`, increments target `disponivel`
- `aumento` and `reducao` modify the `PrevisaoIngresso.quantidade` for the target diretoria+tipo
- Motivo is optional for remanejamento, not tracked for aumento/reducao beyond the adjustment record itself
- Incidents are informational records — they don't change inventory but are surfaced in the dashboard
- Canonical incident types: `entrega_errada`, `quantidade_divergente`, `destinatario_invalido`, `outro`
- All adjustments record the acting user and timestamp

## Verification

- Reallocation between diretorias updates both source and target availability
- Reallocation fails if source has insufficient availability
- Aumento increases planned and available counts
- Reducao fails if it would drop planned below distributed
- Incidents are recorded and listable with correct canonical types

---

# Task 7: Build Dashboard Ativos Backend

Create the backend analytics endpoint for the assets dashboard, following the same pattern as the leads dashboard.

## TODOs

- Create schemas in `backend/app/schemas/dashboard_ativos.py`: `DashboardAtivosQuery`, `DashboardAtivosKpis`, `DashboardAtivosSeries`, `DashboardAtivosResponse`
- Create service `backend/app/services/dashboard_ativos.py` with `build_dashboard_ativos()` function
- Implement KPIs: total planejado, total recebido, total bloqueado, total disponivel, total distribuido, total remanejado, total aumentado, total reduzido, total problemas
- Implement breakdown by diretoria (= area in v1) with the same KPI split
- Implement breakdown by tipo_ingresso with the same KPI split
- Implement time series for distributions over time
- Add endpoint `GET /dashboard/ativos` in a new router `backend/app/routers/dashboard_ativos.py`
- Support filters: evento_id, diretoria_id, tipo_ingresso, data_inicio, data_fim
- Register router in `main.py`
- Write tests for KPI calculations and filters

## Details

- Follow the exact pattern of `dashboard_leads.py` router and `DashboardLeadsResponse` schema structure
- KPIs are computed by aggregating across `PrevisaoIngresso`, `RecebimentoIngresso`, `DistribuicaoIngresso`, `AjusteIngresso`, `OcorrenciaIngresso`
- Agency visibility filtering follows the same `_apply_visibility` pattern
- v1 does not expose this as an API for OpenClaw (out of scope)
- `Area` = `Diretoria` for v1 purposes

## Verification

- KPIs return correct aggregated counts matching the underlying data
- Filtering by evento_id returns only data for that event
- Breakdown by diretoria sums to the total KPIs
- Time series returns distribution counts per period

---

# Task 8: Build Frontend Operational Screens

Evolve the existing ativos/ingressos frontend pages to support the new v2 domain: event configuration, inventory view, distribution with recipient selection, and adjustment forms.

## TODOs

- Create API client `frontend/src/services/ingressos_v2.ts` with functions for all v2 endpoints
- Create event configuration page/modal: select active ticket types, set supply mode
- Evolve `AtivosList.tsx` to show inventory by tipo_ingresso with columns for planejado, recebido, bloqueado, disponivel, distribuido
- Create distribution interface: select available ticket → enter recipient name + email → submit → show lifecycle status
- Create receipt registration form for external mode: quantity, artifact upload/link/instructions
- Create adjustment forms: reallocation (source → target), increase, reduction
- Create incident reporting form with canonical type dropdown and description
- Add cancellation action on distributed tickets with confirmation dialog
- Show lifecycle status badges on distribution list (enviado, confirmado, utilizado, cancelado)
- Add PDF download button for internal-mode tickets

## Details

- Follow existing UI patterns from `AtivosList.tsx` and `IngressosPortal.tsx` (cards, filters, modals)
- Recipient selection interface: list of available tickets filtered by tipo, click to assign, fill name+email in modal
- Mode-specific UI: hide receipt registration for internal mode; hide PDF download for external mode
- Reuse existing component patterns (filter bars, data tables, status chips)
- Route structure: keep `/ativos` and `/ingressos` routes, add sub-routes or tabs for v2 features

## Verification

- Can configure an event with selected ticket types and supply mode
- Inventory view shows correct counts by tipo_ingresso
- Can distribute a ticket and see it appear with `enviado` status
- Can cancel a distribution and see it return to available
- PDF download works for internal-mode tickets
- Adjustment forms correctly update inventory

---

# Task 9: Build Frontend Dashboard Ativos

Add the assets dashboard page to the frontend dashboard module, following the leads dashboard pattern.

## TODOs

- Add `ativos-dashboard` entry to `dashboardManifest.ts` with route `/dashboard/ativos`, domain `ativos`, enabled: true
- Create API client function `getDashboardAtivos()` in `frontend/src/services/dashboard_ativos.ts`
- Create `DashboardAtivosPage.tsx` in `frontend/src/pages/dashboard/`
- Implement KPI cards row: planejado, recebido, bloqueado, disponivel, distribuido, problemas
- Implement breakdown table by diretoria with all KPI columns
- Implement breakdown chart by tipo_ingresso (stacked bar or grouped bar)
- Implement distribution timeline chart
- Add event and date range filters
- Register route in `AppRoutes.tsx`
- Write tests for loading, empty, and populated states

## Details

- Follow the visual and structural pattern from the leads dashboard pages (KPI cards, charts, filters)
- Reuse existing dashboard layout components (`DashboardCard`, grid system)
- Charts can use the same charting library already in use in the leads dashboard
- The content aligns with the `Acompanhamento Alceu.pdf` reference: overview by area (diretoria), by ticket type, distribution status, and problems
- Filters: evento selector, diretoria selector, date range picker

## Verification

- Dashboard appears in the dashboard home manifest
- KPI cards show correct aggregated numbers
- Breakdown by diretoria matches the total KPIs
- Filters correctly narrow the displayed data
- Loading and empty states render correctly

---

# Task 10: Implement OpenClaw Minimal Write API

Expose a minimal authenticated API contract that allows the external OpenClaw skill to register external ticket receipts.

## TODOs

- Create router `backend/app/routers/integracoes_ingressos.py` with prefix `/integracoes/ingressos/v1`
- Implement `POST /integracoes/ingressos/v1/recebimentos` — accepts evento_id, diretoria_id, tipo_ingresso, quantidade, artifact metadata; delegates to `registrar_recebimento()` service
- Add API key or service-account authentication (separate from user JWT) via header `X-API-Key`
- Add request validation and error responses matching the internal API patterns
- Add rate limiting or basic abuse guard
- Register router in `main.py`
- Write tests with mock API key
- Document the contract in `backend/docs/api_integracoes_ingressos.md`

## Details

- This is the **write-only** contract for v1; read/analytics API for OpenClaw is out of scope
- API key is stored as an environment variable (`OPENCLAW_API_KEY`) and validated via a dependency
- The endpoint reuses the same `registrar_recebimento()` service from Task 3 — no separate logic
- Request body includes optional `correlation_id` for the caller to trace operations
- Response returns the created `RecebimentoIngresso` ID and the updated inventory snapshot

## Verification

- Endpoint accepts a valid receipt and returns inventory snapshot
- Request without valid API key returns 401
- Invalid payload (missing required fields, unknown tipo_ingresso) returns 422
- Receipt triggers the same reconciliation/blocking logic as the internal endpoint