---
doc_id: "INTAKE-FRAMEWORK3.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "FRAMEWORK3"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "interna"
integrations:
  - "framework-governanca"
  - "agent-orchestrator"
  - "npbb-crud"
change_type: "nova-capacidade"
audit_rigor: "elevated"
---

# INTAKE - FRAMEWORK3

> Este intake adapta o FRAMEWORK3 ao paradigma `delivery-first` / `feature-first`
> do FRAMEWORK4 sem mudar a natureza da demanda original.

## 0. Rastreabilidade de Origem

- projeto de origem: npbb (este repositorio)
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: consolidar o framework de projetos atual em uma capacidade persistente e assistida por IA, reduzindo trabalho manual de governanca e preparando o projeto para planejamento por features demonstraveis, sem romper compatibilidade com os artefatos e prompts existentes. O contexto funcional continua ancorado em [PROJETOS/Algoritmo.md](../Algoritmo.md).

## 1. Resumo Executivo

- nome curto da iniciativa: FRAMEWORK3 - Governanca Assistida por Features
- tese em 1 frase: transformar o fluxo documental manual de planejamento e execucao de projetos em uma experiencia governada por features entregaveis, suportada por CRUD, orquestracao de agentes e rastreabilidade persistida.
- valor esperado em 3 linhas:
  1. eliminar a copia manual de arquivos `SESSION-*` e `TEMPLATE-*` e reduzir o trabalho operacional repetitivo do PM.
  2. permitir que o projeto seja planejado e executado a partir de features demonstraveis, com gates humanos onde necessario e automacao forte onde houver seguranca.
  3. persistir prompts, decisoes, aprovacoes e evidencias para auditoria, analytics e futuro treinamento de um LLM especialista em gestao de projetos.

## 2. Problema ou Oportunidade

- problema atual: o framework atual depende de copia, renomeacao e preenchimento manual de artefatos Markdown, com baixa automacao operacional e pouca centralizacao de historico.
- evidencia do problema: o fluxo corrente exige repetir a cada projeto a criacao manual de intake, PRD, fases, epicos, issues e tasks a partir de arquivos-base, alem de gates manuais sucessivos.
- custo de nao agir: o PM continua consumindo tempo em trabalho mecanico, a operacao nao escala com seguranca e o historico fica fragmentado para auditoria e treinamento.
- por que agora: o framework ja atingiu maturidade suficiente para migrar do planejamento orientado a arquitetura para um planejamento orientado a entrega, sem perder a governanca existente.

## 3. Publico e Operadores

- usuario principal: PM / Product Manager responsavel por abrir, aprovar e acompanhar projetos
- usuario secundario: engenheiros e agentes IA que executam issues e tasks
- operador interno: AgentOrchestrator e subagentes especializados
- quem aprova ou patrocina: PM, com poder de definir o nivel de autonomia operacional por projeto

## 4. Jobs to be Done

- job principal: conduzir um projeto do intake ate a auditoria de fase com rastreabilidade completa e menor dependencia de operacao manual repetitiva.
- jobs secundarios:
  - consultar o estado de qualquer feature, fase, epico, issue ou task
  - revisar historico de aprovacoes, prompts e artefatos gerados
  - usar os dados persistidos para melhoria continua e treinamento futuro
- tarefa atual que sera substituida: copiar e adaptar arquivos da pasta `COMUM/`, preencher cabecalhos manualmente e controlar gates de aprovacao de forma artesanal

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. PM informa o contexto bruto do projeto e gera um intake estruturado com rastreabilidade e lacunas explicitas.
2. IA converte o intake aprovado em um PRD `feature-first`, com features demonstraveis, criterios de aceite e impactos arquiteturais por feature.
3. O planejamento hierarquico deriva fases, epicos, issues e tasks a partir das features do PRD, mantendo a rastreabilidade `feature -> fase -> epico -> issue`.
4. O orquestrador executa issues elegiveis com subagentes, aplica gates de revisao e aciona auditoria de fase ao final dos ciclos relevantes.
5. O sistema persiste historico operacional, aprovacoes, evidencias e artefatos para consulta, auditoria e reutilizacao futura.

## 6. Escopo Inicial

### Dentro

- modelo de dados para projetos, intake, PRD, fases, epicos, sprints, issues, tasks, auditorias e execucoes de agentes
- CRUD para abertura, edicao, consulta e navegacao de projetos e artefatos
- orquestracao do fluxo de planejamento e execucao conforme governanca existente
- planejamento do projeto orientado a features demonstraveis em vez de fases tecnicas
- persistencia de prompts, outputs, aprovacoes, diffs e historico para auditoria e treinamento
- modulo administrativo integrado ao dashboard do NPBB

### Fora

- substituicao completa do sistema documental atual como unica fonte de verdade
- interface mobile
- multi-tenancy avancado
- fine-tuning real de LLM nesta fase

## 7. Resultado de Negocio e Metricas

- objetivo principal: reduzir em mais de 80% o tempo manual do PM no ciclo de governanca e planejamento de projeto.
- metricas leading: numero de projetos iniciados via FRAMEWORK3, percentual de etapas automatizadas com seguranca, volume de eventos operacionais persistidos por projeto.
- metricas lagging: tempo medio para levar um projeto do intake ate a execucao de issue, qualidade percebida das entregas, taxa de auditorias aprovadas sem retrabalho estrutural.
- criterio minimo para considerar sucesso: o FRAMEWORK3 deve conseguir levar um projeto do intake aprovado ate uma issue executavel com rastreabilidade completa e historico persistido.

## 8. Restricoes e Guardrails

- restricoes tecnicas: reutilizar o stack existente do NPBB (FastAPI, PostgreSQL, React/Vite) e preservar compatibilidade com a estrutura atual em `PROJETOS/`.
- restricoes operacionais: obedecer aos arquivos `GOV-*`, `SESSION-*`, `TEMPLATE-*` e ao algoritmo de negocio sem inventar novas regras fora da governanca vigente.
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: buscar MVP funcional em poucas iteracoes, priorizando fluxo util antes de automacao total.
- restricoes de design ou marca: manter a linguagem e a disciplina documental do framework atual.

## 9. Dependencias e Integracoes

- sistemas internos impactados: backend FastAPI, banco PostgreSQL, frontend React/Vite, superfice administrativa do NPBB e sistema de agentes
- sistemas externos impactados: nenhum
- dados de entrada necessarios: conteudo dos arquivos `GOV-*`, `SESSION-*`, `TEMPLATE-*`, contexto do projeto fornecido pelo PM e regras do [PROJETOS/Algoritmo.md](../Algoritmo.md)
- dados de saida esperados: artefatos Markdown canonicos, registros estruturados no banco, historico de execucao e trilha de auditoria

## 10. Arquitetura Afetada

- backend: novos servicos e contratos para CRUD, planejamento, orquestracao e registro de execucoes
- frontend: modulo admin para abrir projetos, navegar hierarquia e consultar historico operacional
- banco/migracoes: novas tabelas e relacoes para artefatos, execucoes, aprovacoes e auditorias
- observabilidade: logs estruturados de execucao, trilha de aprovacoes e evidencias de automacao
- autorizacao/autenticacao: reutilizar o modelo atual do NPBB, com guardas adequadas para operacao administrativa
- rollout: incremental, com coexistencia entre fluxo documental legado e fluxo assistido no FRAMEWORK3

## 11. Riscos Relevantes

- risco de produto: transformar o projeto em uma plataforma excessivamente tecnica e perder o foco em entregas demonstraveis.
- risco tecnico: manter compatibilidade com a governanca documental enquanto adiciona persistencia, CRUD e orquestracao.
- risco operacional: calibrar corretamente quando exigir aprovacao humana e quando permitir execucao automatizada.
- risco de dados: registrar historico incompleto ou pouco util para auditoria e treinamento futuro.
- risco de adocao: o PM nao confiar na automacao se o fluxo ficar opaco ou dificil de inspecionar.

## 12. Nao-Objetivos

- nao substituir completamente os arquivos Markdown por banco de dados
- nao criar um novo framework de agentes do zero sem reaproveitar a governanca existente
- nao considerar a arquitetura como eixo principal de planejamento do projeto

## 13. Contexto Especifico para Problema ou Refatoracao

> Para este intake `new-capability`, a secao fica registrada apenas como contexto complementar.

- sintoma observado: trabalho repetitivo para abrir e planejar projetos com base em arquivos manuais
- impacto operacional: perda de tempo do PM, baixa escalabilidade do processo e historico fragmentado
- evidencia tecnica: proliferacao de `SESSION-*`, `TEMPLATE-*` e artefatos hierarquicos que dependem de copia e adaptacao manual
- componente(s) afetado(s): `PROJETOS/COMUM/`, estrutura `PROJETOS/<PROJETO>/`, backend, frontend admin e camada de agentes
- riscos de nao agir: manter um framework funcional, mas operacionalmente caro e dificil de escalar

## 14. Lacunas Conhecidas

Liste tudo que a IA nao pode inventar sozinha:

- regra de negocio ainda nao definida: niveis exatos de autonomia configuraveis por projeto e criterio formal de elegibilidade por etapa.
- dependencia ainda nao confirmada: forma final de integracao entre o AgentOrchestrator e o ambiente/cliente de agentes em uso.
- dado ainda nao disponivel: formato final do dataset de treinamento e politicas de retencao/curadoria.
- decisao de UX ainda nao fechada: desenho detalhado da experiencia administrativa no dashboard.
- outro ponto em aberto: estrategia precisa de migracao ou onboarding de projetos legados para o fluxo assistido.

## 15. Perguntas que o PRD Precisa Responder

- quais features entregaveis estruturam o FRAMEWORK3 e como cada uma sera demonstrada?
- como a rastreabilidade `feature -> fase -> epico -> issue` sera preservada em todo o planejamento?
- como o orquestrador decide quando solicitar aprovacao humana e quando pode seguir automaticamente?
- como persistencia, auditoria e historico operacional entram como capacidade habilitadora das features sem virarem o eixo principal do plano?

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
