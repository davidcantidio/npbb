---
doc_id: "FEATURE-5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-5"
feature_slug: "EMISSAO-INTERNA-COM-QR"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-1"
  - "FEATURE-2"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-5 - Emissao Interna com QR

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-1`, `FEATURE-2`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `emissao de ingressos internos unitarios em PDF com QR unico (UUID vinculado a nome e email do destinatario), preparado para validacao futura de uso unico.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Metricas leading**: percentual de eventos com tipos de ingresso configurados; percentual de lotes com origem e artefatos rastreados; tempo entre recebimento e disponibilidade; percentual de distribuicoes com status registrado; percentual de ingressos internos emitidos com QR unico; percentual de ingressos com ciclo de vida completo rastreado (`enviado → confirmado → utilizado`).`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: A operacao precisa emitir ingressos internos unitarios em PDF com QR unico vinculado ao destinatario para garantir rastreabilidade e preparacao para validacao futura.
- **Resultado de negocio esperado**: Habilitar emissao interna com identificacao unica por destinatario, reduzindo fraudes e erros de distribuicao.

## 2. Comportamento Esperado

- Cada ingresso interno gera um PDF com QR unico (UUID) atrelado ao nome e email do destinatario.
- A emissao registra o estado `qr_emitido` e mantem trilha de auditoria.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-1`, `FEATURE-2`]

## 4. Criterios de Aceite

- [ ] Ao emitir ingresso, um PDF e gerado com QR unico (UUID) e armazenado com metadados do destinatario.
- [ ] O estado `qr_emitido` e registrado e exibido na interface e APIs de consulta.
- [ ] Reemissao gera novo QR e invalida o anterior, mantendo historico de alteracoes.

## 5. Riscos Especificos

- Risco de dados: arquivos, links, QR codes e emails de destinatarios podem expor acessos indevidos se storage, expiracao e auditoria nao forem definidos cedo.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Persistencia de emissao e QRs. | Tabelas para bilhetes internos, UUID, estados e trilha de reemissao. |
| Backend | Servico de emissao e PDF. | Geracao de QR/UUID, render de PDF e seguranca de links. |
| Frontend | Acao de emissao e downloads. | UI para emitir, reemitir e acessar comprovantes com status. |
| Testes | Testes de unicidade e estados. | Garantia de UUID unico, reemissao e auditoria. |
| Observabilidade | Logs de emissao. | Metricas de tempo de emissao e falhas de geracao de PDF/QR. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-5.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-5-01-<SLUG>/README.md` |
| US-5.2 | <comportamento complementar> | 2 | US-5.1 | todo | `user-stories/US-5-02-<SLUG>/README.md` |

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
