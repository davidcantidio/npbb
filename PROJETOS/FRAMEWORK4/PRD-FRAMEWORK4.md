---
doc_id: "PRD-FRAMEWORK4.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "FRAMEWORK4"
intake_origin: "INTAKE-FRAMEWORK4.md"
---

# PRD - FRAMEWORK4

> Este PRD reorganiza o escopo do FRAMEWORK3 em torno de **Features** (comportamentos entregáveis).
> O FRAMEWORK3 será arquivado como referência histórica.

**Intake de Origem**: [INTAKE-FRAMEWORK4.md](./INTAKE-FRAMEWORK4.md)

**Origem do Escopo**: [PRD-FRAMEWORK3.md](../FRAMEWORK3/PRD-FRAMEWORK3.md)

---

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-FRAMEWORK4.md](./INTAKE-FRAMEWORK4.md)
- **Versão do intake**: 1.0
- **Data de criação**: 2026-03-18
- **PRD de origem**: [PRD-FRAMEWORK3.md](../FRAMEWORK3/PRD-FRAMEWORK3.md)
- **Observação**: Este PRD mantém 100% do escopo do FRAMEWORK3, reorganizado em Features.

---

## 1. Resumo Executivo

- **Nome do projeto**: FRAMEWORK4 - Sistema CRUD + Orquestrador Feature-First
- **Tese em 1 frase**: Sistema CRUD + Orquestrador de Agentes para gestão automatizada de projetos, planejado com Features como eixo principal.
- **Valor esperado em 3 linhas**:
  1. Eliminar trabalho manual de cópia/renomeação de arquivos.
  2. Orquestrador de agentes que gerencia o fluxo Intake → PRD → Fases → Tasks.
  3. Persistir histórico para treinamento de LLM especialista.

---

## 2. Problema ou Oportunidade

- **Problema atual**: FRAMEWORK3 foi planejado no paradigma arquitetura-first. Precisa migrar para paradigma feature-first.
- **Evidência do problema**: Novo template de PRD em COMUM é feature-first.
- **Custo de não agir**: FRAMEWORK3 fica obsoleto.
- **Por que agora**: Novo paradigma está pronto para uso.

---

## 3. Público e Operadores

- **Usuário principal**: PM
- **Usuário secundário**: Engenheiros e agentes IA
- **Operador interno**: AgentOrchestrator + subagentes
- **Quem aprova**: PM

---

## 4. Jobs to be Done

- **Job principal**: Gestão automatizada de projetos (CRUD + Orquestrador)
- **Jobs secundários**:
  - Consultar status de projetos
  - Revisar histórico de decisões
  - Coletar dados para treinamento

---

## 5. Escopo

### Dentro

- Modelo de dados completo
- CRUD completo
- AgentOrchestrator
- Persistência de histórico
- Interface admin
- Modos de operação (HITL, autonomous)

### Fora

- Fine-tuning real
- Interface mobile

---

## 6. Resultado de Negócio e Métricas

- **Objetivo principal**: Same as FRAMEWORK3
- **Métricas leading**: Same as FRAMEWORK3
- **Métricas lagging**: Same as FRAMEWORK3

---

## 7. Restrições e Guardrails

- Mesmo stack técnico
- Compatibilidade com governança feature-first
- Coexistência com projetos legados

---

## 8. Dependências e Integrações

- Backend: FastAPI
- Banco: PostgreSQL
- Frontend: React/Vite
- Governança: GOV-*, TEMPLATE-*, SESSION-*

---

## 9. Arquitetura Geral do Projeto

- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Frontend**: Módulo admin no dashboard NPBB
- **Banco**: Novas tabelas (framework_project, framework_intake, etc.)
- **Orquestrador**: AgentOrchestrator service
- **Governança**: Arquivos GOV-* como fonte de verdade

---

## 10. Riscos Globais

- Risco de transição (garantir que nada se perca)
- Resistência a migrar de paradigma

---

## 11. Não-Objetivos

- Alterar escopo do sistema
- Fine-tuning real
- Abandonar governança feature-first

---

# 12. Features do Projeto

> **Este é o eixo principal do planejamento**. Cada feature representa um comportamento
> entregável. O escopo completo do FRAMEWORK3 está distribuído nestas Features.

---

## Feature 1: Gestão de Projetos

### Objetivo de Negócio

CRUD completo para gestão de projetos, intakes, PRDs, fases, épicos, sprints, issues e tasks.

### Comportamento Esperado

Usuário consegue criar, ler, atualizar e deletar projetos e todos os artefatos relacionados.

### Critérios de Aceite

- [ ] CRUD de projetos funcional
- [ ] CRUD de intakes e PRDs funcional
- [ ] CRUD de fases, épicos, sprints, issues e tasks funcional
- [ ] Rastreabilidade completa entre artefatos

### Dependências com Outras Features

- Feature 2 (requer AgentOrchestrator para automação)
- Feature 3 (armazena histórico)

### Riscos Específicos

- Manter compatibilidade com sistema Markdown existente

### Fases de Implementação

1. **Modelagem e Migration**: Criar tabelas framework_*
2. **API**: Endpoints CRUD para cada entidade
3. **UI**: Interface no módulo admin
4. **Testes**: Unitários e integração

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Tabelas | projects, intakes, prds, phases, epics, sprints, issues, tasks |
| Backend | Endpoints | /api/projects, /api/intakes, /api/prds, etc. |
| Frontend | Telas | Dashboard de projetos, formulários |
| Testes | Suítes | CRUD tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Criar models SQLModel | 3 | - |
| T2 | Criar migrations Alembic | 3 | T1 |
| T3 | Criar endpoints CRUD | 5 | T2 |
| T4 | Criar interface admin | 5 | T3 |
| T5 | Testes unitários | 3 | T4 |

---

## Feature 2: Orquestrador de Agentes

### Objetivo de Negócio

AgentOrchestrator central que gerencia o fluxo de projetos desde o intake até a execução de tasks.

### Comportamento Esperado

Sistema coordena subagentes para executar o fluxo completo: Intake → PRD → Fases → Épicos → Issues → Tasks.

### Critérios de Aceite

- [ ] Orquestrador gerencia fluxo completo
- [ ] Suporte a modos: HITL, semi-autonomous, fully autonomous
- [ ] Decisão de quando pedir aprovação humana
- [ ] Execução de tasks sequencialmente

### Dependências com Outras Features

- Feature 1 (gerencia entidades)
- Feature 3 (registra histórico)

### Riscos Específicos

- Complexidade do orquestrador
- Manter governança como fonte de verdade

### Fases de Implementação

1. **Modelagem**: Definir estados e transições
2. **API**: endpoints de controle
3. **Lógica**: Implementar máquina de estados
4. **Testes**: Integração

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Tabelas | agent_executions, work_orders |
| Backend | Serviço | AgentOrchestrator class |
| Frontend | Componentes | Status timeline, controles |
| Testes | Suítes | Orchestrator tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Definir estados e transições | 3 | - |
| T2 | Implementar AgentOrchestrator | 8 | T1 |
| T3 | Integrar com CRUD | 5 | T2, Feature 1.T3 |
| T4 | Testes de integração | 5 | T3 |

---

## Feature 3: Persistência para Treinamento

### Objetivo de Negócio

Registrar todo o histórico de prompts, decisões, aprovações e artefatos para criar dataset de treinamento.

### Comportamento Esperado

Sistema armazena e permite consultar histórico completo de execução.

### Critérios de Aceite

- [ ] Registro de prompts enviados
- [ ] Registro de outputs gerados
- [ ] Registro de aprovações humanas
- [ ] Registro de diffs e artefatos
- [ ] Consulta e export auditável

### Dependências com Outras Features

- Feature 1 (entidades)
- Feature 2 (execuções)

### Riscos Específicos

- Qualidade dos dados para treinamento
- Volume de dados

### Fases de Implementação

1. **Modelagem**: Tabela agent_execution
2. **API**: Endpoints de histórico
3. **UI**: Visualização de histórico
4. **Export**: Formato para treinamento

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Tabelas | agent_execution, audit_trail |
| Backend | Endpoints | /api/history, /api/export |
| Frontend | Telas | Visualizador de histórico |
| Testes | Suítes | History tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Criar tabela agent_execution | 3 | - |
| T2 | Implementar logging | 5 | T1 |
| T3 | API de consulta | 3 | T2 |
| T4 | Export para treinamento | 5 | T3 |

---

## Feature 4: Interface Admin

### Objetivo de Negócio

Módulo admin integrado ao dashboard NPBB para gestão de projetos.

### Comportamento Esperado

Usuário acessa interface web para criar e gerenciar projetos.

### Critérios de Aceite

- [ ] Dashboard de projetos
- [ ] Formulários de criação
- [ ] Visualização de status
- [ ] Controles de operação

### Dependências com Outras Features

- Feature 1 (CRUD)
- Feature 2 (orquestrador)

### Fases de Implementação

1. **Modelagem**: Layout de páginas
2. **Components**: Reutilizar existentes
3. **Pages**: Criar páginas admin
4. **Integração**: Conectar com API

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | N/A | - |
| Backend | N/A | - |
| Frontend | Páginas | /admin/projects, /admin/intakes |
| Testes | E2E | Admin flow tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Layout admin | 3 | - |
| T2 | Dashboard projetos | 5 | T1 |
| T3 | Formulários | 5 | T2 |
| T4 | Testes E2E | 3 | T3 |

---

## Feature 5: Modos de Operação

### Objetivo de Negócio

Suporte a diferentes níveis de autonomia: human-in-loop, semi-autonomous, fully autonomous.

### Comportamento Esperado

PM configura nível de autonomia por projeto; sistema respeita configuração.

### Critérios de Aceite

- [ ] Configuração por projeto
- [ ] Modo HITL: aprovações manuais
- [ ] Modo semi-autonomous: aprovações em gates críticos
- [ ] Modo fully autonomous: execução automática

### Dependências com Outras Features

- Feature 2 (orquestrador)

### Fases de Implementação

1. **Config**: Campo em project
2. **Lógica**: Interpretar configuração
3. **UI**: Controles de modo

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Campo | project.autonomy_level |
| Backend | Lógica | AutonomyResolver |
| Frontend | Input | Mode selector |
| Testes | Suítes | Autonomy tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Adicionar campo autonomy_level | 2 | - |
| T2 | Implementar lógica | 5 | T1 |
| T3 | UI de configuração | 3 | T2 |

---

## Feature 6: Auditoria de Fase

### Objetivo de Negócio

Processo formal de auditoria de fase com gates, vereditos e follow-ups.

### Comportamento Esperado

Sistema orquestra auditoria, registra vereditos e gerencia follow-ups.

### Critérios de Aceite

- [ ] Gate de auditoria (not_ready → pending → approved/hold)
- [ ] Vereditos: go, hold, cancelled
- [ ] Follow-ups: issue-local, new-intake
- [ ] Notificações

### Dependências com Outras Features

- Feature 1 (entidades)
- Feature 2 (orquestrador)

### Fases de Implementação

1. **Gate**: Máquina de estados
2. **Vereditos**: Lógica de julgamento
3. **Follow-ups**: Geração e rastreamento
4. **Notificações**: Alertas

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Tabelas | audit_logs, gates |
| Backend | Serviço | AuditOrchestrator |
| Frontend | UI | Audit dashboard |
| Testes | Suítes | Audit tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Estados de gate | 3 | - |
| T2 | Workflow de auditoria | 5 | T1 |
| T3 | Follow-ups | 5 | T2 |
| T4 | Notificações | 3 | T3 |

---

## Feature 7: Coexistência Legado

### Objetivo de Negócio

Sistema coexiste com estrutura Markdown atual; projetos legados continuam funcionando.

### Comportamento Esperado

Novos projetos usam sistema; antigos usam Markdown; migração gradual é possível.

### Critérios de Aceite

- [ ] Projetos novos usam banco
- [ ] Projetos legados usam Markdown
- [ ] Leitura de GOV-* como fonte de verdade
- [ ] Migração opcional

### Dependências com Outras Features

- Todas (suporta sistema híbrido)

### Fases de Implementação

1. **Leitura**: Parse de Markdown
2. **Sincronização**: Two-way sync
3. **Migração**: Ferramenta de conversão

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | Leitura | Parse MD to DB |
| Backend | Parser | MD parser |
| Frontend | N/A | - |
| Testes | Suítes | Sync tests |

### Tasks da Feature

| Task ID | Descrição | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Parser Markdown | 5 | - |
| T2 | Sincronização | 8 | T1 |
| T3 | Ferramenta migração | 5 | T2 |

---

# 13. Estrutura de Fases

> As Features são organizadas em Fases conforme dependências.

## Fase 1: Fundação

- **Objetivo**: Criar base de dados e CRUD
- **Features incluídas**:
  - Feature 1: Gestão de Projetos
- **Gate de saída**: CRUD funcional
- **Critérios de aceite**:
  - [ ] Todas as entities com CRUD
  - [ ] Dados persistidos corretamente

## Fase 2: Orquestração

- **Objetivo**: Implementar AgentOrchestrator
- **Features incluídas**:
  - Feature 2: Orquestrador de Agentes
  - Feature 5: Modos de Operação
- **Gate de saída**: Orquestrador funcional
- **Critérios de aceite**:
  - [ ] Fluxo completo funciona
  - [ ] Modos de operação configuráveis

## Fase 3: Histórico e Admin

- **Objetivo**: Persistência e Interface
- **Features incluídas**:
  - Feature 3: Persistência para Treinamento
  - Feature 4: Interface Admin
- **Gate de saída**: Sistema utilizável
- **Critérios de aceite**:
  - [ ] Histórico registrado
  - [ ] UI funcional

## Fase 4: Auditoria

- **Objetivo**: Processo de auditoria
- **Features incluídas**:
  - Feature 6: Auditoria de Fase
- **Gate de saída**: Auditorias funcionais
- **Critérios de aceite**:
  - [ ] Gates funcionam
  - [ ] Follow-ups gerenciados

## Fase 5: Coexistência

- **Objetivo**: Conviver com legado
- **Features incluídas**:
  - Feature 7: Coexistência Legado
- **Gate de saída**: Sistema completo
- **Critérios de aceite**:
  - [ ] Projetos legados funcionam
  - [ ] Migração disponível

---

# 14. Épicos

> Cada épico agrupa issues de uma Feature.

## Épico: Gestão de Projetos

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1: Gestão de Projetos
- **Objetivo**: CRUD completo de todas as entidades
- **SP Total**: 19

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F1-01-001 | Models e Migrations | 6 | todo | F1 |
| ISSUE-F1-01-002 | Endpoints CRUD | 5 | todo | F1 |
| ISSUE-F1-01-003 | Interface Admin | 5 | todo | F1 |
| ISSUE-F1-01-004 | Testes | 3 | todo | F1 |

## Épico: Orquestrador

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 2: Orquestrador de Agentes
- **Objetivo**: AgentOrchestrator funcional
- **SP Total**: 21

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F2-01-001 | Estados e Transições | 3 | todo | F2 |
| ISSUE-F2-01-002 | AgentOrchestrator | 8 | todo | F2 |
| ISSUE-F2-01-003 | Integração CRUD | 5 | todo | F2 |
| ISSUE-F2-01-004 | Testes Integração | 5 | todo | F2 |

## Épico: Histórico

- **ID**: EPIC-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 3: Persistência para Treinamento
- **Objetivo**: Histórico completo
- **SP Total**: 16

## Épico: Interface

- **ID**: EPIC-F3-02
- **Fase**: F3
- **Feature de Origem**: Feature 4: Interface Admin
- **Objetivo**: UI funcional
- **SP Total**: 16

## Épico: Modos

- **ID**: EPIC-F2-02
- **Fase**: F2
- **Feature de Origem**: Feature 5: Modos de Operação
- **Objetivo**: Autonomia configurável
- **SP Total**: 10

## Épico: Auditoria

- **ID**: EPIC-F4-01
- **Fase**: F4
- **Feature de Origem**: Feature 6: Auditoria de Fase
- **Objetivo**: Processo de auditoria
- **SP Total**: 16

## Épico: Coexistência

- **ID**: EPIC-F5-01
- **Fase**: F5
- **Feature de Origem**: Feature 7: Coexistência Legado
- **Objetivo**: Sistema híbrido
- **SP Total**: 18

---

# 15. Dependências Externas

| Dependência | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| FastAPI | Framework | existente | Backend | confirmado |
| PostgreSQL | Banco | existente | Persistência | confirmado |
| React/Vite | Frontend | existente | UI | confirmado |
| GOV-* docs | Docs | COMUM | Governança | confirmado |

---

# 16. Rollout e Comunicação

- **Estratégia de deploy**: Módulo interno, deploy incremental
- **Comunicação de mudanças**: Notificações internas
- **Treinamento necessário**: Documentação atualizada
- **Suporte pós-launch**: Suporte padrão

---

# 17. Revisões e Auditorias

- **Auditorias planejadas**: F1, F2, F3, F4, F5
- **Critérios de auditoria**: GOV-AUDITORIA.md
- **Threshold anti-monolito**: SPEC-ANTI-MONOLITO.md

---

# 18. Checklist de Prontidão

- [x] Intake referenciado e versão confirmada
- [x] Features definidas com critérios de aceite verificáveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Épicos criados e vinculados a Features
- [x] Fases definidas com gates de saída
- [x] Dependências externas mapeadas
- [x] Riscos identificados
- [x] Rollout planejado

---

# 19. Anexos e Referências

- [PRD-FRAMEWORK3.md](../FRAMEWORK3/PRD-FRAMEWORK3.md) - Escopo original
- [INTAKE-FRAMEWORK3.md](../FRAMEWORK3/INTAKE-FRAMEWORK3.md) - Intake original
- [GOV-FRAMEWORK-MASTER.md](../COMUM/GOV-FRAMEWORK-MASTER.md) - Governança
- [TEMPLATE-PRD.md](../COMUM/TEMPLATE-PRD.md) - Template feature-first
- [GOV-BRANCH-STRATEGY.md](../COMUM/GOV-BRANCH-STRATEGY.md) - Branch strategy

---

> **Frase Guia**: "Feature organiza, Task executa, Teste valida"
