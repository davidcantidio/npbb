# Restore Summary - UI + Import XLSX + Dashboard

## O que foi recuperado
- Menu horizontal no header (UI).
- Fluxo completo de importacao XLSX de leads (UI + backend).
- Endpoint de dashboard de leads existente e relatorio agregado TMJ 2025.

## Onde as features estavam
- Recuperadas a partir da branch `restore/import-xlsx` (commits):
  - `ui: restaurar menu horizontal no header`
  - `ui: restaurar botão/tela de importar XLSX (mapeamento de campos + validacoes)`
  - `leads: restaurar fluxo de importar XLSX (backend importer + validacoes)`

## Arquivos principais restaurados
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/pages/EventsList.tsx`
- `frontend/src/pages/LeadsImport.tsx`
- `frontend/src/services/leads_import.ts`
- `backend/app/routers/leads.py`
- `backend/app/models/models.py`
- `backend/app/schemas/lead_import.py`
- `backend/app/utils/*` (normalizacao e matching)
- `backend/alembic/versions/2c7d9f3a8b1c_add_lead_import_fields.py`

## Como validar localmente
```
# backend
cd npbb/backend
python -m pytest -q

# frontend
cd npbb/frontend
npm run lint
npm run typecheck
```
