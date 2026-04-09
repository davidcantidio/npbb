---
doc_id: "PRD-ATIVOS-INGRESSOS"
version: "2.0"
status: "draft"
owner: "PM"
last_updated: "2026-04-06"
project: "ATIVOS-INGRESSOS"
intake_schema_version: "v2"
intake_id: 2
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "workflow-improvement"
delivery_surface: "fullstack-module"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "interna"
change_type: "evolucao"
audit_rigor: "standard"
generated_by: "fabrica-cli"
generator_stage: "prd"
---

# PRD - ATIVOS-INGRESSOS

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-ATIVOS-INGRESSOS.md](./INTAKE-ATIVOS-INGRESSOS.md)
- **Schema intake**: v2
- **Intake ID**: 2
- **Data de criacao**: 2026-04-06
- **PRD derivado**: nao_aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: operação de ativos e ingressos
- **Tese em 1 frase**: criar a capacidade operacional para prever, receber, conciliar, emitir, distribuir e analisar ingressos internos ou provenientes de ticketeiras em um fluxo auditável
- **Valor esperado em 3 linhas**:
  - nome curto da iniciativa: operação de ativos e ingressos
  - tese em 1 frase: criar a capacidade operacional para prever, receber, conciliar, emitir, distribuir e analisar ingressos internos ou provenientes de ticketeiras em um fluxo auditável
  - nao_definido

## 2. Especificacao Funcional

### 2.1 Problema ou Oportunidade

- **Problema atual**: o domínio atual de ativos controla apenas cotas agregadas por `evento + diretoria`, sem tipos de ingresso, sem conciliação `planejado x recebido`, sem inventário unitário por destinatário e sem camada de QR para ingressos internos
- **Evidencia do problema**: nao_definido
- **Custo de nao agir**: nao_definido
- **Por que agora**: a equipe vai assumir a distribuição efetiva dos ingressos e precisa suportar eventos reais com conciliação entre previsão e recebimento, emissão interna segura quando aplicável, recebimento de ticketeira quando aplicável, e visibilidade operacional

### 2.2 Publico e Operadores

- **Usuario principal**: time do projeto
- **Usuario secundario**: nao_definido
- **Operador interno**: fabrica-cli
- **Quem aprova ou patrocina**: nao_definido

### 2.3 Jobs to be Done

- **Job principal**: transformar recebimentos heterogêneos de ingressos (no modo vigente do evento) em inventário distribuível, auditável e visível para a operação
- **Fluxo principal esperado**: receber ingressos, reconciliar estoque, distribuir ao destinatario e acompanhar o ciclo de vida no dashboard
- **Jobs secundarios**: dois modos canônicos de fornecimento, **mutuamente exclusivos por evento**: `interno_emitido_com_qr` e `externo_recebido`; modo alterável pelo administrador com registro auditado
- **Tarefa atual que sera substituida**: fluxo manual sem base unificada

### 2.4 Escopo

### Dentro

- configuração por evento dos tipos de ingresso ativos (`pista`, `pista_premium`, `camarote`), com suporte a eventos que usem apenas um ou dois tipos
- dois modos canônicos de fornecimento, **mutuamente exclusivos por evento**: `interno_emitido_com_qr` e `externo_recebido`; modo alterável pelo administrador com registro auditado
- conciliação entre quantidade planejada e quantidade recebida (modo externo)
- regra de prevalência do `recebido_confirmado` para estoque distribuível em origem ticketeira
- bloqueio automático de saldos dependentes de recebimento externo; desbloqueio automático ao receber novo `recebido_confirmado`; desbloqueio manual por administrador com trilha de auditoria
- bloqueio de excedente da ticketeira até aumento explícito do planejado pelo administrador
- interface de seleção de destinatário por ingresso disponível, com disparo de e-mail e ciclo de vida `enviado → confirmado → utilizado`
- cancelamento de ingresso distribuído com notificação por e-mail ao destinatário e retorno ao saldo disponível
- emissão de ingressos internos unitários em PDF com QR único (UUID vinculado a nome e e-mail do destinatário)
- persistência e rastreabilidade de arquivos compartilhados, ingressos unitários externos entregues como recebidos, links de drive e instruções textuais recebidas
- fluxo de distribuição, remanejamento (entre tipos e entre diretorias), aumento, redução e registro de problemas operacionais (tipos canônicos: `entrega_errada`, `quantidade_divergente`, `destinatario_invalido`, `outro`)
- dashboard de ativos dentro do módulo Dashboard, seguindo o padrão visual e estrutural já adotado em dashboard de leads; conteúdo analítico alinhado à referência [`Acompanhamento Alceu.pdf`](./Acompanhamento%20Alceu.pdf)
- contrato mínimo de API de escrita para integração com skill externa OpenClaw

### Fora

- leitura direta de caixa de e-mail dentro do NPBB
- desenvolvimento da skill OpenClaw neste repositório
- implementação completa do validador/scanner de QR no v1
- conciliação financeira de bilheteria ou integração completa com venda de ingressos
- redesign do módulo Dashboard fora do padrão já homologado no produto
- API de leitura analítica para OpenClaw no v1
- objetivo principal: reduzir erro operacional e tempo de distribuição de ingressos, aumentando a confiabilidade do estoque operacional e a visibilidade executiva sobre ativos
- métricas leading: percentual de eventos com tipos de ingresso configurados; percentual de lotes com origem e artefatos rastreados; tempo entre recebimento e disponibilidade; percentual de distribuições com status registrado; percentual de ingressos internos emitidos com QR único; percentual de ingressos com ciclo de vida completo rastreado (`enviado → confirmado → utilizado`)
- métricas lagging: taxa de reenvio ou erro operacional; tempo médio entre recebimento e envio final; quantidade de bloqueios por falta de recebimento; quantidade de problemas operacionais por evento; uso recorrente do dashboard pela operação
- critério mínimo para considerar sucesso: um evento real consegue ser operado ponta a ponta com previsão, recebimento (se externo), conciliação, emissão/distribuição, ciclo de vida do destinatário e acompanhamento no dashboard sem depender de planilha paralela como fonte de verdade
- referência de cobertura analítica desejada: [`Acompanhamento Alceu.pdf`](./Acompanhamento%20Alceu.pdf) (o PRD deve cruzar cada visão relevante com o que será obrigatório no v1)
- restrições técnicas: a evolução deve conviver com o modelo atual de `CotaCortesia` e `SolicitacaoIngresso` durante a transição, sem quebrar operações existentes antes do rollout controlado
- restrições operacionais: para origem `externo_recebido`, a quantidade distribuível deve refletir o `recebido_confirmado`, mesmo quando divergir do `planejado`; o que ainda não foi recebido conciliado permanece bloqueado; excedente da ticketeira fica bloqueado até aumento explícito do planejado pelo administrador
- restrições operacionais: desbloqueio automático ocorre quando novo `recebido_confirmado` suficiente é registrado; desbloqueio manual por administrador é exceção auditada
- restrições operacionais: `remanejado` é apenas realocação efetiva com efeito imediato nos saldos; aumento, redução e saldo não distribuído aparecem como leituras separadas; motivo do remanejamento não é obrigatório
- restrições operacionais: para v1, a dimensão `Area` do painel será tratada como equivalente a `Diretoria` até decisão documentada em contrário
- restrições operacionais: modo do evento pode ser alterado pelo administrador após início da operação, com registro auditado da mudança
- restrições de ingresso cancelado: cancelamento devolve ingresso ao saldo disponível e notifica o destinatário por e-mail; histórico de cancelamento é preservado
- restrições legais ou compliance: arquivos de ingresso, links, e-mails de destinatários e QR codes devem ser tratados como dados sensíveis sob LGPD, com controle de acesso e trilha auditável
- restrições de prazo: priorizar um corte operacional real para ao menos um evento antes de expandir automações adicionais
- restrições de design ou marca: o PDF de referência orienta informação e gráficos, não layout nem arte; a implementação visual deve seguir o padrão já usado pelo dashboard de leads
- restrições de QR: o QR code emitido no v1 contém UUID único vinculado a nome e e-mail do destinatário; o layout do PDF de ingresso interno é simples e será especificado no PRD; a validação de uso único é etapa futura fora do v1
- sistemas internos impactados: módulo de `ativos`, módulo de `ingressos`, `dashboard`, catálogo de fontes em `internal/registry`, contratos de `internal/ingestao-inteligente`, workbench de `internal/revisao-humana`, serviço atual de e-mail e o domínio de eventos
- sistemas externos impactados: ticketeiras, links de drive recebidos por e-mail, provedores de e-mail de saída (envio ao destinatário e notificação de cancelamento) e skill operacional do OpenClaw
- dados de entrada necessários: evento, diretoria, tipo de ingresso, modo de fornecimento, quantidade planejada, quantidade recebida (modo externo), arquivos ou links, instruções do emissor, destinatário (nome e e-mail), status de envio, confirmação do destinatário, status de utilização, motivo de cancelamento, motivo de remanejamento (opcional), aumento/redução, tipo e descrição de ocorrências
- dados de saída esperados: inventário reconciliado, histórico de distribuição com ciclo de vida por destinatário, bloqueios por recebimento, trilha de remanejamentos, registro de cancelamentos com notificação, registro de problemas, dashboard operacional e contratos consumíveis por integrações externas
- backend: ampliar o domínio atual para suportar configuração de tipos de ingresso por evento, modo único por evento (alterável com auditoria), conciliação `planejado x recebido`, bloqueios e desbloqueios automáticos por recebimento, bloqueio de excedente da ticketeira, emissão interna com QR unitário em PDF, ciclo de vida do ingresso por destinatário (`enviado → confirmado → utilizado → cancelado`), distribuição, remanejamento entre tipos e diretorias, aumento, redução e incidentes operacionais com tipos canônicos
- frontend: evoluir as telas operacionais de ativos/ingressos (incluindo interface de seleção de destinatário por ingresso disponível) e adicionar `Dashboard > Ativos` com leituras separadas para planejado, recebido, bloqueado, disponível, distribuído, remanejado, aumentado, reduzido e problemas
- banco/migrações: criar ou adaptar entidades para tipos de ingresso por evento, previsão, recebimento, divergência de conciliação, excedente bloqueado, artefatos de ingresso, emissão interna com QR único em PDF, ciclo de vida por destinatário, cancelamento, eventos de ajuste e ocorrências com tipo canônico
- observabilidade: `correlation_id` e rastreabilidade entre previsão, recebimento, conciliação, emissão, envio, confirmação, utilização, cancelamento, bloqueio, remanejamento e problema operacional
- autorização/autenticação: manter RBAC atual e endurecer acesso a artefatos sensíveis e operações de distribuição; operações de desbloqueio manual e mudança de modo de evento requerem perfil de administrador com registro auditado
- rollout: ativação gradual por evento, com convivência controlada com o fluxo agregado atual até que o corte operacional esteja validado
- risco de produto: tentar fechar operação, analítico e preparação para automação no mesmo ciclo e diluir a entrega do primeiro evento real
- risco técnico: formatos heterogêneos de ticketeiras e necessidade de coexistir com o modelo agregado atual aumentam a complexidade do domínio e das migrações
- risco operacional: classificação errada, divergência não conciliada ou envio duplicado pode gerar distribuição acima do recebido, tipo incorreto ou destinatário inadequado; cancelamento sem notificação adequada pode causar confusão ao destinatário
- risco de dados: arquivos, links, QR codes e e-mails de destinatários podem expor acessos indevidos se storage, expiração e auditoria não forem definidos cedo
- risco de adoção: a operação pode manter planilhas paralelas se o produto não reduzir trabalho manual de forma tangível no primeiro evento real
- construir integração nativa de inbox IMAP/Gmail/Outlook no NPBB
- desenvolver a skill OpenClaw dentro deste repositório
- entregar o scanner/validador final de QR no v1
- usar o PRD como backlog de features, user stories ou tasks
- expor API de leitura analítica para OpenClaw no v1
- sintoma observado: `nao_aplicavel`
- impacto operacional: `nao_aplicavel`
- evidência técnica: `nao_aplicavel`
- componente(s) afetado(s): `nao_aplicavel`
- riscos de não agir: `nao_aplicavel`
- regra de negócio ainda não definida: catálogo de tipos de ingresso além do trio inicial e política de expansão futura
- dependência ainda não confirmada: estratégia final de storage, expiração e retenção para arquivos, links e ingressos emitidos com QR
- dado ainda não disponível: SLA operacional de envio, retry, bounce e reenvio de e-mails para destinatários
- decisão de UX ainda não fechada: drill-downs e detalhamento do painel de problemas no dashboard; layout definitivo do PDF de ingresso interno (v1 usa layout simples)
- outro ponto em aberto: UX e contrato do futuro validador de QR com semântica de uso único, previsto como etapa posterior no mesmo projeto
- formalizar o modelo canônico de transição entre `planejado`, `recebido_confirmado`, `bloqueado_por_recebimento`, `disponivel` e `distribuido` no modo externo, incluindo o tratamento de excedente da ticketeira e os eventos de domínio e persistência
- formalizar o ciclo de vida do ingresso por destinatário: `enviado → confirmado → utilizado → cancelado`, incluindo gatilhos de e-mail em cada transição
- como representar aumento e redução sem misturar esses eventos com `remanejado`; como registrar a mudança de modo do evento com trilha auditada
- como persistir artefatos externos e ingressos internos emitidos com QR em PDF mantendo rastreabilidade e compliance LGPD
- qual é o contrato mínimo de API de escrita para que a skill OpenClaw possa registrar recebimentos externos
- qual é o contrato mínimo para que a emissão com QR (UUID vinculado a nome e e-mail do destinatário) já nasça preparada para validação futura de uso único
- quais recortes, filtros, tabelas e gráficos do dashboard de ativos são obrigatórios no v1, mapeados explicitamente para as seções de [`Acompanhamento Alceu.pdf`](./Acompanhamento%20Alceu.pdf)
- qual o layout mínimo do PDF de ingresso interno para o v1
- [x] intake_kind está definido
- [x] source_mode está definido
- [x] rastreabilidade de origem está declarada ou marcada como `nao_aplicavel`
- [x] problema está claro
- [x] público principal está claro
- [x] fluxo principal está descrito
- [x] tipos de ingresso e configuração por evento estão definidos
- [x] ciclo de vida do ingresso por destinatário está definido
- [x] regras de bloqueio, desbloqueio automático e desbloqueio manual estão definidas
- [x] tratamento de excedente da ticketeira está definido
- [x] regras de cancelamento e redistribuição estão definidas
- [x] contrato mínimo de QR está definido
- [x] contrato mínimo de API para OpenClaw está definido
- [x] tipos canônicos de problema operacional estão definidos
- [x] escopo dentro/fora está fechado
- [x] métricas de sucesso estão declaradas
- [x] restrições estão declaradas
- [x] dependências e integrações estão declaradas
- [x] arquitetura afetada está mapeada
- [x] riscos relevantes estão declarados
- [x] lacunas conhecidas estão declaradas
- [x] contexto específico de problema/refatoração foi preenchido quando aplicável

### 2.5 Resultado de Negocio e Metricas

- **Objetivo principal**: nao_definido
- **Metricas leading**: nao_definido
- **Metricas lagging**: nao_definido
- **Criterio minimo para considerar sucesso**: nao_definido

### 2.6 Restricoes e Guardrails

- nao_definido

### 2.7 Dependencias e Integracoes

- nao_definido

## 3. Hipoteses Congeladas

- **Resultado do gate de clarificacao**: approved
- **Lacunas resolvidas na clarificacao**:
  - modelo canonico de transicao entre estoque planejado, recebido, bloqueado e distribuido fechado para o v1
  - ciclo de vida do ingresso por destinatario fechado para o v1
- **Hipoteses congeladas**:
  - catalogo inicial de tipos de ingresso do v1 fica restrito a pista, pista_premium e camarote
  - dashboard de ativos do v1 reaproveita o padrao estrutural do dashboard de leads
- **Dependencias externas pendentes**:
  - estrategia final de storage e retencao de artefatos de ingresso
  - SLA de retry, bounce e reenvio de e-mails
- **Riscos de interpretacao**:
  - expansao futura do catalogo de tipos de ingresso
  - detalhamento futuro do validador de QR

## 4. Plano Tecnico

### 4.1 Arquitetura Geral do Projeto

- backend: ampliar o domínio atual para suportar configuração de tipos de ingresso por evento, modo único por evento (alterável com auditoria), conciliação `planejado x recebido`, bloqueios e desbloqueios automáticos por recebimento, bloqueio de excedente da ticketeira, emissão interna com QR unitário em PDF, ciclo de vida do ingresso por destinatário (`enviado → confirmado → utilizado → cancelado`), distribuição, remanejamento entre tipos e diretorias, aumento, redução e incidentes operacionais com tipos canônicos
- frontend: evoluir as telas operacionais de ativos/ingressos (incluindo interface de seleção de destinatário por ingresso disponível) e adicionar `Dashboard > Ativos` com leituras separadas para planejado, recebido, bloqueado, disponível, distribuído, remanejado, aumentado, reduzido e problemas
- banco/migrações: criar ou adaptar entidades para tipos de ingresso por evento, previsão, recebimento, divergência de conciliação, excedente bloqueado, artefatos de ingresso, emissão interna com QR único em PDF, ciclo de vida por destinatário, cancelamento, eventos de ajuste e ocorrências com tipo canônico
- observabilidade: `correlation_id` e rastreabilidade entre previsão, recebimento, conciliação, emissão, envio, confirmação, utilização, cancelamento, bloqueio, remanejamento e problema operacional
- autorização/autenticação: manter RBAC atual e endurecer acesso a artefatos sensíveis e operações de distribuição; operações de desbloqueio manual e mudança de modo de evento requerem perfil de administrador com registro auditado
- rollout: ativação gradual por evento, com convivência controlada com o fluxo agregado atual até que o corte operacional esteja validado

### 4.2 Decisoes Tecnicas e Contratos Relevantes

- **Contratos de API / integracoes**: CLI `fabrica`
- **Persistencia / migracoes**: Postgres (intake v2 como fonte de verdade)
- **Observabilidade e operacao**: trilha `intake_prompt_runs` e `intake_field_lineage`
- **Trade-offs tecnicos assumidos**: Markdown do intake e projecao humana, nao fonte primaria

## 5. Riscos Globais

- risco de produto: tentar fechar operação, analítico e preparação para automação no mesmo ciclo e diluir a entrega do primeiro evento real
- risco técnico: formatos heterogêneos de ticketeiras e necessidade de coexistir com o modelo agregado atual aumentam a complexidade do domínio e das migrações
- risco operacional: classificação errada, divergência não conciliada ou envio duplicado pode gerar distribuição acima do recebido, tipo incorreto ou destinatário inadequado; cancelamento sem notificação adequada pode causar confusão ao destinatário
- risco de dados: arquivos, links, QR codes e e-mails de destinatários podem expor acessos indevidos se storage, expiração e auditoria não forem definidos cedo
- risco de adoção: a operação pode manter planilhas paralelas se o produto não reduzir trabalho manual de forma tangível no primeiro evento real

## 6. Nao-Objetivos

- nao_definido

---

> **Pos-PRD (nao faz parte deste arquivo):** execute
> `fabrica generate features --project ATIVOS-INGRESSOS`
> para o fluxo canonico com provider; use `--proposal-file <JSON>` para modo offline
> e `--legacy` somente para o pipeline heuristico legado.

## 7. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| Postgres | banco | runtime operacional | fonte de verdade intake v2 | required |

## 8. Rollout e Comunicacao

- **Estrategia de deploy**: execucao local por CLI
- **Comunicacao de mudancas**: registrar no PRD e no audit log
- **Treinamento necessario**: uso dos comandos `fabrica`
- **Suporte pos-launch**: acompanhamento da sincronizacao no read model

## 9. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: revisao humana de intake e PRD
- **Criterios de auditoria**: `PROJETOS/COMUM/GOV-AUDITORIA.md`
- **Threshold anti-monolito**: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## 10. Checklist de Prontidao

- [x] Intake v2 carregado do Postgres
- [x] Markdown de intake projetado deterministicamente
- [x] Escopo e metricas transportados
- [x] Proxima etapa explicita para features
- [ ] revisao humana concluida

## 11. Anexos e Referencias

- `PROJETOS/COMUM/GOV-PRD.md`
- `PROJETOS/COMUM/PROMPT-PRD-PARA-FEATURES.md`
- `PROJETOS/COMUM/SESSION-DECOMPOR-PRD-EM-FEATURES.md`
