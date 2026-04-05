---
doc_id: "FEATURE-1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-1"
feature_slug: "CONFIGURACAO-POR-EVENTO"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de: []
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-1 - Configuracao por Evento

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: []

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `configuracao por evento dos tipos de ingresso ativos (`pista`, `pista_premium`, `camarote`), com suporte a eventos que usem apenas um ou dois tipos; tipos nao configurados nao aparecem na interface.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Objetivo principal**: reduzir erro operacional e tempo de distribuicao de ingressos, aumentando a confiabilidade do estoque operacional e a visibilidade executiva sobre ativos.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Metricas leading**: percentual de eventos com tipos de ingresso configurados; percentual de lotes com origem e artefatos rastreados; tempo entre recebimento e disponibilidade; percentual de distribuicoes com status registrado; percentual de ingressos internos emitidos com QR unico; percentual de ingressos com ciclo de vida completo rastreado (`enviado → confirmado → utilizado`).`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: Eventos possuem combinacoes distintas de tipos de ingresso e precisam de configuracao por evento que oculte tipos nao utilizados para evitar erros operacionais e poluicao da interface.
- **Resultado de negocio esperado**: Reduzir erros e retrabalho configurando apenas os tipos de ingresso relevantes por evento, melhorando a clareza operacional e a qualidade do estoque.

## 2. Comportamento Esperado

- Somente os tipos de ingresso configurados por evento aparecem na interface.
- Eventos que utilizam um ou dois tipos sao plenamente suportados sem necessidade de configuracoes artificiais.

## 3. Dependencias entre Features

- **depende_de**: []

## 4. Criterios de Aceite

- [ ] E possivel ativar/desativar tipos de ingresso por evento e persistir configuracoes com sucesso.
- [ ] Tipos desativados nao aparecem em formularios, listagens e distribuicao.
- [ ] A validacao impede salvamento de configuracoes sem ao menos um tipo ativo quando o evento exige distribuicao.
- [ ] Alteracoes de configuracao sao refletidas imediatamente nas permissoes de distribuicao.

## 5. Riscos Especificos

- Risco de adocao: a operacao pode manter planilhas paralelas se o produto nao reduzir trabalho manual de forma tangivel no primeiro evento real.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Nova configuracao por evento. | Tabelas/colunas para mapear evento→tipos_ativos e auditoria de alteracao. |
| Backend | Novas regras de validacao e APIs. | Endpoints para CRUD de configuracao de tipos por evento e cache por evento. |
| Frontend | Ajustes de UI/UX. | Toggles por tipo e filtros que ocultam tipos nao ativos. |
| Testes | Testes de configuracao e exibicao. | Cenarios com 1, 2 e 3 tipos; garantia de ocultacao de nao configurados. |
| Observabilidade | Telemetria de configuracao. | Eventos de auditoria e metricas de adesao por evento. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-1.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-1-01-<SLUG>/README.md` |
| US-1.2 | <comportamento complementar> | 2 | US-1.1 | todo | `user-stories/US-1-02-<SLUG>/README.md` |

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
