---
doc_id: "PRD-FRAMEWORK3.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-17"
project: "FRAMEWORK3"
intake_origin: "INTAKE-FRAMEWORK3.md"
---

# PRD - FRAMEWORK3

**Intake de Origem**: [INTAKE-FRAMEWORK3.md](./INTAKE-FRAMEWORK3.md)
**Algoritmo de Negócio**: [PROJETOS/Algoritmo.md](../Algoritmo.md)

## 1. Objetivo e Contexto

Este PRD formaliza a implementação do projeto FRAMEWORK3: consolidar o framework de projetos atual em um **módulo CRUD + Orquestrador de Agentes** com banco de dados.

O objetivo principal é eliminar o trabalho manual repetitivo de copiar/renomear arquivos da pasta `COMUM/` e preencher cabeçalhos, transferindo mais responsabilidade para a IA via orquestrador e subagentes, enquanto mantém total obediência aos arquivos de governança existentes.

O algoritmo de negócio detalhado (passos 1-27) está em [PROJETOS/Algoritmo.md](../Algoritmo.md). Os passos até a aprovação de Tasks permanecem com gates humanos, a partir da execução de tasks (passo 16) o sistema deve ser altamente automatizado.

FRAMEWORK3 **coexiste** com a estrutura documental atual definida em [PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md](../COMUM/GOV-FRAMEWORK-MASTER.md) e [PROJETOS/COMUM/GOV-ISSUE-FIRST.md](../COMUM/GOV-ISSUE-FIRST.md).

## 2. Problema que Resolve

- Trabalho repetitivo de cópia/renomeação de arquivos Markdown
- Dependência excessiva de aprovações manuais ("sim" em cada passo)
- Falta de rastreabilidade centralizada e histórico estruturado
- Dificuldade de escalar o framework para mais projetos
- Perda de oportunidade de treinar um LLM especialista em gestão de projetos

## 3. Escopo

### Dentro do Escopo

- Módulo CRUD completo para gestão de projetos (`projects`, `intakes`, `prds`, `phases`, `epics`, `issues`, `tasks`)
- `AgentOrchestrator` central que gerencia o fluxo conforme o algoritmo fornecido
- Persistência completa do histórico de prompts, decisões, aprovações e artefatos (`agent_execution` table)
- Integração com governança existente (leitura de `GOV-*`, `SESSION-*`, `TEMPLATE-*`)
- Interface admin acoplada ao dashboard NPBB existente
- Suporte a modos de operação (human-in-loop, semi-autonomous, fully autonomous configurável por projeto)

### Fora do Escopo (Fase 1)

- Fine-tuning real do LLM
- Substituição total do sistema de arquivos Markdown (coexistência)
- Multi-tenancy avançado
- Interface mobile

## 4. Arquitetura

- **Backend**: FastAPI (mesmo stack do NPBB) + SQLModel + PostgreSQL
- **Banco**: Novas tabelas no schema existente (`framework_project`, `framework_intake`, etc.)
- **Orquestrador**: Serviço `AgentOrchestrator` que:
  - Lê governança canônica
  - Gera artefatos MD quando necessário
  - Registra todas as ações para treinamento
  - Decide quando pedir aprovação humana vs executar automaticamente
- **Frontend**: Módulo admin no React/Vite atual
- **Governança**: Continua sendo fonte de verdade (os arquivos `GOV-*` e `SESSION-*` não são removidos)

## 5. Fluxo Proposto (mapeamento do algoritmo do usuário)

O PRD implementa o algoritmo detalhado em [PROJETOS/Algoritmo.md](../Algoritmo.md):

**Fase de Planejamento (com gates humanos):**
1-2. Preenchimento e aprovação do Intake via formulário (usa [SESSION-CRIAR-INTAKE.md](../COMUM/SESSION-CRIAR-INTAKE.md))
3-4. Geração e aprovação do PRD
5-14. Geração sequencial de Fases → Épicos → Sprints → Issues → Tasks (com aprovações humanas)
15. Geração de instruções TDD

**Pipeline de Execução (altamente automatizado a partir do passo 16):**
- Orquestrador preenche [SESSION-IMPLEMENTAR-ISSUE.md](../COMUM/SESSION-IMPLEMENTAR-ISSUE.md) com contexto da task atual
- Subagentes executam tasks sequencialmente (T1, T2... até completar issue)
- Configuração automática de revisão usando [SESSION-REVISAR-ISSUE.md](../COMUM/SESSION-REVISAR-ISSUE.md)
- IA decide status da issue (aprovada/bloqueada/correção) conforme governança
- Ao final de fase: auditoria automática + notificação humana para holds
- Aplicação automática de soluções de hold

O `AgentOrchestrator` coordena subagentes e decide quando pedir aprovação humana conforme o modo configurado por projeto.

## 6. Requisitos Não Funcionais

- Manter **100% de compatibilidade** com projetos existentes
- Todo passo executado por agente deve ser auditável e versionado
- O sistema deve ser capaz de "sentir" o framework atual (ler `boot-prompt.md`, `GOV-*`, etc.)
- Preparação para dataset de treinamento (prompt + output + resultado + feedback humano)

## 7. Riscos e Mitigações

- **Risco**: Complexidade do orquestrador  
  **Mitigação**: Começar conservador (`human_in_loop` como default) e aumentar autonomia gradualmente.

- **Risco**: Quebra de projetos existentes  
  **Mitigação**: FRAMEWORK3 é um módulo adicional. Projetos antigos continuam usando o fluxo documental.

- **Risco**: Qualidade dos dados para treinamento  
  **Mitigação**: Registrar *todos* os passos com contexto rico.

## 8. Métricas de Sucesso

- Redução >70% no tempo manual para criar e gerenciar um projeto
- Pelo menos 5 projetos gerenciados via novo sistema
- Dataset com >1000 registros de execução de agente
- Usuário consegue configurar nível de autonomia por projeto

**Próximo passo recomendado**: Criar a primeira fase (F1 - Fundação do Módulo) com manifesto de épicos seguindo o template em `GOV-ISSUE-FIRST.md`.

---

**Referências**:
- Intake: `./INTAKE-FRAMEWORK3.md`
- Governança: `../COMUM/GOV-FRAMEWORK-MASTER.md`, `../COMUM/GOV-ISSUE-FIRST.md`, `../COMUM/GOV-SCRUM.md`
- Algoritmo do usuário: `../Algoritmo.md`

Este PRD está pronto para aprovação e início da implementação da F1.