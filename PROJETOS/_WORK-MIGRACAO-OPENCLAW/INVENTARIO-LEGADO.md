# INVENTARIO LEGADO - OPENCLAW

Data de consolidacao: 2026-03-20  
Repo-alvo do framework: `openclaw`  
Corpus principal de origem: `assistant-brain`

## 1. Fontes Lidas

### Fontes normativas do framework

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
- `PROJETOS/COMUM/PRD-ADAPTACAO-FEATURE-FIRST.md`
- `PROJETOS/COMUM/TEMPLATE-PRD.md`
- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- `scripts/criar_projeto.py`

### Fontes de inventario e contexto geral

- `INDICE-INFRA-PRD-ARQUITETURA-OPENCLAW.md`
- `assistant-brain/README.md`
- `assistant-brain/PRD/PRD-MASTER.md`
- `assistant-brain/PRD/ROADMAP.md`
- `assistant-brain/ARC/ARC-CORE.md`
- `assistant-brain/SEC/SEC-POLICY.md`
- `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`
- `assistant-brain/PM/TRACEABILITY/FELIX-ALIGNMENT-MATRIX.md`

### Fontes priorizadas para `OC-MISSION-CONTROL`

- `assistant-brain/apps/control-plane/README.md`
- `assistant-brain/apps/ops-api/README.md`
- `assistant-brain/platform/policy-engine/README.md`
- `assistant-brain/PM/PHASES/F10-CONVERGENCIA-PRD-RUNTIME-SEM-REGRESSAO/EPIC-F10-02-CONVERGENCIA-PRD-SEM-PERDA-DE-ESTADO.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-03-BUDGET-PRIVACIDADE-A2A-E-HOOKS-GOVERNADOS.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-04-INTEGRACAO-PROMOCAO-E-EVIDENCIA-OPERACIONAL.md`

### Fontes priorizadas para `OC-HOST-OPS`

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
- `assistant-brain/PM/PHASES/F9-ONBOARDING-CREDENCIAIS-E-CANAIS-AUTOMATIZADOS/EPIC-F9-02-BOOTSTRAP-TELEGRAM-E-SLACK-SOCKET-MANIFEST.md`

### Fontes priorizadas para `OC-TRADING`

- `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`
- `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`
- `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`
- `assistant-brain/INTEGRATIONS/README.md`
- `assistant-brain/INTEGRATIONS/AI-TRADER.md`
- `assistant-brain/INTEGRATIONS/CLAWWORK.md`
- `assistant-brain/INTEGRATIONS/OPENCLAW-UPSTREAM.md`
- `assistant-brain/PRD/ROADMAP.md`
- `assistant-brain/SEC/SEC-POLICY.md`

## 2. Criterios de Corte Aplicados

- O legado descreve pelo menos tres superficies de entrega com ciclos independentes:
  - runtime/control-plane governado;
  - toolkit host-side macOS com `launchd`, Colima e bridges locais;
  - trading de alto risco com gates proprios de enablement.
- O risco acumulado de manter trading no mesmo projeto do runtime e alto:
  - side effect financeiro;
  - credenciais e allowlists proprias;
  - criterios de promote e rollback diferentes do restante da plataforma.
- O toolkit host-side justifica projeto proprio:
  - depende de prerequisitos macOS e restore local;
  - opera binarios e estado fora do Git;
  - possui fluxo de install/validate/restart distinto do control-plane.
- `contracts`, `policy-engine`, docs de seguranca e integracoes nao viram um quarto projeto:
  - nao representam superficie de entrega independente;
  - servem como capacidade transversal que sustenta os outros tres projetos;
  - seriam um projeto docs-only sem loop de entrega separado forte o suficiente.
- O inventario adota `business_domain: governanca` nos Intakes por falta de token canonico para `runtime`, `host` e `trading`.

## 3. Matriz Feature x Projeto x Fonte

| Projeto | Feature priorizada | Fontes principais | Evidencia de implementabilidade atual |
|---|---|---|---|
| `OC-MISSION-CONTROL` | Operar runtime governado com estado preservado | `assistant-brain/PRD/PRD-MASTER.md`, `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/PM/PHASES/F10-CONVERGENCIA-PRD-RUNTIME-SEM-REGRESSAO/EPIC-F10-02-CONVERGENCIA-PRD-SEM-PERDA-DE-ESTADO.md` | backlog e contratos descrevem merge deterministico, `dry-run`, backup e preservacao de estado |
| `OC-MISSION-CONTROL` | Decidir roteamento de modelos com trilha auditavel | `assistant-brain/apps/control-plane/README.md`, `assistant-brain/apps/ops-api/README.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md` | existe superficie `/router/decide` e backlog para decisao calculada no dominio |
| `OC-MISSION-CONTROL` | Persistir runs, memoria e budget por `trace_id` | `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/PRD/ROADMAP.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md` | schemas e epic descrevem `trace_snapshot`, `llm_run`, `credits_snapshot` e correlacao de budget |
| `OC-MISSION-CONTROL` | Executar HITL seguro em canais confiaveis | `assistant-brain/README.md`, `assistant-brain/SEC/SEC-POLICY.md`, `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`, `assistant-brain/PM/PHASES/F9-ONBOARDING-CREDENCIAIS-E-CANAIS-AUTOMATIZADOS/EPIC-F9-02-BOOTSTRAP-TELEGRAM-E-SLACK-SOCKET-MANIFEST.md` | Telegram e Slack fallback aparecem como canais governados com challenge e manifest versionado |
| `OC-MISSION-CONTROL` | Governar A2A e hooks com allowlist e idempotencia | `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/platform/policy-engine/README.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-03-BUDGET-PRIVACIDADE-A2A-E-HOOKS-GOVERNADOS.md` | backlog define allowlist real, validacao de webhook, assinatura, anti-replay e `NO_OP_DUPLICATE` |
| `OC-HOST-OPS` | Instalar toolkit host reproduzivel | `openclaw/README.md`, `openclaw/bin/install-host.sh`, `openclaw/templates/launchd/*.plist.template` | repo-alvo versiona apenas a camada host-side e seu instalador |
| `OC-HOST-OPS` | Restaurar prerequisitos e credenciais locais | `openclaw/docs/restore.md`, `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md` | restore manual de `credentials.json`, `host.env` e binarios locais esta explicitado |
| `OC-HOST-OPS` | Supervisionar `launchd`, Colima, dashboard e Telegram bridge | `openclaw/src/nemoclaw-host/nemoclaw-hostctl`, `openclaw/src/nemoclaw-host/common.sh`, `openclaw/templates/launchd/*.plist.template` | `hostctl status/restart/logs` e os `LaunchAgents` existem como toolkit operacional |
| `OC-HOST-OPS` | Validar recuperacao pos-reboot | `openclaw/docs/restore.md`, `openclaw/bin/validate-host.sh`, `openclaw/src/nemoclaw-host/colima-autostart.sh` | README e restore definem estado esperado e recovery manual |
| `OC-HOST-OPS` | Expor operacao diaria padronizada | `openclaw/README.md`, `openclaw/src/nemoclaw-host/nemoclaw-hostctl` | comandos `status`, `dashboard`, `logs`, `restart` ja estao definidos |
| `OC-TRADING` | Ingerir `signal_intent` de engines externas sem bypass | `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/INTEGRATIONS/AI-TRADER.md`, `assistant-brain/INTEGRATIONS/CLAWWORK.md` | pipeline oficial `signal_intent -> normalizacao -> validator -> HITL -> execution_gateway` esta normatizado |
| `OC-TRADING` | Validar ordens com `pre_trade_validator` e regras hard | `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`, `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md` | risco <= 1%, stoploss obrigatorio, lot/tick/min_notional e gates de bloqueio estao especificados |
| `OC-TRADING` | Operar `execution_gateway_only` com aprovacao humana por ordem | `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/SEC/SEC-POLICY.md` | docs bloqueiam ordem direta externa e exigem HITL explicito em todos os estagios |
| `OC-TRADING` | Promover `paper -> micro-live -> escala` com checklist e evidence refs | `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`, `assistant-brain/PRD/ROADMAP.md` | `TRADING_BLOCKED`, `pre_live_checklist`, `capital_ramp_level=L0` e janelas minimas estao descritos |
| `OC-TRADING` | Governar expansao multiativos sob enablement separado | `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`, `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md` | classes `equities_br`, `fii_br` e `fixed_income_br` seguem bloqueadas ate asset profiles e evals dedicadas |

## 4. Lacunas Abertas

- `Convex` aparece como componente do control-plane, mas o corpus lido nao fecha o recorte exato entre estado em `Convex` e estado canonico em `postgres`.
- O repositório `openclaw` atual nao inclui o codigo do control-plane nem da `ops-api`; a realidade implantavel hoje para esse escopo esta documentada principalmente no `assistant-brain`.
- O toolkit host-side depende de segredos e estado local fora do Git (`~/.nemoclaw/credentials.json`, `host.env`, pairings, logs), entao o fluxo exato de bootstrap em uma maquina nova continua parcialmente manual.
- O roster final de operadores autorizados, canais Slack validados e `backup_operator` nao esta fechado nas fontes lidas; isso precisa permanecer como `nao_definido` nos Intakes.
- Multiativos alem de `crypto_spot` continuam sem adapters e `asset_profiles` publicados no repo-alvo, portanto entram apenas como extensao posterior da capacidade de trading.
- O peso relativo entre `TradingAgents`, `AI-Trader` e modulos futuros de `AgenticTrading` nao esta fechado como politica operacional detalhada.
- A compatibilidade periodica com OpenClaw upstream esta normatizada, mas o ciclo exato de promote/rollback por release upstream segue aberto.
