---
doc_id: "PRD-OC-HOST-OPS.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-HOST-OPS"
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "OPENCLAW-LEGADO"
origin_phase: "F9-F10 OPERACAO HOST"
origin_audit_id: "nao_aplicavel"
origin_report_path: "openclaw/README.md"
product_type: "workflow-improvement"
delivery_surface: "fullstack-module"
business_domain: "governanca"
criticality: "alta"
data_sensitivity: "restrita"
integrations:
  - "openclaw"
  - "nemoclaw-host"
  - "launchd"
  - "colima"
  - "docker"
  - "openshell"
  - "telegram-bridge"
  - "dashboard-tunnel"
  - "host.env"
change_type: "nova-capacidade"
audit_rigor: "elevated"
---

# PRD - OC-HOST-OPS

> Origem: [INTAKE-OC-HOST-OPS.md](PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md)
>
> Este PRD substitui o placeholder de scaffold por backlog real de operacao
> host-side do repositório `openclaw`.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OC-HOST-OPS.md](PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-23
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: OC-HOST-OPS
- **Tese em 1 frase**: consolidar em backlog feature-first a capacidade host-side do OpenClaw para instalar, restaurar, supervisionar e recuperar um host macOS sem depender de memoria informal
- **Valor esperado em 3 linhas**:
  - separar o toolkit host-side do runtime central do Mission Control
  - transformar `install/restore/validate/status/restart` em backlog rastreavel por feature
  - deixar explicita a fronteira entre estado versionado, segredos locais e recovery pos-reboot

## 2. Problema ou Oportunidade

- **Problema atual**: a capacidade host-side existe no repo, mas ainda estava descrita por um PRD placeholder de scaffold
- **Evidencia do problema**: `README.md`, `docs/restore.md`, `bin/install-host.sh`, `bin/validate-host.sh` e `src/nemoclaw-host/*` ja descrevem comportamento real de install, restore, bridge, dashboard e recovery
- **Custo de nao agir**: o backlog segue preso a bootstrap genérico e perde visibilidade sobre dependencias, segredos e blast radius operacional do host
- **Por que agora**: a auditoria do worktree atual mostrou que o repo ja entrega comportamento host-side real e precisa de backlog proprio

## 3. Publico e Operadores

- **Usuario principal**: operador responsavel por restaurar e manter um host macOS funcional para a stack NemoClaw/OpenShell/OpenClaw
- **Usuario secundario**: engenharia e suporte operacional que validam recovery pos-reboot e integridade do ambiente local
- **Operador interno**: scripts host-side, `launchd`, `nemoclaw-hostctl`, Colima, Docker e bridges locais
- **Quem aprova ou patrocina**: mantenedor do ambiente operacional local

## 4. Jobs to be Done

- **Job principal**: restaurar e operar o toolkit host-side do OpenClaw em uma maquina macOS com comportamento previsivel de install, validate, monitoramento e restart
- **Jobs secundarios**: reinstalar a stack sem versionar segredos; inspecionar saude do host; recuperar o ambiente apos reboot ou troca de maquina
- **Tarefa atual que sera substituida**: reconstruir passos de install/restore/restart a partir de scripts e notas dispersas

## 5. Escopo

### Dentro

- install/uninstall/validate do toolkit host-side
- templates `launchd` e sua operacao controlada
- restore de prerequisitos locais, segredos manuais e recovery pos-reboot
- operacao diaria via `nemoclaw-hostctl`, incluindo status, restart, logs e dashboard

### Fora

- contratos do `control-plane`, `ops-api` e logica de roteamento do Mission Control
- logica de trading, `execution_gateway` e gates financeiros
- estado vivo, offsets, pairings, logs e segredos mantidos fora do Git
- deploy cloud alem do host local macOS

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: tornar a camada host-side um produto operacional claro, reproduzivel e separavel do runtime central
- **Metricas leading**:
  - operador completa install/validate com checklist explicito
  - `status` expoe estado objetivo de Colima, cluster, jobs `launchd` e dashboard
  - restore pos-reboot possui fluxo documentado e verificavel
- **Metricas lagging**:
  - reducao de incidentes de bootstrap manual ou recovery improvisado
  - menor tempo para restaurar uma nova maquina host
  - menos drift entre README, restore guide e scripts reais
- **Criterio minimo para considerar sucesso**: o backlog consegue organizar a entrega host-side por features operacionais observaveis

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: escopo limitado a macOS com `launchd`; depende de `node`, `openshell`, `docker`, `colima`, `ssh`, `python3`, `curl`, `jq`
- **Restricoes operacionais**: restore manual de `credentials.json` e `host.env` continua obrigatorio; segredos e estado vivo ficam fora do Git
- **Restricoes legais ou compliance**: canais confiaveis, IDs autorizados e politica de menor privilegio precisam continuar intactos
- **Restricoes de prazo**: este PRD fecha backlog do host-side atual; automacao completa de onboarding pode ser fase posterior
- **Restricoes de design ou marca**: nenhuma alem da reachability do dashboard local

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: `README.md`, `docs/restore.md`, `bin/install-host.sh`, `bin/validate-host.sh`, `src/nemoclaw-host/*`, `templates/launchd/*`, `config/host.env.example`
- **Sistemas externos impactados**: Colima, Docker, OpenShell, Telegram bridge, dashboard remoto host-side
- **Dados de entrada necessarios**: `host.env`, `credentials.json`, binarios locais exigidos e ambiente macOS
- **Dados de saida esperados**: host instalado, validado, monitorado e recuperavel apos reboot

## 9. Arquitetura Geral do Projeto

- **Backend**: scripts host-side, helpers shell/node e templates `launchd`
- **Frontend**: nao aplicavel; o dashboard entra como superficie operacional observada
- **Banco/migracoes**: nao aplicavel
- **Observabilidade**: `validate-host.sh`, `nemoclaw-hostctl status`, logs dos jobs `launchd`, dashboard reachability
- **Autorizacao/autenticacao**: `ALLOWED_CHAT_IDS`, segredos locais e credenciais restauradas manualmente
- **Rollout**: host local do PM primeiro; depois guia de replicacao para outra maquina

## 10. Riscos Globais

- **Risco de produto**: fronteira errada com Mission Control pode misturar backlog host e runtime
- **Risco tecnico**: drift entre README, templates `launchd` e scripts reais
- **Risco operacional**: recovery pos-reboot depender de passos nao documentados
- **Risco de dados**: segredos locais e logs vazarem para o repo
- **Risco de adocao**: operador continuar usando scripts avulsos e nao o fluxo padronizado

## 11. Nao-Objetivos

- redefinir contratos do runtime central
- carregar backlog de trading
- versionar segredos, offsets, pairings ou estado vivo do host

## 12. Features do Projeto

### Feature 1: Instalar toolkit host reproduzivel

#### Objetivo de Negocio

Instalar o toolkit host-side com paths, jobs e defaults consistentes para que o host possa ser recriado sem ajuste manual excessivo.

#### Comportamento Esperado

O operador publica binarios e scripts gerenciados, renderiza `LaunchAgents` a partir de templates versionados e deixa a stack local pronta para validacao.

#### Criterios de Aceite

- `install-host.sh` publica scripts e helpers nos paths gerenciados
- `LaunchAgents` sao renderizados a partir de templates versionados
- o toolkit entra em operacao sem armazenar estado vivo no Git

#### Dependencias com Outras Features

- nenhuma

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Consolidar install + publish de scripts host-side | 3 | - |
| T2 | Alinhar templates `launchd` e reload dos jobs | 3 | T1 |

### Feature 2: Restaurar prerequisitos e credenciais locais

#### Objetivo de Negocio

Garantir que onboarding e troca de maquina tenham fluxo explicito para prerequisitos, segredos e bloqueios de validacao.

#### Comportamento Esperado

O operador sabe o que precisa restaurar antes da validacao; falhas de restore produzem erro acionavel.

#### Criterios de Aceite

- prerequisitos obrigatorios ficam claros antes da validacao
- `credentials.json` e `host.env` entram como restore manual explicito
- falhas de restore bloqueiam validacao com mensagem acionavel

#### Dependencias com Outras Features

- Feature 1

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T3 | Revisar docs de restore e checklist de prerequisitos | 3 | T1 |
| T4 | Garantir mensagens acionaveis para segredos ausentes | 2 | T3 |

### Feature 3: Supervisionar `launchd`, Colima, dashboard e Telegram bridge

#### Objetivo de Negocio

Tornar a saude do host observavel e operavel por comandos padronizados.

#### Comportamento Esperado

`nemoclaw-hostctl` mostra estado de Colima, cluster, jobs `launchd`, dashboard e bridges; `restart` e `logs` funcionam de modo previsivel.

#### Criterios de Aceite

- `status` mostra estado de Colima, cluster, jobs `launchd` e dashboard
- `restart` consegue reativar jobs gerenciados
- logs de bridge/dashboard ficam acessiveis por comando padronizado

#### Dependencias com Outras Features

- Feature 1

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T5 | Consolidar comandos de status e logs do hostctl | 3 | T2 |
| T6 | Padronizar restart e diagnostico dos jobs gerenciados | 3 | T5 |

### Feature 4: Validar recuperacao pos-reboot

#### Objetivo de Negocio

Transformar recovery pos-reboot em rotina reproduzivel e auditavel.

#### Comportamento Esperado

Apos reboot ou troca de maquina, o operador segue um checklist curto, revalida o host e recupera dashboard/bridge sem passos secretos.

#### Criterios de Aceite

- ha estado esperado claro apos reboot
- o recovery padrao e documentado e reproduzivel
- a revalidacao do dashboard e da bridge acontece sem passos secretos

#### Dependencias com Outras Features

- Features 1, 2 e 3

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T7 | Formalizar checklist pos-reboot em docs e validate | 3 | T3, T5 |
| T8 | Evidenciar recovery do host com validacao objetiva | 3 | T7 |

### Feature 5: Expor operacao diaria padronizada

#### Objetivo de Negocio

Permitir que a manutencao diaria do host aconteca por comandos previsiveis e documentados.

#### Comportamento Esperado

O operador usa `status`, `dashboard`, `logs` e `restart` sem reabrir scripts internos nem depender de memoria oral.

#### Criterios de Aceite

- comandos de operacao diaria cabem em `status`, `dashboard`, `logs`, `restart`
- o toolkit permite manutencao sem reabrir scripts internos
- a documentacao de uso diario reflete o comportamento real do hostctl

#### Dependencias com Outras Features

- Features 3 e 4

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T9 | Fechar runbook operacional diario do host | 2 | T6 |
| T10 | Sincronizar README com comportamento real do hostctl | 2 | T8, T9 |

## 13. Estrutura de Fases

## Fase 1: Install e restore do host

- **Objetivo**: fechar install, prerequisitos e restore explicito do ambiente local.
- **Features incluidas**: Feature 1, Feature 2
- **Gate de saida**: host instala e valida com segredos restaurados fora do Git.

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F1-01 | Feature 1, Feature 2 | todo | 11 |

## Fase 2: Supervisao e recovery

- **Objetivo**: observar e recuperar o host apos reboot ou falha operacional.
- **Features incluidas**: Feature 3, Feature 4
- **Gate de saida**: operador diagnostica e recupera host/bridge/dashboard com evidencias reproduziveis.

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F2-01 | Feature 3, Feature 4 | todo | 12 |

## Fase 3: Operacao diaria e hardening

- **Objetivo**: consolidar uso diario e reduzir drift documental.
- **Features incluidas**: Feature 5
- **Gate de saida**: runbook diario e comandos reais estao sincronizados.

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F3-01 | Feature 5 | todo | 4 |

## 14. Epicos

### Epico: Install e restore do host

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1, Feature 2
- **Objetivo**: entregar install, restore e validacao explicitos para o host-side local.
- **Resultado de Negocio Mensuravel**: nova maquina ou reinstalacao parcial nao dependem de memoria oral.
- **Definition of Done**:
  - [ ] install publish consistente
  - [ ] restore manual de segredos documentado
  - [ ] validate bloqueia prerequisitos e segredos ausentes com mensagens acionaveis

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Consolidar install e publish do toolkit host | 6 | todo | Feature 1 |
| ISSUE-F1-01-002 | Formalizar restore e prerequisitos do host | 5 | todo | Feature 2 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| Mission Control | runtime | OC-MISSION-CONTROL | host precisa subir e observar o runtime, sem redefinir seus contratos | active |
| Colima / Docker / OpenShell | infraestrutura local | host macOS | prerequisitos do ambiente | active |

## 16. Rollout e Comunicacao

- **Estrategia de deploy**: host local do PM primeiro; depois replicacao para outra maquina macOS
- **Comunicacao de mudancas**: README, `docs/restore.md` e wrappers do projeto devem apontar para a mesma fila de backlog
- **Treinamento necessario**: uso basico de `nemoclaw-hostctl`, install, validate e restore
- **Suporte pos-launch**: backlog proprio em `PROJETOS/OC-HOST-OPS/`

## 17. Revisoes e Auditorias

- **Auditorias planejadas**: ao fim de cada fase operacional
- **Criterios de auditoria**: aderencia entre scripts, README, restore e comportamento observado no host
- **Threshold anti-monolito**: seguir `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md` quando houver code growth relevante

## 18. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
- [x] Dependencias externas mapeadas
- [x] Riscos e guardrails documentados
- [x] Rollout planejado

## 19. Anexos e Referencias

- [Intake](PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md)
- [Audit Log](PROJETOS/OC-HOST-OPS/AUDIT-LOG.md)
- [README](README.md)
- [Restore](docs/restore.md)
- [Install](bin/install-host.sh)
- [Validate](bin/validate-host.sh)
