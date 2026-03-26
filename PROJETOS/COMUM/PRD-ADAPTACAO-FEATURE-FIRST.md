---
doc_id: "PRD-ADAPTACAO-FEATURE-FIRST"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-18"
project: "COMUM"
intake_kind: "refactor"
source_mode: "original"
origin_project: "COMUM"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "interna"
integrations: []
change_type: "refactor"
audit_rigor: "standard"
---

# PRD - Adaptação do Framework para Modelo Delivery-First / Feature-First

> Este PRD propõe uma adequação mínima do framework de projetos, alterando o eixo principal de organização de "arquitetura-first" (banco/backend/frontend) para um principio `delivery-first`, materializado como `feature-first` no planejamento, sem abrir mão de nenhuma funcionalidade existente: fases, épicos, issues, tasks, sprints, storypoints, governança e atomicidade.

## 1. Resumo Executivo

- **Nome curto**: Adaptação Delivery-First do Framework
- **Tese em 1 frase**: O framework de projetos deve ser orientado a entregas de comportamento/valor (`delivery-first`), usando `feature-first` como forma canônica de planejamento em vez de camadas técnicas (`architecture-first`), mantendo toda a estrutura de governança, fases e atomicidade já existentes.
- **Valor esperado em 3 linhas**:
  - Eliminar risco de projeto "80% pronto" (banco ok, backend quase, frontend mockado)
  - Manter cascata Intake → PRD → Fase → Épico → Issue → Task → Teste
  - Preservar atomicidade e TDD-first, mas reorientados para comportamento

## 2. Problema ou Oportunidade

### Problema Atual

O framework atual, quando aplicado em projetos de código, apresenta um viés implícito de organização por camadas técnicas:

- **Eixo principal atual**: Banco → Backend → Frontend
- **PRD estruturado por**: modelos, endpoints, telas
- **Fases definidas por**: migração, API, UI
- **Tasks organizadas por**: criar tabela, criar endpoint, criar componente

### Evidência do Problema

1. **Risco de integração tardia**: Ao quebrar projetos por camada técnica, o risco é:
   - Backend esperando migration estabilizar
   - Frontend mockando API por tempo demais
   - Merge complexo no final
   - Feature "80% pronta em 3 lugares e pronta em nenhum"

2. **Falsa sensação de progresso**: Muito progresso no Jira (3 branches avançando), pouca coisa funcionando.

3. **Atomicidade Técnica vs Atomicidade de Comportamento**:
   - Atual: "criar tabela users", "criar endpoint POST /users", "criar tela cadastro"
   - Problema: isso é técnico, não entrega valor utilizável

4. **Dependência Cruzada**: Fase de banco bloqueia fase de backend que bloqueia fase de frontend, criando fila artificial.

### Custo de Não Agir

- Continuar gerando projetos com alto risco de integração
- Manter atomicidade tecnicamente correta mas sem valor de entrega demonstrável
- Dificultar priorização por valor de negócio

### Por Que Agora

O framework já está maduro o suficiente (versão 2.x em múltiplos documentos GOV) para passar por uma adequação de eixo sem quebrar a estrutura existente.

## 3. Público e Operadores

- **Usuario principal**: PMs e IAs que utilizam o framework para planejar e executar projetos
- **Usuario secundario**: Desenvolvedores que follow-up de issues e executam tasks
- **Operador interno**: Framework himself
- **Quem aprova**: Mantenedor do framework

## 4. Jobs to be Done

- **Job principal**: Planejar projetos de código com clareza de entrega, não apenas de estrutura técnica
- **Jobs secundarios**:
  - Manter governança existente (fases, épicos, sprints, storypoints)
  - Manter atomicidade e TDD-first
  - Evitar dependência artificial entre camadas
  - Permitir demonstração de valor a cada milestone

## 5. Fluxo Principal Desejado

O fluxo atual é:

```
Intake → PRD → Fases → Épicos → Issues → Tasks → Auditorias
```

Este PRD propõe explicitar uma etapa conceitual intermediaria e reinterpretar o eixo de organizacao:

```
Intake → Sintese conceitual → PRD (Feature-Oriented) → Fases → Épicos → Issues → Tasks → Auditorias
```

## 6. Escopo Inicial

### Dentro

1. **Formalizar a Síntese como etapa conceitual** (entre Intake e PRD)
   - Objetivo: organizar o problema, delimitar escopo, identificar blocos de valor (features candidatas)
   - Não cria novo artefato canônico obrigatório; pode viver como parte da análise de criação do PRD

2. **Reinterpretar eixo do PRD**
   - De: "Arquitetura (Banco/Backend/Frontend)" como organizacao principal
   - Para: "Features" como organizacao principal, com arquitetura como impacto

3. **Manter todas as estruturas existentes**:
   - Fases (F1, F2...)
   - Épicos (dentro de fases)
   - Issues (dentro de épicos)
   - Tasks (dentro de issues)
   - Sprints
   - Storypoints (SP)
   - Auditorias
   - Cascata de fechamento

4. **Atualizar templates**:
   - `TEMPLATE-INTAKE.md`: manter como está
   - `TEMPLATE-PRD.md`: adicionar seção de Features como organizaçao principal
   - template de épico em `GOV-ISSUE-FIRST.md`: adicionar "Feature de Origem" como campo
   - template de issue em `GOV-ISSUE-FIRST.md`: clarificar que task atômica = menor unidade testável de comportamento e manter rastreabilidade de feature

5. **Branch Strategy**:
   - Manter branch por feature, não por camada
   - Documentar em `GOV-BRANCH-STRATEGY.md` (novo)

### Fora

- Consolidar a cadeia principal de governanca em `Intake -> PRD -> Features -> User Stories -> Tasks -> Revisao -> Auditoria de Feature`
- Não alterar limites de sprint (GOV-SPRINT-LIMITES)
- Não alterar spec de task instructions (SPEC-TASK-INSTRUCTIONS)
- Não forçar retrofit em projetos existentes

## 7. Resultado de Negocio e Métricas

- **Objetivo principal**: Framework orientado a entrega de valor, não a estrutura técnica
- **Métricas leading**:
  - Toda issue consegue responder: "qual comportamento isso prova?"
  - Toda task consegue ser demonstrada como ação do usuário
- **Métricas lagging**:
  - Redução de projetos com status "80% pronto" sem entrega utilizável
  - Clareza de DoD por comportamento, não por técnica
- **Critério mínimo para considerar sucesso**:
  - Novo template de PRD com Features como eixo
  - Documentação de Síntese conceitual disponível
  - Branch strategy documentada

## 8. Restrições e Guardrails

- **Restrições técnicas**:
  - Não pode quebrar retrocompatibilidade com artefatos existentes
  - Não pode alterar schema de status canonicos
- **Restrições operacionais**:
  - Projetos em andamento não precisam ser retroativos
  - Issue-first permanece como modo canônico
- **Restrições de governança**:
  - A cadeia principal do framework permanece intacta
  - Apenas artefatos diretamente ligados a criacao de PRD, planejamento e branch strategy podem ser atualizados
  - Cascata Intake→PRD→Fases→Épicos→Issues→Tasks→Auditorias permanece
  - Storypoints e limites de sprint permanecem

## 9. Dependências e Integrações

- **Sistemas internos impactados**: Fluxo documental do framework
- **Sistemas externos impactados**: Nenhum
- **Dados de entrada necessários**: Framework atual em PROJETOS/COMUM/
- **Dados de saída esperados**: Templates e documentos atualizados

## 10. Arquitetura Afetada

- **Backend**: N/A
- **Frontend**: N/A
- **Banco/migracoes**: N/A
- **Observabilidade**: N/A
- **Autorizacao/autenticacao**: N/A
- **Rollout**: N/A

## 11. Riscos Relevantes

- **Risco de produto**: Resistência à mudança de mentalidade
- **Risco técnico**: Nenhum (apenas documentação)
- **Risco operacional**: Conflito com projetos que já usam o modelo atual
- **Risco de dados**: Nenhum
- **Risco de adoção**: Baixa se não houver exemplificação clara

## 12. Não-Objetivos

- Não criar nova etapa documental obrigatória entre Intake e PRD
- Não forçar retrofit em projetos existentes
- Não alterar a cadeia de governança
- Não modificar limites de sprint ou storypoints
- Não abandonar a atomicidade (apenas reinterpretá-la)

## 13. Síntese: Features e Organização por Comportamento

### Conceito de Síntese

A **Síntese** é uma etapa conceitual (não obrigatória como documento) que ocorre na transição Intake → PRD:

1. **Intake** responde: "qual problema existe?"
2. **Síntese** organiza: "como podemos recortar este problema em blocos de valor?"
3. **PRD** decide: "quais features compõem este projeto?"

### Features como Eixo do PRD

Cada **Feature** no PRD deve representar:

- Um comportamento entregável e demonstrável
- Uma unidade de valor para o usuário
- Um recorte que faz sentido completo (banco + backend + frontend + teste)

**Estrutura Proposta**:

```markdown
## Features do Projeto

### Feature 1: <Nome da Feature>
- **Objetivo de negocio**: <o que resolve>
- **Comportamento esperado**: <o que o usuario consegue fazer>
- **Critério de aceite**: <como validar que está pronto>
- **Fases de implementação**:
  1. Modelagem e migration
  2. API
  3. UI
  4. Testes

### Impacts (não é o eixo, é detalhe):
- Banco: <tabelas impactadas>
- Backend: <endpoints>
- Frontend: <telas>
```

### Exemplo: Feature vs Arquitetura

| Arquitetura-First (Atual) | Feature-First (Proposto) |
|---|---|
| Criar tabela users | Usuário consegue se cadastrar |
| Criar endpoint POST /users | (integrado à feature) |
| Criar tela de cadastro | (integrado à feature) |
| Validar email no backend | (integrado à feature) |

### Impacto na Atomicidade

**Atomicidade boa é orientada a comportamento, não a camada**:

- **Atomicidade atual** (técnica): criar tabela, criar endpoint, criar tela
- **Atomicidade correta** (comportamento): usuário consegue se cadastrar com email válido

Mantendo a estrutura de task:

```markdown
Feature: Cadastro de usuário

Tarefas atômicas:
- validar formato de email
- persistir usuário
- retornar erro se duplicado
- exibir mensagem de sucesso

Testes:
- deve aceitar email válido
- deve rejeitar email inválido
- não deve permitir duplicado
```

## 14. Proposta de Alteração: Template de PRD

### Estrutura Proposta para PRD

O template de PRD deve manter toda a estrutura existente, mas reorganizar o eixo:

```markdown
# PRD - <PROJETO>

> ... (seções existentes inalteradas) ...

## Features do Projeto

> Este é o eixo principal do planejamento. Cada feature representa um comportamento
> entregável. Arquitetura (banco/backend/frontend) aparece como impacto de cada feature,
> não como organização principal.

### Feature N: <Nome da Feature>

- **Objetivo de negócio**: <descrição>
- **Comportamento esperado**: <o que o usuário consegue fazer>
- **Critérios de aceite**: <lista verificável>
- **Dependências com outras features**: <se houver>
- **Riscos específicos**: <se houver>

#### Impacts por Feature

| Camada | Impacto |
|---|---|
| Banco | <tabelas> |
| Backend | <endpoints> |
| Frontend | <telas> |

#### Tarefas por Feature

> Cada feature decompõe em tasks que mantêm a atomicidade de comportamento:

| Task | Descrição | SP |
|---|---|---|
| T1 | <ação atômica> | 2 |

---

## Estrutura de Fases (mantida)

> ... (seções existentes inalteradas) ...

## Épicos (mantido)

> ... (seções existentes inalteradas) ...
```

## 15. Proposta de Alteração: Template de Épico

Adicionar campo para rastrear feature de origem no template definido em `GOV-ISSUE-FIRST.md`:

```markdown
## Feature de Origem

- **Feature**: <ID da Feature no PRD>
- **Comportamento coberto**: <resumo>
```

## 16. Proposta: Branch Strategy

Criar `GOV-BRANCH-STRATEGY.md`:

### Regra Principal

**Branch por feature, não por camada**:

- ❌ `feature/backend-login`
- ❌ `feature/frontend-login`
- ❌ `feature/database-login`
- ✅ `feature/feature-2-login`

### Dentro de Cada Branch Feature

Entram:
- Migration/banco
- Endpoint/backend
- Tela/frontend
- Testes

### Branches Técnicas Separadas (Exceção)

Apenas para fundações compartilhadas genuinamente transversais:
- `infra/schema-base`
- `infra/auth-core`
- `infra/design-system`

## 17. Checklist de Prontidão para Implementação

- [ ] Template de PRD atualizado com Features como eixo
- [ ] GOV-BRANCH-STRATEGY.md criado
- [ ] `SESSION-CRIAR-PRD.md` e `PROMPT-INTAKE-PARA-PRD.md` atualizados
- [ ] Template de Épico/Issue em `GOV-ISSUE-FIRST.md` atualizado com rastreabilidade de feature
- [ ] Guideline de Síntese conceitual documentado
- [ ] Este PRD aprovado

## 18. Lacunas Conhecidas

- Exemplos práticos de como converter projeto existente (não é objetivo do MVP)
- Casos de projetos multi-tenancy onde features atravessam domínios
- Integração com ferramentas de gestão (Jira, Linear) - fora escopo

## 19. Decisoes Operacionais

1. O template de PRD atual suporta a reorganizacao sem quebrar a compatibilidade, desde que `Features do Projeto` vire o eixo principal e a rastreabilidade para fases/epicos/issues seja explicitada.
2. Trabalho puramente de infraestrutura compartilhada continua sendo excecao documentada em `GOV-BRANCH-STRATEGY.md`; isso nao autoriza o PRD a voltar para organizacao por camada.

## 20. Resumo de Impacto por Artefato

| Artefato | Ação |
|---|---|
| GOV-FRAMEWORK-MASTER.md | Atualizar fonte de verdade |
| boot-prompt.md | Incluir branch strategy na leitura obrigatoria |
| GOV-ISSUE-FIRST.md | Adicionar rastreabilidade de feature em epico e issue |
| GOV-SPRINT-LIMITES.md | Inalterado |
| GOV-SCRUM.md | Inalterado |
| GOV-INTAKE.md | Inalterado |
| GOV-AUDITORIA.md | Inalterado |
| SPEC-TASK-INSTRUCTIONS.md | Inalterado |
| SESSION-CRIAR-PRD.md | Exigir `TEMPLATE-PRD.md` e PRD orientado a feature |
| PROMPT-INTAKE-PARA-PRD.md | Exigir `Features do Projeto` e rastreabilidade minima |
| SESSION-PLANEJAR-PROJETO.md | Exigir PRD com features como eixo para decomposicao |
| TEMPLATE-INTAKE.md | Inalterado |
| TEMPLATE-PRD.md | Atualizar para `delivery-first` / `feature-first` |
| GOV-BRANCH-STRATEGY.md | Criar e incluir na leitura obrigatoria |

---

## Regra de Ouro

> "Se eu pegar qualquer item e perguntar: 'isso entrega algo utilizável?', se a resposta for não → estrutura errada, se for sim → você acertou."

---

## Frase Guia do Framework

> **"Intake descobre, Sintese organiza, PRD decide, Feature orienta, Task executa, Teste valida"**
