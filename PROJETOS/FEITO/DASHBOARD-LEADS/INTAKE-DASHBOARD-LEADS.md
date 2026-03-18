---
doc_id: "INTAKE-DASHBOARD-LEADS.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-17"
project: "DASHBOARD-LEADS"
intake_kind: "problem"
source_mode: "backfilled"
origin_project: "DASHBOARD-LEADS"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "data-product" # [hipótese: iniciativa orientada a consistencia analitica e dashboards]
delivery_surface: "fullstack-module"
business_domain: "leads" # [hipótese: o nucleo do problema esta na modelagem e classificacao do lead]
criticality: "alta" # [hipótese: erro distorce relatorios e leitura operacional]
data_sensitivity: "lgpd"
integrations:
  - "evento"
  - "ativacao"
  - "lead batch / pipeline ETL"
  - "dashboards de leads"
  - "origens de ticketing/importacao de ingressos"
change_type: "correcao-estrutural" # [hipótese: remediacao sistemica de modelo e leitura]
audit_rigor: "elevated" # [hipótese: envolve dados sensiveis, historico e consistencia analitica]
---

# INTAKE - DASHBOARD-LEADS

> Artefato retrospectivo. Este arquivo formaliza um problema estrutural descoberto em investigacao de producao, sem alegar que este foi o registro original da descoberta.

## 0. Rastreabilidade de Origem

- projeto de origem: DASHBOARD-LEADS
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: backfill documental de um problema estrutural identificado ao investigar por que o dashboard `/dashboard/leads/analise-etaria` retornava vazio para eventos com leads existentes, expondo um paradigma incorreto na relacao entre `Lead`, `Evento` e `Ativacao`

## 1. Resumo Executivo

- nome curto da iniciativa: remediacao estrutural do relacionamento lead-evento-ativacao
- tese em 1 frase: lead deve possuir relacao canonica com evento, enquanto ativacao deve ser tratada como contexto ou tipo de conversao do lead dentro do evento, e nao como precondicao para o lead existir analiticamente
- valor esperado em 3 linhas: eliminar falsos vazios e contagens incompletas em relatorios por evento; alinhar o banco ao paradigma real de negocio dos leads; reduzir remendos ad hoc em queries e dashboards ao criar uma fonte de verdade unica para vinculo de lead com evento

## 2. Problema ou Oportunidade

- problema atual: a modelagem e algumas leituras analiticas assumem, na pratica, que o lead se relaciona ao evento via `AtivacaoLead`, o que e conceitualmente incorreto porque um lead pode existir diretamente no evento por ticketing/importacao sem jamais passar por ativacao
- evidencia do problema: na investigacao do dashboard de analise etaria, a hipotese de `JOIN` vazio foi confirmada; a query original retornava zero linhas porque dependia do caminho `Lead -> AtivacaoLead -> Ativacao -> Evento`, enquanto os leads do evento "Tamo Junto" existiam por outros caminhos de ingestao
- custo de nao agir: dashboards e relatorios por evento continuam omitindo leads reais; a engenharia continua acumulando compensacoes por query; a base passa a representar de forma enganosa a relacao entre captacao, conversao e participacao em evento
- por que agora: o bug ja se manifestou em producao, a investigacao confirmou que o problema nao e apenas de filtro ou UI, e a correcao pontual atual evidencia que a falha e sistemica de modelagem e semantica de dados

## 3. Publico e Operadores

- usuario principal: usuarios internos autenticados do NPBB que consomem dashboards e relatorios de leads por evento
- usuario secundario: [hipótese: times de operacao, marketing e analytics que interpretam volume, cobertura e conversao de leads por evento]
- operador interno: engenharia backend, frontend e dados/ETL responsavel por ingestao, modelagem e consumo analitico
- quem aprova ou patrocina: nao_definido; o contexto nao explicita patrocinador nominal ou aprovador final

## 4. Jobs to be Done

- job principal: consultar e consolidar leads por evento sem depender da origem do dado e sem perder a capacidade de detalhar ativacoes quando isso for necessario
- jobs secundarios: classificar corretamente se o lead pertence ao evento, registrar quando houve conversao em ativacao, e manter coerencia entre ingestao, persistencia e leitura analitica
- tarefa atual que sera substituida: [hipótese: remendos por query e vinculos implicitos para descobrir se um lead "deveria aparecer" em um relatorio por evento]

## 5. Fluxo Principal Desejado

1. um lead entra no sistema por ticketing, ETL, upload/pipeline ou interacao em ativacao
2. o sistema registra de forma canonica a relacao desse lead com o evento correspondente
3. se houver conversao em ativacao, essa conversao e registrada sem substituir nem ocultar o vinculo do lead com o evento
4. qualquer relatorio filtrado por evento contabiliza tanto o lead que foi diretamente ao evento quanto o lead que converteu em uma ativacao ligada a esse evento, com opcao futura de detalhamento por ativacao

## 6. Escopo Inicial

### Dentro

- remediar o paradigma de dominio para que `Lead` tenha classificacao/vinculo canonico com `Evento`
- tratar `Ativacao` como contexto de conversao do lead dentro do evento, e nao como unico elo possivel entre lead e evento
- ajustar ingestao, persistencia e leituras analiticas para contabilizar corretamente leads de evento, leads de ativacao e casos em que nao ha dados de conversao por ticketing
- definir estrategia segura para historico, aceitando retroprocessamento ou reenvio a partir do bronze quando isso for mais eficiente e nao colocar dados de evento em risco

### Fora

- recriar ou alterar dados mestres de evento sem necessidade
- detalhar no dashboard atual a analise por ativacao como requisito desta primeira remediacao
- inventar inferencias de vinculo quando a origem do dado nao permitir determinar com seguranca a relacao com o evento
- executar mudanca destrutiva que coloque em risco os dados de evento ja persistidos

## 7. Resultado de Negocio e Metricas

- objetivo principal: fazer o banco e os consumidores analiticos refletirem corretamente que o lead pode pertencer diretamente ao evento e opcionalmente converter em uma ativacao ligada a esse evento
- metricas leading: novos dados persistem vinculo de evento sem depender de `AtivacaoLead`; consultas por evento deixam de retornar falso vazio quando existem leads validos; testes de reconciliacao conseguem provar que contagens por evento incluem tanto origem direta quanto origem via ativacao
- metricas lagging: reducao de incidentes de inconsistencias em dashboards de leads; convergencia das contagens por evento entre relatorios atuais e futuros; menor necessidade de correcoes pontuais em servicos de dashboard
- criterio minimo para considerar sucesso: qualquer relatorio filtrado por evento deve contabilizar corretamente leads do evento, inclusive quando a conversao ocorreu em ativacao ligada ao evento, sem excluir casos de ticketing/importacao direta e sem exigir remendo especifico por dashboard

## 8. Restricoes e Guardrails

- restricoes tecnicas: preservar compatibilidade com fluxos de ingestao existentes durante a transicao; nao exigir `AtivacaoLead` como precondicao para leitura por evento; manter deduplicacao confiavel entre multiplas origens
- restricoes operacionais: dados de evento devem ser preservados; dados de leads podem ser retroprocessados ou reenviados a partir do bronze quando isso reduzir risco e custo operacional
- restricoes legais ou compliance: dados de leads incluem informacoes pessoais e devem manter tratamento compatível com LGPD
- restricoes de prazo: nao_definido; o contexto nao informa janela, milestone ou deadline
- restricoes de design ou marca: nao_aplicavel nesta fase; o impacto principal e de modelo, ingestao e leitura analitica

## 9. Dependencias e Integracoes

- sistemas internos impactados: modelos `Lead`, `Evento`, `Ativacao`, `AtivacaoLead`, `LeadBatch`, `LeadConversao`, `ConversaoAtivacao`; pipeline ETL/importacao; servicos e endpoints de dashboard; consumidores frontend de relatorios por evento
- sistemas externos impactados: [hipótese: ticketerias e fontes externas de importacao de leads ja integradas ao fluxo atual]
- dados de entrada necessarios: identificadores e metadados de evento, lotes/pipelines de lead, vinculos atuais com ativacao, dados de origem do lead e historico bronze quando necessario para reprocessamento
- dados de saida esperados: relacao canonica persistida entre lead e evento, registro coerente de conversoes em ativacao/evento, e respostas analiticas consistentes para filtros por evento

## 10. Arquitetura Afetada

- backend: dominio e regras de negocio de `Lead`, `Evento`, `Ativacao` e conversoes; pipelines/importadores; camada de servico analitica; contratos dos endpoints que consolidam dados por evento
- frontend: dashboards e filtros que hoje consomem relatorios por evento, especialmente analises em `/dashboard/leads/*`
- banco/migracoes: [hipótese: sera necessaria uma estrutura canonica explicita para vinculo `lead-evento` e uma estrategia de migracao compativel com os dados atuais]
- observabilidade: testes de regressao, reconciliacao entre origens de lead, e evidencias que provem que o total por evento nao varia conforme o caminho de ingestao
- autorizacao/autenticacao: preservar as regras atuais de acesso autenticado aos dashboards e endpoints
- rollout: [hipótese: rollout em transicao segura, priorizando compatibilidade e fonte canonica para novos dados, com historico tratado via retroprocessamento ou reenvio do bronze conforme custo e seguranca]

## 11. Riscos Relevantes

- risco de produto: mudanca de paradigma alterar totais historicos percebidos pelos usuarios sem comunicacao adequada
- risco tecnico: coexistencia temporaria de multiplos caminhos de vinculo gerar duplicidade ou divergencia de contagem
- risco operacional: retroprocessamento ou reenvio de leads causar duplicacao se a estrategia de deduplicacao nao estiver fechada
- risco de dados: manter `Lead.evento_nome = Evento.nome` como mecanismo principal perpetuar vinculo fragil e dependente de texto
- risco de adocao: equipes continuarem resolvendo relatorios com excecoes locais em vez de migrar para a fonte canonica

## 12. Nao-Objetivos

- redesenhar toda a experiencia visual dos dashboards nesta rodada
- entregar agora um relatorio completo de detalhamento por ativacao
- alterar ou reconstruir manualmente a base mestre de eventos

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: o dashboard `http://127.0.0.1:5173/dashboard/leads/analise-etaria` exibia `Nenhum lead encontrado para os filtros aplicados` mesmo havendo leads do evento "Tamo Junto" no banco
- impacto operacional: usuarios passam a interpretar que o evento nao possui leads ou que os filtros estao incorretos, comprometendo a confianca no dashboard e qualquer decisao baseada nele
- evidencia tecnica: a investigacao confirmou que filtros, URL, agencia e request nao eram a causa; o problema era o `JOIN` dependente de `AtivacaoLead`; uma correcao pontual passou a unir tres caminhos (`AtivacaoLead`, `LeadBatch.evento_id` e `Lead.evento_nome = Evento.nome`) e encontrou `1709` leads do evento `TAMO JUNTO BB`, o que resolve o sintoma imediato mas tambem comprova a fragilidade do paradigma atual
- componente(s) afetado(s): `backend/app/services/dashboard_service.py`, endpoint `/dashboard/leads/analise-etaria`, pagina `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`, servico `frontend/src/services/dashboard_age_analysis.ts`, e a modelagem nas entidades `Lead`, `Evento`, `Ativacao`, `AtivacaoLead` e `LeadBatch`
- riscos de nao agir: novos dashboards ou relatorios por evento repetirao a mesma falha; a base continuara mascarando a relacao real entre lead e evento; a regra de negocio ficara espalhada em queries compensatorias em vez de uma modelagem canonica

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: formato final da persistencia canonica do vinculo `lead-evento` e da representacao de conversao em `ativacao` versus conversao direta no `evento`
- dependencia ainda nao confirmada: se o historico sera corrigido por retroprocessamento na base atual ou por reenvio dos leads a partir do bronze
- dado ainda nao disponivel: cobertura real do historico necessario para reconstruir todos os vinculos legados com seguranca e sem duplicidade
- decisao de UX ainda nao fechada: se o produto exibira explicitamente a origem do vinculo do lead no dashboard atual ou se isso ficara transparente ao usuario nesta fase
- outro ponto em aberto: patrocinador nominal e restricao de prazo seguem nao_definido; a correcao atual por query deve ser tratada como transitoria e nao como modelo final

## 15. Perguntas que o PRD Precisa Responder

- qual sera a fonte canonica de verdade para representar a relacao entre `Lead`, `Evento` e `Ativacao` sem ambiguidade semantica
- qual estrategia de migracao, retroprocessamento ou reenvio a partir do bronze entrega consistencia historica com menor risco para os dados ja existentes de evento
- como garantir que relatorios por evento e futuros detalhamentos por ativacao compartilhem a mesma base e nunca divirjam em contagem total

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
