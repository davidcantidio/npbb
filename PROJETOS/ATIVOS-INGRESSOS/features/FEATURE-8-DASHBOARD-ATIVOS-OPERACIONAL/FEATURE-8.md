---
doc_id: "FEATURE-8.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-8"
feature_slug: "DASHBOARD-ATIVOS-OPERACIONAL"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
  - "FEATURE-4"
  - "FEATURE-6"
audit_gate: "not_ready"
---

# FEATURE-8 - Dashboard de ativos operacional

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-8-DASHBOARD-ATIVOS-OPERACIONAL/FEATURE-8.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.3–2.4 (leituras planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido, problemas), 2.6 design (padrao leads), 4.1 frontend, 6 fora (redesign dashboard)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 6 dentro, 14 (drill-down problemas em aberto)
- **depende_de**: `FEATURE-2`, `FEATURE-4`, `FEATURE-6`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: diretorias e operacao nao tem visao consolidada dos saldos e ocorrencias no padrao ja homologado do modulo Dashboard (leads).
- **Resultado de negocio esperado**:
  - **Dashboard > Ativos** expoe leituras **separadas** para as dimensoes operacionais do PRD, alinhadas ao baseline visual/estrutural de leads.
  - Painel de ocorrencias/problemas visivel; drill-down detalhado pode seguir decisao UX pendente (Intake 14) sem bloquear v1 minimo acordado no PRD.

## 2. Comportamento Esperado

- Utilizador autorizado acessa visao por evento (e filtros alinhados ao padrao existente) com indicadores de: planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido, problemas.
- Graficos e tabelas seguem o **mesmo padrao** do dashboard de leads (PRD 2.6 / 6).
- PDF operacional externo citado no intake permanece **referencia informativa** de metricas, nao spec de layout.

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md) *(dados base e rollout)*, [FEATURE-4](../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md) *(recebido/bloqueado)*, [FEATURE-6](../FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/FEATURE-6.md) *(distribuido, remanejado, ajustes, problemas)*

## 4. Criterios de Aceite

- [ ] Nova entrada de navegacao **Dashboard > Ativos** (ou equivalente) acessivel com RBAC consistente.
- [ ] Leituras distintas para planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido e problemas — sem misturar semantica de remanejado com ajustes (PRD 2.6).
- [ ] Acompanhamento por data e painel de ocorrencias conforme escopo minimo fechado na decomposicao US (PRD sec. 3 lista recortes obrigatorios v1 — se ainda abertos, FEATURE documenta entregaveis minimos para **um evento real** sem planilha paralela).
- [ ] Nao redesenha o modulo Dashboard fora do padrao leads (PRD 6).
- [ ] Metricas leading/lagging do PRD 2.5 mapeadas para pelo menos um widget ou export quando dados existirem.

## 5. Riscos Especificos

- Lacuna PRD sec. 3 sobre recortes exatos do v1 — pode exigir decisao rapida na fase US ou ADR para nao atrasar entrega.
- Performance com muitos eventos — paginacao e agregacoes no backend.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: views materializadas ou agregacoes se necessario; sem duplicar fonte de verdade.
2. **API / backend**: endpoints de agregacao read-only, alinhados ao padrao do dashboard de leads existente.
3. **UI / superficie**: reutilizar componentes/patterns do frontend de leads; nova rota sob modulo Dashboard.
4. **Testes e evidencias**: testes de API de agregacao; smoke E2E de navegacao.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Views ou queries agregadas | Performance |
| Backend | Novos endpoints read-only | Cache opcional |
| Frontend | Novas paginas dashboard | Consistencia visual leads |
| Testes | Snapshot/API | |
| Observabilidade | Queries lentas | Alertas se aplicavel |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-8-01 | Agregacoes read-only e endpoints do dashboard de ativos | 5 | nenhuma | todo | [README.md](user-stories/US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS/README.md) |
| US-8-02 | Navegacao Dashboard Ativos e shell com RBAC | 3 | nenhuma | todo | [README.md](user-stories/US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC/README.md) |
| US-8-03 | Widgets das oito dimensoes operacionais | 5 | US-8-01, US-8-02 | todo | [README.md](user-stories/US-8-03-WIDGETS-DIMENSOES-OPERACIONAIS/README.md) |
| US-8-04 | Serie temporal, ocorrencias e metricas PRD 2.5 | 4 | US-8-03 | todo | [README.md](user-stories/US-8-04-SERIE-TEMPORAL-OCORRENCIAS-E-METRICAS-PRD/README.md) |

## 10. Referencias e Anexos

- Documento externo tipo Alceu (citado no intake) apenas informativo

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` correto
- [x] Criterios e impacts preenchidos
- [x] Tabela US apos decomposicao
