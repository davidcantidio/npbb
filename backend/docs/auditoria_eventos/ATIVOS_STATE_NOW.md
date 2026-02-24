# ATIVOS — Estado Atual (baseline antes do restore completo)

Data: 2026-02-05
Branch: restore/ativos-full-ui

## Frontend
Rotas principais (AppLayout + main.tsx):
- /ativos -> frontend/src/pages/AtivosList.tsx
- /ingressos -> frontend/src/pages/IngressosPortal.tsx

Componentes e funcionalidades observadas:
- AtivosList: grid de cards por evento+diretoria, filtros (evento/diretoria/data), modais de atribuição e exclusão, exportação CSV, navegação para /ingressos.
- IngressosPortal (estado pré-restore): listagem administrativa de solicitações com filtros (evento/diretoria) e tabela (solicitante/indicado/status).

Arquivos-chave:
- frontend/src/pages/AtivosList.tsx
- frontend/src/pages/IngressosPortal.tsx
- frontend/src/services/ativos.ts
- frontend/src/services/ingressos.ts
- frontend/src/services/ingressos_admin.ts

## Backend
Endpoints relacionados:
- GET /ativos
- POST /ativos/{evento_id}/{diretoria_id}/atribuir
- DELETE /ativos/{cota_id}
- GET /ativos/export/csv
- GET /ingressos/ativos
- GET /ingressos/solicitacoes
- POST /ingressos/solicitacoes

Arquivos-chave:
- backend/app/routers/ativos.py
- backend/app/routers/ingressos.py
- backend/app/models/models.py (CotaCortesia, SolicitacaoIngresso, Evento, Diretoria, Usuario/Funcionario)
- backend/app/schemas/ingressos.py

## Observações
- Fluxo de solicitação de ingressos para usuário BB (cadastro de diretoria + solicitação) não estava presente na UI atual.
- Cards agrupando diretorias e barras empilhadas por estoque não estavam presentes na UI atual.
