---
doc_id: "FEATURE-3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-3"
feature_slug: "RECONCILIACAO-E-PREVALENCIA"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-1"
  - "FEATURE-2"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-3 - Reconciliacao e Prevalencia

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-1`, `FEATURE-2`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `reconciliacao entre quantidade `planejado` e quantidade `recebido_confirmado`.`
- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `regra de prevalencia do `recebido_confirmado` para ativos originados em ticketeira; excedente da ticketeira fica `bloqueado_por_recebimento` ate aumento explicito do planejado pelo administrador.`
- **Secao / ancora**: `2.7 Restricoes e Guardrails` - **Sintese**: `**Restricoes operacionais**: para origem `externo_recebido`, a quantidade distribuivel deve refletir o `recebido_confirmado`, mesmo quando divergir do `planejado`; excedente da ticketeira fica `bloqueado_por_recebimento` ate aumento explicito do planejado pelo administrador.`
- **Secao / ancora**: `2.8 Dependencias e Integracoes` - **Sintese**: `**Estados canonicos de estoque**: `planejado`, `recebido_confirmado`, `bloqueado_por_recebimento`, `disponivel`, `distribuido`, `aumentado`, `reduzido`, `remanejado`, `problema_registrado`, `qr_emitido` e `qr_validado` (futuro).`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: Divergencias entre `planejado` e `recebido_confirmado` precisam ser conciliadas, aplicando prevalencia do recebido para origem externa e bloqueando excedentes corretamente.
- **Resultado de negocio esperado**: Garantir inventario confiavel, evitando distribuicao acima do recebido e mantendo rastreabilidade de estados.

## 2. Comportamento Esperado

- Quando `recebido_confirmado` < `planejado`, a quantidade distribuivel reflete o recebido.
- Quando `recebido_confirmado` > `planejado`, excedentes sao marcados como `bloqueado_por_recebimento`.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-1`, `FEATURE-2`]

## 4. Criterios de Aceite

- [ ] Para eventos `externo_recebido` com `recebido_confirmado` menor que `planejado`, a quantidade distribuivel exibida e igual a `recebido_confirmado`.
- [ ] Para `recebido_confirmado` maior que `planejado`, o excedente e criado como itens `bloqueado_por_recebimento` e nao entra em `disponivel`.
- [ ] Todos os ajustes atualizam corretamente os estados canonicos e geram trilha de alteracoes para auditoria.

## 5. Riscos Especificos

- Risco operacional: classificacao errada, divergencia nao conciliada, envio duplicado ou cancelamento sem notificacao adequada pode gerar distribuicao acima do recebido, tipo incorreto, destinatario inadequado ou confusao ao destinatario.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Estados e saldos reconciliados. | Views/consultas para saldos por estado e registradores de divergencia. |
| Backend | Rotinas de conciliacao. | Servicos que calculam distribuivel e bloqueios conforme regras de prevalencia. |
| Frontend | Sinalizacao de divergencias. | Indicadores visuais e tooltips para bloqueios e excedentes. |
| Testes | Cenarios de divergencia. | Casos com maior/menor/igual recebido vs planejado e validacao dos estados. |
| Observabilidade | Metricas de reconciliacao. | Contadores de bloqueios por recebimento e alertas de divergencia persistente. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-3.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-3-01-<SLUG>/README.md` |
| US-3.2 | <comportamento complementar> | 2 | US-3.1 | todo | `user-stories/US-3-02-<SLUG>/README.md` |

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
