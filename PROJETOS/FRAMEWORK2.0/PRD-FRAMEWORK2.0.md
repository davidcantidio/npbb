---
doc_id: "PRD-FRAMEWORK2.0-v1.5.md"
version: "1.5"
status: "draft"
owner: "PM"
last_updated: "2026-03-09"
project: "FRAMEWORK2.0"
intake_kind: "refactor"
source_mode: "backfilled"
origin_project: "COMUM"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "alta"
change_type: "refactor"
audit_rigor: "elevated"
---

# CRÍTICA DO FRAMEWORK + PRD-FRAMEWORK2.0

> Este documento tem duas partes. A Parte 1 é a análise crítica do framework atual,
> com pontos de ruído, lacunas e inconsistências identificados. A Parte 2 é o PRD
> do projeto de adequação, que usa o próprio framework como método de execução.

---

# PARTE 1 — ANÁLISE CRÍTICA DO FRAMEWORK

## 1.1 Documento Legado Ativo (Risco Alto)

`PROJETOS/scrum-framework-master (1).md` está explicitamente rotulado como legado
("documento legado em duplicidade"), mas continua presente e acessível no repositório.
Qualquer agente que leia ambos os arquivos recebe instruções contraditórias em pelo
menos três eixos: sistema de status (emoji vs texto), estrutura de templates e
hierarquia de autoridade. O legado declara que "em caso de conflito, este arquivo
prevalece sobre qualquer arquivo de projeto individual" — o que é o inverso da
intenção do framework canônico atual.

**Impacto:** Alto. Um agente mal roteado pode usar o legado como fonte normativa
e gerar artefatos incompatíveis com o padrão issue-first.

**Ação recomendada:** Remover ou mover para `feito/` com nota de deprecação explícita
e data. Não basta o rótulo inline — o arquivo precisa sair do caminho de leitura padrão.

---

## 1.2 Dualidade de Sistema de Status (Ruído Estrutural)

O legado usa símbolos emoji (🔲 🔄 ✅ 🗑️). O canônico usa texto puro
(`todo`, `active`, `done`, `cancelled`). Enquanto ambos coexistem no repositório,
qualquer agente que não leia a instrução de precedência correta pode persistir status
no formato errado — o que quebra qualquer lógica de parsing ou derivação automática
de estado pai/filho.

**Impacto:** Médio direto, alto acumulado. Artefatos com status emoji não são
parseáveis pelos critérios derivados definidos no `SCRUM-GOV.md`.

---

## 1.3 Sobreposição entre SCRUM-GOV e scrum-framework-master (Redundância)

Ambos os documentos canônicos definem, com variações sutis:
- Cadeia de trabalho (`Intake → PRD → Fases → ...`)
- Regras de status e derivação pai/filho
- Regras de auditoria (vereditos, estados de gate)
- Regras de arquivamento de fase

A divergência mais relevante está nas "Regras de Remediação por Auditoria":
`SCRUM-GOV.md` seção 8 define o fluxo com um nível de detalhe, enquanto
`AUDITORIA-GOV.md` define com outro, e os dois não são perfeitamente espelhados.
Um agente que lê apenas um deles opera com especificação incompleta.

**Ação recomendada:** Definir responsabilidade única por seção. `SCRUM-GOV.md`
deve ser o índice de regras de processo. `AUDITORIA-GOV.md` deve ser a única
fonte de verdade sobre auditoria. As duplicações precisam ser eliminadas ou
transformadas em referências explícitas.

---

## 1.4 `prompt_epicos_issues.md` Órfão (Desconexão)

O antigo arquivo `prompt_epicos_issues.md`, depois consolidado como
`PROMPT-PLANEJAR-FASE.md`, existia como prompt operacional
para planejamento de épicos e issues, mas não está referenciado em nenhum ponto
da cadeia canônica: não aparece no `boot-prompt.md`, no `scrum-framework-master.md`
nem no `SCRUM-GOV.md`. Um agente seguindo o boot-prompt nunca saberá que este
prompt existe.

**Impacto:** O artefato existe mas não é utilizável dentro do fluxo formal.
Ou ele deve ser integrado à cadeia canônica (com referência no `boot-prompt.md`
como prompt de planejamento de fase) ou deve ser removido para evitar confusão.

---

## 1.5 Anti-Monolith Sem Threshold Objetivo (Lacuna Crítica)

As classes de achado `monolithic-file` e `monolithic-function` estão definidas em
`AUDITORIA-GOV.md`, mas nenhum documento do framework define o que objetivamente
constitui um monolito. Isso torna o achado dependente do julgamento subjetivo do
auditor. Dois auditores diferentes produzirão vereditos diferentes para o mesmo
arquivo.

**Thresholds ausentes que precisam ser definidos:**
- Tamanho de arquivo (ex: >300 linhas de código lógico = candidato a revisão;
  >500 linhas = monolito confirmado)
- Número de responsabilidades por arquivo (ex: exporta >5 conceitos distintos)
- Profundidade de função (ex: >50 linhas ou >3 níveis de aninhamento)
- Número de imports de domínios diferentes num único arquivo
- Acoplamento de saída (ex: importado por >10 módulos distintos sem ser utilitário)

**Impacto:** Sem critério objetivo, o achado não pode ser comparado entre rodadas
de auditoria nem rastreado como tendência.

---

## 1.6 Monolith → PRD de Refatoração Não Operacionalizado (Lacuna de Fluxo)

`AUDITORIA-GOV.md` define que achados estruturais viram `new-intake` com
`intake_kind: audit-remediation`. Mas não existe:
- Prompt dedicado para "achado de monolito → intake de decomposição"
- Template de intake pré-preenchido para refatoração de arquivo/função monolítica
- Critérios de fatiamento específicos para decomposição (como dividir em módulos,
  quais testes de regressão exigir, como manter compatibilidade de interface)

O caminho existe na teoria mas não está operacionalizado. Na prática, quando um
auditor encontra um monolito e precisa gerar um intake, ele parte do zero — o que
cria inconsistência e aumenta o risco de intakes mal formados.

**Ação recomendada:** Criar `PROMPT-MONOLITH-TO-INTAKE.md` e uma seção específica
no `INTAKE-TEMPLATE.md` para `intake_kind: refactor` com campos dedicados a
decomposição de arquivo/função.

---

## 1.7 Ausência de Prompt de Sessão de Chat (Lacuna Operacional)

`boot-prompt.md` é projetado para Cloud Agent autônomo que lê, decide e executa
sem intervenção. Não existe um prompt equivalente para sessão de chat interativa —
onde o humano diz "execute a issue X da fase Y do projeto Z" e o agente solicita
confirmações inline antes de cada ação material.

Isso força o PM a adaptar manualmente o boot-prompt para uso em chat, aumentando
o risco de operação fora do padrão. São necessários pelo menos três prompts
de sessão distintos:

1. **SESSION-IMPLEMENT.md** — para implementação de issue em chat interativo
2. **SESSION-AUDIT.md** — para conduzir auditoria de fase em sessão de chat
3. **SESSION-REFACTOR.md** — para conduzir refatoração de monolito como mini-projeto

---

## 1.8 DECISION-PROTOCOL Desconectado da Auditoria (Gap de Rastreabilidade)

Os risk tiers R0–R3 do `DECISION-PROTOCOL.md` não aparecem em nenhum campo do
template de relatório de auditoria, nem nas issues. Uma decisão arquitetural
tomada durante implementação (ex: introduzir nova dependência, mudar contrato de
interface) não tem trilha formal de volta ao DECISION-PROTOCOL. O auditor não
consegue verificar se decisões R2/R3 foram formalmente aprovadas.

**Ação recomendada:** Adicionar no template de issue um campo `decision_refs`
opcional. Adicionar na seção "Conformidades/Não Conformidades" do relatório de
auditoria uma linha de verificação de decisões registradas.

---

## 1.9 Template de Relatório Sem Métricas de Monolito (Lacuna de Template)

A tabela "Saúde Estrutural do Código" no `AUDITORIA-REPORT-TEMPLATE.md` é genérica
e cobre todos os achados numa única estrutura. Não há seção dedicada a métricas de
complexidade ou tamanho, o que impede análise de tendência entre rodadas de auditoria
(ex: "o arquivo X cresceu 40% entre F1-R01 e F1-R02").

---

## 1.10 Gate de Auditoria Sem Checklist de Transição (Ambiguidade Operacional)

O estado `pending` do gate no manifesto da fase depende de o agente perceber que
todos os épicos estão `done` e atualizar o campo manualmente. Não existe checklist
explícito nem critério formal no template do manifesto da fase que defina exatamente
quando essa transição deve ocorrer e quem deve executá-la.

---

## 1.11 Listas de Leitura Paralelas em Prompts Canônicos (Drift Silencioso)

`PROMPT-INTAKE-PARA-PRD.md` e `AUDITORIA-PROMPT.md` definem cada um sua própria
lista numerada de arquivos a ler em vez de apontar para a ordem canônica do
`boot-prompt.md`. Quando o framework for atualizado — por exemplo, ao adicionar
`SPEC-ANTI-MONOLITO.md` em F2 — essas listas ficam desatualizadas silenciosamente.
Inconsistência já presente: `AUDITORIA-PROMPT.md` inclui `WORK-ORDER-SPEC.md`
mas omite `SPRINT-LIMITS.md`; o `boot-prompt.md` inclui os dois.

**Ação recomendada:** Substituir as listas internas por ponteiro para
`boot-prompt.md` Níveis 1–3, adicionando apenas os artefatos específicos da
operação que não estão cobertos pelos níveis canônicos.

---

## 1.12 Gate Intake → PRD Definido em Três Lugares com Critérios Divergentes

O critério "quando o intake está pronto para PRD" aparece em `INTAKE-FRAMEWORK.md`
(7 perguntas narrativas), `scrum-framework-master.md` seção 6 (lista de campos
mínimos) e `SCRUM-GOV.md` (checklist de itens do arquivo). Os três têm
granularidade e framing diferentes. Para `intake_kind: refactor`, os dois últimos
listam campos extras obrigatórios que o primeiro não menciona no gate.

**Ação recomendada:** Consolidar o gate canônico em `GOV-INTAKE.md` como fonte
única. Os demais documentos devem referenciar esse gate, não redefini-lo.

---

## 1.13 `source_mode: backfilled` Sem Regra Operacional (Lacuna Crítica de Fluxo)

O valor `backfilled` existe nas taxonomias controladas mas nenhum documento define
o que ele implica: quais seções são obrigatórias mesmo em backfill, se o gate de
PRD se aplica integralmente, e o que é válido como contexto de origem quando o
PRD já existe antes do intake. O agente bloqueou ao iniciar o FRAMEWORK2.0
exatamente por falta dessa regra.

**Ação recomendada:** Adicionar seção "Intakes Retroativos (`source_mode:
backfilled`)" em `GOV-INTAKE.md`.

---

## 1.14 `SCRUM-GOV.md` Copia Critérios de `TASK_INSTRUCTIONS_SPEC.md`

A seção "Regras de Task Instructions" do `SCRUM-GOV.md` reproduz integralmente
os 5 fatores que tornam `required` obrigatório — os mesmos já definidos em
`TASK_INSTRUCTIONS_SPEC.md`. `ISSUE-FIRST-TEMPLATES.md` já faz a coisa certa:
referencia o spec sem copiar. Uma atualização no spec não se propaga para o gov.

**Ação recomendada:** Substituir a lista em `SCRUM-GOV.md` por ponteiro para
`SPEC-TASK-INSTRUCTIONS.md`.

---

## 1.15 SESSION-INTAKE e SESSION-PLAN Existem sem Rastreabilidade Formal

`SESSION-INTAKE.md` e `SESSION-PLAN.md` foram produzidos e estão em uso, mas não
constam como entregáveis de nenhuma fase do PRD. F3 previa apenas SESSION-IMPLEMENT,
SESSION-AUDIT e SESSION-REFACTOR. Sem rastreabilidade formal, esses artefatos
podem ser sobrescritos ou ignorados por um agente que leia o PRD como escopo.

---

## 1.16 Nomenclatura dos Arquivos não Comunica Propósito nem Uso

Os arquivos de `PROJETOS/COMUM/` não seguem convenção de nomenclatura que
comunique ao PM o que fazer com eles. `INTAKE-TEMPLATE.md` parece documento, não
template preenchível. `AUDITORIA-PROMPT.md` e `SESSION-INTAKE.md` têm prefixos
diferentes para arquivos do mesmo tipo funcional. Um PM novo não consegue
distinguir o que é para ler, o que é para preencher e o que é para colar no chat.

**Ação recomendada:** Adotar convenção de prefixo por tipo funcional e renomear
todos os arquivos de `PROJETOS/COMUM/`. Ver seção "Convenção de Nomenclatura" na
Parte 2.

---

## Resumo dos Pontos por Prioridade

| # | Ponto | Tipo | Prioridade |
|---|---|---|---|
| 1.1 | Documento legado ativo | Risco de ruído | Crítica |
| 1.2 | Dualidade de status | Inconsistência | Alta |
| 1.3 | Sobreposição SCRUM-GOV / master | Redundância | Alta |
| 1.5 | Anti-monolith sem threshold | Lacuna objetiva | Alta |
| 1.7 | Ausência de prompts de sessão | Lacuna operacional | Alta |
| 1.13 | `source_mode: backfilled` sem regra operacional | Lacuna crítica de fluxo | Alta |
| 1.16 | Nomenclatura não comunica propósito | Usabilidade | Alta |
| 1.6 | Monolith → PRD não operacionalizado | Lacuna de fluxo | Média |
| 1.4 | `prompt_epicos_issues.md` órfão e com hardcode | Desconexão | Média |
| 1.8 | DECISION-PROTOCOL desconectado da auditoria | Gap de rastreabilidade | Média |
| 1.11 | Listas de leitura paralelas nos prompts canônicos | Drift silencioso | Média |
| 1.12 | Gate intake→PRD triplicado com critérios divergentes | Redundância | Média |
| 1.14 | `SCRUM-GOV` copia critérios de `TASK_INSTRUCTIONS_SPEC` | Redundância | Baixa-média |
| 1.15 | SESSION-INTAKE e SESSION-PLAN sem rastreabilidade formal | Lacuna | Baixa-média |
| 1.9 | Template de auditoria sem métricas de monolito | Lacuna de template | Baixa |
| 1.10 | Gate sem checklist de transição | Ambiguidade | Baixa |

---

# PARTE 2 — PRD-FRAMEWORK2.0

## Objetivo

Adequar o framework de governança `PROJETOS/COMUM/` para eliminar inconsistências,
lacunas operacionais e ruídos identificados na análise crítica, tornando o fluxo
`Intake → PRD → Fases → Épicos → Issues → Tasks → Auditorias` mais assertivo,
rastreável e resistente à interpretação subjetiva — com fluxo operável de ponta
a ponta em sessão de chat interativo.

O projeto usa o próprio framework como método de execução.

---

## Fluxo Canônico do Framework (do Intake às Instructions)

Este é o fluxo completo que o framework deve suportar após as três fases do
projeto. Cada linha indica o artefato de entrada, o prompt que aciona a etapa
e o artefato de saída.

```
╔══════════════════════════════════════════════════════════════╗
║  PM tem contexto bruto de um problema ou iniciativa          ║
╚══════════════════════════╤═══════════════════════════════════╝
                           │
              [ SESSION-CRIAR-INTAKE.md ]
              usa: TEMPLATE-INTAKE.md + GOV-INTAKE.md
                           │
                           ▼
              ┌────────────────────────┐
              │  INTAKE-<PROJETO>.md   │  ← preenchido e aprovado
              └────────────┬───────────┘
                           │
              [ SESSION-CRIAR-PRD.md ]
              usa: PROMPT-INTAKE-PARA-PRD.md internamente
                           │
                           ▼
              ┌────────────────────────┐
              │  PRD-<PROJETO>.md      │  ← aprovado pelo PM
              └────────────┬───────────┘
                           │
              [ SESSION-PLANEJAR-PROJETO.md ]
              usa: PROMPT-PLANEJAR-FASE.md internamente
              *(ou GOV-ISSUE-FIRST.md + SPEC-TASK-INSTRUCTIONS.md
                se PROMPT-PLANEJAR-FASE.md for depreciado — ver EPIC-F1-04)*
              produz: fases → épicos → issues com tasks
              e instructions embutidas quando required
                           │
                           ▼
              ┌───────────────────────────────────────┐
              │  F<N>_EPICS.md                        │
              │  EPIC-F<N>-<NN>-<NOME>.md             │
              │  issues/ISSUE-*.md                    │
              │    └─ tasks (checklist inline)        │
              │    └─ instructions (bloco inline      │
              │       quando task_mode: required)     │
              │  sprints/SPRINT-*.md                  │
              └────────────┬──────────────────────────┘
                           │
              [ SESSION-IMPLEMENTAR-ISSUE.md ]   ← chat interativo
              [ boot-prompt.md ]                 ← agente autônomo
                           │
                           ▼
              ┌────────────────────────┐
              │  Código implementado   │
              └────────────┬───────────┘
                           │
              [ SESSION-AUDITAR-FASE.md ]   ← chat interativo
              [ PROMPT-AUDITORIA.md ]       ← agente autônomo
                           │
                           ▼
              ┌──────────────────────────────────────┐
              │  RELATORIO-AUDITORIA-F<N>-R<NN>.md   │
              │  AUDIT-LOG.md atualizado             │
              └────────────┬─────────────────────────┘
                           │
              se veredito go → fase move para feito/
              se veredito hold com monolito encontrado:
                           │
              [ SESSION-REFATORAR-MONOLITO.md ]
              usa: PROMPT-MONOLITO-PARA-INTAKE.md
              usa: SPEC-ANTI-MONOLITO.md como threshold
                           │
                           ▼
              INTAKE-<PROJETO>-REFACTOR-<SLUG>.md
              → reinicia o ciclo a partir do intake
```

**Artefatos de entrada que o PM preenche ou fornece:**
- `TEMPLATE-INTAKE.md` — preenchido para criar o intake
- `TEMPLATE-AUDITORIA-RELATORIO.md` — preenchido pelo auditor
- `TEMPLATE-AUDITORIA-LOG.md` — mantido cumulativamente

**Prompts que o PM cola no chat:**
- `SESSION-CRIAR-INTAKE.md` — cria intake a partir de contexto bruto
- `SESSION-CRIAR-PRD.md` — cria PRD a partir do intake aprovado
- `SESSION-PLANEJAR-PROJETO.md` — cria fases, épicos, issues, tasks e instructions
- `SESSION-IMPLEMENTAR-ISSUE.md` — implementa uma issue específica
- `SESSION-AUDITAR-FASE.md` — audita uma fase
- `SESSION-REFATORAR-MONOLITO.md` — refatora monolito como mini-projeto

**Documentos de governança que o PM lê (não cola, não preenche):**
- `GOV-FRAMEWORK-MASTER.md`, `GOV-SCRUM.md`, `GOV-AUDITORIA.md`,
  `GOV-INTAKE.md`, `GOV-SPRINT-LIMITES.md`, `GOV-WORK-ORDER.md`,
  `GOV-DECISOES.md`, `GOV-ISSUE-FIRST.md`

**Especificações técnicas referenciadas em auditorias e implementações:**
- `SPEC-TASK-INSTRUCTIONS.md`, `SPEC-ANTI-MONOLITO.md`

---

## Convenção de Nomenclatura para `PROJETOS/COMUM/`

Todos os arquivos de `PROJETOS/COMUM/` adotarão prefixo que comunica ao PM o que
fazer com o arquivo:

| Prefixo | Significa | O PM faz o quê |
|---|---|---|
| `GOV-` | Governança normativa | Lê para entender as regras do framework |
| `TEMPLATE-` | Template preenchível | Preenche para criar artefato de projeto |
| `SESSION-` | Prompt de sessão de chat | Cola no chat para acionar fluxo guiado com HITL |
| `PROMPT-` | Prompt interno canônico | Usado por SESSIONs e boot-prompt — PM não cola diretamente |
| `SPEC-` | Especificação técnica | Lê como referência durante auditoria ou implementação |

**Mapa completo de renomeação:**

| Nome atual | Nome novo | Tipo |
|---|---|---|
| `scrum-framework-master.md` | `GOV-FRAMEWORK-MASTER.md` | GOV |
| `SCRUM-GOV.md` | `GOV-SCRUM.md` | GOV |
| `AUDITORIA-GOV.md` | `GOV-AUDITORIA.md` | GOV |
| `INTAKE-FRAMEWORK.md` | `GOV-INTAKE.md` | GOV |
| `SPRINT-LIMITS.md` | `GOV-SPRINT-LIMITES.md` | GOV |
| `WORK-ORDER-SPEC.md` | `GOV-WORK-ORDER.md` | GOV |
| `DECISION-PROTOCOL.md` | `GOV-DECISOES.md` | GOV |
| `ISSUE-FIRST-TEMPLATES.md` | `GOV-ISSUE-FIRST.md` | GOV |
| `INTAKE-TEMPLATE.md` | `TEMPLATE-INTAKE.md` | TEMPLATE |
| `AUDITORIA-REPORT-TEMPLATE.md` | `TEMPLATE-AUDITORIA-RELATORIO.md` | TEMPLATE |
| `AUDITORIA-LOG-TEMPLATE.md` | `TEMPLATE-AUDITORIA-LOG.md` | TEMPLATE |
| `TASK_INSTRUCTIONS_SPEC.md` | `SPEC-TASK-INSTRUCTIONS.md` | SPEC |
| `ANTI-MONOLITH-SPEC.md` *(novo)* | `SPEC-ANTI-MONOLITO.md` | SPEC |
| `PROMPT-INTAKE-PARA-PRD.md` | `PROMPT-INTAKE-PARA-PRD.md` *(mantém — nome já segue convenção PROMPT-)* | PROMPT |
| `AUDITORIA-PROMPT.md` | `PROMPT-AUDITORIA.md` | PROMPT |
| `prompt_epicos_issues.md` | `PROMPT-PLANEJAR-FASE.md` | PROMPT |
| `PROMPT-MONOLITH-TO-INTAKE.md` *(novo)* | `PROMPT-MONOLITO-PARA-INTAKE.md` | PROMPT |
| `TEMPLATE - SESSION-INTAKE.md` *(existente)* | `SESSION-CRIAR-INTAKE.md` | SESSION |
| `SESSION-CRIAR-PRD.md` *(novo)* | `SESSION-CRIAR-PRD.md` | SESSION |
| `TEMPLATE - SESSION-PLAN.md` *(existente)* | `SESSION-PLANEJAR-PROJETO.md` | SESSION |
| `SESSION-IMPLEMENT.md` *(novo)* | `SESSION-IMPLEMENTAR-ISSUE.md` | SESSION |
| `SESSION-AUDIT.md` *(novo)* | `SESSION-AUDITAR-FASE.md` | SESSION |
| `SESSION-REFACTOR.md` *(novo)* | `SESSION-REFATORAR-MONOLITO.md` | SESSION |
| `SESSION-PROMPTS-MAP.md` *(existente)* | `SESSION-MAPA.md` | SESSION |

`boot-prompt.md` permanece em `PROJETOS/` (não em `COMUM/`) e não é renomeado —
é o ponto de entrada do agente autônomo, não um artefato do framework para o PM.

---

## Contexto

O framework atual é funcional e já opera em produção no projeto NPBB/Plataforma
Banco do Brasil. No entanto, acumulou inconsistências estruturais que aumentam o
risco de ruído na leitura por agentes de IA e na operação manual pelo PM. Os
problemas se concentram em quatro eixos: (1) documentos legados e redundantes
que contaminam o namespace normativo, (2) lacuna de operacionalização do fluxo
anti-monolith, (3) ausência de prompts de sessão para cobertura completa do fluxo
em chat interativo, e (4) nomenclatura opaca que impede o PM de navegar o framework
sem leitura prévia de todos os arquivos.

## Escopo

### Dentro

- Renomeação de todos os arquivos de `PROJETOS/COMUM/` para o padrão de prefixo
  `GOV-` / `TEMPLATE-` / `SESSION-` / `PROMPT-` / `SPEC-`
- Atualização de todas as referências internas após renomeação
- Deprecação e remoção do documento legado `scrum-framework-master (1).md`
- Eliminação de sobreposições entre `GOV-SCRUM.md` e `GOV-FRAMEWORK-MASTER.md`
  com definição explícita de responsabilidade única por seção
- Substituição de listas de leitura paralelas em `PROMPT-INTAKE-PARA-PRD.md` e
  `PROMPT-AUDITORIA.md` por ponteiros para `boot-prompt.md`
- Consolidação do gate intake→PRD em `GOV-INTAKE.md` como fonte única
- Adição de regra operacional para `source_mode: backfilled` em `GOV-INTAKE.md`
- Substituição da cópia de critérios de `task_instruction_mode` em `GOV-SCRUM.md`
  por ponteiro para `SPEC-TASK-INSTRUCTIONS.md`
- Integração ou deprecação formal de `PROMPT-PLANEJAR-FASE.md`, incluindo correção
  do hardcode do projeto `npbb`
- Criação de `SPEC-ANTI-MONOLITO.md` com thresholds objetivos por linguagem
- Criação de `PROMPT-MONOLITO-PARA-INTAKE.md`
- Criação de `SESSION-CRIAR-PRD.md`
- Criação de `SESSION-IMPLEMENTAR-ISSUE.md`, `SESSION-AUDITAR-FASE.md`,
  `SESSION-REFATORAR-MONOLITO.md`
- Registro formal e validação de `SESSION-CRIAR-INTAKE.md` e
  `SESSION-PLANEJAR-PROJETO.md` como entregáveis do projeto
- Adição de campo opcional `decision_refs` no template de issue em
  `GOV-ISSUE-FIRST.md` para rastrear decisões R2/R3 tomadas durante
  implementação — completando o achado 1.8 que cobre também o template de
  auditoria (EPIC-F2-02)
- Atualização do `TEMPLATE-AUDITORIA-RELATORIO.md` com seção de métricas de
  complexidade estrutural e campo `decision_refs`
- Atualização do template de manifesto de fase com checklist de transição de gate
- Atualização do `boot-prompt.md` para referenciar `SESSION-MAPA.md`

### Fora

- Mudança de conteúdo ou escopo de projetos ativos que já usam o framework
- Criação de automação ou CLI além de arquivos Markdown
- Integração com Slack ou outros canais (postergado)
- Thresholds anti-monolito para linguagens além de TypeScript e Python

## Arquitetura Afetada

Todos os arquivos em `PROJETOS/COMUM/` e `PROJETOS/boot-prompt.md`.
Nenhuma mudança em código de aplicação. Projetos ativos que referenciam esses
arquivos precisam ter seus links atualizados no mesmo change set da renomeação.

## Fases Previstas

| Fase | Nome | Objetivo | Épicos | Status |
|---|---|---|---|---|
| F1 | Harmonização e Renomeação | Legado, sobreposições, drift e nomenclatura | 6 | todo |
| F2 | Anti-Monolith Enforcement | Thresholds objetivos e prompt de refatoração | 3 | todo |
| F3 | Prompts de Sessão | Cobertura completa do fluxo em chat | 5 | todo |

---

## F1 — Harmonização e Renomeação

**Objetivo:** Limpar o namespace normativo — eliminar o legado, resolver
sobreposições, corrigir drift silencioso e renomear todos os arquivos para que
o propósito de cada um seja imediatamente legível.

**Épicos previstos:**

- **EPIC-F1-01 — Renomeação para Convenção de Prefixo**
  Renomear todos os arquivos de `PROJETOS/COMUM/` conforme o mapa de renomeação
  definido na seção "Convenção de Nomenclatura". Este épico tem blast radius amplo:
  além dos arquivos de `COMUM/` e do `boot-prompt.md`, projetos ativos (ex: NPBB)
  podem ter caminhos hardcoded para os nomes atuais em arquivos de fase, épico e
  issue. O change set deve portanto:
  1. Renomear os arquivos de `PROJETOS/COMUM/`
  2. Atualizar todas as referências internas entre os arquivos de `COMUM/`
  3. Atualizar `boot-prompt.md`
  4. Auditar cada projeto ativo em `PROJETOS/` para identificar referências aos
     nomes antigos e corrigi-las antes do merge
  Nenhum merge pode ocorrer enquanto existir referência ao nome antigo em qualquer
  arquivo de projeto ativo. Este épico deve ser executado antes dos demais para
  que os épicos seguintes usem os nomes novos como referência canônica.

- **EPIC-F1-02 — Deprecação do Legado**
  Mover `scrum-framework-master (1).md` para `PROJETOS/COMUM/feito/` com nota de
  deprecação e data. Verificar se algum arquivo ativo referencia o legado após
  a renomeação e corrigir.

- **EPIC-F1-03 — Unificação de Responsabilidades e Eliminação de Drift**
  - Mapear e resolver sobreposições entre `GOV-SCRUM.md` e `GOV-FRAMEWORK-MASTER.md`
  - Substituir listas de leitura paralelas em `PROMPT-INTAKE-PARA-PRD.md` e
    `PROMPT-AUDITORIA.md` por ponteiros para `boot-prompt.md` Níveis 1–3
  - Consolidar o gate intake→PRD em `GOV-INTAKE.md` como fonte única, removendo
    redefinições dos outros dois documentos
  - Substituir a cópia dos critérios de `task_instruction_mode` em `GOV-SCRUM.md`
    por ponteiro para `SPEC-TASK-INSTRUCTIONS.md`
  - Adicionar campo opcional `decision_refs` no template de issue em
    `GOV-ISSUE-FIRST.md` para rastrear decisões R2/R3 tomadas durante
    implementação (complementa o campo homônimo previsto no template de auditoria
    em EPIC-F2-02 — achado 1.8 coberto em ambos os lados)
  - Atualizar `boot-prompt.md` para referenciar `SESSION-MAPA.md`

- **EPIC-F1-04 — Integração ou Deprecação de `PROMPT-PLANEJAR-FASE.md`**
  Avaliar se o conteúdo difere do que já existe no `boot-prompt.md`. Este épico
  tem decisão estrutural obrigatória antes de encerrar:

  - Se **complementar**: integrar à cadeia canônica com referência no
    `boot-prompt.md`, corrigir o hardcode do projeto `npbb`, e manter
    `SESSION-PLANEJAR-PROJETO.md` apontando para `PROMPT-PLANEJAR-FASE.md`
    como guia de estrutura.
  - Se **redundante**: deprecar com nota formal e atualizar
    `SESSION-PLANEJAR-PROJETO.md` para apontar diretamente para
    `GOV-ISSUE-FIRST.md` + `SPEC-TASK-INSTRUCTIONS.md` como referências de
    estrutura, eliminando a dependência do prompt depreciado.

  A decisão deve ser registrada em `GOV-DECISOES.md` antes do merge.
  `SESSION-PLANEJAR-PROJETO.md` não pode ficar apontando para arquivo depreciado
  — a atualização do SESSION é parte do DoD deste épico, independentemente do
  caminho escolhido.

- **EPIC-F1-05 — Regra Operacional para `source_mode: backfilled`**
  Adicionar seção "Intakes Retroativos" em `GOV-INTAKE.md` definindo: contextos
  válidos de origem, campos obrigatórios mesmo em backfill, e se o gate de PRD
  se aplica integralmente ou com exceções documentadas.

- **EPIC-F1-06 — Checklist de Transição de Gate no Manifesto de Fase**
  Atualizar o template de `F<N>_<PROJETO>_EPICS.md` para incluir checklist explícito
  de transição de gate (`not_ready → pending → hold/approved`) com critérios
  verificáveis por item.

**Definition of Done da F1:**
- Todos os arquivos de `PROJETOS/COMUM/` seguem a convenção de prefixo
- Todas as referências internas entre arquivos de `COMUM/` e em `boot-prompt.md`
  apontam para os nomes novos
- Nenhum arquivo de projeto ativo em `PROJETOS/` referencia nome antigo de arquivo
  de `COMUM/` (auditoria feita como parte de EPIC-F1-01)
- Nenhum documento legado no caminho de leitura padrão do agente
- Cada regra normativa existe em exatamente um documento, com referências nos demais
- Nenhum prompt canônico tem lista de leitura própria — todos apontam para `boot-prompt.md`
- Gate intake→PRD existe em um único lugar (`GOV-INTAKE.md`)
- `source_mode: backfilled` tem regra operacional documentada
- `GOV-ISSUE-FIRST.md` tem campo `decision_refs` no template de issue
- Decisão sobre `PROMPT-PLANEJAR-FASE.md` registrada em `GOV-DECISOES.md`
- `SESSION-PLANEJAR-PROJETO.md` não aponta para nenhum arquivo depreciado
- `boot-prompt.md` referencia `SESSION-MAPA.md`
- Template de manifesto de fase tem checklist de transição de gate

---

## F2 — Anti-Monolith Enforcement

**Objetivo:** Tornar o achado de monolito objetivo, mensurável e operacionalmente
rastreável, desde a detecção na auditoria até a geração do intake de refatoração.

**Dependência:** EPIC-F1-01 deve estar done antes de F2 iniciar. EPIC-F2-02
atualiza `TEMPLATE-AUDITORIA-RELATORIO.md` — nome que só existe após a renomeação
de F1-01. Iniciar F2 antes disso significa editar o nome antigo e criar divergência.

**Épicos previstos:**

- **EPIC-F2-01 — SPEC-ANTI-MONOLITO.md**
  Criar especificação com thresholds objetivos por linguagem (TypeScript/React e
  Python como primárias). Incluir limites de linhas por arquivo, linhas por função,
  exports por arquivo, imports cruzados de domínio e critérios de complexidade
  ciclomática simplificada. Definir como os thresholds se relacionam com as classes
  de achado existentes em `GOV-AUDITORIA.md`.

  Thresholds propostos (base de discussão):
  ```
  monolithic-file:
    linhas_de_codigo_logico: > 400 (aviso),  > 600 (bloqueante)
    exports_distintos:       > 7   (aviso),  > 12  (bloqueante)
    imports_de_dominios:     > 5 domínios distintos

  monolithic-function:
    linhas_por_funcao:       > 60  (aviso),  > 100 (bloqueante)
    niveis_de_aninhamento:   > 3
    parametros:              > 6
  ```

- **EPIC-F2-02 — Seção de Métricas no `TEMPLATE-AUDITORIA-RELATORIO.md`**
  Adicionar seção "Análise de Complexidade Estrutural" com tabela de
  arquivos/funções acima de threshold, tendência em relação à rodada anterior,
  e campo `decision_refs` para rastrear decisões R2/R3 formalizadas na fase
  auditada. Referenciar `SPEC-ANTI-MONOLITO.md` como critério.

- **EPIC-F2-03 — PROMPT-MONOLITO-PARA-INTAKE.md**
  Criar prompt canônico para transformar achado de monolito em intake de
  refatoração. Recebe: arquivo/função identificado, métricas observadas, relatório
  de auditoria de origem. Produz: `INTAKE-<PROJETO>-REFACTOR-<SLUG>.md` com
  `intake_kind: refactor`, rastreabilidade para auditoria, proposta de decomposição
  em módulos, critérios de compatibilidade de interface e riscos de regressão.

**Definition of Done da F2:**
- `SPEC-ANTI-MONOLITO.md` existe com thresholds objetivos por linguagem
- `TEMPLATE-AUDITORIA-RELATORIO.md` inclui seção de métricas de complexidade
- `PROMPT-MONOLITO-PARA-INTAKE.md` produz intake válido contra `TEMPLATE-INTAKE.md`
- `GOV-AUDITORIA.md` referencia `SPEC-ANTI-MONOLITO.md` como fonte de threshold

---

## F3 — Prompts de Sessão

**Objetivo:** Garantir cobertura completa do fluxo canônico em chat interativo —
do intake às instructions, e da implementação à auditoria com remediação de
monolito. Inclui registro formal dos prompts já existentes e criação dos restantes.

**Dependência de fase:** F3 só pode iniciar após F1 completamente done. EPIC-F3-01
valida os prompts existentes contra as mudanças de F1 — nomes novos, ponteiros
consolidados, gate unificado, regra de backfilled. Iniciar F3 antes de F1 done
significa validar contra um estado intermediário que mudará novamente.

**Épicos previstos:**

- **EPIC-F3-01 — Registro e Validação dos Prompts Antecipados**
  Pré-requisito: F1 completamente done.
  Registrar `SESSION-CRIAR-INTAKE.md` e `SESSION-PLANEJAR-PROJETO.md` como
  artefatos formais em `SESSION-MAPA.md`. Auditar ambos contra todas as mudanças
  produzidas em F1: nomes novos de arquivos, ponteiros para `boot-prompt.md`,
  regra de backfilled em `GOV-INTAKE.md`, gate unificado, e resultado da decisão
  de EPIC-F1-04 sobre `SESSION-PLANEJAR-PROJETO.md`. Corrigir toda divergência
  encontrada antes de prosseguir para os épicos seguintes.

- **EPIC-F3-02 — SESSION-CRIAR-PRD.md**
  Prompt de sessão para transformar um intake aprovado em PRD. Parâmetros:
  `PROJETO`, `INTAKE_PATH`, `OBSERVACOES`. Executa as duas passagens do
  `PROMPT-INTAKE-PARA-PRD.md` (validação do intake → geração do PRD) com parada
  para confirmação do PM antes de cada uma. Não grava o PRD sem aprovação explícita.

- **EPIC-F3-03 — SESSION-IMPLEMENTAR-ISSUE.md**
  Prompt de sessão para implementação de issue específica em chat. Parâmetros:
  `PROJETO`, `FASE`, `ISSUE_ID`, `ISSUE_PATH`. Confirma escopo antes de iniciar,
  solicita aprovação inline antes de cada ação material, produz checklist de DoD
  ao final. Não executa descoberta autônoma de fase ou épico.

- **EPIC-F3-04 — SESSION-AUDITAR-FASE.md**
  Prompt de sessão para auditoria de fase em chat. Parâmetros: `PROJETO`, `FASE`,
  `RODADA`, `BASE_COMMIT`. Conduz auditoria em etapas confirmadas. Ao encontrar
  monolito acima de threshold, oferece inline a opção de iniciar
  `PROMPT-MONOLITO-PARA-INTAKE.md`. Grava relatório e atualiza AUDIT-LOG ao final.

- **EPIC-F3-05 — SESSION-REFATORAR-MONOLITO.md**
  Prompt de sessão para refatoração de monolito como mini-projeto. Parâmetros:
  `PROJETO`, `INTAKE_PATH`, `ARQUIVO_ALVO`, `AUDIT_REF`. Conduz: validação do
  intake → PRD de refatoração → fases de decomposição → execução issue a issue →
  auditoria de compatibilidade de interface.

**Definition of Done da F3:**
- `SESSION-MAPA.md` lista todos os seis prompts de sessão com status atualizado
- Todos os prompts de sessão seguem o padrão: parâmetros + ponteiro para
  `boot-prompt.md` + protocolo HITL + regras inegociáveis
- Nenhum prompt de sessão duplica conteúdo normativo — todos usam ponteiros
- `boot-prompt.md` referencia `SESSION-MAPA.md` como ponto de entrada para chat
- `GOV-SCRUM.md` registra a distinção entre modo agente autônomo e modo sessão de chat
- Fluxo completo (intake → instructions → implementação → auditoria) operável
  inteiramente via prompts de sessão sem adaptação manual pelo PM

---

## Indicadores de Sucesso

- Todos os arquivos de `PROJETOS/COMUM/` com prefixo que comunica propósito
- Zero documentos legados ativos no caminho de leitura canônica do agente
- 100% das seções normativas com responsabilidade de documento única
- Fluxo completo intake→instructions executável em chat sem adaptação manual
- Thresholds de monolito utilizados em pelo menos uma rodada de auditoria de
  projeto ativo
- PM novo consegue identificar o que fazer com cada arquivo sem leitura prévia
  de toda a documentação

## Riscos

- **Risco de legado `(1)` inexistente:** o achado 1.1 descreve `scrum-framework-master (1).md`
  como arquivo legado ativo a ser depreciado. Nos arquivos reais de `PROJETOS/COMUM/`
  apenas `scrum-framework-master.md` (v1.4, status `active`) foi localizado — o arquivo
  com parênteses não foi confirmado. Antes de executar EPIC-F1-02, verificar se
  `scrum-framework-master (1).md` existe em outro diretório do repositório. Se não
  existir, EPIC-F1-02 se reduz a uma verificação e pode ser fechado sem ação material.
  arquivos de `PROJETOS/COMUM/` quebra referências em projetos ativos. Mitigação:
  EPIC-F1-01 deve atualizar todas as referências no mesmo change set; cada projeto
  ativo deve ter seus arquivos auditados antes do merge.
- **Risco de threshold inadequado:** thresholds sem validação empírica podem gerar
  falsos positivos. Mitigação: F2 inclui rodada de calibração contra projeto ativo
  antes de fixar valores.
- **Risco de prompt de sessão subutilizado:** sem tabela de decisão
  "sessão vs agente autônomo", o PM pode não saber quando usar qual modo.
  Mitigação: `SESSION-MAPA.md` inclui tabela de decisão.

## Não-Objetivos

- Não é objetivo migrar projetos ativos para novos templates
- Não é objetivo criar automação ou CLI além de arquivos Markdown
- Não é objetivo revisar conteúdo substantivo de qualquer PRD de projeto ativo
- Não é objetivo definir thresholds para linguagens além de TypeScript e Python

## Referência de Intake

> Este PRD foi gerado a partir de análise crítica direta dos documentos do
> framework, sem intake formal prévio. Um `INTAKE-FRAMEWORK2.0.md` formal com
> `source_mode: backfilled` deve ser gerado a partir deste PRD antes do início
> de F1, usando `SESSION-CRIAR-INTAKE.md` com o conteúdo deste documento como
> `CONTEXT`.

> **Histórico de versões:**
> - v1.0 — PRD inicial: 10 achados, 3 fases, 10 épicos
> - v1.1 — +5 achados (1.11–1.15): listas paralelas, gate triplicado, backfilled,
>   cópia SCRUM-GOV, prompts sem rastreabilidade. F1: +1 épico. F3: +EPIC-F3-00.
> - v1.2 — +1 achado (1.16 nomenclatura). Fluxo canônico completo adicionado.
>   Convenção de prefixo definida com mapa completo de renomeação. F1 reorganizada
>   e expandida para 6 épicos com EPIC-F1-01 de renomeação como pré-requisito dos
>   demais. F3 reorganizada para 5 épicos com SESSION-CRIAR-PRD como novo entregável.
> - v1.3 — Correções estruturais: frontmatter corrigido para FRAMEWORK2.0. Blast
>   radius de EPIC-F1-01 explicitado com obrigatoriedade de auditoria de projetos
>   ativos antes do merge. Dependência F3→F1 declarada explicitamente em F3-01.
>   Bifurcação de EPIC-F1-04 resolvida com dois caminhos e DoD fechado para ambos.
>   Campo `decision_refs` adicionado ao escopo de EPIC-F1-03 e ao DoD de F1.
>   Nota explicativa adicionada para PROMPT-INTAKE-PARA-PRD.md na tabela de renomeação.
> - v1.4 — Quatro correções: título do documento corrigido para FRAMEWORK2.0.
>   `source_mode` no frontmatter corrigido de `original` para `backfilled`.
>   Diagrama de fluxo com nota condicional sobre `PROMPT-PLANEJAR-FASE.md`.
>   Dependência de F2 em EPIC-F1-01 declarada explicitamente.
> - v1.5 — Validação cruzada contra arquivos reais de `PROJETOS/COMUM/`. Dois
>   ajustes: nomes dos arquivos SESSION corrigidos no mapa de renomeação
>   (`TEMPLATE - SESSION-INTAKE.md` e `TEMPLATE - SESSION-PLAN.md` eram listados
>   pelos seus `doc_id` internos). Risco adicionado sobre `scrum-framework-master (1).md`
>   não confirmado nos arquivos reais — EPIC-F1-02 requer verificação antes de execução.
>   Diagrama de fluxo com nota condicional sobre `PROMPT-PLANEJAR-FASE.md`
>   (dependente do resultado de EPIC-F1-04). Dependência de F2 em EPIC-F1-01
>   declarada explicitamente para evitar edição de nome antigo.
