---
doc_id: "DECISAO-PROJETOS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
---

# DECISAO DE PROJETOS - MIGRACAO OPENCLAW

## Data da Decisao

- decisao original: 2026-03-20
- atualizacao desta rodada: 2026-03-23

## Nomes Finais e Faixas

### Backlog principal

- `OC-MISSION-CONTROL`
- `OC-HOST-OPS`
- `QMD`
- `OC-TRADING`

### Canario / governanca

- `OC-SMOKE-SKILLS`
- `scripts/criar_projeto.py` como fonte compartilhada do scaffold

## Justificativa das Fronteiras

### `OC-MISSION-CONTROL`

- cobre a capacidade central de runtime governado:
  - control-plane
  - `ops-api`
  - roteamento de modelos
  - memoria operacional
  - budget, privacidade, A2A e hooks governados
  - canais HITL como superficie operacional do runtime
- recebe o legado que fala de produto/plataforma em `PRD-MASTER`, `ROADMAP`, `ARC-CORE`, `SEC-POLICY` e fases `F10`/`F11`
- fica explicitamente fora deste projeto:
  - toolkit macOS `nemoclaw-host`
  - rollout financeiro de trading
  - onboarding e restore local como capacidade host-side

### `OC-HOST-OPS`

- cobre a camada reproduzivel de operacao host-side do repo `openclaw` atual:
  - install/uninstall/validate
  - `LaunchAgents`
  - supervisao de Colima
  - tunnel de dashboard
  - Telegram bridge
  - operacao diaria via `nemoclaw-hostctl`
- justifica projeto proprio porque:
  - depende de macOS + `launchd`
  - depende de binarios e credenciais fora do Git
  - tem fluxo de restore e reboot recovery diferente do runtime de produto
- fica explicitamente fora deste projeto:
  - contratos de `control-plane`
  - logica de roteamento/model catalog
  - logica de trading e gates financeiros

### `QMD`

- cobre a memoria operacional em camadas com backend QMD:
  - `memory.backend: qmd`
  - `MEMORY.md`, notas diarias e consolidacao noturna
  - politicas de conflito memoria-vs-canonico
  - eventuais entidades, `summary.md`, `items.json` e decay em fases posteriores
- justifica projeto proprio porque:
  - tem contratos, riscos e rollout diferentes do runtime core e do host-side
  - toca o workspace versionado de Assis e a politica de autoridade dos canonicos
  - exige backlog proprio para consolidacao, recall e HITL de conflito
- fica explicitamente fora deste projeto:
  - redefinicao do runtime core do Mission Control
  - toolkit host-side macOS
  - vertical Trading e seus gates financeiros

### `OC-TRADING`

- cobre a vertical de alto risco com contratos, validadores e gates proprios:
  - `signal_intent`
  - `pre_trade_validator`
  - `execution_gateway`
  - `pre_live_checklist`
  - enablement por estagio
  - integracoes `TradingAgents`, `AI-Trader`, `ClawWork` e venues
- justifica projeto proprio por blast radius e governanca:
  - side effect financeiro
  - credenciais e allowlists proprias
  - promotion gates independentes
  - priorizacao separada do runtime central
- fica explicitamente fora deste projeto:
  - redefinicao do runtime core
  - toolkit host macOS
  - expansao multiativos como entrega MVP imediata

### `OC-SMOKE-SKILLS`

- existe como projeto-canario do framework:
  - valida roteamento, autonomia, execucao, revisao e auditoria das skills `openclaw-*`
  - usa `GUIA-TESTE-SKILLS.md` e `./bin/check-openclaw-smoke.sh` como contrato de aceite
- nao entra no backlog principal:
  - nao descreve um produto
  - nao substitui planejamento de `OC-MISSION-CONTROL`, `OC-HOST-OPS`, `QMD` ou `OC-TRADING`

## Dependencias Cruzadas

| Projeto | Depende de | Contrato esperado |
|---|---|---|
| `OC-MISSION-CONTROL` | `PROJETOS/COMUM` e corpus `assistant-brain` | framework, taxonomias, contratos e backlog base |
| `OC-HOST-OPS` | `OC-MISSION-CONTROL` apenas no nivel de runtime consumido localmente | host precisa conseguir iniciar e observar o runtime, sem redefinir seus contratos |
| `QMD` | `OC-MISSION-CONTROL` e workspace versionado `openclaw-workspace/` | memoria operacional, autoridade dos canonicos e consolidacao do workspace Assis |
| `OC-TRADING` | `OC-MISSION-CONTROL` | trading depende de HITL, policy, audit trail, budget e execution backbone |
| `OC-SMOKE-SKILLS` | `PROJETOS/COMUM`, `scripts/criar_projeto.py` e a suite `openclaw-*` | prova controlada do framework e do scaffold compartilhado |

## Ordem Atualizada de Feitura

### Faixa canario / governanca

1. `scripts/criar_projeto.py`
2. `OC-SMOKE-SKILLS`

### Backlog principal

1. `OC-MISSION-CONTROL`
2. `OC-HOST-OPS`
3. `QMD`
4. `OC-TRADING`

## Racional da Ordem

- `scripts/criar_projeto.py` vem primeiro porque era a fonte compartilhada do drift
- `OC-SMOKE-SKILLS` vem logo depois para provar o scaffold corrigido e a suite `openclaw-*`
- `OC-MISSION-CONTROL` estabiliza o backbone normativo e operacional consumido pelos demais projetos
- `OC-HOST-OPS` vem em seguida porque descreve o codigo host-side real deste repo
- `QMD` entra depois de host estabilizado porque toca workspace, memoria e politica de autoridade
- `OC-TRADING` fica por ultimo por risco e dependencia forte do backbone central

## Defaults de Backfill

- `OC-HOST-OPS` e `OC-TRADING` mantem `source_mode: backfilled`
- `QMD` permanece `source_mode: original`
- `OC-SMOKE-SKILLS` permanece projeto-canario, nao backlog principal
- quando o worktree atual ja materializa parte do escopo, a auditoria deve reconciliar o backlog com essa realidade em vez de fingir que ela nao existe
