# SPEC — Migração do Framework OpenClaw para Arquitetura Feature-First Simplificada

---

## Intake

**Problema:** O framework atual usa uma hierarquia de seis níveis
(Fase > Épico > Issue > Sprint > Task > Instruction) que foi projetada para
times humanos. Sprints controlam capacidade que agentes de IA não têm.
Épicos e Fases são camadas de agrupamento sem comportamento próprio.
Issues não forçam o critério de "para quem" e "para quê".

**Oportunidade:** Migrar para uma hierarquia de quatro níveis
(Feature > User Story > Task > Instruction) que é mais alinhada com execução
autônoma por agentes de IA, elimina overhead estrutural sem perda de
atomicidade, e torna cada nível semanticamente significativo.

**Critério de sucesso:** Todos os documentos `GOV-*`, `SPEC-*`, `TEMPLATE-*`,
`SESSION-*` e `boot-prompt.md` atualizados e consistentes com a nova
hierarquia. Nenhuma referência a Sprint, Épico ou Fase deve permanecer nos
artefatos canônicos.

---

## PRD

### Hierarquia canônica de destino

```text
Intake      → gate humano
PRD         → gate humano
Feature     → gate senior (auditoria de feature: go | hold)
User Story  → gate senior (review: aprovada | correcao_requerida)
Task        → execução do agente local (TDD obrigatório quando aplicável)
```

### Invariantes que não mudam

- Markdown como fonte de verdade; SQLite como índice derivado
- Gate humano apenas em Intake e PRD
- Gate senior (opus via OpenRouter) em tudo depois do PRD
- Bloco `ALINHAMENTO PRD` antes de cada execução material
- `GOV-COMMIT-POR-TASK.md` — commit após cada task
- `SPEC-ANTI-MONOLITO.md` — thresholds estruturais na auditoria
- `GOV-BRANCH-STRATEGY.md` — branch por Feature
- Ciclo de correção dentro da mesma User Story até aprovada
- Ciclo de hold dentro da mesma Feature até auditoria go
- Artefato de encerramento de projeto ao final de todas as Features

### Dependências entre Features

```text
Feature 1 → sem dependências (pode iniciar imediatamente após PRD)
Feature 2 → depende_de: [Feature 1]
Feature 3 → depende_de: [Feature 1]
Feature 4 → depende_de: [Feature 2, Feature 3]
```

---

## Feature 1 — Documentos de Governança Centrais

**Objetivo:** Atualizar os documentos que definem a hierarquia e o ciclo de
trabalho do framework para refletir a nova arquitetura.

**Critérios de aceite:**
- `GOV-FRAMEWORK-MASTER.md` descreve a hierarquia Feature > User Story > Task
- `GOV-SCRUM.md` remove Sprints e Épicos do ciclo de trabalho
- `GOV-USER-STORY.md` (novo) define tamanho máximo, critérios e DoD de US
- Nenhum dos três documentos referencia Sprint, Épico ou Fase

---

### User Story 1.1 — Atualizar GOV-FRAMEWORK-MASTER.md

**Como** agente executor do framework,
**quero** que o mapa de alto nível reflita a nova hierarquia,
**para** que qualquer agente que leia o master entenda a cadeia correta.

**Arquivos a tocar:**
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`

**Critérios Given/When/Then:**
- Given o arquivo atual com referências a Fase, Épico e Sprint
- When o agente atualiza a seção "Estrutura Canônica do Repositório"
- Then a hierarquia listada deve ser exatamente `Feature > User Story > Task`
- And a tabela "Fontes de Verdade por Tema" deve apontar para os novos
  documentos `GOV-USER-STORY.md` e `GOV-AUDITORIA-FEATURE.md`
- And não deve existir nenhuma ocorrência de "Sprint", "Épico" ou "Fase"
  fora de uma seção de compatibilidade retroativa

**Tasks:**

#### Task 1.1.1
```yaml
objetivo: Reescrever seção "Estrutura Canônica do Repositório"
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
passos_atomicos:
  - Localizar seção "1. Estrutura Canônica do Repositório"
  - Substituir hierarquia Fase/Épico/Issue/Sprint por Feature/UserStory/Task
  - Atualizar o diagrama de diretórios para refletir nova estrutura de pastas:
      PROJETOS/<PROJETO>/
        INTAKE-<PROJETO>.md
        PRD-<PROJETO>.md
        AUDIT-LOG.md
        features/
          FEATURE-<N>-<NOME>/
            FEATURE-<N>.md
            user-stories/
              US-<N>-<NN>-<NOME>/
                README.md
                TASK-1.md
            auditorias/
              RELATORIO-AUDITORIA-F<N>-R<NN>.md
        encerramento/
          RELATORIO-ENCERRAMENTO.md
resultado_esperado: Seção reescrita sem referências a Fase/Épico/Sprint
stop_conditions:
  - Parar se encontrar dependência entre seções que exija reescrever o
    documento inteiro antes de salvar parcialmente
```

#### Task 1.1.2
```yaml
objetivo: Atualizar tabela "Fontes de Verdade por Tema"
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
passos_atomicos:
  - Remover linhas referentes a Sprint e Épico da tabela
  - Adicionar linha: "tamanho e DoD de User Story | GOV-USER-STORY.md"
  - Adicionar linha: "auditoria de feature | GOV-AUDITORIA-FEATURE.md"
  - Adicionar linha: "encerramento de projeto | TEMPLATE-ENCERRAMENTO.md"
  - Atualizar linha de "auditoria de fase" para "auditoria de feature"
resultado_esperado: Tabela consistente com novos artefatos canônicos
stop_conditions:
  - Parar se o novo documento referenciado ainda não existir; criar
    placeholder vazio antes de referenciar
```

#### Task 1.1.3
```yaml
objetivo: Atualizar seção "Modos de Operação" e "Artefatos Canônicos"
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
passos_atomicos:
  - Substituir artefatos "manifesto da fase", "manifesto do épico",
    "issue canônica" pelos equivalentes novos
  - Manter artefatos inalterados: intake, PRD, audit-log, task, relatório
  - Adicionar artefato "relatório de encerramento"
resultado_esperado: Seções coerentes com nova hierarquia
stop_conditions:
  - Parar e reportar se algum artefato não tiver equivalente claro no
    novo modelo
```

---

### User Story 1.2 — Atualizar GOV-SCRUM.md

**Como** agente executor,
**quero** que o ciclo de trabalho não mencione Sprints, Épicos ou Fases,
**para** que o fluxo operacional seja correto do primeiro ao último passo.

**Arquivos a tocar:**
- `PROJETOS/COMUM/GOV-SCRUM.md`

**Critérios Given/When/Then:**
- Given o arquivo atual com cadeia `Intake > PRD > Fases > Épicos > Issues > Tasks`
- When o agente atualiza a cadeia principal
- Then deve ler `Intake > PRD > Features > User Stories > Tasks`
- And a seção "Definition of Done por Tipo" deve cobrir Feature, User Story e Task
- And a seção "Procedimento de Review-Ready" deve operar no nível de User Story
- And a seção "Gate de Auditoria" deve operar no nível de Feature

**Tasks:**

#### Task 1.2.1
```yaml
objetivo: Reescrever cadeia de trabalho e unidade operacional canônica
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-SCRUM.md
passos_atomicos:
  - Atualizar linha "Cadeia de Trabalho" para nova hierarquia
  - Reescrever seção "Unidade Operacional Canônica":
      feature = unidade de entrega completa com auditoria própria
      user story = menor unidade documental completa para execução
      task = menor item executável dentro da user story
  - Remover todas as referências a Sprint como unidade operacional
resultado_esperado: Cadeia e unidades consistentes com nova arquitetura
stop_conditions:
  - Parar se a remoção de Sprint quebrar referência em outra seção do
    mesmo arquivo; resolver a seção dependente antes de salvar
```

#### Task 1.2.2
```yaml
objetivo: Atualizar Definition of Done por Tipo
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-SCRUM.md
passos_atomicos:
  - Remover DoD de "Fase", "Épico" e "Sprint"
  - Adicionar DoD de "Feature":
      - dependências satisfeitas declaradas no PRD
      - todas as User Stories done
      - auditoria com veredito go
      - branch mergeada para main
  - Adicionar DoD de "User Story":
      - arquivo próprio com frontmatter padronizado
      - user story, contexto técnico, critérios Given/When/Then e DoD declarados
      - tasks decupadas com task_instruction_mode definido
      - handoff de revisão persistido ao concluir execução
      - done somente após revisão do agente senior aprovada
  - Manter DoD de "Intake" e "Task" inalterados
resultado_esperado: DoDs presentes para Feature, User Story e Task
```

#### Task 1.2.3
```yaml
objetivo: Atualizar procedimento de Review-Ready e regras de status
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-SCRUM.md
passos_atomicos:
  - Substituir "Issue" por "User Story" em toda a seção de Review-Ready
  - Atualizar cascata de fechamento para: US > Feature (sem épico, sem sprint)
  - Atualizar regras de status para os novos níveis
  - Remover seção "Arquivamento de Fase"; adicionar "Encerramento de Feature":
      quando feature atingir done, mover pasta para features/encerradas/
resultado_esperado: Procedimentos operacionais corretos para nova hierarquia
```

---

### User Story 1.3 — Criar GOV-USER-STORY.md

**Como** agente executor,
**quero** um documento normativo que defina tamanho, critérios e DoD de
User Story,
**para** que o limite de atomicidade que as Sprints davam seja preservado
como regra explícita.

**Arquivos a tocar:**
- `PROJETOS/COMUM/GOV-USER-STORY.md` (criar)

**Critérios Given/When/Then:**
- Given que não existe documento de limite para User Stories
- When o agente cria o documento
- Then deve conter limites numéricos explícitos de tamanho
- And deve definir critério de elegibilidade para execução
- And deve definir quando `task_instruction_mode: required` é obrigatório

**Tasks:**

#### Task 1.3.1
```yaml
objetivo: Criar GOV-USER-STORY.md com frontmatter e limites canônicos
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/GOV-USER-STORY.md
passos_atomicos:
  - Criar arquivo com frontmatter padrão (doc_id, version, status, owner,
    last_updated)
  - Adicionar seção "Limites Canônicos":
      max_tasks_por_user_story: 5
      max_story_points_por_user_story: 5
      max_user_stories_por_feature: sem limite fixo
      criterio_de_tamanho: executável em uma única sessão de agente sem ambiguidade
  - Adicionar seção "Critério de Elegibilidade para Execução":
      - user story com task_instruction_mode required sem tasks detalhadas
        não é elegível
      - user story com dependência de outra US não done não é elegível
  - Adicionar seção "Quando required é obrigatório" (mesmos critérios de
    SPEC-TASK-INSTRUCTIONS.md adaptados para o nível de US)
resultado_esperado: Arquivo criado com limites e critérios canônicos
stop_conditions:
  - Parar se algum limite proposto conflitar com SPEC-TASK-INSTRUCTIONS.md;
    resolver conflito antes de salvar
```

---

## Feature 2 — Templates de Artefato

**Objetivo:** Criar e atualizar os templates que os agentes usam para gerar
os artefatos documentais da nova hierarquia.

**Depende de:** Feature 1

**Critérios de aceite:**
- `TEMPLATE-PRD.md` usa Features como eixo e referencia User Stories
- `TEMPLATE-USER-STORY.md` (novo) define estrutura canônica da US
- `TEMPLATE-TASK.md` mantém TDD, adiciona rastreabilidade para US de origem
- `TEMPLATE-AUDITORIA-FEATURE.md` (novo) versão leve do relatório atual
- `TEMPLATE-ENCERRAMENTO.md` (novo) artefato de fechamento de projeto

---

### User Story 2.1 — Atualizar TEMPLATE-PRD.md

**Como** agente de produto,
**quero** um template de PRD que use Features como eixo e elimine seções
de Fase e Épico,
**para** que o PRD seja a fonte de verdade direta para decomposição em
User Stories.

**Arquivos a tocar:**
- `PROJETOS/COMUM/TEMPLATE-PRD.md`

**Tasks:**

#### Task 2.1.1
```yaml
objetivo: Remover seções de Fases e Épicos do template
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/TEMPLATE-PRD.md
passos_atomicos:
  - Remover seções "13. Estrutura de Fases" e "14. Épicos"
  - Manter seção "12. Features do Projeto" como eixo principal
  - Dentro de cada Feature, adicionar campo "User Stories planejadas":
      | US ID | Título | SP estimado | Depende de |
      |-------|--------|-------------|------------|
  - Adicionar campo "depende_de" no cabeçalho de cada Feature
  - Atualizar checklist de prontidão removendo itens de fase/épico
resultado_esperado: Template sem referências a Fase ou Épico
```

---

### User Story 2.2 — Criar TEMPLATE-USER-STORY.md

**Como** agente executor,
**quero** um template canônico para User Stories,
**para** que toda US criada tenha estrutura consistente e elegível para
execução.

**Arquivos a tocar:**
- `PROJETOS/COMUM/TEMPLATE-USER-STORY.md` (criar)

**Tasks:**

#### Task 2.2.1
```yaml
objetivo: Criar template de User Story com todos os campos canônicos
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/TEMPLATE-USER-STORY.md
passos_atomicos:
  - Criar arquivo com frontmatter:
      doc_id, version, status, owner, last_updated,
      task_instruction_mode, feature_id, decision_refs
  - Adicionar campos obrigatórios:
      - User Story (Como / Quero / Para)
      - Feature de Origem (ID e comportamento coberto)
      - Contexto Técnico
      - Critérios Given/When/Then
      - Definition of Done da US
      - Tasks (lista com links para TASK-N.md)
      - Arquivos Reais Envolvidos
      - Artefato Mínimo
      - Handoff para Revisão (mesmo modelo do README.md atual de issue)
      - Dependências (Feature pai, PRD, outras USs)
resultado_esperado: Template criado e consistente com GOV-USER-STORY.md
```

---

### User Story 2.3 — Criar TEMPLATE-AUDITORIA-FEATURE.md

**Como** agente senior,
**quero** um template de auditoria mais leve que o atual,
**para** que auditar Features seja ágil o suficiente para acontecer
com frequência sem gerar overhead documental excessivo.

**Arquivos a tocar:**
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md` (criar)

**Critérios Given/When/Then:**
- Given o template atual `TEMPLATE-AUDITORIA-RELATORIO.md` com 15 seções
- When o agente cria o template de feature
- Then deve ter no máximo 8 seções
- And deve manter as seções de achados, veredito e follow-ups
- And deve eliminar seções de prestação de contas de rodadas anteriores
  quando for primeira rodada

**Tasks:**

#### Task 2.3.1
```yaml
objetivo: Criar TEMPLATE-AUDITORIA-FEATURE.md com estrutura enxuta
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/TEMPLATE-AUDITORIA-FEATURE.md
passos_atomicos:
  - Criar frontmatter com: doc_id, version, status, verdict, feature_id,
    reviewer_model, base_commit, round, supersedes, followup_destination,
    last_updated
  - Criar 8 seções canônicas:
      1. Resumo Executivo (3 linhas máximo)
      2. Escopo Auditado (feature, USs, commits, testes)
      3. Prestação de Contas de Follow-ups (só quando round > 1 e hold anterior)
      4. Conformidades
      5. Não Conformidades (com evidência obrigatória por achado)
      6. Análise Estrutural (usando SPEC-ANTI-MONOLITO.md)
      7. Decisão (veredito, gate da feature, follow-up padrão)
      8. Follow-ups (bloqueantes e não bloqueantes)
  - Omitir seções de "Verificação de Decisões Registradas",
    "Bugs e Riscos Antecipados" e "Cobertura de Testes" como seções
    separadas — integrar no corpo de Não Conformidades
resultado_esperado: Template criado com 8 seções, coerente com GOV-AUDITORIA.md
```

---

### User Story 2.4 — Criar TEMPLATE-ENCERRAMENTO.md

**Como** PM,
**quero** um artefato de encerramento de projeto,
**para** que exista registro formal quando todas as Features forem aprovadas.

**Arquivos a tocar:**
- `PROJETOS/COMUM/TEMPLATE-ENCERRAMENTO.md` (criar)

**Tasks:**

#### Task 2.4.1
```yaml
objetivo: Criar template de encerramento de projeto
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/TEMPLATE-ENCERRAMENTO.md
passos_atomicos:
  - Criar frontmatter com: doc_id, version, status, project, owner,
    last_updated, features_total, features_done, data_encerramento
  - Criar seções:
      1. Resumo do Projeto (objetivo original do PRD, resultado entregue)
      2. Features Entregues (tabela: Feature | Auditoria | Veredito | Data)
      3. Métricas de Entrega (USs total, tasks total, rounds de correção médio)
      4. Desvios do PRD (o que mudou de escopo e por quê)
      5. Débitos Técnicos Conhecidos (achados não bloqueantes deixados abertos)
      6. Decisão de Encerramento (go | cancelado | suspenso)
resultado_esperado: Template criado e referenciado em GOV-FRAMEWORK-MASTER.md
```

---

## Feature 3 — Documentos Operacionais e Skills

**Objetivo:** Atualizar os documentos SESSION-*, o boot-prompt e as skills
do agente para operar na nova hierarquia.

**Depende de:** Feature 1, Feature 2

**Critérios de aceite:**
- `boot-prompt.md` descobre Features e User Stories, não Fases e Issues
- `SESSION-IMPLEMENTAR-US.md` (novo ou renomeado) opera no nível de User Story
- `SESSION-AUDITAR-FEATURE.md` (novo ou renomeado) opera no nível de Feature
- Skills `.codex/skills/openclaw-*/SKILL.md` atualizadas para nova nomenclatura

---

### User Story 3.1 — Atualizar boot-prompt.md

**Como** agente autônomo,
**quero** que o boot-prompt descubra a próxima User Story elegível dentro
da próxima Feature ativa,
**para** que o fluxo autônomo funcione sem referências a Fase ou Issue.

**Arquivos a tocar:**
- `PROJETOS/COMUM/boot-prompt.md`

**Tasks:**

#### Task 3.1.1
```yaml
objetivo: Reescrever algoritmo de descoberta de unidade elegível
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/boot-prompt.md
passos_atomicos:
  - Substituir Níveis 4/5/6 (Fases > Épico ativo > Issue) pelos novos:
      Nível 4 — Features:
        ler features/<N>-<NOME>/FEATURE-<N>.md em ordem numérica
        se feature done e auditoria approved: avançar para próxima
        se todas USs done e auditoria não approved: modo AUDITORIA-FEATURE
        se há US active: esta é a US de trabalho
        se há US todo e dependências satisfeitas: próxima US elegível
      Nível 5 — User Story ativa:
        ler features/<N>-<NOME>/user-stories/<US>/README.md
        verificar task_instruction_mode
        selecionar próxima TASK-N.md com status todo ou active
      Nível 6 — Task:
        ler TASK-N.md selecionada
        verificar tdd_aplicavel e campos obrigatórios
  - Atualizar quadro de confirmação para nova nomenclatura:
      MODO / PROJETO / FEATURE ALVO / US ALVO / TASK ALVO /
      TASK_INSTR_MODE / SP / DEPENDÊNCIAS / DECISÃO
  - Atualizar sequência mínima para ISSUE → US
  - Atualizar sequência mínima para AUDITORIA-FASE → AUDITORIA-FEATURE
resultado_esperado: boot-prompt sem referências a Fase, Épico ou Sprint
stop_conditions:
  - Parar se a nova estrutura de diretórios não estiver definida em
    GOV-FRAMEWORK-MASTER.md; ler antes de reescrever
```

---

### User Story 3.2 — Criar SESSION-IMPLEMENTAR-US.md

**Como** agente executor em sessão interativa,
**quero** um SESSION específico para execução de User Story,
**para** que o fluxo interativo opere na nova hierarquia.

**Arquivos a tocar:**
- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md` (criar a partir de SESSION-IMPLEMENTAR-ISSUE.md)

**Tasks:**

#### Task 3.2.1
```yaml
objetivo: Criar SESSION-IMPLEMENTAR-US.md baseado no SESSION-IMPLEMENTAR-ISSUE.md atual
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md
passos_atomicos:
  - Copiar SESSION-IMPLEMENTAR-ISSUE.md como base
  - Substituir todos os termos: Issue→US, issue_id→us_id, ISSUE_PATH→US_PATH,
    ISSUE_ID→US_ID, epico→feature
  - Atualizar parâmetros de entrada: remover FASE, adicionar FEATURE_ID
  - Atualizar cascata de fechamento: US > Feature (sem épico, sem sprint)
  - Manter intactos: bloco ALINHAMENTO PRD, protocolo TDD, GOV-COMMIT-POR-TASK,
    bloco de handoff para revisão, parâmetro ROUND
  - Atualizar referências normativas: SESSION-IMPLEMENTAR-ISSUE → SESSION-IMPLEMENTAR-US
resultado_esperado: SESSION funcional para nova hierarquia sem referências a Issue
```

---

### User Story 3.3 — Criar SESSION-AUDITAR-FEATURE.md

**Como** agente senior em sessão interativa,
**quero** um SESSION específico para auditoria de Feature,
**para** que o fluxo de auditoria use o novo template mais leve.

**Arquivos a tocar:**
- `PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md` (criar a partir de SESSION-AUDITAR-FASE.md)

**Tasks:**

#### Task 3.3.1
```yaml
objetivo: Criar SESSION-AUDITAR-FEATURE.md baseado no SESSION-AUDITAR-FASE.md atual
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md
passos_atomicos:
  - Copiar SESSION-AUDITAR-FASE.md como base
  - Substituir todos os termos: Fase→Feature, fase→feature, FASE→FEATURE
  - Atualizar template de relatório referenciado para
    TEMPLATE-AUDITORIA-FEATURE.md
  - Atualizar pré-checagem de elegibilidade: verificar USs da Feature
    (todas done ou cancelled) antes de iniciar auditoria
  - Manter intactos: algoritmo de verificação de follow-ups bloqueantes,
    vereditos go|hold|cancelled, handoff para SESSION-REMEDIAR-HOLD
  - Adicionar passo final: se go, verificar se todas as Features estão done;
    se sim, sugerir geração de RELATORIO-ENCERRAMENTO.md
resultado_esperado: SESSION funcional para auditoria de Feature
```

---

### User Story 3.4 — Atualizar skills do agente

**Como** agente operando via OpenClaw,
**quero** que as skills reflitam a nova nomenclatura,
**para** que o roteamento e a execução usem os termos corretos.

**Arquivos a tocar:**
- `.codex/skills/openclaw-autonomous/SKILL.md`
- `.codex/skills/openclaw-router/SKILL.md`
- `.codex/skills/openclaw-session-issue-execution/SKILL.md` → renomear conceito
- `SESSION-MAPA.md`

**Tasks:**

#### Task 3.4.1
```yaml
objetivo: Atualizar openclaw-autonomous para nova hierarquia
tdd_aplicavel: false
arquivos_a_tocar:
  - .codex/skills/openclaw-autonomous/SKILL.md
passos_atomicos:
  - Substituir referências a Fase/Épico/Issue por Feature/US nos protocolos
  - Atualizar bloco ALINHAMENTO PRD para incluir campo US_ID de origem
  - Atualizar descrição de modo AUDITORIA para AUDITORIA-FEATURE
resultado_esperado: Skill consistente com nova hierarquia
```

#### Task 3.4.2
```yaml
objetivo: Atualizar openclaw-router com novas rotas
tdd_aplicavel: false
arquivos_a_tocar:
  - .codex/skills/openclaw-router/SKILL.md
passos_atomicos:
  - Atualizar fluxo canônico completo para Feature > US > Task
  - Substituir rota "executar uma issue" por "executar uma User Story"
    apontando para SESSION-IMPLEMENTAR-US.md
  - Substituir rota "auditar uma fase" por "auditar uma feature"
    apontando para SESSION-AUDITAR-FEATURE.md
  - Adicionar rota "encerrar projeto" quando todas as features estiverem done
resultado_esperado: Router com rotas corretas para nova arquitetura
```

#### Task 3.4.3
```yaml
objetivo: Atualizar SESSION-MAPA.md
tdd_aplicavel: false
arquivos_a_tocar:
  - PROJETOS/COMUM/SESSION-MAPA.md
passos_atomicos:
  - Remover SESSION-IMPLEMENTAR-ISSUE, SESSION-AUDITAR-FASE das tabelas
  - Adicionar SESSION-IMPLEMENTAR-US e SESSION-AUDITAR-FEATURE
  - Atualizar gatilhos rápidos para nova nomenclatura
  - Atualizar tabela comparativa boot-prompt vs SESSION para nova hierarquia
resultado_esperado: Mapa consistente sem referências a Issue ou Fase
```

---

## Auditoria de Projeto (encerramento)

Ao concluir as Features 1, 2 e 3, gerar `encerramento/RELATORIO-ENCERRAMENTO.md`
usando `TEMPLATE-ENCERRAMENTO.md` com:

- todas as Features entregues listadas com veredito de auditoria
- desvios de escopo em relação a este spec documentados
- débitos técnicos conhecidos (ex: SESSION-* legados não removidos, apenas
  depreciados) registrados como follow-ups não bloqueantes
- decisão de encerramento: `go` se todas as Features tiverem auditoria aprovada

---

## Regras de execução deste spec

1. Ler este arquivo inteiro antes de executar qualquer task
2. Emitir bloco `ALINHAMENTO PRD` antes de cada task usando este spec como PRD
3. Executar Features na ordem declarada respeitando `depende_de`
4. Dentro de cada Feature, executar User Stories na ordem listada
5. Dentro de cada User Story, executar tasks na ordem numerada
6. Commit após cada task: `OPENCLAW-MIGRATION <US_ID> <TASK_ID>: <descrição>`
7. Review de agente senior após cada User Story completa
8. Auditoria de agente senior após cada Feature completa
9. Não remover documentos legados — marcar como `status: deprecated` com
   ponteiro para o substituto
10. Se qualquer task encontrar conflito entre o spec e a governança existente,
    parar e reportar antes de resolver arbitrariamente
