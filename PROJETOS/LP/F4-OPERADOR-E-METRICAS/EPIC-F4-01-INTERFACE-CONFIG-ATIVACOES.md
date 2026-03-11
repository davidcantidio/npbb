---
doc_id: "EPIC-F4-01-INTERFACE-CONFIG-ATIVACOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F4-01 - Interface de Configuração de Ativações

## Objetivo

Implementar interface no frontend para o operador criar, editar e listar ativações, configurar tipo de conversão (única/múltipla) e visualizar/baixar QR. Conforme PRD seções 3 e 12 (Fase 4).

## Resultado de Negocio Mensuravel

O operador configura ativações sem depender de API direta; cada ativação tem QR visível e baixável.

## Contexto Arquitetural

- Frontend React/Vite
- Endpoints CRUD de ativações já existentes (F1)
- Autenticação de operador
- QR gerado no backend; exibir imagem ou link

## Definition of Done do Epico

- [ ] Listagem de ativações por evento
- [ ] Formulário de criação/edição de ativação
- [ ] Campo conversão única/múltipla
- [ ] QR exibido e baixável
- [ ] Protegido por autenticação de operador
- [ ] Testes E2E

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-01-001 | Listagem e formulário de ativações | Página de ativações do evento; criar/editar | 3 | todo | [ISSUE-F4-01-001-LISTAGEM-E-FORMULARIO-ATIVACOES.md](./issues/ISSUE-F4-01-001-LISTAGEM-E-FORMULARIO-ATIVACOES.md) |
| ISSUE-F4-01-002 | Exibição e download de QR | Exibir QR na interface; botão download | 2 | todo | [ISSUE-F4-01-002-EXIBICAO-E-DOWNLOAD-QR.md](./issues/ISSUE-F4-01-002-EXIBICAO-E-DOWNLOAD-QR.md) |

## Artifact Minimo do Epico

- `frontend/src/` (páginas, componentes)
- `frontend/e2e/` (testes)

## Dependencias

- [F1](../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [F2](../F2-FLUXO-CPF-FIRST-E-CONVERSAO/F2_LP_EPICS.md)
- [F3](../F3-RECONHECIMENTO-E-EXPERIENCIA-FLUIDA/F3_LP_EPICS.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F4_LP_EPICS.md)
