---
doc_id: "DECISION-PROTOCOL.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# DECISION-PROTOCOL - DASHBOARD-LEADS-ETARIA

## Objetivo

Registrar decisoes especificas do projeto `dashboard-leads-etaria` quando houver alteracao de escopo, convencao visual, contrato de API, estrutura de componentes ou qualquer outro ajuste que contradiga o framework comum ou o PRD vigente.

## Status Atual

- `DECISAO-DLE-001` aprovada: manter a rota interna do endpoint em `/dashboard/leads/analise-etaria` nesta fase.

## DECISAO-DLE-001 - Contrato de rota interna da analise etaria

**Data:** 2026-03-08  
**Status:** aprovada  
**Contexto:** O PRD e parte dos artefatos da fase F1 passaram a citar `GET /api/v1/dashboard/leads/analise-etaria`, mas a arquitetura atual do repositorio usa `VITE_API_BASE_URL=/api` no frontend com proxy/rewrite para rotas internas sem versionamento no backend. O consumidor real da feature e os testes existentes ja usam `/dashboard/leads/analise-etaria`.

**Decisao:** Nesta fase, o contrato interno do backend para a analise etaria permanece `GET /dashboard/leads/analise-etaria`. O prefixo `/api` continua sendo responsabilidade da base URL/proxy do cliente. Nenhum alias `/v1` sera criado nesta entrega.

**Alternativas consideradas:**
- Manter `/api/v1` como contrato interno: rejeitada porque diverge do padrao operacional atual do backend e do frontend.
- Criar alias `/v1` temporario: rejeitada porque aumentaria superficie de contrato sem necessidade funcional imediata.

**Consequencias:** Os artefatos imediatos da F1 devem refletir `/dashboard/leads/analise-etaria`. Referencias remanescentes a `/api/v1` fora da F1 ficam tratadas como drift documental para follow-up posterior.

**Aprovada por:** Produto / Engenharia  
**Referencias:** `frontend/src/services/http.ts`, `frontend/src/services/dashboard_age_analysis.ts`, `backend/app/routers/dashboard.py`

## Regras Locais

- usar `PROJETOS/COMUM/DECISION-PROTOCOL.md` como taxonomia base
- registrar neste arquivo apenas decisoes especificas do projeto
- qualquer mudanca estrutural deve referenciar o documento comum correspondente
- decisoes sobre contratos de API ou thresholds de cobertura devem apontar para o PRD do projeto
