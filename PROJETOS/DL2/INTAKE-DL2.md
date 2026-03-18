---
doc_id: "INTAKE-DL2.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "DL2"
intake_kind: "refactor"
source_mode: "backfilled"
origin_project: "DASHBOARD-LEADS"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "data-product"
delivery_surface: "fullstack-module"
business_domain: "dashboard"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "dashboard-leads"
  - "pipeline-etl-importacao"
  - "ticketing-importacao-de-ingressos"
  - "modelagem-lead-evento-ativacao"
  - "frontend-dashboard"
change_type: "refactor"
audit_rigor: "elevated"
---

# INTAKE - DL2

> Artefato retrospectivo e sucessor. Este intake substitui a versao inicial de `DL2`
> e reabre, em formato `feature-first`, a remediacao que antes estava espalhada no
> projeto legado agora arquivado em `PROJETOS/FEITO/DASHBOARD-LEADS/`.

## 0. Rastreabilidade de Origem

- projeto de origem: DASHBOARD-LEADS
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: o projeto legado `DASHBOARD-LEADS` foi planejado sob um eixo `architecture-first`, com backlog fragmentado em fundacao, backfill, consumidores e endurecimento antes de fechar features demonstraveis; `DL2` reabre a mesma remediacao como projeto sucessor, orientado a dashboards confiaveis por evento e com migracao controlada do backlog tecnico ja descoberto

## 1. Resumo Executivo

- nome curto da iniciativa: DL2 - dashboards de leads confiaveis por evento
- tese em 1 frase: replanejar a remediacao do legado `DASHBOARD-LEADS` em formato `feature-first` para que os dashboards de leads por evento deixem de depender de correcoes locais e passem a refletir uma semantica consistente de `Lead`, `Evento` e `Ativacao`
- valor esperado em 3 linhas:
  1. restaurar confianca nos endpoints e telas prioritarias de `/dashboard/leads/*`
  2. transformar modelagem canonica, backfill historico e retirada de heuristicas em trabalho habilitador rastreado por feature
  3. encerrar o legado como arquivo morto e concentrar planejamento, execucao e auditoria somente em `DL2`

## 2. Problema ou Oportunidade

- problema atual: a remediacao iniciada em `DASHBOARD-LEADS` atacou corretamente sintomas tecnicos importantes, mas foi estruturada por eixos internos de arquitetura antes de fechar features demonstraveis; isso deixou o caminho `intake -> PRD -> fases -> issues -> tasks` fraco para um projeto cujo valor principal e devolver dashboards confiaveis por evento
- evidencia do problema: o legado tem um intake detalhado, um `PRD-DASHBOARD-LEADS.md` vazio e fases separadas em `F1` fundacao do vinculo canonico, `F2` retroprocessamento historico, `F3` paridade de consumidores analiticos e `F4` retirada de heuristico; a propria estrutura mostra backlog tecnico relevante, mas sem um PRD utilizavel que organize o plano por features entregaveis
- custo de nao agir: o time continua com dashboards e relatorios sujeitos a falso vazio e divergencia de contagem, enquanto o backlog tecnico permanece desacoplado do valor visivel ao usuario e do gate `feature-first` esperado pelo framework atual
- por que agora: o framework vigente mudou para `delivery-first` / `feature-first`, `DASHBOARD-LEADS` foi explicitamente deprecado e o legado precisa virar tombstone agora, para que a execucao futura aconteca somente sobre um projeto sucessor alinhado ao paradigma atual

## 3. Publico e Operadores

- usuario principal: usuarios internos autenticados do NPBB que consomem dashboards e relatorios de leads por evento
- usuario secundario: times de operacao, marketing e analytics que dependem de contagens consistentes de leads para leitura de performance por evento
- operador interno: PM e engenharia backend, frontend e dados responsaveis por replanejar o backlog legado e executar a remediacao sucessora em `DL2`
- quem aprova ou patrocina: nao_definido; o contexto nao informa patrocinador nominal e esse ponto deve permanecer em `Lacunas Conhecidas`

## 4. Jobs to be Done

- job principal: consultar dashboards e relatorios de leads por evento com contagens confiaveis, independentemente da origem do lead ou do caminho de conversao
- jobs secundarios: replanejar o backlog legado em features demonstraveis, preservar a semantica canonica entre `Lead`, `Evento` e `Ativacao`, e executar retroprocessamento ou endurecimento somente quando isso provar um ganho visivel nas superfices priorizadas
- tarefa atual que sera substituida: backlog organizado por fundacao tecnica, backfill e consumidores isolados, sem um eixo unico de feature que leve do intake ate tasks orientadas ao valor entregue

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. o usuario filtra um dashboard ou relatorio de leads por evento em `/dashboard/leads/*`
2. a plataforma consolida leads do evento tanto por origem direta quanto por conversao em ativacao, sem excluir casos validos por causa do caminho de ingestao
3. os endpoints e consumidores frontend retornam contagens e breakdowns coerentes entre si para o mesmo evento
4. a engenharia entrega e valida as etapas tecnicas de modelagem, backfill e endurecimento como habilitadoras dessas features visiveis, e nao como um plano paralelo dissociado do resultado final

## 6. Escopo Inicial

### Dentro

- replanejar o backlog legado de `DASHBOARD-LEADS` em formato `feature-first`, com dashboards confiaveis por evento como eixo principal
- priorizar as superfices `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio` como caminho visivel de valor
- carregar semantica canonica de `Lead`, `Evento` e `Ativacao`, backfill historico e retirada controlada de heuristicas apenas quando conectados a essas features
- migrar o contexto e o aprendizado do legado arquivado para `DL2`, com rastreabilidade clara do que vira feature, habilitador, cancelamento ou nao-objetivo

### Fora

- criar novas superfices analiticas sem relacao direta com os dashboards de leads ja priorizados
- redesenhar UX, identidade visual ou payloads de frontend alem do necessario para preservar contratos existentes
- executar modernizacoes genericas de ETL, plataforma ou governanca que nao sejam necessarias para restaurar confianca nas leituras por evento
- manter `DASHBOARD-LEADS` como superficie ativa de planejamento ou execucao depois do tombstone

## 7. Resultado de Negocio e Metricas

- objetivo principal: restaurar a confianca nos dashboards de leads por evento e alinhar o backlog tecnico a features demonstraveis sob o projeto sucessor `DL2`
- metricas leading: endpoints priorizados deixam de retornar falso vazio quando existem leads validos; contagens para o mesmo evento convergem entre analise etaria, dashboard agregado e relatorio; backlog herdado do legado passa a apontar para features ou habilitadores explicitamente rastreados
- metricas lagging: reducao de incidentes e de correcoes locais em queries de dashboard; maior estabilidade de contagens historicas entre consumidores analiticos; confianca operacional maior no uso dos dashboards por evento
- criterio minimo para considerar sucesso: as superfices priorizadas de `/dashboard/leads/*` passam a retornar contagens coerentes para o mesmo evento, e cada etapa tecnica restante da remediacao fica justificada por uma feature de valor visivel ao usuario

## 8. Restricoes e Guardrails

- restricoes tecnicas: preservar o stack atual do NPBB, manter compatibilidade com contratos relevantes do frontend e nao usar `PRD-DASHBOARD-LEADS.md` como fonte de negocio porque o arquivo legado esta vazio
- restricoes operacionais: `DASHBOARD-LEADS` deve ser tornado arquivo morto imediatamente; `DL2` passa a ser a unica superficie ativa para intake, PRD e execucao futura dessa remediacao
- restricoes legais ou compliance: dados de leads seguem sujeitos a LGPD e nao podem perder rastreabilidade durante backfill, reconciliacao ou endurecimento
- restricoes de prazo: nao_definido; o contexto nao informa milestone ou deadline e esse ponto deve permanecer aberto
- restricoes de design ou marca: nao redesenhar a UX atual dos dashboards nesta rodada; o foco e confiabilidade analitica e reorganizacao feature-first

## 9. Dependencias e Integracoes

- sistemas internos impactados: servicos backend de dashboard e agregacao por evento, modelagem `Lead`/`Evento`/`Ativacao`, pipelines ETL e importacao, consumidores frontend de `/dashboard/leads/*`, governanca documental do projeto sucessor
- sistemas externos impactados: ticketerias e fontes externas de importacao de leads que alimentam o contexto de evento
- dados de entrada necessarios: intake legado arquivado, arvore de fases/epicos/issues do legado, identificadores e metadados de evento, origem dos leads, vinculos atuais com ativacao e evidencias historicas necessarias para reconciliacao
- dados de saida esperados: intake e PRD sucessores aprovados, backlog `feature-first` rastreavel, dashboards confiaveis por evento e estrategia clara para carregar ou descartar itens tecnicos herdados

## 10. Arquitetura Afetada

- backend: servicos e consultas que consolidam leads por evento, semantica de `Lead`, `Evento` e `Ativacao`, e endpoints agregados de dashboard
- frontend: paginas e services que consomem `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio`
- banco/migracoes: estrategia de vinculo canonico `lead-evento`, retroprocessamento historico, reconciliacao e endurecimento de dados ja persistidos
- observabilidade: testes de regressao, comparacao de contagens entre consumidores e evidencias de paridade entre fontes de lead por evento
- autorizacao/autenticacao: preservar o modelo atual de acesso autenticado aos dashboards
- rollout: legado arquivado como tombstone e toda continuidade da remediacao concentrada em `DL2`, com rollout incremental por feature validada

## 11. Riscos Relevantes

- risco de produto: reorganizar o plano pode atrasar percepcao de entrega se as features nao forem definidas com valor visivel logo no PRD
- risco tecnico: migrar backlog tecnico sem um PRD legado utilizavel pode criar duplicidade ou perda de contexto se a rastreabilidade nao for fechada com rigor
- risco operacional: coexistencia breve entre arquivo morto e projeto sucessor pode levar times a consultarem o legado errado se o tombstone nao estiver explicito
- risco de dados: backfill ou reconciliacao mal calibrados podem duplicar, omitir ou reclassificar leads de forma incorreta
- risco de adocao: equipes continuarem tratando modelagem e queries compensatorias como fins em si, em vez de sustentacao de features analiticas confiaveis

## 12. Nao-Objetivos

- nao manter `DASHBOARD-LEADS` como projeto ativo em paralelo
- nao abrir novas features de analytics fora das superfices atuais de `/dashboard/leads/*`
- nao transformar esta rodada em redesenho visual ou reformulacao completa de UX

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: o dashboard `http://127.0.0.1:5173/dashboard/leads/analise-etaria` exibia `Nenhum lead encontrado para os filtros aplicados` mesmo havendo leads do evento no banco, e o projeto legado que atacou o problema acabou planejado por eixos tecnicos antes de fechar o recorte de feature
- impacto operacional: usuarios internos perdem confianca nos dashboards por evento, engenharia tende a corrigir sintomas por query isolada e o planejamento fica disperso entre fundacao, backfill e consumidores sem um eixo unico de entrega
- evidencia tecnica: a investigacao previa confirmou que o caminho dependente de `AtivacaoLead` gerava falso vazio e uma correcao pontual encontrou `1709` leads do evento `TAMO JUNTO BB`; alem disso, o legado ficou com intake preenchido, `PRD-DASHBOARD-LEADS.md` vazio e fases `F1` a `F4` organizadas como fundacao tecnica, retroprocessamento, consumidores analiticos e endurecimento
- componente(s) afetado(s): `backend/app/services/dashboard_service.py`, endpoint `/dashboard/leads/analise-etaria`, pagina `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`, servico `frontend/src/services/dashboard_age_analysis.ts`, modelagem `Lead`/`Evento`/`Ativacao`, e a arvore documental agora arquivada em `PROJETOS/FEITO/DASHBOARD-LEADS/`
- riscos de nao agir: os dashboards continuam sujeitos a falso vazio e divergencia de contagem, o backlog tecnico segue desancorado de features demonstraveis e o legado deprecado permanece competindo com o projeto sucessor pelo mesmo espaco de execucao

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: ordenacao final das features do PRD sucessor e criterio para decidir quais itens tecnicos do legado viram habilitadores, cancelamentos ou follow-ups posteriores
- dependencia ainda nao confirmada: estrategia exata para migrar ou reescrever cada issue do legado dentro do backlog `feature-first` de `DL2`
- dado ainda nao disponivel: comunicacao operacional necessaria caso as contagens historicas mudem apos consolidacao canonica e backfill
- decisao de UX ainda nao fechada: se algum dashboard precisara expor ao usuario a origem do vinculo do lead ou se esse detalhe permanece transparente nesta fase
- outro ponto em aberto: patrocinador nominal e restricao de prazo permanecem `nao_definido`, e o PRD precisara decidir como tratar itens tecnicos do legado que nao sustentem diretamente as features priorizadas

## 15. Perguntas que o PRD Precisa Responder

- quais features demonstraveis vao organizar `DL2` para provar valor nas superfices `/dashboard/leads/analise-etaria`, `/dashboard/leads` e `/dashboard/leads/relatorio`
- como semantica canonica, backfill historico e retirada de heuristicas entram como habilitadores dessas features sem voltar ao paradigma `architecture-first`
- quais itens do backlog arquivado em `PROJETOS/FEITO/DASHBOARD-LEADS/` serao migrados, fundidos, adiados ou cancelados no projeto sucessor
- como validar rollout e nao-regressao para que as contagens por evento se mantenham coerentes entre consumidores analiticos

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
