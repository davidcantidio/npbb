---
doc_id: "INTAKE-FRAMEWORK4.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "FRAMEWORK4"
intake_kind: "refactor"
source_mode: "derived"
origin_project: "FRAMEWORK3"
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
change_type: "refactor"
audit_rigor: "elevated"
---

# INTAKE - FRAMEWORK4

> Este intake é derivado do FRAMEWORK3 e representa a migração para o novo paradigma **feature-first**.
> O objetivo é manter o mesmo escopo do FRAMEWORK3 (sistema CRUD + Orquestrador de Agentes),
> mas reorganizar o planejamento em torno de **features** (comportamentos entregáveis) ao invés
> de camadas técnicas.

## 0. Rastreabilidade de Origem

- **projeto de origem**: FRAMEWORK3
- **fase de origem**: todas (F1-F5)
- **auditoria de origem**: nao_aplicavel
- **relatorio de origem**: [PRD-FRAMEWORK3.md](../FRAMEWORK3/PRD-FRAMEWORK3.md)
- **motivo da abertura deste intake**: Migrar o FRAMEWORK3 para o novo paradigma feature-first do framework de projetos. O FRAMEWORK3 será arquivado como referência histórica.

## 1. Resumo Executivo

- **nome curto da iniciativa**: FRAMEWORK4 - Sistema CRUD + Orquestrador Feature-First
- **tese em 1 frase**: Reorganizar o sistema CRUD + Orquestrador de Agentes do FRAMEWORK3 em torno de features (comportamentos entregáveis), mantendo todo o escopo e valor já definidos.
- **valor esperado em 3 linhas**:
  1. Manter 100% do escopo do FRAMEWORK3 (CRUD + Orquestrador + Histórico + Admin)
  2. Reorganizar o planejamento em Features como eixo principal
  3. Aplicar o novo paradigma feature-first mantendo governança existente

## 2. Problema ou Oportunidade

- **problema atual**: O FRAMEWORK3 foi planejado no paradigma anterior (arquitetura-first). Precisa ser migrado para o novo paradigma feature-first.
- **evidencia do problema**: O framework de projetos (PROJETOS/COMUM/) foi atualizado para paradigma feature-first, com templates e governança organizados em torno de features.
- **custo de nao agir**: FRAMEWORK3 fica fora do novo padrão, dificulta manutenção e onboarding.
- **por que agora**: O novo paradigma está pronto (templates, governança) e o FRAMEWORK3 é um projeto ativo que precisa ser migrado.

## 3. Publico e Operadores

- **usuario principal**: PM / Product Manager
- **usuario secundario**: Engenheiros e agentes IA que executam tasks
- **operador interno**: AgentOrchestrator + subagentes
- **quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **job principal**: Sistema CRUD + Orquestrador de Agentes para gestão automatizada de projetos
- **jobs secundarios**:
  - Consultar status de qualquer projeto/fase/issue
  - Revisar histórico completo de decisões e artefatos gerados
  - Treinar/future-proof o sistema com os dados coletados
- **tarefa atual que sera substituida**: Herdado do FRAMEWORK3 - mesma entrega, novo paradigma

## 5. Fluxo Principal Desejado

O fluxo segue o novo paradigma feature-first:

1. **Intake** (este documento)
2. **Síntese** (organização do problema em features candidatas)
3. **PRD** (Features organizadas como eixo principal)
4. **Fases** (derivadas das Features, não mais F1-F5 arbitrary)
5. **Épicos** (agrupados por Feature)
6. **Issues** (vinculadas a Features)
7. **Tasks** (atomicidade orientada a comportamento)
8. **Auditorias** (mesmo fluxo do FRAMEWORK3)

## 6. Escopo Inicial

### Dentro

Manter 100% do escopo do FRAMEWORK3:

- Modelo de dados completo (projects, intakes, prds, phases, epics, sprints, issues, tasks, audit_logs, agent_executions)
- CRUD completo para gestão de projetos
- AgentOrchestrator central com suporte a modos (autonomous / hitl)
- Integração com governança documental existente
- Persistência de histórico para treinamento
- Módulo admin no frontend NPBB

### Fora

- Reimplementar algo que já funciona (apenas migrar paradigma)
- Fine-tuning real do LLM (apenas preparação dos dados)

## 7. Resultado de Negocio e Metricas

- **objetivo principal**: Entregar o mesmo sistema do FRAMEWORK3, mas planejado com Features como eixo.
- **metricas leading**: Same as FRAMEWORK3
- **metricas lagging**: Same as FRAMEWORK3
- **criterio minimo para considerar sucesso**: FRAMEWORK4 consegue criar e executar projetos no novo paradigma feature-first.

## 8. Restricoes e Guardrails

- **restricoes tecnicas**: Mesmo stack do FRAMEWORK3 (FastAPI, PostgreSQL, React/Vite)
- **restricoes operacionais**: Manter compatibilidade com governança feature-first (GOV-*, TEMPLATE-*)
- **restricoes legais ou compliance**: nao_aplicavel
- **restricoes de prazo**: Same as FRAMEWORK3
- **restricoes de design ou marca**: Following new template structure

## 9. Dependencias e Integracoes

- **sistemas internos impactados**: Same as FRAMEWORK3
- **sistemas externos impactados**: nenhum
- **dados de entrada necessarios**: PRD-FRAMEWORK3.md, Issues e Tasks existentes do FRAMEWORK3
- **dados de saida esperados**: Novo projeto no paradigma feature-first

## 10. Arquitetura Afetada

- **backend**: Same as FRAMEWORK3
- **frontend**: Same as FRAMEWORK3
- **banco/migrações**: Same as FRAMEWORK3
- **observabilidade**: Same as FRAMEWORK3
- **autorização/autenticação**: Same as FRAMEWORK3
- **rollout**: Same as FRAMEWORK3

## 11. Riscos Relevantes

- **risco de produto**: Nenhum - mesmo escopo
- **risco tecnico**: Nenhum - mesmo sistema
- **risco operacional**: Risco de transição - garantir que nada se perca
- **risco de dados**: Nenhum
- **risco de adocao**: Resistência a migrar de paradigma

## 12. Nao-Objetivos

- Não alterar o escopo do sistema (mantém 100% do FRAMEWORK3)
- Não fazer fine-tuning real (apenas preparação de dados)
- Não abandonar a governança feature-first

## 13. Contexto Especifico para Problema ou Refatoracao

> Obrigatório para `intake_kind: problem | refactor | audit-remediation`.

- **sintoma observado**: FRAMEWORK3 foi planejado no paradigma arquitetura-first
- **impacto operacional**: Manter dois paradigmas no framework causa confusão
- **evidencia tecnica**: Template de PRD em COMUM agora é feature-first
- **componente(s) afetado(s)**: PROJETOS/FRAMEWORK3/ → PROJETOS/FRAMEWORK4/
- **riscos de nao agir**: FRAMEWORK3 fica obsoleto e fora do padrão

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: Nenhuma - usa mesmo escopo do FRAMEWORK3
- dependencia ainda nao confirmada: Nenhuma nova
- decisao de UX ainda nao fechada: Herdado do FRAMEWORK3
- outro ponto em aberto: Nenhum

## 15. Perguntas que o PRD Precisa Responder

- Quais são as Features que derivam do PRD-FRAMEWORK3?
- Como mapear as fases F1-F5 em Features?
- Como tratar as Issues existentes do FRAMEWORK3?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada
- [x] problema esta claro (migração de paradigma)
- [x] publico principal esta claro
- [x] fluxo principal esta descrito (feature-first)
- [x] escopo dentro/fora esta fechado (mesmo do FRAMEWORK3)
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de refatoracao foi preenchido
