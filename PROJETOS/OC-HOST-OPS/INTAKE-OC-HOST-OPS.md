---
doc_id: "INTAKE-OC-HOST-OPS.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-20"
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

# INTAKE - OC-HOST-OPS

> Intake retroativo da camada host-side reproduzivel do repositório `openclaw`.

## 0. Rastreabilidade de Origem

- projeto de origem: toolkit operacional macOS para NemoClaw/OpenShell/OpenClaw
- fase de origem: restore host-side, onboarding de canais e operacao local do runtime
- auditoria de origem: nao_aplicavel
- relatorio de origem: `openclaw/README.md`, `openclaw/docs/restore.md`, `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`
- motivo da abertura deste intake: isolar em um projeto feature-first a capacidade host-side que hoje existe no repo `openclaw`, sem misturar runtime core ou trading

### Fontes principais

- `openclaw/README.md`
- `openclaw/docs/restore.md`
- `openclaw/bin/install-host.sh`
- `openclaw/bin/validate-host.sh`
- `openclaw/bin/uninstall-host.sh`
- `openclaw/src/nemoclaw-host/nemoclaw-hostctl`
- `openclaw/src/nemoclaw-host/common.sh`
- `openclaw/src/nemoclaw-host/telegram-bridge.sh`
- `openclaw/src/nemoclaw-host/dashboard-tunnel.sh`
- `openclaw/templates/launchd/colima-autostart.plist.template`
- `openclaw/templates/launchd/dashboard-tunnel.plist.template`
- `openclaw/templates/launchd/telegram-bridge.plist.template`
- `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`
- `assistant-brain/SEC/SEC-POLICY.md`
- `assistant-brain/PM/PHASES/F9-ONBOARDING-CREDENCIAIS-E-CANAIS-AUTOMATIZADOS/EPIC-F9-02-BOOTSTRAP-TELEGRAM-E-SLACK-SOCKET-MANIFEST.md`

### Mapeamento de features prioritarias

- `Instalar toolkit host reproduzivel`
  - actor: operador da maquina host
  - fontes: `openclaw/README.md`, `openclaw/bin/install-host.sh`, `openclaw/templates/launchd/*.plist.template`
- `Restaurar prerequisitos e credenciais locais`
  - actor: operador em bootstrap ou troca de maquina
  - fontes: `openclaw/docs/restore.md`, `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`
- `Supervisionar launchd, Colima, dashboard e Telegram bridge`
  - actor: operador do host
  - fontes: `openclaw/src/nemoclaw-host/nemoclaw-hostctl`, `openclaw/src/nemoclaw-host/common.sh`
- `Validar recuperacao pos-reboot`
  - actor: operador e suporte operacional
  - fontes: `openclaw/docs/restore.md`, `openclaw/bin/validate-host.sh`
- `Expor operacao diaria padronizada`
  - actor: operador da stack local
  - fontes: `openclaw/README.md`, `openclaw/src/nemoclaw-host/nemoclaw-hostctl`

## 1. Resumo Executivo

- nome curto da iniciativa: operacao host-side do OpenClaw
- tese em 1 frase: consolidar em um projeto feature-first a capacidade de instalar, restaurar, supervisionar e recuperar o toolkit host-side macOS que sustenta a operacao local do OpenClaw
- valor esperado em 3 linhas:
  - separar o que e infraestrutura host reproduzivel do que e runtime/produto no `assistant-brain`
  - tornar claro o valor entregue pelo repo `openclaw`: install, validate, restart, logs e restore do host
  - permitir backlog e PRD proprio para operacao local sem contaminar Mission Control ou Trading

## 2. Problema ou Oportunidade

- problema atual: o repo `openclaw` atual concentra apenas a camada host-side macOS, mas essa capacidade ainda nao esta descrita em um intake proprio; ela aparece como detalhe operacional em READMEs, scripts e onboarding, o que dificulta priorizacao e fronteira com runtime core
- evidencia do problema: `openclaw/README.md` e `docs/restore.md` descrevem restore, `LaunchAgents`, bridges e prerequisitos locais, enquanto o corpus `assistant-brain` trata o produto e o runtime em outro repositorio
- custo de nao agir: o host-side continuara parecendo um detalhe de documentacao, quando na pratica e uma superficie operacional independente com dependencias, segredos, reboot recovery e blast radius proprio
- por que agora: a migracao do legado para feature-first precisa preservar a realidade implantavel do repo-alvo `openclaw`

## 3. Publico e Operadores

- usuario principal: operador responsavel por restaurar e manter um host macOS funcional para a stack NemoClaw/OpenShell/OpenClaw
- usuario secundario: engenharia e suporte operacional que validam recovery pos-reboot e integridade do ambiente local
- operador interno: scripts host-side, `launchd`, `nemoclaw-hostctl`, Colima, Docker e bridges locais
- quem aprova ou patrocina: mantenedor do ambiente operacional local

## 4. Jobs to be Done

- job principal: restaurar e operar o toolkit host-side do OpenClaw em uma maquina macOS com comportamento previsivel de install, validate, monitoramento e restart
- jobs secundarios:
  - reinstalar a stack sem versionar segredos nem estado vivo no Git
  - inspecionar saude de Colima, tunnel de dashboard e Telegram bridge
  - recuperar o host apos reboot sem depender de memoria informal
- tarefa atual que sera substituida: reconstruir manualmente os passos de install/restore/restart a partir de varios scripts e notas operacionais

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. O operador prepara `host.env`, restaura `~/.nemoclaw/credentials.json` e confirma os binarios locais exigidos.
2. O instalador publica scripts em `~/.local/lib/nemoclaw-host`, renderiza `LaunchAgents` e recarrega os jobs gerenciados.
3. O validador confere prerequisitos, credenciais, `ALLOWED_CHAT_IDS`, conectividade da stack e reachability do dashboard.
4. O operador usa `nemoclaw-hostctl` para consultar status, abrir dashboard, ler logs e reiniciar servicos quando necessario.
5. Apos reboot ou troca de maquina, o fluxo de restore e repetido com evidencia de recovery do host.

### Features MVP priorizadas

#### Feature 1 - Instalar toolkit host reproduzivel

- actor: operador da maquina host
- DoD comportamental:
  - instalador publica binarios e scripts sob paths gerenciados
  - `LaunchAgents` sao renderizados a partir de templates versionados
  - o toolkit entra em operacao sem armazenar estado vivo no Git
- dependencias: `install-host.sh`, templates `launchd`, `host.env`
- riscos: drift entre template, install e estrutura realmente esperada pelo host

#### Feature 2 - Restaurar prerequisitos e credenciais locais

- actor: operador em onboarding ou migracao de maquina
- DoD comportamental:
  - prerequisitos obrigatorios ficam claros antes da validacao
  - `credentials.json` e `host.env` entram como restore manual explicito
  - falhas de restore bloqueiam validacao com mensagem acionavel
- dependencias: docs de restore, segredos locais, binarios externos
- riscos: dependencias fora do Git permanecerem implicitas

#### Feature 3 - Supervisionar `launchd`, Colima, dashboard e Telegram bridge

- actor: operador do host
- DoD comportamental:
  - `status` mostra estado de Colima, cluster, jobs `launchd` e dashboard
  - `restart` consegue reativar jobs gerenciados
  - logs de bridge/dashboard ficam acessiveis por comando padronizado
- dependencias: `nemoclaw-hostctl`, `common.sh`, runtime local
- riscos: diagnósticos superficiais esconderem falhas reais do host

#### Feature 4 - Validar recuperacao pos-reboot

- actor: suporte operacional
- DoD comportamental:
  - ha estado esperado claro apos reboot
  - o recovery padrao e documentado e reproduzivel
  - revalidacao do dashboard e da bridge acontece sem passos secretos
- dependencias: `validate-host.sh`, `restore.md`, `launchd`
- riscos: reboot recovery depender de pareamentos ou estado nao versionado

#### Feature 5 - Expor operacao diaria padronizada

- actor: operador da stack local
- DoD comportamental:
  - comandos de operacao diaria cabem em `status`, `dashboard`, `logs`, `restart`
  - o toolkit permite manutencao sem reabrir scripts internos
  - a documentacao de uso diario reflete o comportamento dos comandos reais
- dependencias: README, helper scripts, tunnel/bridge
- riscos: divergencia entre README e comportamento real do hostctl

## 6. Escopo Inicial

### Dentro

- install/uninstall/validate do toolkit host-side
- templates `launchd` e sua operacao controlada
- restore de prerequisitos locais, segredos manuais e recovery pos-reboot
- operacao diaria via `nemoclaw-hostctl`, incluindo status, restart, logs e dashboard

### Fora

- contracts de `control-plane`, `ops-api` e logica de roteamento do Mission Control
- logica de trading, `execution_gateway`, `pre_trade_validator` e gates financeiros
- estado vivo, offsets, pairings, logs e segredos mantidos localmente fora do Git
- deploy cloud e operacao de producao alem do host local macOS

## 7. Resultado de Negocio e Metricas

- objetivo principal: tornar a camada host-side um produto operacional claro, reproduzivel e separavel do runtime central
- metricas leading:
  - operador consegue completar install/validate com o checklist explicito
  - `status` expoe estado objetivo de Colima, cluster, jobs `launchd` e dashboard
  - restore pos-reboot possui fluxo documentado e verificavel
- metricas lagging:
  - reducao de incidentes de bootstrap manual ou recovery improvisado
  - menor tempo para restaurar uma nova maquina host
  - menos drift entre README, restore guide e scripts reais
- criterio minimo para considerar sucesso: o PRD posterior consegue organizar a entrega host-side por features operacionais e nao por lista dispersa de scripts

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - escopo limitado a macOS com `launchd`
  - depende de `node`, `openshell`, `docker`, `colima`, `ssh`, `python3`, `curl`, `jq`
  - segredos e estado vivo nao entram em Git
- restricoes operacionais:
  - restore manual de `credentials.json` e `host.env` continua obrigatorio
  - `ALLOWED_CHAT_IDS` e demais identificadores do bridge precisam estar corretos antes da validacao
  - recovery precisa manter supervisao de dashboard e Telegram bridge
- restricoes legais ou compliance:
  - credenciais e logs locais seguem politica de menor privilegio e nao podem vazar para o repositorio
  - canais confiaveis e IDs autorizados precisam continuar controlados
- restricoes de prazo: este intake apenas formaliza a capacidade; nao fecha toda a automacao de onboarding do futuro
- restricoes de design ou marca: nenhuma alem da reachability do dashboard local

## 9. Dependencias e Integracoes

- sistemas internos impactados:
  - `bin/install-host.sh`
  - `bin/validate-host.sh`
  - `src/nemoclaw-host/*`
  - `templates/launchd/*`
  - `config/host.env.example`
- sistemas externos impactados:
  - macOS `launchd`
  - Colima
  - Docker
  - OpenShell
  - Telegram bridge local
- dados de entrada necessarios:
  - `~/.config/nemoclaw-host/host.env`
  - `~/.nemoclaw/credentials.json`
  - binarios locais exigidos
  - identificadores autorizados de Telegram
- dados de saida esperados:
  - toolkit instalado sob `~/.local/lib/nemoclaw-host`
  - `LaunchAgents` carregados
  - status operacional consultavel por `nemoclaw-hostctl`

Dependencia cruzada declarada:

- este projeto consome um runtime funcional, mas nao redefine contratos de `OC-MISSION-CONTROL`
- este projeto nao inclui nenhuma logica de risco ou execucao de `OC-TRADING`

## 10. Arquitetura Afetada

- backend: scripts shell e Node do toolkit host-side, sem `control-plane` de produto
- frontend: dashboard local acessado por tunnel, sem UI nova dedicada
- banco/migracoes: nao aplicavel
- observabilidade: logs locais, `status` de jobs, health do cluster e reachability do dashboard
- autorizacao/autenticacao: `ALLOWED_CHAT_IDS`, credenciais locais restauradas manualmente, controles de bridge e secrets fora do Git
- rollout: install local, validate, reboot recovery e manutencao continua no host macOS

## 11. Riscos Relevantes

- risco de produto: o host-side continuar invisivel como capacidade independente e receber backlog incompleto
- risco tecnico: scripts e templates divergem do que o README/restore guide prometem
- risco operacional: restore pos-reboot depender de estado local nao documentado ou de binarios faltantes
- risco de dados: secrets locais, pairings e logs serem manipulados fora do controle esperado
- risco de adocao: operadores manterem runbooks informais em vez de usar install/validate/status padronizados

## 12. Nao-Objetivos

- nao reescrever o runtime core do OpenClaw
- nao desenhar politica de trading ou de `execution_gateway`
- nao versionar segredos, offsets, logs ou estado vivo do host
- nao expandir a capacidade para Linux, Windows ou deploy cloud nesta fase

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: politica final de quem possui e aprova o restore de credenciais e `host.env` em troca de maquina
- dependencia ainda nao confirmada: bootstrap exato do cluster OpenShell e seus checks detalhados fora do que o repo documenta
- dado ainda nao disponivel: inventario formal dos segredos, pairings e arquivos locais que o operador precisa restaurar alem de `credentials.json`
- decisao de UX ainda nao fechada: comportamento esperado do dashboard apos reboot equivalente e eventual necessidade de segundo `open`
- outro ponto em aberto:
  - estrategia de logs/retencao local alem do escopo do Git
  - papel exato do fallback Slack no host-side versus no runtime de produto

## 15. Perguntas que o PRD Precisa Responder

- Quais fases e issues traduzem install, validate, restore e recovery em backlog sem misturar runtime core?
- Quais evidencias minimas tornam um host elegivel para promote operacional apos bootstrap ou reboot?
- Qual e o contrato minimo de compatibilidade entre toolkit host-side e runtime consumido localmente?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
