---
doc_id: "FEATURE-2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-2"
feature_slug: "MODOS-DE-FORNECIMENTO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-1"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-2 - Modos de Fornecimento

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-1`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `dois modos canonicos de fornecimento, mutuamente exclusivos por evento: `interno_emitido_com_qr` e `externo_recebido`; modo alteravel pelo administrador apos inicio da operacao, com registro auditado da mudanca.`
- **Secao / ancora**: `2.7 Restricoes e Guardrails` - **Sintese**: `**Restricoes operacionais**: modo do evento pode ser alterado pelo administrador apos inicio da operacao, com registro auditado da mudanca.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Criterio minimo para considerar sucesso**: um evento real consegue ser operado ponta a ponta com previsao, recebimento (se externo), conciliacao, emissao e distribuicao, com ciclo de vida do destinatario rastreado e acompanhamento no dashboard, sem depender de planilha paralela como fonte de verdade.`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: A operacao precisa definir e, quando necessario, alterar o modo de fornecimento por evento entre `interno_emitido_com_qr` e `externo_recebido`, assegurando exclusividade e trilha de auditoria.
- **Resultado de negocio esperado**: Garantir controle e rastreabilidade do modo de fornecimento por evento, permitindo ajustes operacionais sem comprometer a governanca.

## 2. Comportamento Esperado

- Somente um modo pode estar ativo por evento em qualquer momento.
- A troca de modo gera registro de auditoria com responsavel, timestamp e valores antes/depois.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-1`]

## 4. Criterios de Aceite

- [ ] Selecionar `interno_emitido_com_qr` desabilita a opcao `externo_recebido` na interface e vice-versa.
- [ ] A API rejeita persistencia de dois modos simultaneos para o mesmo evento com erro de validacao (422) e mensagem explicativa.
- [ ] Alteracao de modo apos inicio da operacao cria registro de auditoria contendo usuario, timestamp, modo_anterior e modo_novo.
- [ ] Durante a transicao, fluxos existentes (CotaCortesia/SolicitacaoIngresso) continuam funcionais conforme os guardrails de convivencia definidos.

## 5. Riscos Especificos

- Risco tecnico: formatos heterogeneos de ticketeiras e necessidade de coexistir com o modelo agregado atual aumentam a complexidade do dominio e das migracoes.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Campos/entidades para estado do modo. | Persistir modo por evento e trilha de auditoria das mudancas. |
| Backend | Regras de exclusividade e auditoria. | Validacao de exclusividade e endpoints para mudanca com logs estruturados. |
| Frontend | Controles de selecao bloqueados mutuamente. | UI reflete o modo atual e confirma mudanca com alerta de impacto. |
| Testes | Testes de exclusividade e auditoria. | Cenarios de alteracao durante operacao e rejeicao de modos simultaneos. |
| Observabilidade | Logs e metricas de modo. | Eventos de mudanca e contadores por modo ativo. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-2.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-2-01-<SLUG>/README.md` |
| US-2.2 | <comportamento complementar> | 2 | US-2.1 | todo | `user-stories/US-2-02-<SLUG>/README.md` |

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
