---
doc_id: "PRD-DASHBOARD-LEADS.md"
version: "0.1"
status: "draft"
intake_kind: "problem"
owner: "PM"
last_updated: "2026-03-17"
origin_intake: "INTAKE-DASHBOARD-LEADS.md"
delivery_surface: "fullstack-module"
---

# PRD - DASHBOARD-LEADS
## Remediacao Estrutural do Vinculo Lead-Evento

## Cabecalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | problem -> remediacao controlada |
| Origem do intake | `INTAKE-DASHBOARD-LEADS.md` |
| Log de auditoria | `AUDIT-LOG.md` |
| Superficie afetada | backend de dominio/ingestao/dashboard, frontend consumidor de dashboards, banco/migracoes, ETL/importacao |

## 1. Objetivo e Contexto

Este PRD define a remediacao estrutural para tornar canonica e auditavel a relacao entre `Lead` e `Evento`, retirando `AtivacaoLead` do papel indevido de elo obrigatorio para leitura analitica por evento.

O problema ja se manifestou em producao no dashboard `/dashboard/leads/analise-etaria`: havia leads reais do evento, mas a leitura retornava vazio porque dependia do caminho `Lead -> AtivacaoLead -> Ativacao -> Evento`. A correcao transitora atual ja unifica tres caminhos de leitura (`AtivacaoLead`, `LeadBatch.evento_id` e `Lead.evento_nome = Evento.nome`) com deduplicacao por `(lead_id, evento_id)`, o que resolve o sintoma imediato, mas confirma que o modelo ainda depende de heuristicas e compensacoes.

O objetivo deste PRD e substituir a heuristica por uma fonte canonica de verdade para vinculo `lead-evento`, preservando `Ativacao` como contexto de conversao dentro do evento e mantendo compatibilidade operacional durante a transicao.

## 2. Base de Verdade Utilizada

### 2.1 Fatos confirmados

- O intake documenta sintoma em producao, impacto operacional, evidencia tecnica e componentes afetados.
- O backend atual ja possui correcao transitora no servico de dashboard que unifica tres caminhos de vinculacao e deduplica por `(lead_id, evento_id)`.
- O fluxo publico de submit cria/atualiza `Lead` com `evento_nome = evento.nome` e so cria `AtivacaoLead` quando ha `ativacao`.
- `LeadBatch` ja possui `evento_id`, o que indica que parte do pipeline conhece explicitamente o evento sem depender de ativacao.
- O frontend do dashboard ja consome um contrato estavel em `/dashboard/leads/analise-etaria` e nao precisa de mudanca de payload para corrigir a semantica do dominio.

### 2.2 Inferencias operacionais

- Qualquer relatorio por evento que nao compartilhe a mesma logica transitora atual pode voltar a divergir ou produzir falso vazio.
- `Lead.evento_nome` e evidencia util de origem, mas e fragil demais para permanecer como mecanismo principal de vinculacao.
- A remediacao precisa ser sistemica: corrigir apenas a query atual perpetuaria drift entre ingestao, persistencia e leitura analitica.

## 3. Escopo

### Dentro

- criar uma representacao canonica e persistida do vinculo `lead-evento`
- garantir que novos fluxos de ingestao e submit persistam esse vinculo sem depender de `AtivacaoLead`
- tratar `AtivacaoLead` e `ConversaoAtivacao` como contexto de conversao dentro do evento, nao como fonte primaria de pertencimento do lead ao evento
- retroprocessar ou reconstruir historico de forma segura e auditavel
- migrar consumidores analiticos por evento para a fonte canonica
- manter o contrato externo do dashboard etario estavel durante a remediacao
- adicionar observabilidade, reconciliacao e testes de paridade para a transicao

### Fora

- redesenho visual do dashboard
- detalhamento de UX por origem do vinculo nesta rodada
- remocao destrutiva imediata de campos ou tabelas legadas
- reescrita manual de dados mestres de evento
- inferencia silenciosa de evento em casos historicos ambiguos
- deduplicacao global de pessoa entre eventos diferentes

## 4. Modelo-ALVO de Dominio

### 4.1 Fonte canonica

A fonte canonica de verdade para pertencimento de lead a evento passa a ser uma nova relacao persistida `lead_evento` (nome logico e fisico recomendado), com unicidade por `(lead_id, evento_id)`.

Contrato minimo da nova persistencia:

- `id`
- `lead_id` -> FK para `lead`
- `evento_id` -> FK para `evento`
- `source_kind` -> enum/string controlado (`ativacao`, `lead_batch`, `evento_nome_backfill`, `manual_reconciled`)
- `source_ref_id` -> identificador opcional do artefato de origem
- `created_at`
- `updated_at`

Restricao obrigatoria:

- `UNIQUE (lead_id, evento_id)`

Regra de privacidade:

- a nova tabela nao deve duplicar PII do lead; apenas chaves e metadata minima de rastreabilidade.

### 4.2 Papel dos artefatos existentes

- `LeadEvento` passa a ser a unica fonte canonica para filtros e agregacoes por evento.
- `AtivacaoLead` continua existindo para representar participacao/conversao em ativacao especifica.
- `ConversaoAtivacao` continua registrando o evento de conversao via ativacao.
- `LeadBatch.evento_id` permanece metadata de ingestao e passa a alimentar a criacao do vinculo canonico.
- `Lead.evento_nome` permanece como dado bruto de origem e apoio de reconciliacao, nunca como fonte primaria de leitura analitica apos a migracao.

### 4.3 Invariantes de negocio

- todo `AtivacaoLead` valido deve corresponder a um `LeadEvento` do mesmo `evento_id` da ativacao
- um mesmo `lead` pode ter multiplos `LeadEvento` para eventos diferentes
- multiplas ativacoes do mesmo evento nao podem criar mais de um `LeadEvento` para o mesmo par `(lead_id, evento_id)`
- analytics consolidados continuam contando por vinculo `lead-evento`, nao por pessoa global unica
- nenhum consumidor analitico por evento pode depender de `AtivacaoLead` como precondicao para existencia do lead no evento

## 5. Requisitos Funcionais e de Integracao

### 5.1 Escrita de novos dados

- `POST /leads` e o wrapper publico da landing devem sempre garantir `LeadEvento` usando `event_id` ou `ativacao.evento_id`
- submit sem ativacao deve criar/assegurar `LeadEvento` mesmo sem gerar `AtivacaoLead`
- submit com ativacao deve criar/assegurar `LeadEvento` e depois `AtivacaoLead` no mesmo contexto transacional
- pipeline/importacao que finalize leads com `LeadBatch.evento_id` deve criar/assegurar `LeadEvento`
- novos fluxos ETL nao podem depender de `Lead.evento_nome` como mecanismo final de vinculacao quando o `evento_id` puder ser resolvido

### 5.2 Historico e backfill

- backfill deve ser idempotente e baseado em `UNIQUE (lead_id, evento_id)`
- ordem de resolucao historica:
  1. `AtivacaoLead -> Ativacao.evento_id`
  2. `LeadBatch.evento_id`
  3. `Lead.evento_nome` apenas quando o match com `Evento.nome` for unico e deterministico
- casos ambiguos ou nao resolvidos devem ir para relatorio de reconciliacao; nao podem ser inferidos silenciosamente
- reenvio a partir do bronze e fallback controlado para lotes onde o banco atual nao der evidencia suficiente

### 5.3 Leitura analitica

- `dashboard_service` e demais servicos por evento devem migrar para `LeadEvento` como base de leitura
- o contrato externo de `/dashboard/leads/analise-etaria` deve permanecer inalterado nesta remediacao
- filtros de visibilidade por agencia, filtros de periodo e semantica do consolidado devem ser preservados
- futuras analises por ativacao devem partir de `LeadEvento` + contexto de ativacao, nunca substituir o vinculo canonico

### 5.4 Observabilidade e reconciliacao

- gerar relatorio de paridade entre leitura transitoria atual e leitura canonica antes do switch final
- medir `% de novos leads com LeadEvento criado`
- medir volume de historicos nao reconciliados
- expor contagem de duplicidades evitadas por `UNIQUE (lead_id, evento_id)`
- registrar evidencias de migracao e reconciliacao para auditoria

## 6. Metricas de Sucesso

### Leading

- 100% dos novos fluxos com `evento_id` resolvido persistem `LeadEvento`
- dashboards por evento deixam de depender de uniao heuristica de fontes
- testes de paridade mostram delta zero para casos resolvidos pelo mesmo conjunto de dados
- historico reconciliavel e materializado sem duplicidade por `(lead_id, evento_id)`

### Lagging

- reducao de incidentes de falso vazio ou divergencia em dashboards de leads por evento
- convergencia de contagens entre analise etaria e futuros relatorios filtrados por evento
- menor necessidade de hotfix local em queries de dashboard
- auditoria futura consegue apontar uma unica fonte canonica para relacionamento `lead-evento`

### Criterio minimo de sucesso

Qualquer relatorio filtrado por evento deve contabilizar corretamente leads do evento, com ou sem ativacao, sem depender de remendo especifico por dashboard e sem inventar vinculos onde a origem historica for ambigua.

## 7. Fases Propostas

### F1 - Fundacao do Vinculo Canonico

**Objetivo:** introduzir `LeadEvento` e garantir escrita canonica para novos dados sem quebrar consumidores atuais.

**Epicos/entregas:**

- modelagem ORM + migration da tabela `lead_evento`
- servico unico de `ensure_lead_event(...)` para criacao idempotente do vinculo
- adaptacao de submit publico e fluxos de ativacao para garantir `LeadEvento`
- adaptacao de pipeline/importacao para garantir `LeadEvento` em novos lotes com `evento_id`
- testes unitarios e de integracao para unicidade, idempotencia e coerencia entre `AtivacaoLead` e `LeadEvento`

**Gate de saida da fase:**

- novos writes relevantes persistem `LeadEvento`
- nao existe duplicidade para `(lead_id, evento_id)`
- contrato do dashboard permanece inalterado

### F2 - Retroprocessamento e Reconciliacao Historica

**Objetivo:** reconstruir historico confiavel sem inferencia silenciosa.

**Epicos/entregas:**

- job idempotente de backfill a partir de `AtivacaoLead`, `LeadBatch.evento_id` e `Lead.evento_nome` deterministico
- relatorio de reconciliacao para casos ambiguos ou nao resolvidos
- criterio operacional para quando usar reenvio do bronze em vez de backfill direto
- testes de idempotencia, cobertura de precedencia e nao criacao de vinculo em casos ambiguos

**Gate de saida da fase:**

- todos os casos historicos resolviveis estao materializados em `LeadEvento`
- backlog de casos ambiguos esta explicitado e auditavel
- nenhuma alteracao destrutiva foi aplicada em dados mestres de evento

### F3 - Migracao dos Consumidores Analiticos

**Objetivo:** trocar a leitura por evento para a fonte canonica, preservando comportamento externo.

**Epicos/entregas:**

- migracao de `dashboard_service` e demais servicos/event endpoints priorizados para leitura via `LeadEvento`
- testes de paridade entre leitura antiga e leitura nova
- comparacao shadow/canary antes da troca definitiva
- manutencao do payload atual do frontend

**Gate de saida da fase:**

- `/dashboard/leads/analise-etaria` usa `LeadEvento` como fonte primaria
- contagens por evento e consolidado permanecem corretas
- filtros de auth/visibilidade e periodo seguem sem regressao

### F4 - Desativacao do Heuristico e Endurecimento Operacional

**Objetivo:** retirar dependencia estrutural da uniao transitora e consolidar governanca do novo modelo.

**Epicos/entregas:**

- remocao de fallback runtime baseado em `AtivacaoLead`, `LeadBatch` e `evento_nome` como fonte analitica primaria
- runbook de rollback e reconciliacao
- instrumentacao final de observabilidade e evidencias para auditoria
- documentacao explicita de campos legados ainda mantidos apenas como origem bruta/compatibilidade

**Gate de saida da fase:**

- nenhum consumidor analitico principal depende do hotfix heuristico
- rollback operacional esta testado
- trilha de auditoria da remediacao esta completa

## 8. Riscos e Mitigacoes

| Risco | Mitigacao |
|---|---|
| Dual-write criar drift entre legados e fonte canonica | encapsular criacao do vinculo em servico unico e testar transacoes ponta a ponta |
| Mesmo lead em varias ativacoes do mesmo evento inflar contagem | `UNIQUE (lead_id, evento_id)` + testes dedicados |
| Match por `evento_nome` criar vinculo errado no historico | permitir apenas match unico e deterministico; resto vai para reconciliacao |
| Mudanca de totais historicos surpreender usuarios | executar paridade, registrar deltas e comunicar alteracao semantica antes do switch |
| Duplicacao de dados sensiveis | limitar `lead_evento` a FKs e metadata minima, sem copiar PII |
| Reenvio do bronze gerar duplicidade operacional | usar apenas quando backfill direto nao for suficiente e validar idempotencia por par canonico |

## 9. Rollout e Rollback

### Rollout

1. introduzir `LeadEvento` e dual-write para novos fluxos
2. materializar historico resolvivel com backfill idempotente
3. executar comparacao de paridade entre leitura transitoria e leitura canonica
4. trocar consumidores analiticos priorizados para `LeadEvento`
5. remover dependencia do hotfix heuristico como fonte primaria

### Rollback

- se a leitura canonica divergir, consumidores analiticos podem retornar temporariamente ao caminho transitorio atual enquanto a paridade e corrigida
- este PRD nao autoriza apagar `Lead.evento_nome`, `LeadBatch.evento_id`, `AtivacaoLead` ou outras evidencias legadas
- qualquer necessidade de alterar o contrato externo do dashboard sai deste PRD e exige novo intake ou revisao explicita

## 10. Validacao e Cenarios de Teste

- lead publico com `event_id` e sem `ativacao_id` cria `LeadEvento` e nao depende de `AtivacaoLead`
- lead publico com `ativacao_id` cria `LeadEvento` e `AtivacaoLead` coerentes com o mesmo evento
- lead importado via batch com `LeadBatch.evento_id` cria `LeadEvento` sem precisar de ativacao
- backfill a partir de `AtivacaoLead` e `LeadBatch` e idempotente
- backfill via `Lead.evento_nome` so cria vinculo quando o match for unico; caso ambiguo vai para reconciliacao
- mesmo lead em duas ativacoes do mesmo evento conta uma vez para `(lead_id, evento_id)`
- mesmo lead em eventos diferentes continua contando um vinculo por evento no consolidado
- `/dashboard/leads/analise-etaria` preserva payload e filtros atuais apos migrar para `LeadEvento`
- filtros de agencia e periodo continuam corretos
- cenarios de falso vazio observados no intake deixam de ocorrer com a fonte canonica

## 11. Assuncoes e Hipoteses Declaradas

1. `Lead` pode se relacionar legitimamente a mais de um evento ao longo do tempo; por isso a forma canonica escolhida e uma relacao dedicada `lead_evento`, e nao um unico `evento_id` em `Lead`.
2. O contrato externo atual de `/dashboard/leads/analise-etaria` deve permanecer estavel durante toda a remediacao.
3. Casos historicos sem evidencia suficiente nao devem ser inferidos; devem permanecer explicitamente pendentes de reconciliacao.
4. Reenvio a partir do bronze sera fallback controlado, nao estrategia padrao para todo o historico.
5. O consolidado continuara contando por vinculo `lead-evento`, nao por pessoa global deduplicada entre eventos diferentes.
6. Exibir a origem do vinculo no dashboard fica fora desta rodada e pode virar escopo futuro apos a base canonica estabilizar.

## 12. Referencia de Intake

Este PRD deriva de `INTAKE-DASHBOARD-LEADS.md`, com contexto adicional de `AUDIT-LOG.md` e da evidencia de producao resumida no proprio intake. Por se tratar de `source_mode: backfilled`, a rastreabilidade operacional desta remediacao fica ancorada no intake e nas evidencias tecnicas nele declaradas ate que exista artefato historico mais granular.
