---
doc_id: "INTAKE-DASHBOARD-LEADS-ETARIA.md"
version: "1.1"
status: "backfilled"
owner: "PM"
last_updated: "2026-03-08"
project: "DASHBOARD-LEADS-ETARIA"
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "DASHBOARD-LEADS-ETARIA"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "data-product"
delivery_surface: "fullstack-module"
business_domain: "dashboard"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "lead model"
  - "dashboard frontend"
  - "JWT auth"
  - "ETL leads dataset"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

# INTAKE - DASHBOARD-LEADS-ETARIA

> Artefato retrospectivo. Este arquivo foi reconstruido a partir do PRD vigente para formalizar a etapa `Intake -> PRD` sem alegar que este foi o registro original da descoberta.

## 0. Rastreabilidade de Origem

- projeto de origem: DASHBOARD-LEADS-ETARIA
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: backfill documental da origem da iniciativa

## 1. Resumo Executivo

- nome curto da iniciativa: dashboard portfolio com analise etaria por evento
- tese em 1 frase: centralizar a analise etaria de leads no proprio NPBB elimina relatorios manuais e cria uma base extensivel para novos dashboards
- valor esperado em 3 linhas: disponibilizar um subpainel navegavel, autenticado e auditavel com consolidado e detalhamento por evento, usando os dados ja ingeridos pelo pipeline e estendendo o modelo de leads para cobertura BB

## 2. Problema ou Oportunidade

- problema atual: relatorios analiticos sao produzidos fora do sistema e distribuidos manualmente
- evidencia do problema: a analise etaria e outras trilhas do portfolio nao possuem um painel interno consistente, versionado e sempre atualizado
- custo de nao agir: lentidao na tomada de decisao, retrabalho operacional e baixa extensibilidade para novas analises
- por que agora: o pipeline ETL ja possui os dados-base e o frontend pode receber uma arquitetura de subpainel extensivel

## 3. Publico e Operadores

- usuario principal: usuario autenticado do NPBB que consome analises de leads por evento
- usuario secundario: time de negocio/operacao que interpreta cobertura BB e distribuicao etaria
- operador interno: engenharia de backend e frontend responsavel por evoluir o portfolio de dashboards
- quem aprova ou patrocina: trilha de analytics/dashboards do produto NPBB

## 4. Jobs to be Done

- job principal: consultar rapidamente a distribuicao etaria e cobertura BB por evento dentro do sistema
- jobs secundarios: comparar eventos, interpretar media/mediana, filtrar por periodo e preparar a base para dashboards futuros
- tarefa atual que sera substituida: geracao externa e distribuicao manual de relatorios analiticos

## 5. Fluxo Principal Desejado

1. usuario autenticado acessa `/dashboard`
2. seleciona a analise etaria no portfolio de dashboards
3. visualiza consolidado geral e detalhes por evento com filtros de periodo/evento
4. interpreta cobertura BB, faixas etarias e destaques consolidados sem sair do NPBB

## 6. Escopo Inicial

### Dentro

- estender o modelo `Lead` com campos de cobertura BB/Estilo
- criar endpoint tipado para analise etaria
- introduzir arquitetura de dashboard com manifesto, layout e rotas protegidas
- implementar pagina da analise etaria com KPI cards, grafico, tabela, banners e estados da interface

### Fora

- dashboards futuros alem da trilha reservada
- exportacao PDF/Excel
- permissionamento granular por dashboard
- cache ou otimizacoes avancadas de performance nao exigidas pelo PRD inicial

## 7. Resultado de Negocio e Metricas

- objetivo principal: tornar a analise etaria por evento disponivel dentro do produto de forma navegavel e reutilizavel
- metricas leading: endpoint funcionando com filtros, navegacao protegida ativa, pagina respondendo com dados reais
- metricas lagging: reducao de relatorios manuais externos e uso recorrente do dashboard pelos usuarios autenticados
- criterio minimo para considerar sucesso: backend e frontend conectados, thresholds de cobertura BB respeitados e pagina tratando loading/empty/error sem regressao

## 8. Restricoes e Guardrails

- restricoes tecnicas: usar JWT existente, preservar padrao declarativo de rotas e manter payload tipado entre backend e frontend
- restricoes operacionais: dados BB ausentes nao podem ser inferidos; precisam ser exibidos com banners de cobertura
- restricoes legais ou compliance: dados de lead e data de nascimento exigem tratamento com rigor LGPD
- restricoes de prazo: fatiamento em 3 fases com backend, arquitetura de dashboard e UI final
- restricoes de design ou marca: o portfolio deve suportar crescimento sem redesign do layout raiz

## 9. Dependencias e Integracoes

- sistemas internos impactados: modelo `Lead`, rotas API, paginas frontend de dashboard, menu principal, autenticacao
- sistemas externos impactados: nenhum sistema externo novo; cobertura BB depende de processo de cruzamento de dados ja existente
- dados de entrada necessarios: `lead`, `evento`, `data_nascimento`, `is_cliente_bb`, filtros de periodo e evento
- dados de saida esperados: payload consolidado + por evento e pagina analitica tipada no frontend

## 10. Arquitetura Afetada

- backend: modelos SQLModel, migrations Alembic, schemas Pydantic, servicos e router dashboard
- frontend: manifesto de dashboards, layout raiz, home, pagina `LeadsAgeAnalysisPage` e componentes visuais
- banco/migracoes: adicao de `is_cliente_bb` e `is_cliente_estilo`
- observabilidade: testes backend e frontend direcionados para contrato, estados e visualizacoes
- autorizacao/autenticacao: acesso protegido por Bearer token / rotas autenticadas
- rollout: backend primeiro, depois arquitetura de dashboard, depois UI completa

## 11. Riscos Relevantes

- risco de produto: thresholds de cobertura BB serem mal interpretados sem banners e tooltips claros
- risco tecnico: drift de contrato entre endpoint backend e tipos do frontend
- risco operacional: migracao de banco e cobertura parcial de dados BB gerarem interpretacoes erradas
- risco de dados: calculo etario com datas ausentes ou invalidadas afetar percentuais
- risco de adocao: arquitetura do dashboard nao escalar bem para analises futuras se o manifesto for mal definido

## 12. Nao-Objetivos

- entregar dashboards futuros alem da analise etaria
- criar motor generico de BI ou exportacao nesta rodada
- alterar o processo externo de cruzamento de dados BB

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: nenhum bloqueio critico remanescente no PRD atual
- dependencia ainda nao confirmada: thresholds futuros podem ser refinados por decisao posterior, mas o default do PRD e suficiente para iniciar
- dado ainda nao disponivel: alguns eventos podem ter cobertura BB parcial e isso deve ser tratado como condicao normal do produto
- decisao de UX ainda nao fechada: detalhes finos de visualizacao podem evoluir sem quebrar o contrato funcional do PRD
- outro ponto em aberto: este documento e retrospectivo e serve como fonte canonica daqui para frente

## 15. Perguntas que o PRD Precisa Responder

- quais campos e agregacoes o endpoint de analise etaria precisa expor
- como o dashboard portfolio deve escalar para novas analises sem redesenho estrutural
- como representar cobertura BB incompleta sem inferir valores ausentes

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
