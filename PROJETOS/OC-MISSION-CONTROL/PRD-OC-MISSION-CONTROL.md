---
doc_id: "PRD-OC-MISSION-CONTROL.md"
version: "2.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-20"
project: "OC-MISSION-CONTROL"
intake_kind: "new-product"
source_mode: "backfilled"
origin_project: "OPENCLAW-LEGADO"
origin_phase: "F0-F11"
origin_audit_id: "nao_aplicavel"
origin_report_path: "assistant-brain/PRD/PRD-MASTER.md"
product_type: "platform-capability"
delivery_surface: "backend-api"
business_domain: "governanca"
criticality: "critica"
data_sensitivity: "restrita"
integrations:
  - "assistant-brain"
  - "control-plane"
  - "ops-api"
  - "openclaw-gateway"
  - "policy-engine"
  - "postgres"
  - "convex"
  - "telegram"
  - "slack"
  - "litellm"
  - "openrouter"
change_type: "novo-produto"
audit_rigor: "strict"
---

# PRD - OC-MISSION-CONTROL

> Origem: [INTAKE-OC-MISSION-CONTROL.md](PROJETOS/OC-MISSION-CONTROL/INTAKE-OC-MISSION-CONTROL.md)
>
> Este PRD traduz o intake retroativo do Mission Control para uma trilha inicial
> de entrega observável e reproduzível: catálogo OpenRouter, topologia
> multi-agent, bootstrap host-side e validação operacional.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OC-MISSION-CONTROL.md](PROJETOS/OC-MISSION-CONTROL/INTAKE-OC-MISSION-CONTROL.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-20
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: OC-MISSION-CONTROL
- **Tese em 1 frase**: tornar o OpenClaw operável como Mission Control governado, com agentes especializados e modelos roteados por OpenRouter de forma reproduzível e auditável.
- **Valor esperado em 3 linhas**:
  - explicitar qual agente atende qual tipo de tarefa e com qual modelo
  - reduzir bootstrap manual do runtime local/host-side para um fluxo repetível
  - preparar a evolução futura de roteamento governado sem misturar host toolkit com backlog financeiro

## 2. Problema ou Oportunidade

- **Problema atual**: o runtime OpenClaw ainda não nasce com uma topologia explícita de agentes especializados, catálogo OpenRouter e binding operacional reproduzível.
- **Evidencia do problema**: o intake já exige roteamento de modelos com trilha requested/effective, mas o repositório atual só cobre parcialmente o bootstrap host-side e não materializa uma configuração multi-agent utilizável.
- **Custo de nao agir**: escolha de modelo continua implícita, delegação entre agentes permanece ad hoc e o bootstrap de ambiente depende de intervenção manual difícil de auditar.
- **Por que agora**: o repositório já contém o ponto técnico de bootstrap host-side e o OpenClaw 2026.2.14 já suporta `agents.list[].model`, `bindings[]` e OpenRouter nativamente.

## 3. Publico e Operadores

- **Usuario principal**: operador de runtime que precisa subir e manter um OpenClaw governado e reproduzível
- **Usuario secundario**: PM, arquitetura e auditoria que precisam entender como cada tarefa é roteada
- **Operador interno**: toolkit host-side (`bin/install-host.sh`, `src/nemoclaw-host/helper.js`) e runtime OpenClaw
- **Quem aprova ou patrocina**: mantenedor do produto/plataforma OpenClaw

## 4. Jobs to be Done

- **Job principal**: operar o OpenClaw com um trio especializado de agentes (`planner`, `builder`, `auditor`) apoiado por OpenRouter, mantendo `main` como fallback/compatibilidade.
- **Jobs secundarios**:
  - bootstrapar a configuração `~/.openclaw/openclaw.json` e a topologia de workspaces sem drift
  - rotear o ingresso do Telegram para o agente `planner`
  - permitir delegação explícita de planejamento -> execução -> auditoria
- **Tarefa atual que sera substituida**: editar manualmente config, modelos, bindings e workspaces toda vez que o ambiente precisa ser refeito

## 5. Escopo

### Dentro

- topologia multi-agent com `main`, `planner`, `builder` e `auditor`
- catálogo OpenRouter com aliases e fallbacks definidos no config
- binding Telegram inicial para `planner`
- bootstrap host-side reproduzível do config local e do sync remoto
- validação operacional e runbook curto no repositório

### Fora

- serviço de domínio `/router/decide` com persistência `requested_model/effective_model`
- persistência de `llm_run`, `router_decision`, `trace_snapshot` e budget por `trace_id`
- múltiplos bots/canais por agente no v1
- rollout financeiro ou execução real da vertical trading

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: deixar explícita e repetível a primeira topologia governada de agentes/modelos do Mission Control
- **Metricas leading**:
  - `~/.openclaw/openclaw.json` materializa `main/planner/builder/auditor` em ambiente novo
  - o catálogo OpenRouter contém os modelos-alvo e aliases estáveis
  - `planner` tem binding Telegram configurado no runtime
- **Metricas lagging**:
  - `bin/validate-host.sh` confirma a topologia local sem regressão do toolkit host-side
  - operadores deixam de reconfigurar manualmente OpenClaw após reinstalação/restore
  - a documentação operacional reflete corretamente o roteamento tarefa -> agente -> modelo
- **Criterio minimo para considerar sucesso**: um ambiente novo consegue reproduzir a topologia parcial OpenRouter e o binding Telegram do `planner` sem secrets em Git

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**:
  - usar capacidades nativas do OpenClaw 2026.2.14 (`agents.list[].model`, `bindings[]`, catálogo de modelos)
  - não versionar segredos nem credenciais no Git
  - evitar conflito com a porta `18789`, já reservada ao dashboard remoto host-side
- **Restricoes operacionais**:
  - `main` permanece como fallback/compatibilidade e não entra no OpenRouter por padrão
  - o Telegram do v1 ingressa sempre em `planner`; `builder` e `auditor` entram por delegação/manual
  - o toolkit host-side não pode perder a capacidade de subir o dashboard remoto atual
- **Restricoes legais ou compliance**:
  - secrets apenas em ambiente local/host.env, auth profile ou config fora do Git
  - nenhum token real em docs versionadas
- **Restricoes de prazo**: entregar a trilha inicial reproduzível sem esperar a evolução completa do roteador de domínio do intake
- **Restricoes de design ou marca**: não há UI dedicada como driver principal; o foco é operação e governança

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**:
  - `src/nemoclaw-host/*`
  - `bin/install-host.sh`
  - `bin/validate-host.sh`
  - `README.md`
  - `~/.openclaw/openclaw.json`
- **Sistemas externos impactados**:
  - OpenRouter
  - Telegram
  - OpenShell sandbox/gateway
- **Dados de entrada necessarios**:
  - modelos alvo por agente
  - `OPENROUTER_API_KEY` local-only quando desejado
  - `OPENCLAW_TELEGRAM_*` local-only quando desejado
  - sandbox/model selection atual do host-side quando houver sync remoto
- **Dados de saida esperados**:
  - config OpenClaw multi-agent reproduzível
  - bindings e workspaces gerados
  - validações locais documentadas e automatizadas

## 9. Arquitetura Geral do Projeto

> Visão geral de impacto arquitetural (detalhes por feature na seção Features)

- **Backend**: `helper.js` passa a materializar topologia multi-agent/OpenRouter, inclusive merge em config local e remota
- **Frontend**: nao aplicavel; a superficie operacional segue CLI, dashboard e canais confiáveis
- **Banco/migracoes**: nao aplicavel nesta fase
- **Observabilidade**: `validate-host.sh`, `README.md` e artefatos de fase tornam o bootstrap auditável
- **Autorizacao/autenticacao**: OpenRouter e Telegram continuam fora do Git; a configuração só referencia variáveis locais
- **Rollout**: bootstrap local primeiro, sync remoto preservando o dashboard host-side já existente

## 10. Riscos Globais

- **Risco de produto**: esta fase cobre só a primeira fatia do Mission Control e não fecha o roteador de domínio prometido pelo intake
- **Risco tecnico**: drift entre topologia local e sync remoto, ou colisão de porta com o dashboard host-side
- **Risco operacional**: ambiente ficar “configurado mas não autenticado” quando `OPENROUTER_API_KEY` ou token do Telegram não estiverem presentes
- **Risco de dados**: secrets inadvertidamente colocados em Git ou em docs versionadas
- **Risco de adocao**: operadores continuarem usando só o `main` e não explorarem o trio especializado

## 11. Nao-Objetivos

- não implementar ainda o roteamento requested/effective persistido em banco
- não introduzir múltiplos canais automáticos além do Telegram no v1
- não substituir integralmente o agente `main`
- não expandir o escopo para trading, memory store ou budget engine

## 12. Features do Projeto

### Feature 1: Fundacao do projeto

#### Objetivo de Negocio

Manter o scaffold do projeto e a estrutura issue-first rastreável para as fases seguintes.

#### Comportamento Esperado

O PM e a engenharia conseguem navegar no projeto, seguir wrappers locais e localizar fases, épicos e issues sem drift estrutural.

#### Criterios de Aceite

- [ ] intake, PRD, audit log e wrappers locais existem
- [ ] F1-FUNDACAO permanece como bootstrap documental canônico
- [ ] a fase F1 referencia corretamente o PRD e a issue bootstrap

#### Dependencias com Outras Features

- nenhuma

#### Riscos Especificos

- drift documental se o PRD evoluir e a fundação permanecer desatualizada

#### Fases de Implementacao

1. Scaffold e wrappers
2. Fase F1 e issue bootstrap
3. Auditoria-base da fundação

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | nao aplicavel | nenhuma migracao |
| Backend | nao aplicavel | somente artefatos documentais |
| Frontend | nao aplicavel | nenhum impacto |
| Testes | smoke documental | consistencia de paths e wrappers |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | estabilizar scaffold e wrappers | 3 | - |
| T2 | manter rastreabilidade da fundação | 2 | T1 |

### Feature 2: Rotear tarefas por agentes especializados com OpenRouter

#### Objetivo de Negocio

Reduzir a escolha manual implícita de modelo e deixar explícito qual agente executa cada tipo de tarefa.

#### Comportamento Esperado

O runtime passa a expor `planner`, `builder` e `auditor` com modelos e fallbacks definidos, enquanto `main` permanece como fallback compatível.

#### Criterios de Aceite

- [ ] `agents.list[]` materializa `main`, `planner`, `builder` e `auditor`
- [ ] `agents.defaults.models` contém o catálogo OpenRouter com aliases estáveis
- [ ] `planner`, `builder` e `auditor` usam OpenRouter com modelos/fallbacks definidos
- [ ] `planner` consegue delegar para `builder` e `auditor`

#### Dependencias com Outras Features

- Feature 3: para bootstrap reproduzível em ambiente novo

#### Riscos Especificos

- o catálogo OpenRouter virar allowlist sem incluir o modelo primário de `main`
- configuração ficar correta no papel mas sem auth real disponível

#### Fases de Implementacao

1. Catálogo OpenRouter e aliases
2. Topologia `main/planner/builder/auditor`
3. Bindings e delegação mínima
4. Verificação local do runtime

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | nao aplicavel | nenhuma migracao |
| Backend | `~/.openclaw/openclaw.json` | `agents.defaults.models`, `agents.list[]`, `bindings[]`, `channels.telegram.*` |
| Frontend | dashboard/CLI | inspeção via `openclaw agents list --bindings` e `openclaw models status` |
| Testes | validação operacional | checagem de agentes, bindings e catálogo |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | definir catálogo OpenRouter e aliases | 2 | - |
| T2 | configurar topologia multi-agent e fallbacks | 3 | T1 |
| T3 | validar delegação e binding Telegram | 2 | T2 |

### Feature 3: Bootstrap host-side reproduzível do Mission Control

#### Objetivo de Negocio

Eliminar bootstrap manual do `~/.openclaw` e alinhar ambiente local com o sync remoto sem vazar segredos para o repositório.

#### Comportamento Esperado

`install-host.sh` e `helper.js` passam a materializar a topologia OpenClaw/OpenRouter e `validate-host.sh` confirma que a configuração local está pronta.

#### Criterios de Aceite

- [ ] `helper.js` faz merge da topologia multi-agent/OpenRouter no config local
- [ ] `helper.js` preserva a sincronização remota do dashboard host-side
- [ ] `install-host.sh` chama o bootstrap local idempotente
- [ ] `config/host.env.example` documenta apenas placeholders locais, sem secrets versionados

#### Dependencias com Outras Features

- Feature 2: depende dos modelos/agentes definidos

#### Riscos Especificos

- instalar o toolkit sem `openclaw` disponível e não materializar a topologia
- romper o fluxo remoto existente ao tocar no helper do dashboard

#### Fases de Implementacao

1. Merge de config local/remoto no helper
2. Chamada automática via install-host
3. Placeholders e defaults em `host.env`
4. Verificação de regressão do fluxo host-side

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | nao aplicavel | nenhuma migracao |
| Backend | `src/nemoclaw-host/*`, `bin/install-host.sh` | bootstrap local e sync remoto |
| Frontend | dashboard remoto | preservar o uso de `127.0.0.1:18789` |
| Testes | validação host-side | checagem de config, agentes e workspaces |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | tornar o helper multi-agent/OpenRouter | 3 | - |
| T2 | acoplar bootstrap ao install-host | 2 | T1 |
| T3 | validar regressão do dashboard host-side | 2 | T2 |

### Feature 4: Operar e validar o fluxo híbrido

#### Objetivo de Negocio

Dar à operação um runbook curto e uma validação objetiva do que significa “ambiente pronto” para o trio especializado.

#### Comportamento Esperado

O operador consegue entender quando usar `planner`, `builder` e `auditor`, como o Telegram entra no fluxo e como verificar a configuração.

#### Criterios de Aceite

- [ ] README descreve bootstrap, matriz tarefa -> agente e checks manuais
- [ ] `validate-host.sh` valida a topologia local sem depender de secret real
- [ ] a fase F2 possui épicos/issues que rastreiam configuração, automação e validação operacional

#### Dependencias com Outras Features

- Feature 2
- Feature 3

#### Riscos Especificos

- docs refletirem comportamento diferente do bootstrap real
- validação exigir token real e ficar inutilizável em ambiente novo

#### Fases de Implementacao

1. Runbook operacional curto
2. Checks automatizados no validate-host
3. Fase/épicos/issues de acompanhamento

#### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | nao aplicavel | nenhuma migracao |
| Backend | `bin/validate-host.sh` | validações locais adicionais |
| Frontend | README/docs | runbook operacional |
| Testes | smoke operacional | checklist executável e inspeção por CLI |

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | documentar o fluxo híbrido | 2 | - |
| T2 | automatizar validações locais | 2 | T1 |
| T3 | manter rastreabilidade em fase/épicos/issues | 1 | T2 |

## 13. Estrutura de Fases

## Fase 1: F1-FUNDACAO

- **Objetivo**: consolidar o scaffold inicial do projeto.
- **Features incluídas**:
  - Feature 1
- **Gate de saída**: o projeto tem base documental íntegra e pronta para as fases seguintes.
- **Critérios de aceite**:
  - intake, PRD e audit log presentes
  - wrappers locais existentes
  - phase/epic/issue bootstrap rastreáveis

### Épicos da Fase 1

| Épico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F1-01 | Feature 1 | todo | 5 |

## Fase 2: F2-OPENROUTER-E-AGENTES

- **Objetivo**: tornar reproduzível a primeira topologia governada de agentes/modelos do Mission Control.
- **Features incluídas**:
  - Feature 2
  - Feature 3
  - Feature 4
- **Gate de saída**: a topologia `main/planner/builder/auditor` existe, o bootstrap host-side a materializa e a validação operacional a confirma.
- **Critérios de aceite**:
  - catálogo OpenRouter e aliases presentes
  - `planner` possui binding Telegram de ingresso
  - `install-host.sh` materializa o bootstrap local
  - `validate-host.sh` confirma a topologia local

### Épicos da Fase 2

| Épico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F2-01 | Feature 2 | todo | 7 |
| EPIC-F2-02 | Feature 3 | todo | 7 |
| EPIC-F2-03 | Feature 4 | todo | 5 |

## 14. Épicos

### Épico: Fundacao do projeto

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: manter o scaffold inicial e a estrutura issue-first íntegros.
- **Resultado de Negócio Mensurável**: o projeto continua navegável e pronto para fases seguintes.
- **Contexto Arquitetural**: wrappers, fase bootstrap e issue inicial.
- **Definition of Done**:
  - [ ] F1 permanece consistente com o PRD
  - [ ] issue bootstrap continua rastreável

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO | Estabilizar scaffold inicial do projeto | 3 | todo | Feature 1 |

### Épico: Catalogo OpenRouter e topologia multi-agent

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: explicitar agentes especializados, modelos e fallbacks no runtime OpenClaw.
- **Resultado de Negócio Mensurável**: o operador visualiza e usa `planner`, `builder` e `auditor` sem escolher modelos manualmente em cada tarefa.
- **Contexto Arquitetural**: `~/.openclaw/openclaw.json`, `agents.defaults.models`, `agents.list[]`, `bindings[]`.
- **Definition of Done**:
  - [ ] catálogo OpenRouter presente
  - [ ] agentes especializados configurados
  - [ ] binding Telegram do `planner` materializado

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS | Configurar catálogo OpenRouter e agentes especializados | 5 | todo | Feature 2 |

### Épico: Automacao host-side do bootstrap OpenClaw

- **ID**: EPIC-F2-02
- **Fase**: F2
- **Feature de Origem**: Feature 3
- **Objetivo**: materializar a topologia local/remota a partir do toolkit host-side sem secrets no Git.
- **Resultado de Negócio Mensurável**: reinstalar o toolkit recria a topologia OpenClaw esperada sem edição manual do config.
- **Contexto Arquitetural**: `src/nemoclaw-host/helper.js`, `bin/install-host.sh`, `config/host.env.example`.
- **Definition of Done**:
  - [ ] helper faz merge local e remoto
  - [ ] install-host aciona bootstrap local
  - [ ] placeholders locais documentam os inputs necessários

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW | Automatizar bootstrap host-side do OpenClaw | 5 | todo | Feature 3 |

### Épico: Documentacao e validacao operacional

- **ID**: EPIC-F2-03
- **Fase**: F2
- **Feature de Origem**: Feature 4
- **Objetivo**: descrever o fluxo híbrido e automatizar a verificação de prontidão local.
- **Resultado de Negócio Mensurável**: o operador sabe quando usar cada agente e consegue confirmar a topologia sem leitura profunda de código.
- **Contexto Arquitetural**: `README.md`, `bin/validate-host.sh`, docs/artefatos da fase.
- **Definition of Done**:
  - [ ] runbook curto publicado
  - [ ] validate-host cobre a topologia local
  - [ ] fase F2 rastreia as três frentes principais

### Issues do Épico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA | Documentar e validar operação híbrida | 3 | todo | Feature 4 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| OpenRouter | provider | externo | modelos/fallbacks do trio especializado | pending |
| Telegram | canal | externo | binding inicial do `planner` | pending |
| OpenShell sandbox | runtime-host | interno/infra | sync remoto do dashboard e config | active |

## 16. Rollout e Comunicacao

- **Estratégia de deploy**: bootstrap local primeiro, depois sync remoto preservando o dashboard host-side
- **Comunicação de mudanças**: README e `validate-host.sh` passam a ser a referência curta para operação
- **Treinamento necessário**: entendimento do papel de `planner`, `builder` e `auditor`
- **Suporte pós-launch**: validar auth OpenRouter/Telegram quando secrets locais forem disponibilizados

## 17. Revisões e Auditorias

- **Auditorias planejadas**:
  - F1-R01
  - F2-R01
- **Critérios de auditoria**:
  - aderência do bootstrap à topologia declarada
  - ausência de segredos no Git
  - preservação do dashboard remoto host-side
- **Threshold anti-monolito**: evitar que helper, README e validate-host voltem a esconder a topologia em lógica implícita

## 18. Checklist de Prontidão

- [x] Intake referenciado e versão confirmada
- [x] Features definidas com critérios de aceite verificáveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Rastreabilidade explícita `Feature -> Fase -> Épico -> Issue`
- [x] Épicos criados e vinculados às features
- [x] Fases definidas com gates de saída
- [x] Dependências externas mapeadas
- [x] Riscos identificados e mitigação inicial descrita
- [x] Rollout inicial definido

## 19. Anexos e Referências

- [Intake](PROJETOS/OC-MISSION-CONTROL/INTAKE-OC-MISSION-CONTROL.md)
- [Audit Log](PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md)
- [F1 - Fundacao](PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/F1_OC-MISSION-CONTROL_EPICS.md)
- [F2 - OpenRouter e Agentes](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/F2_OC-MISSION-CONTROL_EPICS.md)
- [Epic F2-01](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md)
- [Epic F2-02](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md)
- [Epic F2-03](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-03-DOCUMENTACAO-E-VALIDACAO-OPERACIONAL.md)
- [Auditoria base F2](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/auditorias/RELATORIO-AUDITORIA-F2-R01.md)

> Frase Guia: "Agente certo, modelo certo, bootstrap certo."
