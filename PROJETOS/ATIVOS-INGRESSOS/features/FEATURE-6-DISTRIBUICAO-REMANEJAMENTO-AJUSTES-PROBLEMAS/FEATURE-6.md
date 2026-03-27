---
doc_id: "FEATURE-6.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-6"
feature_slug: "DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-2"
  - "FEATURE-3"
  - "FEATURE-4"
  - "FEATURE-5"
audit_gate: "not_ready"
---

# FEATURE-6 - Distribuicao, remanejamento, ajustes e problemas operacionais

> **Papel deste arquivo**: manifesto canonico da **Feature** versionado em Git, sob
> `features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/FEATURE-6.md`.

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md) — sec. 2.3 (estados `distribuido`, `remanejado`, `aumentado`, `reduzido`, `problema_registrado`, passo 4), 2.4 dentro (fluxo distribuicao), 2.6 (remanejado vs aumento/reducao), 4.1
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md) — sec. 5–6
- **depende_de**: `FEATURE-2`, `FEATURE-3`, `FEATURE-4`, `FEATURE-5`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: a operacao precisa distribuir, remanejar, ajustar previsao e registrar incidentes sem planilhas paralelas, respeitando tetos de recebido (externo) e emissoes (interno).
- **Resultado de negocio esperado**:
  - **Distribuido** reflete envio efetivo ao destinatario com status rastreavel (incl. reenvios quando no escopo).
  - **Remanejado** registra apenas realocacao efetiva; **aumentado** e **reduzido** aparecem como leituras distintas (PRD 2.6).
  - **Problema registrado** alimenta acompanhamento e dashboard (FEATURE-8).

## 2. Comportamento Esperado

- Operador executa distribuicao respeitando `disponivel` derivado de FEATURE-4 (externo) e regras de emissao FEATURE-5 (interno).
- Remanejamento entre areas/categorias/destinatarios gera trilha auditavel.
- Aumentos e reducoes registrados sem conflitar semanticamente com remanejamento.
- Registro de ocorrencias operacionais com campos minimos para painel de problemas.

## 3. Dependencias entre Features

- **depende_de**: [FEATURE-2](../FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md), [FEATURE-3](../FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md), [FEATURE-4](../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md), [FEATURE-5](../FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/FEATURE-5.md)

## 4. Criterios de Aceite

- [ ] Distribuicao bloqueada quando saldo disponivel insuficiente para origem externa (FEATURE-4).
- [ ] Historico de **remanejamento** consultavel com motivo quando exigido pelo PRD/intake.
- [ ] Leituras de **aumentado** e **reduzido** separadas de **remanejado** em API ou views acordadas (PRD 2.6 / risco sec. 3).
- [ ] **Problema registrado** criavel e listavel por evento; visivel para alimentar FEATURE-8.
- [ ] Convivencia com `SolicitacaoIngresso` legado ate migracao (PRD 4.0 / 2.6) documentada e testada.

## 5. Riscos Especificos

- Complexidade de UX para operador nao confundir remanejamento com ajuste de previsao.
- SLA de email/reenvio (Intake lacuna) pode afetar apenas mensagens, nao o registro de estado distribuido.

## 6. Estrategia de Implementacao

1. **Modelagem e migration**: eventos de dominio ou tabelas para distribuicao, remanejamento, ajustes, incidentes.
2. **API / backend**: transacoes consistentes; validacao de saldo; integracao com email saida para notificacoes se ja existir.
3. **UI / superficie**: `IngressosPortal` e fluxos admin evoluidos; indicadores de estado.
4. **Testes e evidencias**: cenarios de bloqueio, remanejamento, aumento/reducao, problema.

## 7. Impacts por Camada

| Camada | Impacto | Detalhamento |
|--------|---------|----------------|
| Banco | Historicos e constraints | Integridade referencial |
| Backend | `ingressos.py` e servicos | Estados e transicoes |
| Frontend | Portal e admin | Fluxos operacionais |
| Testes | `test_ingressos_endpoints` estendidos | |
| Observabilidade | Trilha completa ate problema | |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|-------|--------|-------------|------------|--------|-----------|
| US-6-01 | Distribuicao respeitando saldo disponivel | 5 | FEATURE-2, FEATURE-3, FEATURE-4, FEATURE-5 | todo | [README.md](user-stories/US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md) |
| US-6-02 | Remanejamento auditavel | 4 | US-6-01 `done`; FEATURE-2..5 | todo | [README.md](user-stories/US-6-02-REMANEJAMENTO-AUDITAVEL/README.md) |
| US-6-03 | Ajustes de previsao separados de remanejamento | 5 | US-6-01 `done`; US-6-02 recomendado; FEATURE-2..5 | todo | [README.md](user-stories/US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO/README.md) |
| US-6-04 | Registro e listagem de problemas operacionais | 4 | US-6-01 `done`; FEATURE-2..5 | todo | [README.md](user-stories/US-6-04-PROBLEMAS-OPERACIONAIS/README.md) |
| US-6-05 | Convivencia com SolicitacaoIngresso legado | 5 | US-6-01..US-6-04 `done`; FEATURE-2..5 | todo | [README.md](user-stories/US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO/README.md) |

## 10. Referencias e Anexos

- PRD baseline `SolicitacaoIngresso` em 4.0

---

## Checklist de prontidao do manifesto

- [x] `feature_key` e pasta alinhados
- [x] PRD e intake referenciados
- [x] `depende_de` correto
- [x] Criterios e impacts preenchidos
- [x] Tabela US apos decomposicao
