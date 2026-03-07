# Framework de Projetos Scrum — Referência Canônica
> Documento legado em duplicidade. Para novos projetos e para o fluxo `issue-first`, use `PROJETOS/COMUM/scrum-framework-master.md` como fonte canônica.

**Arquivo:** `PROJETOS/COMUM/FRAMEWORK-REF.md`  
**Versão:** 1.0.0 | **Data:** 2026-03-03  
**Agente executor:** OpenClaw Agent OS  
**Status:** aprovado

> Este é o único documento de referência do framework. Todos os outros arquivos em `PROJETOS/COMUM/` são contratos normativos complementares que este documento orquestra. Em caso de conflito, este arquivo prevalece sobre qualquer arquivo de projeto individual.

---

## PARTE 1 — SCRUM-GOV: Governança do Processo

### 1.1 Hierarquia de Autoridade

```
FRAMEWORK-REF.md  (este arquivo — normativo máximo)
    └── SCRUM-GOV.md          (regras do processo)
    └── DECISION-PROTOCOL.md  (como decidir e registrar decisões)
    └── SPRINT-LIMITS.md      (limites operacionais por sprint)
    └── WORK-ORDER-SPEC.md    (contratos de work order para OpenClaw)
         └── PRD-<PROJETO>.md (normativo do projeto)
              └── <FN>_<PROJETO>_EPICS.md  (normativo da fase)
                   └── EPIC-FN-NN-<NOME>.md (normativo do épico)
```

Em conflito entre documentos do mesmo nível, o mais recente (por `version` + `last_updated`) prevalece.

### 1.2 Papéis

| Papel | Quem | Responsabilidade |
|---|---|---|
| **Product Owner (PO)** | Humano | Aprova PRD, aprova go/no-go de fase, resolve conflitos de escopo |
| **Engenheiro** | Humano ou OpenClaw | Executa issues, produz código e documentação |
| **Revisor de Fase** | OpenClaw (PROMPT-05) | Verifica DoD antes de avançar fase |
| **Árbitro de Decisão** | PO + DECISION-PROTOCOL | Ratifica decisões com impacto normativo |

### 1.3 Cerimônias Mínimas

| Cerimônia | Trigger | Responsável | Output |
|---|---|---|---|
| **Planejamento de Fase** | Início de cada fase | PO + OpenClaw | `<FN>_<PROJETO>_EPICS.md` aprovado |
| **Planejamento de Épico** | Antes de iniciar épico | OpenClaw (PROMPT-03) | `EPIC-FN-NN.md` com issues + tarefas |
| **Execução de Issue** | Sprint ativo | OpenClaw (PROMPT-04) | Código/doc + status ✅ no épico |
| **Review de Fase** | Último épico concluído | OpenClaw (PROMPT-05) | Parecer go/no-go documentado |

### 1.4 Regras de Processo

1. **Fases são portões:** F<N+1> só inicia após go explícito na review de F<N>.
2. **PRD é imutável durante uma fase.** Mudanças de escopo só são válidas entre fases, com bump de versão e entrada no DECISION-PROTOCOL.
3. **Issues concluídas não voltam ao backlog.** Retrabalho vira nova issue.
4. **Toda issue executada pelo OpenClaw requer confirmação HITL** antes de commit em repositório de produção.
5. **Épicos cancelados vão para `feito/` com status 🗑️** e nota de justificativa.
6. **Nenhum épico pode ser criado fora do ciclo de planejamento de fase** sem ADR registrado.

---

## PARTE 2 — DECISION-PROTOCOL: Como Decidir e Registrar

### 2.1 Gatilhos Obrigatórios para Registro de Decisão

Qualquer uma das situações abaixo exige um registro formal em `DECISION-PROTOCOL.md` do projeto:

- Mudança de stack, framework ou biblioteca relevante
- Mudança de escopo (adicionar ou remover funcionalidade do PRD)
- Criação de dependência entre projetos ou entre fases
- Decisão que contradiz uma decisão anterior registrada
- Decisão de segurança (autenticação, autorização, dados sensíveis)
- Decisão arquitetural com impacto em mais de um épico

### 2.2 Formato de Registro de Decisão

```markdown
## DECISÃO-<PROJETO>-<NNN>
**Data:** YYYY-MM-DD
**Status:** proposta | aprovada | deprecada
**Contexto:** <o que motivou esta decisão — 2–4 frases>
**Decisão:** <o que foi decidido — 1–2 frases diretas>
**Alternativas consideradas:**
- Alternativa A: <e por que foi rejeitada>
- Alternativa B: <e por que foi rejeitada>
**Consequências:** <o que muda no projeto com esta decisão>
**Aprovada por:** <nome do PO ou responsável>
**Referências:** <links, PRD section, ADR, etc.>
```

### 2.3 Processo de Aprovação

```
OpenClaw identifica necessidade de decisão
    │
    ▼
OpenClaw propõe decisão em formato DECISÃO-XXX-NNN (status: proposta)
    │
    ▼ HITL obrigatório
PO aprova, rejeita ou solicita ajuste
    │
    ▼
Status atualizado para "aprovada" e arquivo commitado
```

**Regra:** OpenClaw nunca implementa uma decisão com status `proposta`. Implementação só começa após status `aprovada`.

---

## PARTE 3 — SPRINT-LIMITS: Limites Operacionais

### 3.1 Limites por Sprint

| Dimensão | Limite | Observação |
|---|---|---|
| Duração do sprint | 1 semana | Ajustável por projeto no PRD |
| Story Points por sprint | 13 SP | Hard limit — não negociável |
| Issues por sprint | ≤ 5 | Foco e terminalidade |
| Épicos ativos simultaneamente | 1 por fase | Paralelismo só com aprovação explícita |
| Tarefas por issue | ≤ 8 | Se ultrapassar, a issue deve ser decomposta |
| SP máximo por issue | 5 SP | Issues ≥ 8 SP devem ser divididas |

### 3.2 Escala de Story Points

| SP | Complexidade | Critério |
|---|---|---|
| 1 | Trivial | < 30 min; mudança pontual, sem risco |
| 2 | Simples | 30–90 min; bem compreendido, sem surpresas |
| 3 | Médio | 2–4h; alguma investigação necessária |
| 5 | Complexo | 4–8h; múltiplas partes envolvidas |
| 8 | Muito complexo | 1–2 dias; considerar dividir |
| 13 | Épico disfarçado | **Obrigatório dividir antes de executar** |

### 3.3 Critério de Divisão de Issue

Uma issue **deve** ser dividida quando qualquer uma das condições for verdadeira:
- Estimativa ≥ 8 SP
- Possui mais de 8 tarefas
- Toca mais de 2 camadas arquiteturais (ex: banco + API + UI)
- Tem mais de 3 critérios de aceitação independentes entre si

### 3.4 Princípios de Código

Antes de escrever código, pensar na arquitetura. Priorizar:
- **Modularidade:** responsabilidade única por módulo/função; evitar arquivos e funções monolíticas
- **Manutenibilidade:** legibilidade, nomes claros, baixo acoplamento, alta coesão
- **Boas práticas:** DRY, separação de concerns, testabilidade, extensibilidade sem quebrar o existente

Código que cresce sem estrutura vira dívida técnica. O engenheiro deve aplicar esses princípios em toda implementação.

---

## PARTE 4 — WORK-ORDER-SPEC: Contrato de Work Order para OpenClaw

### 4.1 O que é uma Work Order

Uma Work Order é o contrato formal entre o operador humano e o OpenClaw para executar um prompt do framework. Ela garante que o OpenClaw saiba exatamente: **o que fazer, com quais fontes, qual o output esperado, e onde pedir aprovação humana.**

### 4.2 Estrutura de Work Order

```yaml
# work-order: <ID único>
work_order_id: WO-<PROJETO>-<YYYY-MM-DD>-<SEQ>
prompt:        PROMPT-<NN>   # qual prompt do framework executar
modelo:        openrouter-main | openrouter-review  # ver seção 4.4
workspace:     workspaces/main
projeto:       <NOME-DO-PROJETO>
fase:          F<N>-<NOME>
epico:         EPIC-F<N>-<NN>-<NOME>   # omitir se não aplicável
issue:         <ISSUE-ID>              # omitir se não aplicável

fontes:
  - PROJETOS/COMUM/FRAMEWORK-REF.md
  - PROJETOS/<PROJETO>/PRD-<PROJETO>.md
  - PROJETOS/<PROJETO>/F<N>-<FASE>/<FN>_<PROJETO>_EPICS.md
  - PROJETOS/<PROJETO>/F<N>-<FASE>/EPIC-F<N>-<NN>-<NOME>.md  # se aplicável

output:
  tipo:    arquivo | codigo | relatorio
  caminho: PROJETOS/<PROJETO>/F<N>-<FASE>/<NOME-DO-ARQUIVO>.md
  acao:    criar | atualizar | revisar

hitl:
  requer_aprovacao: true | false
  ponto_de_parada:  antes_do_output | apos_rascunho | nao_aplicavel
  canal:            telegram | slack
```

### 4.2-A Estratégia de Agente por EPIC (Cloud Agent)

**Regra:** um Cloud Agent por EPIC. Não um agente por fase, não um agente por projeto.

| Escopo | Agente | Justificativa |
|---|---|---|
| 1 EPIC | ✅ 1 Cloud Agent | Escopo isolado, branch única, PR revisável |
| 1 Fase inteira | ❌ Não usar | Contexto grande demais, falhas afetam múltiplos épicos |
| 1 Issue | ⚠️ Somente se a issue for trivial (SP=1) | Overhead de VM desnecessário |

**Fluxo padrão por EPIC:**
1. Abrir `PROJETOS/<PROJETO>/F<N>-<FASE>/PROMPT-EPIC-FN-NN.md`
2. Copiar conteúdo completo → colar no Cloud Agent (`Ctrl+E`)
3. Selecionar branch `main` como partida
4. Aguardar PR → revisar → merge
5. Só então disparar o agente do próximo EPIC

**Arquivos que cada agente DEVE ler primeiro (obrigatório em todo prompt):**
1. `AGENTS.md` — gotchas de ambiente
2. `PRD-<PROJETO>.md` — normativo
3. `EPIC-FN-NN-<NOME>.md` — escopo do trabalho
4. Arquivos de código referenciados no EPIC

### 4.3 Checkpoints HITL por Tipo de Prompt

| Prompt | Checkpoint HITL | Motivo |
|---|---|---|
| PROMPT-01 (PRD → Fases) | **Obrigatório — antes de salvar** | Fases têm impacto normativo alto |
| PROMPT-02 (Fase → Épicos) | **Obrigatório — antes de salvar** | Épicos vinculam sprint planning |
| PROMPT-03 (Épico → Issues) | Recomendado — após rascunho | Issues guiam execução direta |
| PROMPT-04 (Execução de Issue) | **Obrigatório — antes de commit** | Código em produção |
| PROMPT-05 (Review de Fase) | **Obrigatório — go/no-go** | Libera próxima fase |

### 4.4 Roteamento de Modelo por Tipo de Tarefa

| Tarefa | Modelo | Justificativa |
|---|---|---|
| Decomposição de PRD em fases | `openrouter-review` | Decisão normativa de alto impacto |
| Planejamento de épicos | `openrouter-review` | Impacto em múltiplos sprints |
| Detalhamento de issues/tarefas | `openrouter-main` | Operacional, iterativo |
| Execução de issue (código) | `openrouter-main` | Day-to-day |
| Review de fase / DoD | `openrouter-review` | Avaliação crítica |
| Fallback (cloud indisponível) | `local-fallback-7b` | Apenas tarefas não críticas |

---

## PARTE 5 — Estrutura de Arquivos e Nomenclatura

### 5.1 Estrutura Canônica

```
PROJETOS/
├── COMUM/
│   ├── FRAMEWORK-REF.md          ← este arquivo
│   ├── SCRUM-GOV.md              ← extrato da Parte 1 (standalone)
│   ├── DECISION-PROTOCOL.md      ← extrato da Parte 2 (standalone)
│   ├── SPRINT-LIMITS.md          ← extrato da Parte 3 (standalone)
│   └── WORK-ORDER-SPEC.md        ← extrato da Parte 4 (standalone)
│
└── <NOME-DO-PROJETO>/
    ├── PRD-<NOME-DO-PROJETO>.md
    ├── DECISION-PROTOCOL.md      ← decisões específicas do projeto
    ├── feito/                    ← épicos/issues arquivados
    │
    ├── F1-<NOME-DA-FASE>/
    │   ├── F1_<PROJETO>_EPICS.md
    │   ├── EPIC-F1-01-<NOME>.md
    │   └── EPIC-F1-02-<NOME>.md
    │
    └── F2-<NOME-DA-FASE>/
        ├── F2_<PROJETO>_EPICS.md
        └── EPIC-F2-01-<NOME>.md
```

### 5.2 Convenção de Nomenclatura

| Artefato | Padrão | Exemplo |
|---|---|---|
| Pasta de projeto | `<NOME-MAIUSCULO-HIFENS>` | `MIGRACAO-VPS-HOSTINGER` |
| Pasta de fase | `F<N>-<NOME-MAIUSCULO-HIFENS>` | `F3-REFATORACAO-CLI` |
| Arquivo de épicos | `F<N>_<PROJETO-UNDERLINE>_EPICS.md` | `F3_LEAD_ETL_FUSION_EPICS.md` |
| Arquivo de épico | `EPIC-F<N>-<NN>-<NOME-HIFENS>.md` | `EPIC-F3-02-REMOCAO-DUPLICACOES.md` |
| ID de issue | `<PROJ>-F<N>-<NN>-<MMM>` | `ETL-F3-02-004` |
| ID de tarefa | `<ISSUE-ID>-T<N>` | `ETL-F3-02-004-T2` |
| Work Order | `WO-<PROJ>-<YYYY-MM-DD>-<SEQ>` | `WO-ETL-2026-03-03-001` |

### 5.3 Legenda de Status

| Símbolo | Significado |
|---|---|
| 🔲 | Backlog — não iniciado |
| 🔄 | Em andamento |
| ⏸️ | Bloqueado (motivo obrigatório) |
| ✅ | Concluído e validado |
| 🗑️ | Cancelado (justificativa obrigatória) |

---

## PARTE 6 — Templates

### 6.1 Template: PRD-\<PROJETO\>.md

```markdown
# PRD — <Nome do Projeto>
**version:** 1.0.0 | **last_updated:** YYYY-MM-DD
**status:** rascunho | em revisão | aprovado
**owner:** <nome>

---
## 1. Visão do Produto
## 2. Objetivo Central e Resultado Mensurável
## 3. Contexto e Motivação
## 4. Escopo
### Dentro do escopo
### Fora do escopo (explícito)
## 5. Requisitos Funcionais
| ID | Requisito | Prioridade | Status |
|---|---|---|---|
| RF-01 | | Must | 🔲 |
## 6. Requisitos Não-Funcionais
| ID | Requisito | Meta |
|---|---|---|
## 7. Stack e Decisões Técnicas Vinculantes
## 8. Fases Previstas
| Fase | Nome | Objetivo | DoD resumido | Status |
|---|---|---|---|---|
## 9. Definition of Done do Projeto
## 10. Riscos Principais
## 11. Dependências Externas
## 12. Glossário
```

### 6.2 Template: F\<N\>\_\<PROJETO\>\_EPICS.md

```markdown
# Épicos — <Projeto> / F<N> — <Nome da Fase>
**version:** 1.0.0 | **last_updated:** YYYY-MM-DD
**projeto:** <Nome> | **fase:** F<N>
**prd:** ../PRD-<PROJETO>.md
**status:** rascunho | aprovado

---
## Objetivo da Fase
## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F<N>-01 | | | nenhuma | 🔲 | `EPIC-F<N>-01-<NOME>.md` |

## Dependências entre Épicos
## Definition of Done da Fase
- [ ]
## Notas e Restrições
```

### 6.3 Template: EPIC-F\<N\>-\<NN\>-\<NOME\>.md

```markdown
# EPIC-F<N>-<NN> — <Nome do Épico>
**version:** 1.0.0 | **last_updated:** YYYY-MM-DD
**projeto:** <Nome> | **fase:** F<N> | **status:** 🔲

---
## 1. Resumo do Épico
## 2. Contexto Arquitetural
## 3. Riscos e Armadilhas
## 4. Definition of Done do Épico
- [ ]

---
## Issues

### <PROJ>-F<N>-<NN>-001 — <Título>
**tipo:** feature | refactor | bugfix | docs | infra
**sp:** <N> | **prioridade:** alta | média | baixa | **status:** 🔲
**depende de:** (issue ID ou nenhuma)

**Descrição:**

**Critérios de Aceitação:**
- [ ] AC-1:

**Tarefas:**
- [ ] T1:
- [ ] T2:

**Notas técnicas:**

---
### <PROJ>-F<N>-<NN>-002 — <Título>
<!-- repetir bloco -->
```

---

## PARTE 7 — Prompts Canônicos do OpenClaw

> Cada prompt é uma Work Order semi-estruturada. O OpenClaw lê o prompt, carrega as fontes indicadas e produz o output no caminho especificado. **O bloco `## Parâmetros desta instância` é o único que muda entre execuções.**

---

### PROMPT-01 — PRD → Estrutura de Fases

**Work Order tipo:** planejamento normativo  
**Modelo:** `openrouter-review`  
**HITL:** obrigatório antes de salvar

```
Você é o OpenClaw atuando como engenheiro sênior e PM técnico.

Sua tarefa é ler o PRD do projeto indicado e propor a estrutura completa de fases de desenvolvimento.

Fontes de verdade (carregue e respeite):
- PRD: {{prd_path}}
- Governança: PROJETOS/COMUM/FRAMEWORK-REF.md (Partes 1, 3)
- Protocolo de decisão: PROJETOS/COMUM/FRAMEWORK-REF.md (Parte 2)

Regras não negociáveis:
- Cada fase: objetivo único, entregável verificável, DoD testável
- Nomenclatura: F<N>-<NOME-MAIUSCULO-HIFENS>
- Fases sequenciais por padrão; paralelismo exige justificativa
- Nenhuma fase pode contradizer o escopo do PRD

Estrutura obrigatória da resposta:
1. Leitura do objetivo central do PRD (confirmação em 1–2 frases)
2. Quantidade de fases e justificativa da granularidade
3. Para cada fase:
   a. ID e nome
   b. Objetivo (1 frase)
   c. Entregável principal verificável
   d. Dependência da fase anterior
   e. Definition of Done (lista de critérios testáveis)
4. Mapa de dependências entre fases (ASCII)
5. Riscos de sequenciamento identificados
6. Atualizar tabela "Fases Previstas" no PRD com as fases propostas

Output: atualização da seção "Fases Previstas" no PRD + resposta estruturada acima.
HITL: aguardar aprovação do PO antes de salvar qualquer alteração no PRD.

## Parâmetros desta instância
prd_path:      PROJETOS/{{projeto}}/PRD-{{projeto}}.md
projeto:       {{NOME-DO-PROJETO}}
observacoes:   {{restrições adicionais ou contexto}}
```

---

### PROMPT-02 — Fase → Arquivo de Épicos

**Work Order tipo:** planejamento de fase  
**Modelo:** `openrouter-review`  
**HITL:** obrigatório antes de salvar

```
Você é o OpenClaw atuando como engenheiro sênior.

Sua tarefa é ler o PRD e o objetivo da fase indicada e produzir o arquivo de épicos completo.

Fontes de verdade (carregue e respeite):
- PRD: {{prd_path}}
- Governança: PROJETOS/COMUM/FRAMEWORK-REF.md (Partes 1, 3, 5)
- Sprint limits: PROJETOS/COMUM/FRAMEWORK-REF.md (Parte 3)

Regras não negociáveis:
- Cada épico: escopo único, uma responsabilidade técnica
- Épicos paralelos só com dependência declarada como "nenhuma"
- Nenhum épico cria acoplamento não previsto no PRD
- Arquivo de saída: F<N>_<PROJETO>_EPICS.md (template da Parte 6.2)
- Todo épico deve ter DoD com critérios testáveis

Estrutura obrigatória da resposta (Markdown puro, pronto para salvar):
1. Cabeçalho completo (template 6.2)
2. Objetivo da fase (2–3 frases)
3. Para cada épico:
   a. ID: EPIC-F<N>-<NN>
   b. Nome descritivo
   c. Objetivo (1 frase)
   d. Resultado esperado no sistema ao concluir
   e. Dependências (outros épicos ou "nenhuma")
   f. Definition of Done (lista)
   g. Nome do arquivo correspondente
4. Tabela-resumo dos épicos
5. Mapa de dependências entre épicos
6. Definition of Done da fase

Output: criar arquivo {{output_path}}
HITL: aguardar aprovação do PO antes de salvar.

## Parâmetros desta instância
projeto:       {{NOME-DO-PROJETO}}
fase:          F{{N}} — {{NOME-DA-FASE}}
prd_path:      PROJETOS/{{projeto}}/PRD-{{projeto}}.md
output_path:   PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/F{{N}}_{{PROJETO}}_EPICS.md
observacoes:   {{restrições adicionais}}
```

---

### PROMPT-03 — Épico → Issues e Tarefas

**Work Order tipo:** planejamento de épico  
**Modelo:** `openrouter-main`  
**HITL:** recomendado após rascunho

```
Você é o OpenClaw atuando como engenheiro sênior especializado em decomposição técnica.

Sua tarefa é ler o contexto do projeto e produzir o arquivo completo do épico indicado,
com todas as issues e tarefas detalhadas.

Fontes de verdade (carregue e respeite):
- PRD: {{prd_path}}
- Arquivo de épicos da fase: {{epics_path}}
- Governança: PROJETOS/COMUM/FRAMEWORK-REF.md (todas as partes)

Objetivos não negociáveis:
- Issues com escopo único — sem responsabilidades mistas
- Cada issue completável em ≤ 1 sprint (ref: Parte 3)
- Tarefas atômicas — executáveis por uma pessoa em 1 sessão
- Critérios de aceitação verificáveis (comportamento, não intenção)
- Issues ≥ 8 SP devem ser divididas antes de apresentar
- Ao planejar issues: considerar arquitetura modular, manutenibilidade e evitar monolitos (arquivos/funções grandes demais)

Estrutura obrigatória (Markdown puro — template 6.3):
1. Cabeçalho completo
2. Resumo do épico (2–4 frases)
3. Contexto arquitetural relevante
4. Riscos e armadilhas identificados
5. Definition of Done do épico
6. Para cada issue:
   a. ID: {{PROJ}}-F<N>-<NN>-<MMM>
   b. Título descritivo
   c. Tipo / SP / Prioridade / Status 🔲
   d. Dependências
   e. Descrição (3–6 linhas)
   f. Critérios de Aceitação (verificáveis)
   g. Tarefas (atômicas, T1/T2/T3...)
   h. Notas técnicas
7. Tabela-resumo das issues
8. Notas de implementação globais do épico

Output: criar arquivo {{output_path}}
HITL: apresentar rascunho ao PO antes de salvar como definitivo.
Não traga boas práticas genéricas não referenciadas nos docs do projeto.

## Parâmetros desta instância
projeto:       {{NOME-DO-PROJETO}}
fase:          F{{N}} — {{NOME-DA-FASE}}
epico:         EPIC-F{{N}}-{{NN}}-{{NOME-DO-EPICO}}
prd_path:      PROJETOS/{{projeto}}/PRD-{{projeto}}.md
epics_path:    PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/F{{N}}_{{PROJETO}}_EPICS.md
output_path:   PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/EPIC-F{{N}}-{{NN}}-{{NOME}}.md
observacoes:   {{ex: "seguir ADR-03", "não criar novos endpoints"}}
```

---

### PROMPT-04 — Executar Issue

**Work Order tipo:** execução técnica  
**Modelo:** `openrouter-main`  
**HITL:** obrigatório antes de commit em produção

```
Você é o OpenClaw atuando como engenheiro sênior especializado em arquitetura limpa
e prevenção de monolitos acidentais.

Sua tarefa é implementar a issue indicada, respeitando integralmente os critérios
de aceitação e as restrições arquiteturais do projeto.

Fontes de verdade (carregue e respeite):
- Arquivo do épico com a issue: {{epic_path}}
- PRD: {{prd_path}}
- Governança: PROJETOS/COMUM/FRAMEWORK-REF.md (Partes 1, 2, 4)

Objetivos não negociáveis:
- Implementar exatamente os Critérios de Aceitação — nem mais, nem menos
- Não introduzir dependências não previstas no PRD ou nos docs de arquitetura
- Manter ou aumentar testabilidade
- Registrar qualquer desvio necessário como proposta de DECISÃO (Parte 2)
- Ao final: atualizar status da issue para ✅ no arquivo do épico

Princípios de código (pensar na arquitetura antes de codificar):
- Modularidade: responsabilidade única por módulo/função, evitar arquivos e funções monolíticas
- Manutenibilidade: código legível, nomes claros, baixo acoplamento, alta coesão
- Boas práticas: DRY, separação de concerns, testabilidade, extensibilidade sem quebrar o existente

Estrutura obrigatória da resposta:
1. Escopo da issue compreendido (1–3 frases de confirmação)
2. Abordagem escolhida e justificativa
3. Código / configuração / documentação produzida
4. Testes (unitários/integração) quando aplicável
5. Checklist dos Critérios de Aceitação (✅ ou ⚠️ com explicação)
6. Proposta de DECISÃO (se houver desvio — formato Parte 2.2)
7. Próximos passos (próxima issue dependente, se houver)

HITL: aguardar aprovação do PO antes de commitar em repositório de produção.
Não implemente além do escopo sem aprovação explícita.

## Parâmetros desta instância
projeto:       {{NOME-DO-PROJETO}}
fase:          F{{N}} — {{NOME-DA-FASE}}
epico:         EPIC-F{{N}}-{{NN}}-{{NOME}}
issue:         {{PROJ}}-F{{N}}-{{NN}}-{{MMM}}
epic_path:     PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/EPIC-F{{N}}-{{NN}}-{{NOME}}.md
prd_path:      PROJETOS/{{projeto}}/PRD-{{projeto}}.md
observacoes:   {{restrições específicas desta execução}}
```

---

### PROMPT-05 — Review de Fase / Go-No-Go

**Work Order tipo:** avaliação normativa  
**Modelo:** `openrouter-review`  
**HITL:** obrigatório — decisão de go/no-go é do PO

```
Você é o OpenClaw atuando como revisor de fase.

Sua tarefa é verificar se todos os critérios do Definition of Done da fase foram
atingidos e emitir um parecer go/no-go fundamentado.

Fontes de verdade (carregue e respeite):
- Arquivo de épicos da fase: {{epics_path}}
- Todos os arquivos de épico da fase: PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/EPIC-*.md
- PRD: {{prd_path}}
- Governança: PROJETOS/COMUM/FRAMEWORK-REF.md (Partes 1, 2)

Estrutura obrigatória da resposta:
1. Resumo do estado da fase (2–3 frases)
2. Status de cada épico (✅ / ⚠️ parcial / ❌ pendente)
3. Verificação item a item do DoD da fase
4. Issues em aberto ou bloqueadas (se houver)
5. Dívida técnica identificada (se houver)
6. Parecer:
   - ✅ GO — fase concluída, pode avançar para F<N+1>
   - ⚠️ GO CONDICIONAL — pode avançar com ressalvas documentadas
   - ❌ NO-GO — bloqueios críticos listados
7. Ações necessárias antes do go (se NO-GO ou GO CONDICIONAL)

Output: relatório salvo em {{output_path}}
HITL: o parecer é do OpenClaw; a decisão final de avançar é do PO.
Tom: técnico, preciso, sem suavização de problemas.

## Parâmetros desta instância
projeto:       {{NOME-DO-PROJETO}}
fase_revisada: F{{N}} — {{NOME-DA-FASE}}
proxima_fase:  F{{N+1}} — {{NOME-DA-PROXIMA-FASE}}
epics_path:    PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/F{{N}}_{{PROJETO}}_EPICS.md
prd_path:      PROJETOS/{{projeto}}/PRD-{{projeto}}.md
output_path:   PROJETOS/{{projeto}}/F{{N}}-{{FASE}}/REVIEW-F{{N}}-GO-NOGO.md
observacoes:   {{contexto adicional}}
```

---

## PARTE 8 — Fluxo Operacional Completo

```
┌─────────────────────────────────────────────────────────────┐
│  CICLO DE VIDA DE UM PROJETO NO OPENCLAW SCRUM FRAMEWORK    │
└─────────────────────────────────────────────────────────────┘

1. PO cria PRD-<PROJETO>.md (usando template 6.1)
        │
        ▼ Work Order: PROMPT-01 (modelo: review)
2. OpenClaw propõe fases  ──► HITL: PO aprova fases
        │
        ▼ Work Order: PROMPT-02 por fase (modelo: review)
3. OpenClaw cria F<N>_<PROJETO>_EPICS.md  ──► HITL: PO aprova épicos
        │
        ▼ Work Order: PROMPT-03 por épico (modelo: main)
4. OpenClaw cria EPIC-F<N>-<NN>-<NOME>.md  ──► HITL: PO revisa issues
        │
        ▼  SPRINT PLANNING: PO seleciona issues do sprint (≤ 13 SP)
        │
        ▼ Work Order: PROMPT-04 por issue (modelo: main)
5. OpenClaw executa issue  ──► HITL: PO aprova antes de commit
        │
        ▼  (repetir PROMPT-04 até épico completo)
        │
        ▼  (repetir PROMPT-03 + PROMPT-04 até fase completa)
        │
        ▼ Work Order: PROMPT-05 (modelo: review)
6. OpenClaw emite parecer go/no-go  ──► HITL: PO decide avançar
        │
        ▼  (ir para próxima fase — voltar ao passo 3)
```

---

## PARTE 9 — Migração Futura para Slack

Quando o framework migrar para Slack via OpenClaw, o mapeamento será:

| Conceito local | Equivalente Slack |
|---|---|
| Pasta `PROJETOS/<PROJETO>/` | Canal `#proj-<nome>` |
| `PRD-<PROJETO>.md` | Post fixado + arquivo no canal |
| `<FN>_EPICS.md` | Thread de planejamento da fase |
| `EPIC-FN-NN-<NOME>.md` | Thread de épico com checklist |
| Issue | Sub-thread dentro do épico |
| Tarefa | Checkbox na thread da issue |
| Status 🔄 / ✅ | Reação emoji padronizada (`⚙️` / `✅`) |
| HITL de aprovação | Mensagem com botões via `/oc-approve` e `/oc-reject` |
| `feito/` | Canal `#proj-<nome>-arquivo` |
| Work Order | Comando `/oc-work-order` com YAML inline |

**Pré-requisitos para migração:**
- OpenClaw com Slack Socket Mode ativo (`config/slack-app-manifest.socket-mode.yaml`)
- Comandos `/oc-approve`, `/oc-reject`, `/oc-kill` operacionais
- Workspace OpenClaw com permissão de escrita no canal do projeto

---

*Este documento é a fonte canônica do framework. Atualize `version` e `last_updated` ao fazer qualquer alteração. Mudanças estruturais exigem entrada em `DECISION-PROTOCOL.md`.*
