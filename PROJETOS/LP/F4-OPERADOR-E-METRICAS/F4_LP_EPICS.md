---
doc_id: "F4_LP_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
audit_gate: "not_ready"
---

# Epicos - LP / F4 - Operador e Métricas

## Objetivo da Fase

Implementar interface de configuração de ativações (QR, tipo de conversão), visualização de conversões por ativação e métricas/observabilidade.

## Gate de Saida da Fase

O operador pode configurar ativações via interface, visualizar conversões por ativação e acessar métricas (número de ativações, conversões por ativação, taxa de reconhecimento).

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F4-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F4-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F4-01 | Interface de Configuração de Ativações | UI para criar/editar ativações, configurar QR e tipo de conversão | F1, F2, F3 | todo | [EPIC-F4-01-INTERFACE-CONFIG-ATIVACOES.md](./EPIC-F4-01-INTERFACE-CONFIG-ATIVACOES.md) |
| EPIC-F4-02 | Visualização de Conversões e Métricas | Listar conversões por ativação; métricas leading/lagging | F1, F2, F3 | todo | [EPIC-F4-02-VISUALIZACAO-CONVERSOES-METRICAS.md](./EPIC-F4-02-VISUALIZACAO-CONVERSOES-METRICAS.md) |

## Dependencias entre Epicos

- `EPIC-F4-01`: depende de F1, F2, F3
- `EPIC-F4-02`: depende de F1, F2, F3

## Escopo desta Fase

### Dentro
- Interface para criar/editar ativações
- Exibição de QR na interface
- Configuração de conversão única/múltipla
- Listagem de conversões por ativação
- Métricas: ativações por evento, conversões por ativação, taxa de reconhecimento
- Observabilidade básica

### Fora
- Integração com sistemas de impressão de QR
- Métricas avançadas ou dashboards externos

## Definition of Done da Fase

- [ ] Operador cria/edita ativações via UI
- [ ] QR exibido e baixável na interface
- [ ] Conversões por ativação visualizáveis
- [ ] Métricas leading e lagging acessíveis
- [ ] Testes E2E da interface de operador

## Navegacao Rapida

- [Intake](../INTAKE-LP-QR-ATIVACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Audit Log](../AUDIT-LOG.md)
