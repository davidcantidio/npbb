---
doc_id: "INTAKE-FRAMEWORK3.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-17"
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

> Este intake formaliza a evolução do framework de projetos atual para um sistema CRUD + orquestrador de agentes com persistência em banco de dados.

## 0. Rastreabilidade de Origem

- projeto de origem: npbb (este repositório)
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: Consolidar o framework de projetos em um sistema CRUD + orquestrador de agentes. O usuário atualmente copia e renomeia arquivos da pasta COMUM, preenche cabeçalhos manualmente e aprova cada gate. Ver algoritmo detalhado em [PROJETOS/Algoritmo.md](../Algoritmo.md). Deseja deixar mais a cargo da IA (orquestrador + subagentes), persistir todo o histórico para treinamento futuro de LLM especialista e manter obediência aos arquivos de governança existentes.

## 1. Resumo Executivo

- nome curto da iniciativa: FRAMEWORK3 - Orquestrador de Projetos + CRUD
- tese em 1 frase: Transformar o framework de governança documental em um sistema persistente, automatizado e preparado para treinamento de LLM, mantendo toda a governança existente.
- valor esperado em 3 linhas:
  1. Eliminar o trabalho manual de copiar/renomear arquivos MD e preencher cabeçalhos.
  2. Criar um orquestrador de agentes que gerencia o fluxo Intake → PRD → Fases → Tasks com opção de modo autônomo ou HITL.
  3. Persistir todo o histórico (prompts, decisões, artefatos) para criar dataset de treinamento de um LLM especialista em gestão de projetos.

## 2. Problema ou Oportunidade

- problema atual: Fluxo manual repetitivo (copiar SESSION-*.md, TEMPLATE-*.md, preencher frontmatter, aprovar manualmente em cada gate), falta de persistência centralizada, dificuldade de rastreabilidade e impossibilidade atual de treinar um modelo especializado.
- evidencia do problema: Usuário reporta que "eu me pego copiando, renomeando arquivos md da pasta PROJETO/COMUM" e que "está na hora de automatizar".
- custo de nao agir: Tempo significativo do PM/usuário em tarefas repetitivas + perda de oportunidade de coletar dados ricos para fine-tuning.
- por que agora: O framework já está maduro (FRAMEWORK2.0) e o volume de projetos justifica a construção de uma camada de automação + dados.

## 3. Publico e Operadores

- usuario principal: PM / Product Manager (usuário atual)
- usuario secundario: Engenheiros e agentes IA que executam tasks
- operador interno: AgentOrchestrator + subagentes
- quem aprova ou patrocina: PM (pode configurar nível de autonomia)

## 4. Jobs to be Done

- job principal: Gerenciar o ciclo completo de um projeto desde o intake até a execução e auditoria de forma automatizada e rastreável.
- jobs secundarios: 
  - Consultar status de qualquer projeto/fase/issue
  - Revisar histórico completo de decisões e artefatos gerados
  - Treinar/future-proof o sistema com os dados coletados
- tarefa atual que sera substituida: Copiar arquivos da pasta COMUM + uso manual de SESSION-*.md

## 5. Fluxo Principal Desejado

O fluxo segue rigorosamente o algoritmo descrito em [PROJETOS/Algoritmo.md](../Algoritmo.md) e os arquivos de governança:

1. Preenchimento do intake via formulário (baseado em [PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md](../COMUM/SESSION-CRIAR-INTAKE.md))
2. PM aprova Intake
3. IA gera PRD baseado no Intake
4. PM aprova PRD
5. IA gera Fases do projeto
6. Humano aprova Fases
7. IA gera Épicos
8. Humano aprova Épicos
9. IA gera Sprints
10. Humano aprova Sprints
11. IA gera Issues
12. Humano aprova Issues
13. IA gera Tasks
14. Humano aprova Tasks
15. IA gera instruções TDD para as Tasks

**A partir do passo 16 (pipeline de execução) é possível automatizar fortemente** usando orquestrador + subagentes:
- Preencher SESSION-IMPLEMENTAR-ISSUE.md com contexto da task (ex: F1-01-001-T1)
- IA executa tasks sequencialmente
- Ao final de issue, configurar SESSION-REVISAR-ISSUE.md com diffs/commits
- IA revisa e decide (aprovada, bloqueada, correção)
- Ao final de fase → processo de auditoria
- Aplicar soluções de hold automaticamente quando autorizado

Todo o histórico de prompts, decisões, aprovações e artefatos será persistido para treinamento futuro de LLM.

## 6. Escopo Inicial

### Dentro

- Modelo de dados completo (projects, intakes, prds, phases, epics, sprints, issues, tasks, audit_logs, agent_executions)
- CRUD completo para gestão de projetos
- AgentOrchestrator central com suporte a modos (autonomous / hitl)
- Integração com governança documental existente (GOV-*, TEMPLATE-*, SESSION-*)
- Persistência de histórico para treinamento (prompts, outputs, aprovações, diffs)
- Módulo admin no frontend NPBB

### Fora

- Substituição completa do sistema documental atual (projetos existentes devem continuar funcionando)
- Interface mobile
- Multi-tenancy avançado
- Fine-tuning real do LLM (apenas preparação dos dados)

## 7. Resultado de Negocio e Metricas

- objetivo principal: Reduzir em >80% o tempo manual gasto na gestão de projetos no framework.
- metricas leading: Número de projetos criados via novo sistema, % de steps automatizados, volume de dados coletados por projeto.
- metricas lagging: Tempo médio para completar um projeto completo, satisfação do PM, qualidade das entregas (medida por auditoria).
- criterio minimo para considerar sucesso: FRAMEWORK3 consegue criar um projeto completo (do intake até tasks) de forma automatizada e persistir todo o histórico.

## 8. Restricoes e Guardrails

- restricoes tecnicas: Deve reutilizar o stack existente (FastAPI, PostgreSQL, React/Vite) e não quebrar projetos existentes no diretório PROJETOS/
- restricoes operacionais: Manter compatibilidade total com boot-prompt.md e SESSION-*.md
- restricoes legais ou compliance: nao_aplicavel
- restricoes de prazo: Entregar MVP funcional em poucas iterações
- restricoes de design ou marca: Seguir exatamente o padrão de governança documental existente

## 9. Dependencias e Integracoes

- sistemas internos impactados: backend FastAPI, banco PostgreSQL, frontend React, sistema de agentes
- sistemas externos impactados: nenhum
- dados de entrada necessarios: Conteúdo dos arquivos de governança atuais (GOV-*, TEMPLATE-*, SESSION-*)
- dados de saida esperados: Artefatos MD gerados + registros no banco + histórico estruturado para treinamento

## 10. Arquitetura Afetada

- backend: Novo app de orquestração + models/schemas/endpoints
- frontend: Novo módulo admin no dashboard existente
- banco/migracoes: Novas tabelas + migrações Alembic
- observabilidade: Logs detalhados de execução de agentes
- autorizacao/autenticacao: Reutilizar auth existente do NPBB
- rollout: Como módulo interno, pode ser incremental

## 11. Riscos Relevantes

- risco de produto: Complexidade excessiva do orquestrador
- risco tecnico: Manter compatibilidade com framework documental atual
- risco operacional: Mudança de fluxo pode confundir usuário inicial
- risco de dados: Garantir qualidade e completude dos dados para treinamento futuro
- risco de adocao: Resistência a abandonar o fluxo 100% manual

## 12. Nao-Objetivos

- Não substituir completamente o sistema de arquivos Markdown (manter como fonte de verdade ou fallback)
- Não implementar fine-tuning real do modelo nesta fase
- Não criar um novo framework de agentes do zero (reutilizar o existente)

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: Trabalho manual repetitivo de cópia de arquivos e preenchimento de templates
- impacto operacional: Tempo significativo gasto em tarefas não-valorosas
- evidencia tecnica: Múltiplos arquivos SESSION-*.md e TEMPLATE-*.md que são copiados manualmente
- componente(s) afetado(s): PROJETOS/COMUM/ + estrutura de PROJETOS/<PROJETO>/
- riscos de nao agir: Escalabilidade limitada do framework atual

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: Níveis exatos de autonomia configuráveis por projeto
- dependencia ainda nao confirmada: Como o orquestrador vai interagir com o Cursor Agent atual
- decisao de UX ainda nao fechada: Design exato da interface admin
- outro ponto em aberto: Estratégia exata de migração de projetos existentes

## 15. Perguntas que o PRD Precisa Responder

- Como o AgentOrchestrator decide quando pedir aprovação humana vs executar automaticamente?
- Qual será o formato exato dos registros de histórico para treinamento?
- Como manter compatibilidade total com projetos que usam apenas o sistema documental?
- Qual o modelo de permissões para o módulo admin?

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
