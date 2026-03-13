---
doc_id: "INTAKE-FRAMEWORK2.0.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-09"
project: "FRAMEWORK2.0"
intake_kind: "refactor"
source_mode: "backfilled"
origin_project: "COMUM"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "interna"
integrations:
  - "PROJETOS/COMUM"
change_type: "refactor"
audit_rigor: "elevated"
---

# INTAKE - FRAMEWORK2.0

## 0. Rastreabilidade de Origem

- projeto de origem: `COMUM`
- fase de origem: `nao_aplicavel`
- auditoria de origem: `nao_aplicavel`
- relatorio de origem: `nao_aplicavel`
- motivo da abertura deste intake: backfill a partir da analise critica consolidada no `PRD-FRAMEWORK2.0.md`

## 1. Resumo Executivo

- nome curto da iniciativa: `FRAMEWORK2.0`
- tese em 1 frase: reduzir ruido, duplicacao normativa e lacunas operacionais no framework documental de `PROJETOS/`
- valor esperado em 3 linhas:
  padronizar nomes e responsabilidades dos artefatos comuns
  tornar o fluxo de chat interativo operavel de ponta a ponta
  transformar o achado de monolito em regra objetiva e rastreavel

## 2. Problema ou Oportunidade

- problema atual: o framework possui documentos legados, regras duplicadas, prompts desconectados e lacunas em fluxo de remediacao estrutural
- evidencia do problema: analise critica consolidada em `PRD-FRAMEWORK2.0.md`
- custo de nao agir: agentes e PMs podem operar com leitura errada, links quebrados e governanca inconsistente
- por que agora: o repositorio ja usa o framework em projetos ativos e o custo de drift cresce a cada iteracao

## 3. Publico e Operadores

- usuario principal: PM que opera `PROJETOS/` em chat ou Cloud Agent
- usuario secundario: agentes de IA executores e auditores
- operador interno: engenharia de produto responsavel pela manutencao do framework
- quem aprova ou patrocina: PM / engenharia

## 4. Jobs to be Done

- job principal: operar projetos documentais sem ambiguidade de fluxo ou de nomenclatura
- jobs secundarios: gerar intake, PRD, planejamento, execucao e auditoria com prompts consistentes
- tarefa atual que sera substituida: adaptacao manual de prompts e interpretacao ad hoc de documentos redundantes

## 5. Fluxo Principal Desejado

1. PM escolhe o modo certo (`boot-prompt` ou `SESSION-*`)
2. framework aponta uma ordem de leitura unica e nomes de arquivos autoexplicativos
3. planejamento gera fases, epicos, issues e sprints sem drift
4. execucao e auditoria usam prompts de sessao com HITL quando necessario
5. achado estrutural gera intake de remediacao rastreavel

## 6. Escopo Inicial

### Dentro

- renomeacao de artefatos de `PROJETOS/COMUM/`
- unificacao das regras de intake, scrum e auditoria
- criacao de prompts de sessao faltantes
- criacao de spec anti-monolito e prompt de remediacao

### Fora

- mudanca de escopo de projetos ativos alem de atualizacao de referencias
- automacao ou CLI alem de arquivos Markdown
- thresholds para linguagens alem de TypeScript/React e Python

## 7. Resultado de Negocio e Metricas

- objetivo principal: tornar o framework operavel sem ambiguidade documental
- metricas leading: zero referencias antigas em projetos ativos; prompts de sessao completos e navegaveis
- metricas lagging: menor retrabalho por interpretacao errada e menor ruido em auditorias
- criterio minimo para considerar sucesso: framework comum renomeado, regras consolidadas e fluxo de sessao coberto

## 8. Restricoes e Guardrails

- restricoes tecnicas: alteracoes limitadas a Markdown e links documentais
- restricoes operacionais: nao inventar requisitos fora do PRD
- restricoes legais ou compliance: nao aplicavel
- restricoes de prazo: entregar em change set unico coerente
- restricoes de design ou marca: manter estilo documental existente

## 9. Dependencias e Integracoes

- sistemas internos impactados: `PROJETOS/COMUM`, `boot-prompt.md`, projetos ativos
- sistemas externos impactados: nenhum
- dados de entrada necessarios: PRD atual e documentos comuns existentes
- dados de saida esperados: docs renomeados, specs novos, prompts novos e backlog issue-first do projeto

## 10. Arquitetura Afetada

- backend: nao aplicavel
- frontend: nao aplicavel
- banco/migracoes: nao aplicavel
- observabilidade: nao aplicavel
- autorizacao/autenticacao: nao aplicavel
- rollout: update coordenado de nomes e referencias no mesmo change set

## 11. Riscos Relevantes

- risco de produto: links quebrados em projetos ativos
- risco tecnico: renomeacao parcial gerar drift
- risco operacional: uso de thresholds anti-monolito sem calibracao minima
- risco de dados: nao aplicavel
- risco de adocao: PM continuar usando prompt errado por nomenclatura antiga

## 12. Nao-Objetivos

- nao migrar projetos feitos para novos templates
- nao introduzir automacao fora de Markdown
- nao revisar conteudo substantivo de PRDs ativos alem do necessario para referencias

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: documentos comuns com nome ambiguidade, regras duplicadas e fluxo incompleto de sessao/monolito
- impacto operacional: planejamento, execucao e auditoria exigem interpretacao manual excessiva
- evidencia tecnica: `PRD-FRAMEWORK2.0.md`
- componente(s) afetado(s): `PROJETOS/COMUM/`, `PROJETOS/boot-prompt.md`, projetos ativos
- riscos de nao agir: consolidacao de drift e abertura de projetos fora do padrao canonico

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: nenhuma critica alem da decisao sobre `PROMPT-PLANEJAR-FASE`, resolvida em `GOV-DECISOES.md`
- dependencia ainda nao confirmada: nenhuma
- dado ainda nao disponivel: futuras calibracoes adicionais alem de `dashboard-leads-etaria`
- decisao de UX ainda nao fechada: nao aplicavel
- outro ponto em aberto: nenhum bloqueio atual

## 15. Perguntas que o PRD Precisa Responder

- como particionar a adequacao em fases e epicos sem quebrar o framework em uso
- quais artefatos precisam ser renomeados, criados ou consolidados
- como tratar thresholds anti-monolito e remediacao em chat interativo

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
