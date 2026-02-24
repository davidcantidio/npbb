# Restore Ativos — Summary

Data: 2026-02-05

## Onde a feature foi encontrada
- **Frontend (UI)**: `frontend/src/pages/AtivosList.tsx` (existia desde `f59b8f7` e ajustada em `4b8dbd0`).
- **Docs de contrato**: `docs/tela-inicial/menu/Ativos/ativos.md` (especifica endpoints, regras e payload).
- **Backend (parcial)**: `backend/app/routers/ingressos.py` tinha endpoints de ingressos em commit `4b8dbd0`, mas estava incompleto no HEAD (faltava GET /ingressos/solicitacoes).
- **Modelos**: `SolicitacaoIngresso` e enums existiam em `4b8dbd0` e haviam sumido do `models.py`.

## O que foi restaurado/reimplementado
- **Backend**
  - Router `/ativos` completo (listar, atribuir, excluir, exportar CSV).
  - Router `/ingressos` atualizado com `GET /ingressos/solicitacoes` (admin) restaurado.
  - Modelos `SolicitacaoIngresso`, `SolicitacaoIngressoStatus`, `SolicitacaoIngressoTipo`.
  - `CotaCortesia` com unique constraint `(evento_id, diretoria_id)` e index em `diretoria_id`.
  - Migração Alembic para `solicitacao_ingresso` + constraint/índices.
- **Frontend**
  - Service `frontend/src/services/ativos.ts`.
  - Rota `/ativos` ligada a `AtivosList`.
  - Rota `/ingressos` ligada a `IngressosPortal`.

## Arquivos principais alterados
- Backend: `backend/app/models/models.py`, `backend/app/routers/ativos.py`,
  `backend/app/routers/ingressos.py`, `backend/app/main.py`,
  `backend/alembic/versions/7c6d5e4f3a2b_add_solicitacao_ingresso_and_cota_unique.py`
- Frontend: `frontend/src/services/ativos.ts`, `frontend/src/main.tsx`
- Tests: `backend/tests/test_ativos_endpoints.py`

## Como validar localmente
Backend:
```
python -m pytest -q
```

Frontend:
```
npm run dev
```
Navegar para:
- `http://localhost:5173/ativos`
- `http://localhost:5173/ingressos`
