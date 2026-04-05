---
doc_id: "FEATURE-8"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-04-05"
project: "ATIVOS-INGRESSOS"
feature_key: "FEATURE-8"
feature_slug: "DASHBOARD-OPERACIONAL-DE-ATIVOS"
prd_path: "../../PRD-ATIVOS-INGRESSOS.md"
intake_path: "../../INTAKE-ATIVOS-INGRESSOS.md"
depende_de:
  - "FEATURE-3"
  - "FEATURE-4"
  - "FEATURE-5"
  - "FEATURE-6"
  - "FEATURE-7"
audit_gate: "not_ready"
generated_by: "fabrica-cli"
generator_stage: "feature"
---

# FEATURE-8 - Dashboard Operacional de Ativos

## 0. Rastreabilidade

- **Projeto**: `ATIVOS-INGRESSOS`
- **PRD**: [PRD-ATIVOS-INGRESSOS.md](../../PRD-ATIVOS-INGRESSOS.md)
- **Intake**: [INTAKE-ATIVOS-INGRESSOS.md](../../INTAKE-ATIVOS-INGRESSOS.md)
- **depende_de**: [`FEATURE-3`, `FEATURE-4`, `FEATURE-5`, `FEATURE-6`, `FEATURE-7`]

### Evidencia no PRD

- **Secao / ancora**: `2.5 Escopo > Dentro` - **Sintese**: `dashboard de ativos dentro do modulo Dashboard, seguindo o padrao visual e estrutural ja adotado no dashboard de leads; conteudo analitico alinhado a referencia `Acompanhamento Alceu.pdf`.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Criterio de cobertura analitica minima**: o dashboard do v1 precisa expor, no minimo, os KPIs `Total Recebidos`, `Total Utilizados` e `Total Remanejados`, a leitura temporal por data, a distribuicao por `Area/Diretoria` e tipo de ingresso, e a tabela de problemas operacionais observada na referencia analitica.`
- **Secao / ancora**: `2.6 Resultado de Negocio e Metricas` - **Sintese**: `**Metricas lagging**: taxa de reenvio ou erro operacional; tempo medio entre recebimento e envio final; quantidade de bloqueios por falta de recebimento; quantidade de problemas operacionais por evento; uso recorrente do dashboard pela operacao.`

## 1. Objetivo de Negocio

- **Problema que esta feature resolve**: A operacao e a gestao precisam de visibilidade padronizada dos KPIs e cortes analiticos do inventario e da distribuicao para tomada de decisao.
- **Resultado de negocio esperado**: Oferecer acompanhamento operacional e executivo com indicadores confiaveis e navegacao alinhada ao padrao do produto.

## 2. Comportamento Esperado

- Exibicao dos KPIs principais e cortes por tempo, Area/Diretoria e tipo de ingresso.
- Tabela de problemas operacionais e leitura de remanejamentos de forma auditavel.

## 3. Dependencias entre Features

- **depende_de**: [`FEATURE-3`, `FEATURE-4`, `FEATURE-5`, `FEATURE-6`, `FEATURE-7`]

## 4. Criterios de Aceite

- [ ] O dashboard exibe `Total Recebidos`, `Total Utilizados` e `Total Remanejados` conforme definicao do PRD.
- [ ] Ha leitura temporal por data e distribuicao por `Area/Diretoria` e tipo de ingresso.
- [ ] A tabela de problemas operacionais e exibida, com capacidade de filtro por evento/diretoria/tipo.

## 5. Riscos Especificos

- Risco de produto: tentar fechar operacao, analitico e preparacao para automacao no mesmo ciclo pode diluir a entrega do primeiro evento real.

## 6. Estrategia de Implementacao

1. Decompor a feature em User Stories a partir do comportamento esperado.
2. Derivar tasks a partir das US sem criar backlog paralelo fora da arvore canonica.
3. Validar criterios de aceite, dependencias e impactos por camada ao longo da execucao.

## 7. Impactos por Camada

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | Consultas e agregacoes analiticas. | Views e materializacoes para KPIs e series temporais. |
| Backend | Endpoints de analytics. | Agregacoes por dimensoes e servir dados para o modulo Dashboard. |
| Frontend | Paginas e componentes de dashboard. | KPI cards, series temporais, distribuicoes e tabela de problemas. |
| Testes | Validacao de KPIs e filtros. | Testes de consistencia numerica e navegabilidade dos filtros. |
| Observabilidade | Saude do pipeline analitico. | Monitores para freshness, latencia e erros nas agregacoes. |

## 8. Estado Operacional

- **status**: `todo`
- **audit_gate**: `not_ready`

## 9. User Stories (rastreabilidade)

> Preencher apenas apos a etapa `Feature -> User Stories`.

| US ID | Titulo | SP estimado | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-8.1 | <comportamento fatiado> | 3 | - | todo | `user-stories/US-8-01-<SLUG>/README.md` |
| US-8.2 | <comportamento complementar> | 2 | US-8.1 | todo | `user-stories/US-8-02-<SLUG>/README.md` |

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
