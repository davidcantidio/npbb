---
doc_id: "PRD-FRAMEWORK-GOV-v1.0.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-09"
project: "FRAMEWORK-GOV"
intake_kind: "refactor"
source_mode: "original"
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

# CRÍTICA DO FRAMEWORK + PRD-FRAMEWORK-GOV

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

O arquivo `PROJETOS/COMUM/prompt_epicos_issues.md` existe como prompt operacional
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

## Resumo dos Pontos por Prioridade

| # | Ponto | Tipo | Prioridade |
|---|---|---|---|
| 1.1 | Documento legado ativo | Risco de ruído | Crítica |
| 1.2 | Dualidade de status | Inconsistência | Alta |
| 1.3 | Sobreposição SCRUM-GOV / master | Redundância | Alta |
| 1.5 | Anti-monolith sem threshold | Lacuna objetiva | Alta |
| 1.7 | Ausência de prompts de sessão | Lacuna operacional | Alta |
| 1.6 | Monolith → PRD não operacionalizado | Lacuna de fluxo | Média |
| 1.4 | prompt_epicos_issues.md órfão | Desconexão | Média |
| 1.8 | DECISION-PROTOCOL desconectado | Gap de rastreabilidade | Média |
| 1.9 | Template sem métricas de monolito | Lacuna de template | Baixa |
| 1.10 | Gate sem checklist de transição | Ambiguidade | Baixa |

---

# PARTE 2 — PRD-FRAMEWORK-GOV

## Objetivo

Adequar o framework de governança `PROJETOS/COMUM/` para eliminar inconsistências,
lacunas operacionais e ruídos identificados na análise crítica, tornando o fluxo
`Intake → PRD → Fases → Épicos → Issues → Tasks → Auditorias` mais assertivo,
rastreável e resistente à interpretação subjetiva.

O projeto usa o próprio framework como método de execução.

## Contexto

O framework atual é funcional e já opera em produção no projeto NPBB/Plataforma
Banco do Brasil. No entanto, acumulou inconsistências estruturais que aumentam o
risco de ruído na leitura por agentes de IA e na operação manual pelo PM. Os
problemas identificados se concentram em três eixos: (1) documentos legados e
redundantes que contaminam o namespace normativo, (2) lacuna de operacionalização
do fluxo anti-monolith, e (3) ausência de prompts de sessão para uso em chat
interativo.

## Escopo

### Dentro

- Deprecação e remoção do documento legado `scrum-framework-master (1).md`
- Eliminação de sobreposições entre `SCRUM-GOV.md` e `scrum-framework-master.md`
  com definição explícita de responsabilidade única por seção
- Integração do `prompt_epicos_issues.md` na cadeia canônica ou deprecação formal
- Definição de thresholds objetivos para `monolithic-file` e `monolithic-function`
  em documento normativo dedicado (`ANTI-MONOLITH-SPEC.md`)
- Criação de prompt operacional `PROMPT-MONOLITH-TO-INTAKE.md` para transformar
  achado de monolito em intake de refatoração estruturado
- Criação de três prompts de sessão de chat: `SESSION-IMPLEMENT.md`,
  `SESSION-AUDIT.md`, `SESSION-REFACTOR.md`
- Atualização do `AUDITORIA-REPORT-TEMPLATE.md` com seção de métricas de monolito
  e campo de verificação de decisões registradas
- Atualização do template de manifesto de fase com checklist de transição de gate

### Fora

- Mudança de conteúdo ou escopo de projetos ativos que já usam o framework
- Criação de nova ferramenta de automação ou CLI
- Integração com Slack ou outros canais (postergado)
- Revisão de INTAKE-TEMPLATE ou PRD-TEMPLATE além dos campos de monolito e decisão

## Arquitetura Afetada

Todos os arquivos em `PROJETOS/COMUM/`. Nenhuma mudança em código de aplicação.
Impacto direto nos projetos ativos que referenciam esses arquivos normativos.

## Fases Previstas

| Fase | Nome | Objetivo | Status |
|---|---|---|---|
| F1 | Harmonização Normativa | Eliminar legado, ruído e sobreposições | todo |
| F2 | Anti-Monolith Enforcement | Thresholds objetivos e prompt de refatoração | todo |
| F3 | Prompts de Sessão | Prompts de chat para implement, audit e refactor | todo |

---

## F1 — Harmonização Normativa

**Objetivo:** Limpar o namespace normativo do framework, eliminando documentos
legados, resolvendo sobreposições e garantindo que cada documento tenha
responsabilidade única e seja referenciado corretamente na cadeia canônica.

**Épicos previstos:**

- **EPIC-F1-01 — Deprecação do Legado**
  Mover `scrum-framework-master (1).md` para `PROJETOS/COMUM/feito/` com nota de
  deprecação. Verificar se algum arquivo ativo referencia o legado e corrigir.

- **EPIC-F1-02 — Unificação de Responsabilidades SCRUM-GOV / master**
  Mapear todas as seções sobrepostas entre os dois documentos canônicos. Para cada
  sobreposição, definir qual documento é a fonte de verdade e substituir o outro
  por referência explícita. Atualizar o `boot-prompt.md` para refletir a hierarquia
  correta de leitura.

- **EPIC-F1-03 — Integração ou Deprecação de prompt_epicos_issues.md**
  Avaliar se o conteúdo de `prompt_epicos_issues.md` é diferente do que já existe
  no `boot-prompt.md`. Se for complementar, integrá-lo à cadeia canônica com
  referência no `boot-prompt.md`. Se for redundante, deprecar com nota formal.

- **EPIC-F1-04 — Checklist de Transição de Gate no Manifesto de Fase**
  Atualizar o template de `F<N>_<PROJETO>_EPICS.md` para incluir checklist explícito
  de transição de gate (`not_ready → pending → hold/approved`) com critérios
  verificáveis por item.

**Definition of Done da F1:**
- Nenhum documento legado no caminho de leitura padrão do agente
- Cada regra normativa existe em exatamente um documento com referências nos demais
- `boot-prompt.md` referencia corretamente todos os prompts operacionais ativos
- Template de manifesto de fase tem checklist de transição de gate

---

## F2 — Anti-Monolith Enforcement

**Objetivo:** Tornar o achado de monolito objetivo, mensurável e operacionalmente
rastreável, desde a detecção na auditoria até a geração do intake de refatoração.

**Épicos previstos:**

- **EPIC-F2-01 — ANTI-MONOLITH-SPEC.md**
  Criar documento normativo com thresholds objetivos por linguagem (TypeScript/React
  e Python como primárias). Incluir: limites de linhas por arquivo, limites de
  linhas por função, limite de exports por arquivo, limite de imports cruzados de
  domínio, critérios de complexidade ciclomática simplificada. Definir como esses
  thresholds se relacionam com as classes de achado existentes.

  Thresholds propostos (base de discussão):
  ```
  monolithic-file:
    linhas_de_codigo_logico: > 400  (aviso), > 600 (bloqueante)
    exports_distintos:       > 7    (aviso), > 12  (bloqueante)
    imports_de_dominios:     > 5 dominios distintos

  monolithic-function:
    linhas_por_funcao:       > 60   (aviso), > 100 (bloqueante)
    niveis_de_aninhamento:   > 3
    parametros:              > 6
  ```

- **EPIC-F2-02 — Seção de Métricas no Template de Auditoria**
  Adicionar ao `AUDITORIA-REPORT-TEMPLATE.md` uma seção "Análise de Complexidade
  Estrutural" com tabela de arquivos/funções acima de threshold, tendência em
  relação à rodada anterior, e campo `decision_refs` para rastrear decisões R2/R3
  formalizadas durante a fase auditada.

- **EPIC-F2-03 — PROMPT-MONOLITH-TO-INTAKE.md**
  Criar prompt canônico para transformar um achado de monolito identificado em
  auditoria num intake de refatoração completo. O prompt deve:
  - Receber como input: arquivo/função identificado, métricas observadas, relatório
    de auditoria de origem
  - Produzir: `INTAKE-<PROJETO>-REFACTOR-<SLUG>.md` com `intake_kind: refactor`,
    rastreabilidade para auditoria de origem, proposta de decomposição em módulos,
    critérios de compatibilidade de interface e riscos de regressão
  - Referenciar `ANTI-MONOLITH-SPEC.md` como critério normativo

**Definition of Done da F2:**
- `ANTI-MONOLITH-SPEC.md` existe com thresholds objetivos por linguagem
- Template de auditoria inclui seção de métricas de complexidade
- `PROMPT-MONOLITH-TO-INTAKE.md` existe e produz intake válido contra o template
- `AUDITORIA-GOV.md` referencia `ANTI-MONOLITH-SPEC.md` como fonte de threshold

---

## F3 — Prompts de Sessão

**Objetivo:** Criar prompts operacionais para uso em sessões de chat interativo,
cobrindo os três modos principais de trabalho: implementação de issue, auditoria
de fase e refatoração de monolito como mini-projeto.

**Épicos previstos:**

- **EPIC-F3-01 — SESSION-IMPLEMENT.md**
  Prompt de sessão para implementação de issue em chat. Diferenças em relação
  ao `boot-prompt.md`:
  - Recebe como parâmetro explícito: projeto, fase, issue ID
  - Confirma escopo com o PM antes de iniciar execução
  - Solicita aprovação inline antes de cada ação material (criar arquivo, modificar
    arquivo existente, executar comando)
  - Não executa descoberta autônoma de fase/épico — o PM já informou o alvo
  - Produz checklist de DoD ao final para confirmação do PM

- **EPIC-F3-02 — SESSION-AUDIT.md**
  Prompt de sessão para auditoria de fase em chat. Diferenças em relação ao
  prompt canônico de auditoria:
  - Recebe: projeto, fase, rodada de auditoria (ex: R01), commit base ou "worktree"
  - Conduz a auditoria em etapas confirmadas: leitura de artefatos, listagem de
    achados preliminares, confirmação antes de emitir veredito
  - Ao encontrar monolito acima de threshold, oferece ao PM a opção de já iniciar
    o fluxo `PROMPT-MONOLITH-TO-INTAKE.md` inline
  - Produz relatório no formato canônico e atualiza AUDIT-LOG no final

- **EPIC-F3-03 — SESSION-REFACTOR.md**
  Prompt de sessão para conduzir refatoração de monolito como mini-projeto. Recebe
  o intake gerado por `PROMPT-MONOLITH-TO-INTAKE.md` e conduz:
  - Validação do intake antes de iniciar
  - Geração do PRD de refatoração (escopo mínimo, rollback, testes de regressão)
  - Fatiamento em épicos e issues de decomposição
  - Execução issue a issue com confirmações inline
  - Auditoria final de compatibilidade de interface

**Definition of Done da F3:**
- Os três prompts de sessão existem em `PROJETOS/COMUM/`
- Cada prompt tem seção "Parâmetros obrigatórios" clara e seção "Confirmações HITL"
- `boot-prompt.md` referencia os três prompts de sessão como alternativa para uso
  em chat interativo
- `SCRUM-GOV.md` registra a distinção entre "modo agente autônomo" e "modo sessão
  de chat" como variação operacional válida

---

## Indicadores de Sucesso

- Zero documentos legados ativos no caminho de leitura canônica do agente
- 100% das seções normativas com responsabilidade de documento única
- Thresholds de monolito definidos e utilizados em pelo menos uma rodada de
  auditoria de projeto ativo
- Prompts de sessão utilizados com sucesso em pelo menos uma sessão de chat
  de implementação e uma de auditoria

## Riscos

- **Risco de regressão normativa:** alterar `SCRUM-GOV.md` ou `boot-prompt.md`
  pode quebrar agentes já em execução em projetos ativos. Mitigação: cada mudança
  deve ser versionada e comunicada antes de ser merged.
- **Risco de threshold inadequado:** thresholds definidos sem validação empírica
  podem gerar falsos positivos ou negativos. Mitigação: F2 deve incluir uma rodada
  de calibração contra pelo menos um projeto ativo antes de fixar os valores.
- **Risco de prompt de sessão subutilizado:** sem documentação de quando usar
  sessão vs agente autônomo, o PM pode continuar usando o boot-prompt mesmo em
  contextos onde o SESSION-* seria mais adequado. Mitigação: adicionar tabela de
  decisão no `boot-prompt.md`.

## Não-Objetivos

- Não é objetivo deste PRD migrar projetos ativos para novos templates
- Não é objetivo criar automação ou tooling além de arquivos Markdown
- Não é objetivo revisar o conteúdo substantivo de qualquer PRD de projeto ativo
- Não é objetivo definir thresholds para linguagens além de TypeScript e Python

## Referência de Intake

> Este PRD foi gerado a partir de análise crítica direta dos documentos do framework,
> sem intake formal prévio. Para o projeto FRAMEWORK-GOV, este documento serve
> simultaneamente como intake e PRD inicial, dado o escopo de refatoração bem
> delimitado. Um `INTAKE-FRAMEWORK-GOV.md` formal deve ser gerado a partir deste
> PRD antes do início de F1.
