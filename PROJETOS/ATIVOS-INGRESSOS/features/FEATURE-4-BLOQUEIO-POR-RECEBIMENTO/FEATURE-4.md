---
doc_id: "FEATURE-4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-4"
feature_slug: "BLOQUEIO-POR-RECEBIMENTO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-3"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-4 - Bloqueio por Recebimento

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-3`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `desbloqueio automatico de saldo quando novo `recebido_confirmado` suficiente e registrado; desbloqueio manual por administrador com trilha de auditoria.`
- **Secao / ancora**: `2.7 Restricoes e Guardrails` - **Sintese**: `**Restricoes operacionais**: desbloqueio automatico ocorre quando novo `recebido_confirmado` suficiente e registrado; desbloqueio manual por administrador e excecao auditada.`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: Saldos bloqueados por divergencia de recebimento devem ser desbloqueados automaticamente quando houver novo `recebido_confirmado` suficiente ou por acao manual auditada do administrador.
- **Resultado de negocio esperado**: Acelerar disponibilidade operacional sem riscos, liberando automaticamente o que passou a estar conciliado e registrando excecoes manuais.

## 2. Comportamento Esperado

- Quando o recebido confirmado atingir o planejado, o bloqueio correspondente e liberado automaticamente.
- Administradores conseguem executar desbloqueio manual com auditoria.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-3`]

## 4. Criterios de Aceite

- [ ] Ao registrar novo `recebido_confirmado` suficiente, itens `bloqueado_por_recebimento` migram para `disponivel` automaticamente e o evento e auditado.
- [ ] Desbloqueio manual exige confirmacao explicita e grava usuario, timestamp e justificativa (quando informada).
- [ ] Tentativas de desbloqueio quando o saldo ainda nao e elegivel retornam erro de validacao com orientacao da regra.

## 5. Riscos Especificos

- Risco operacional: processos manuais sem auditoria podem liberar saldo incorretamente.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Transicoes de estado. | Registro de historico de desbloqueios automaticos e manuais. |
| Backend | Jobs e regras de elegibilidade. | Servicos que avaliam recebidos e executam transicoes atomicas com logs. |
| Frontend | Acoes administrativas. | Botao/acao de desbloqueio manual com confirmacao e exibicao de logs. |
| Testes | Fluxos automatico e manual. | Testes para desbloqueio por novo recebido e para tentativas indevidas. |
| Observabilidade | Auditoria e alertas. | Eventos de desbloqueio, contadores e alertas de excecoes manuais. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-4.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-4-01-<SLUG>/README.md` |
| US-4.2 | <comportamento complementar> | 2 | US-4.1 | todo | `user-stories/US-4-02-<SLUG>/README.md` |

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
