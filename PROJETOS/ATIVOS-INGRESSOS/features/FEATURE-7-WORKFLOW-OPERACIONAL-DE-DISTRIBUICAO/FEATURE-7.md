---
doc_id: "FEATURE-7"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-7"
feature_slug: "WORKFLOW-OPERACIONAL-DE-DISTRIBUICAO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-3"
  - "FEATURE-4"
  - "FEATURE-5"
  - "FEATURE-6"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-7 - Workflow Operacional de Distribuicao

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-3`, `FEATURE-4`, `FEATURE-5`, `FEATURE-6`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `interface de selecao de destinatario (nome e email) por ingresso disponivel, com disparo de email pelo sistema e rastreamento do ciclo de vida: `enviado → confirmado → utilizado → cancelado`. cancelamento de ingresso distribuido com notificacao por email ao destinatario e retorno ao saldo disponivel para redistribuicao. fluxo de distribuicao, remanejamento entre tipos e entre diretorias, aumento, reducao e registro de problemas operacionais com tipos canonicos.`
- **Secao / ancora**: `2.8 Dependencias e Integracoes` - **Sintese**: `**Dados de saida esperados**: inventario reconciliado, historico de distribuicao com ciclo de vida por destinatario, bloqueios por recebimento, trilha de remanejamentos, registro de cancelamentos com notificacao, registro de problemas, dashboard operacional e contratos consumiveis por integracoes externas.`
- **Secao / ancora**: `2.8 Dependencias e Integracoes` - **Sintese**: `**Sistemas externos impactados**: ticketeiras, links de drive recebidos por email, provedores de email de saida (envio ao destinatario e notificacao de cancelamento) e skill operacional do OpenClaw.`
- **Secao / ancora**: `2.7 Restricoes e Guardrails` - **Sintese**: `**Restricoes operacionais**: `remanejado` significa apenas realocacao efetiva com efeito imediato nos saldos; permitido entre tipos de ingresso e entre diretorias; motivo nao obrigatorio; aumento, reducao e saldo nao distribuido precisam aparecer como leituras separadas.`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: A distribuicao precisa selecionar destinatarios, disparar emails e rastrear o ciclo de vida completo, incluindo cancelamentos e remanejamentos com reflexo imediato de saldos.
- **Resultado de negocio esperado**: Reduzir falhas na entrega e dar rastreabilidade ponta a ponta da distribuicao por destinatario.

## 2. Comportamento Esperado

- Selecao de destinatario (nome e email) por item disponivel, com envio de email automatico.
- Rastreamento do ciclo de vida `enviado → confirmado → utilizado → cancelado` com timestamps e reversao de saldo apos cancelamento.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-3`, `FEATURE-4`, `FEATURE-5`, `FEATURE-6`]

## 4. Criterios de Aceite

- [ ] A interface permite selecionar destinatario e dispara email de envio registrando estado `enviado`.
- [ ] As transicoes `enviado → confirmado → utilizado → cancelado` sao persistidas com timestamp e usuario (quando aplicavel).
- [ ] Ao cancelar, o destinatario e notificado por email e o ingresso retorna ao saldo `disponivel`.
- [ ] Remanejamentos entre tipos/diretorias atualizam saldos imediatamente e aparecem como leituras separadas de aumento/reducao, sem obrigatoriedade de motivo.

## 5. Riscos Especificos

- Risco operacional: envio duplicado ou cancelamento sem notificacao pode confundir destinatarios e comprometer a experiencia.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Tabelas de ciclo de vida e remanejamento. | Persistencia por destinatario, trilha de remanejamentos e cancelamentos. |
| Backend | Orquestracao de distribuicao e emails. | Servicos para transicoes de estado, notificacoes e regras de remanejamento. |
| Frontend | UI de distribuicao e gerenciamento. | Fluxos de selecao, envio, cancelamento e remanejamento com validacoes. |
| Testes | E2E de distribuicao. | Cenarios de envio, confirmacao, utilizacao, cancelamento e remanejamento. |
| Observabilidade | Eventos de ciclo de vida. | Logs por destinatario e metricas de taxa de confirmacao/uso/cancelamento. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-7.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-7-01-<SLUG>/README.md` |
| US-7.2 | <comportamento complementar> | 2 | US-7.1 | todo | `user-stories/US-7-02-<SLUG>/README.md` |

## 10. Referencias e Anexos

- `PROJETOS/COMUM/GOV-FEATURE.md`
- `PROJETOS/COMUM/PROMPT-FEATURE-PARA-USER-STORIES.md`

---

## Checklist de prontidao do manifesto

- [ ] `feature_key`, `feature_slug` e pasta `FEATURE-<N>-<SLUG>/` estao coerentes
- [ ] PRD e intake estao referenciados com caminhos relativos corretos
- [ ] Evidencia no PRD esta preenchida com `secao / ancora` + `sintese`
- [ ] `depende_de` reflete a ordem real entre features
- [ ] Criterios de aceite e impactos por camada estao preenchidos
- [ ] Tabela de User Stories so e atualizada apos a etapa `Feature -> User Stories`

> Frase guia: Feature organiza, User Story fatia, Task executa, Teste valida.
