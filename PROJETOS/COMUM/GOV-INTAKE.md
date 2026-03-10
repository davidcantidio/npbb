---
doc_id: "GOV-INTAKE.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# GOV-INTAKE

## Objetivo

Formalizar a etapa `Intake -> PRD` para que a IA gere PRDs completos, auditaveis,
nao ingenuos e reutilizaveis tanto para novas iniciativas quanto para problemas,
refactors e remediacoes estruturais.

## Regra Canonica

- todo fluxo novo comeca em `INTAKE-<PROJETO>.md` ou `INTAKE-<PROJETO>-<SLUG>.md`
- o PRD so e elegivel quando referenciar explicitamente o arquivo de intake usado como origem
- se o intake estiver incompleto, a IA deve devolver lacunas criticas em vez de improvisar regra de negocio
- achados estruturais originados de auditoria podem abrir novos intakes com `intake_kind: audit-remediation`
- se `intake_kind` for `problem`, `refactor` ou `audit-remediation`, o PRD gerado deve ser de remediacao controlada

## Taxonomias Controladas

Usar apenas valores desta lista, salvo decisao documentada em `GOV-DECISOES.md`:

- `intake_kind`: `new-product`, `new-capability`, `problem`, `refactor`, `audit-remediation`
- `source_mode`: `original`, `backfilled`, `audit-derived`
- `product_type`: `campaign-experience`, `internal-tool`, `data-product`, `platform-capability`, `integration`, `workflow-improvement`
- `delivery_surface`: `frontend-web`, `backend-api`, `fullstack-module`, `data-pipeline`, `admin-panel`, `docs-governance`
- `business_domain`: `landing-pages`, `dashboard`, `leads`, `eventos`, `etl`, `crm`, `autenticacao`, `governanca`
- `criticality`: `baixa`, `media`, `alta`, `critica`
- `data_sensitivity`: `publica`, `interna`, `restrita`, `lgpd`
- `change_type`: `novo-produto`, `nova-capacidade`, `evolucao`, `migracao`, `refactor`, `correcao-estrutural`
- `audit_rigor`: `standard`, `elevated`, `strict`

`integrations` permanece lista livre de sistemas, servicos, APIs ou modulos afetados.

## Campos Minimos Obrigatorios

O intake nao esta pronto para PRD sem:

- problema ou oportunidade
- publico ou operador principal
- job to be done dominante
- fluxo principal esperado
- objetivo de negocio e metricas de sucesso
- restricoes e nao-objetivos
- dependencias e integracoes
- arquitetura ou superficies impactadas
- riscos relevantes
- lacunas conhecidas
- rastreabilidade de origem quando o intake vier de auditoria ou backfill

Para `intake_kind: problem | refactor | audit-remediation`, tambem sao obrigatorios:

- sintoma observado
- impacto operacional
- evidencia tecnica
- componente(s) afetado(s)
- riscos de nao agir

## Intakes Retroativos (`source_mode: backfilled`)

`backfilled` existe para reconstruir um intake a partir de evidencias ja existentes.
Ele nao cria uma via reduzida de intake nem autoriza PRD com menos clareza.

Contextos validos de origem:

- PRD existente sem intake formal
- conjunto de artefatos ativos de um projeto ja em andamento
- analise critica consolidada de documentos vigentes
- contexto historico fornecido pelo PM com rastreabilidade suficiente

Regras operacionais:

- `backfilled` muda a origem da evidencia, nao os campos minimos obrigatorios
- o intake retroativo continua obrigado a preencher problema ou oportunidade, publico ou operador principal, job to be done dominante, fluxo principal esperado, objetivo de negocio e metricas de sucesso, restricoes e nao-objetivos, dependencias e integracoes, arquitetura ou superficies impactadas, riscos relevantes e lacunas conhecidas
- quando `intake_kind` for `problem`, `refactor` ou `audit-remediation`, o backfill tambem continua obrigado a registrar sintoma observado, impacto operacional, evidencia tecnica, componente(s) afetado(s) e riscos de nao agir
- a rastreabilidade de origem continua obrigatoria em todo backfill e deve apontar o documento, auditoria ou contexto historico usado como base
- o gate `Intake -> PRD` continua valendo integralmente
- `backfilled` nao dispensa nenhuma secao exigida pelo gate e nao cria excecao para avancar com lacunas criticas
- campos historicos desconhecidos podem ficar como `nao_definido` somente se isso nao bloquear objetivo, escopo, restricoes, arquitetura ou riscos
- todo `nao_definido` precisa aparecer em `Lacunas Conhecidas`

## Gate de Prontidao para PRD

Esta e a fonte unica do gate `Intake -> PRD`.

A etapa de geracao do PRD so deve avancar quando o `INTAKE-*.md`, inclusive em `source_mode: backfilled`, responder com clareza suficiente:

- por que isso existe
- para quem existe
- o que entra e o que nao entra
- onde a mudanca toca na arquitetura
- como o sucesso sera medido
- quais restricoes e riscos sao incontornaveis
- o que ainda esta em aberto
- se existe origem auditavel de um problema ou remediacao

## Regra Anti-PRD-Ingenuo

A IA nao pode:

- preencher silenciosamente regra de negocio nao declarada
- inferir dependencia externa critica sem marcar como hipotese
- transformar wishlist em escopo fechado sem nao-objetivos claros
- ignorar restricoes de dados, seguranca, rollout ou operacao
- tratar remediacao estrutural como ajuste pontual quando o proprio intake declarar escopo sistemico

## Convivencia de PRD Derivado com PRD Principal

Quando um intake `audit-remediation` ou `refactor` gerar um PRD proprio, o
padrao canonico de convivencia com o PRD principal do projeto e o seguinte:

**PRD sibling com ponteiro no PRD principal (padrao C)**

- o PRD de remediacao vive como documento independente no formato
  `PRD-<PROJETO>-<SLUG>.md`, na raiz do projeto, ao lado do PRD principal
- o PRD sibling referencia o PRD principal e o intake de origem em seu cabecalho
- o PRD principal ganha uma secao `## PRDs Derivados` na ultima posicao do
  documento, com uma linha por sibling:

```markdown
## PRDs Derivados

| PRD | Intake de Origem | Auditoria de Origem | Escopo |
|---|---|---|---|
| [PRD-<PROJETO>-<SLUG>.md](./PRD-<PROJETO>-<SLUG>.md) | [INTAKE-<PROJETO>-<SLUG>.md](./INTAKE-<PROJETO>-<SLUG>.md) | F<N>-R<NN> | <resumo de uma linha> |
```

- o PRD sibling e o PRD principal tem ciclos de auditoria independentes; as
  fases do sibling nao aparecem no manifesto de fases do principal
- a secao `## PRDs Derivados` do principal e atualizada a cada novo sibling,
  mas nenhuma outra secao do principal e alterada
- se o PRD principal ainda nao tiver a secao `## PRDs Derivados`, ela deve ser
  criada no momento em que o primeiro sibling for gerado

Nao e permitido:

- adicionar fases de remediacao diretamente ao PRD principal
- gerar PRD de remediacao sem apontar o intake de origem no cabecalho do sibling
- omitir o ponteiro no PRD principal quando o sibling existir

## Artefatos Vinculados

- template preenchivel: `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
- prompt canonico: `PROJETOS/COMUM/PROMPT-INTAKE-PARA-PRD.md`
- sessao de intake: `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- sessao de PRD: `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
