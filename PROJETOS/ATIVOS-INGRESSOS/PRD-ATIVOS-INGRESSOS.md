---
doc_id: "PRD-ATIVOS-INGRESSOS.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "workflow-improvement"
delivery_surface: "fullstack-module"
business_domain: "eventos"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "ativos"
  - "ingressos"
  - "dashboard"
  - "internal/registry"
  - "internal/ingestao-inteligente"
  - "internal/revisao-humana"
  - "email"
change_type: "evolucao"
audit_rigor: "elevated"
---

# PRD - ATIVOS-INGRESSOS

> Origem: [INTAKE-ATIVOS-INGRESSOS.md](INTAKE-ATIVOS-INGRESSOS.md)
>
> Este PRD descreve a capacidade de produto para operar ativos e ingressos
> fim a fim. A decomposicao em features, user stories e tasks ocorrera
> apenas na etapa explicita `PRD -> Features`.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-ATIVOS-INGRESSOS.md](INTAKE-ATIVOS-INGRESSOS.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-26
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: ATIVOS-INGRESSOS
- **Tese em 1 frase**: criar a capacidade operacional para prever, receber, conciliar, emitir, distribuir e analisar ingressos internos e externos com rastreabilidade completa
- **Valor esperado em 3 linhas**:
  - consolidar previsao, recebimento, conciliacao e distribuicao em uma unica fonte de verdade operacional
  - emitir ingressos internos unitarios com QR unico por destinatario e preparar o dominio para validacao futura de uso unico
  - entregar um dashboard operacional de ativos que mostre planejado, recebido, bloqueado, distribuido, remanejado, ajustado e problemas

## 2. Problema ou Oportunidade

- **Problema atual**: o produto atual controla apenas cotas agregadas por evento e diretoria, sem categoria, sem conciliacao entre cadastro e recebimento efetivo, sem inventario unitario por destinatario e sem emissao interna com QR
- **Evidencia do problema**: os modulos atuais de `ativos` e `ingressos` dependem de `CotaCortesia` e `SolicitacaoIngresso`, nao suportam categorias como `pista`, `pista premium` e `camarote`, nao distinguem `planejado` de `recebido_confirmado`, e o dashboard existente cobre leads, nao a operacao de ativos
- **Custo de nao agir**: a operacao segue dependente de email, drive e planilhas paralelas, o que amplia risco de erro na distribuicao, bloqueia visibilidade gerencial e impede padronizacao da emissao interna
- **Por que agora**: a equipe passara a assumir a distribuicao efetiva dos ingressos e precisa operar pelo menos um evento real com confiabilidade, auditoria e analytics

## 3. Publico e Operadores

- **Usuario principal**: equipe operacional NPBB responsavel por receber, emitir, distribuir e acompanhar ingressos
- **Usuario secundario**: diretorias, gestores e patrocinadores internos que precisam acompanhar saldo, bloqueios, distribuicao e ocorrencias
- **Operador interno**: operacao NPBB no produto e skill externa do OpenClaw consumindo APIs do sistema para leitura de emails e ingestao de ativos
- **Quem aprova ou patrocina**: PM e lideranca operacional de eventos

## 4. Jobs to be Done

- **Job principal**: transformar recebimentos heterogeneos de ingressos em inventario distribuivel, auditavel e utilizavel pela operacao no dia a dia
- **Jobs secundarios**: configurar categorias por evento, conciliar divergencias de quantidade, emitir ingressos internos com QR, bloquear distribuicao quando houver dependencia de recebimento externo, registrar problemas operacionais e analisar o comportamento dos ativos no dashboard
- **Tarefa atual que sera substituida**: consolidar manualmente previsao, recebimento, envio e excecoes em planilhas, emails e links de drive

## 5. Escopo

### Dentro

- configuracao por evento das categorias iniciais `pista`, `pista premium` e `camarote`
- dois modos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`
- inventario reconciliado entre `planejado` e `recebido_confirmado`
- bloqueio de distribuicao quando aumento externo ainda nao tiver sido recebido
- emissao interna unitario-por-destinatario com QR unico
- persistencia de arquivos, links e instrucoes associados aos ativos externos
- workflow de distribuicao, remanejamento, aumento, reducao e registro de problemas
- dashboard operacional de ativos dentro do modulo Dashboard

### Fora

- integracao nativa de inbox dentro do NPBB
- desenvolvimento da skill OpenClaw neste repositorio
- scanner ou validador final de QR no v1
- integracao financeira completa com bilheteria ou venda de ingressos

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir erro operacional e tempo de distribuicao de ingressos, criando uma base confiavel para operacao e gestao
- **Metricas leading**: percentual de eventos com categorias configuradas; percentual de recebimentos conciliados; percentual de ingressos internos emitidos com QR unico; tempo entre recebimento e disponibilidade; percentual de distribuicoes com status registrado
- **Metricas lagging**: taxa de erro ou reenvio; tempo medio entre recebimento e envio final; quantidade de bloqueios por falta de recebimento; quantidade de problemas por evento; uso recorrente do dashboard pela operacao
- **Criterio minimo para considerar sucesso**: um evento real consegue ser operado ponta a ponta com previsao, recebimento, conciliacao, emissao ou distribuicao e acompanhamento no dashboard sem depender de planilha como fonte de verdade

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: a evolucao deve conviver com o modelo atual de ativos agregados durante a transicao e preservar compatibilidade suficiente para rollout controlado
- **Restricoes operacionais**: para origem ticketeira, `recebido_confirmado` prevalece sobre `planejado` como base de estoque distribuivel
- **Restricoes operacionais**: aumentos externos ficam `bloqueado_por_recebimento` ate a chegada do correspondente ativo
- **Restricoes operacionais**: `remanejado` nao pode ser usado para encobrir aumentos, reducoes ou saldo ainda nao distribuido
- **Restricoes legais ou compliance**: emails, arquivos, links e QR codes devem ser tratados como dados sensiveis, com controle de acesso e trilha auditavel
- **Restricoes de prazo**: o primeiro corte precisa ser operacional em evento real, antes de automacoes adicionais
- **Restricoes de design ou marca**: o dashboard deve seguir o padrao visual do modulo de leads; o PDF externo serve como referencia de conteudo, nao de layout

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: `ativos`, `ingressos`, `dashboard`, catalogo de fontes em `internal/registry`, contratos de `internal/ingestao-inteligente`, workbench de `internal/revisao-humana`, servico de email e dominio de eventos
- **Sistemas externos impactados**: ticketeiras, links de drive enviados por terceiros, provedores de email de saida e skill externa do OpenClaw
- **Dados de entrada necessarios**: evento, diretoria, categoria, modo de fornecimento, quantidade planejada, quantidade recebida, arquivos ou links, instrucoes, destinatarios, status de envio, motivos de ajuste e ocorrencias
- **Dados de saida esperados**: inventario reconciliado, historico de distribuicao, bloqueios por recebimento, trilha de ajustes, registro de problemas e agregados do dashboard

## 9. Arquitetura Geral do Projeto

> Visao unificada de impacto arquitetural em nivel de projeto. O
> detalhamento por entregavel fica para a etapa `PRD -> Features`.

- **Backend**: ampliar o dominio atual para suportar categorias por evento, dois modos canonicos de fornecimento, reconciliacao `planejado x recebido`, bloqueios por recebimento, emissao interna com QR unitario, distribuicao, remanejamento, aumento, reducao e ocorrencias operacionais
- **Frontend**: evoluir as telas de ativos e ingressos e criar a subsecao `Dashboard > Ativos` com leitura separada para planejado, recebido, distribuido, bloqueado, remanejado, ajustado e problemas
- **Banco/migracoes**: introduzir ou adaptar entidades para configuracao de categoria, previsao, recebimento, divergencia de conciliacao, artefato externo, emissao interna com QR unico, distribuicao por destinatario e eventos de ajuste
- **Observabilidade**: correlation_id e trilha auditavel entre previsao, recebimento, conciliacao, emissao, envio, bloqueio e problema; a emissao com QR deve persistir identidade suficiente para validacao futura de uso unico
- **Autorizacao/autenticacao**: manter RBAC atual e endurecer acesso a artefatos sensiveis e operacoes de distribuicao
- **Rollout**: ativacao gradual por evento, com foco inicial em um evento real e convivencia controlada com o fluxo agregado legado

## 10. Riscos Globais

- **Risco de produto**: tentar entregar operacao, analytics e preparacao para automacao em um unico corte sem preservar a usabilidade do primeiro evento real
- **Risco tecnico**: a convivencia entre novo dominio e modelo legado, combinada com formatos heterogeneos de ticketeira, aumenta a complexidade de migracao e integracao
- **Risco operacional**: divergencias mal conciliadas, bloqueios ignorados ou emissao incorreta podem gerar distribuicao acima do recebido, categoria errada ou destinatario inadequado
- **Risco de dados**: arquivos, links e QR codes podem expor acesso indevido se storage, expiracao e auditoria nao forem tratados cedo
- **Risco de adocao**: a operacao pode manter controles paralelos se o produto nao reduzir trabalho manual de forma perceptivel no primeiro corte

## 11. Nao-Objetivos

- construir inbox nativo no NPBB
- implementar o scanner ou validador final de QR no v1
- tratar o PRD como backlog de features, user stories ou tasks
- redesenhar o modulo Dashboard fora do padrao existente

> **Pos-PRD (nao faz parte deste arquivo):** a decomposicao entregavel
> ocorrera em etapa dedicada. A sequencia esperada de temas e:
> fundacao do dominio, recebimento e conciliacao de ticketeira, emissao
> e distribuicao, dashboard operacional de ativos e validacao de QR em
> etapa posterior no mesmo projeto.

## 12. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| Ticketeiras | operacao | terceiros | fornecem arquivos, links e quantidades efetivamente recebidas | active |
| Email de saida | servico | infraestrutura | entrega comunicacoes e envios operacionais | active |
| PDF operacional externo | referencia | operacao | orienta KPIs, tabelas e graficos do dashboard | active |

## 13. Rollout e Comunicacao

- **Estrategia de deploy**: liberar por evento, com piloto em evento real e convivencia temporaria com o fluxo agregado atual
- **Comunicacao de mudancas**: alinhar operacao, PM e stakeholders sobre novos estados canonicos (`planejado`, `recebido_confirmado`, `bloqueado_por_recebimento`, `distribuido`, `remanejado`, `aumentado`, `reduzido`, `problema_registrado`)
- **Treinamento necessario**: treinamento curto para operacao sobre reconciliacao, emissao interna com QR e leitura do dashboard
- **Suporte pos-launch**: acompanhamento reforcado no primeiro evento real e revisao das lacunas de UX, storage e validacao futura de QR

## 14. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: intake e PRD permanecem gates humanos; apos aprovacao do PRD, o projeto segue para decomposicao `PRD -> Features` e auditorias passam a ocorrer por feature, conforme governanca comum
- **Criterios de auditoria**: rastreabilidade de estados canonicos, aderencia aos guardrails operacionais, ausencia de backlog estruturado no PRD e coerencia entre rollout, riscos e arquitetura
- **Threshold anti-monolito**: a decomposicao deve preservar fronteiras entre dominio operacional, integracoes externas, emissao/distribuicao e analytics, evitando um modulo unico com regras cruzadas sem governanca

## 15. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
- [x] Arquitetura geral e rollout descritos sem catalogo de Features nem tabelas de User Stories neste PRD
- [x] Dependencias externas mapeadas
- [x] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

## 16. Anexos e Referencias

- [Intake](INTAKE-ATIVOS-INGRESSOS.md)
- [Audit Log](AUDIT-LOG.md)
- [Relatorio de encerramento](encerramento/RELATORIO-ENCERRAMENTO.md)
- [Contrato atual da tela de Ativos](../../docs/tela-inicial/menu/Ativos/ativos.md)
- [Contrato atual do Dashboard de Leads](../../docs/tela-inicial/menu/Dashboard/leads_dashboard.md)

> Frase Guia: "PRD direciona; Feature organiza; User Story fatia; Task executa; Teste valida."
