# ATIVOS — Restore Summary

Data: 2026-02-05
Branch: restore/ativos-full-ui

## O que foi recuperado
- UI de "cadastro do usuário + solicitação de ingresso" (BB) recuperada do commit `f59b8f7`.
  - Arquivo base: `frontend/src/pages/IngressosPortal.tsx`.
  - Recursos: seleção de diretoria, cards de cotas disponíveis, modal de solicitação (self/terceiro).

## O que foi mantido
- Listagem administrativa de solicitações (tabela com filtros) preservada no mesmo endpoint de UI para perfis não-BB.

## O que foi inferido
- Cards agrupados por diretoria + barras empilhadas por estoque **não foram encontrados no histórico**.
  - Implementação mínima criada no frontend usando os dados de `GET /ativos`.
  - Detalhes em `docs/auditoria_eventos/ATIVOS_RESTORE_NOTES.md`.

## Arquivos principais alterados
- frontend/src/pages/IngressosPortal.tsx
- frontend/src/pages/AtivosList.tsx
- backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md
- backend/docs/auditoria_eventos/ATIVOS_RESTORE_NOTES.md

## Como validar
Frontend:
- `npm run dev`
- Verificar:
  - /ingressos: BB vê solicitação + cadastro de diretoria; não-BB vê tabela admin.
  - /ativos: cards por evento + seção por diretoria com barras empilhadas.

Backend:
- `python -m pytest -q` (endpoints de /ativos e /ingressos)
