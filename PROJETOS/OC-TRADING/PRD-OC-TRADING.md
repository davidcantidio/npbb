---
doc_id: "PRD-OC-TRADING.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-TRADING"
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "OPENCLAW-LEGADO"
origin_phase: "F1-F2 TRADING"
origin_audit_id: "nao_aplicavel"
origin_report_path: "assistant-brain/VERTICALS/TRADING/TRADING-PRD.md"
product_type: "platform-capability"
delivery_surface: "backend-api"
business_domain: "governanca"
criticality: "critica"
data_sensitivity: "restrita"
integrations:
  - "OC-MISSION-CONTROL"
  - "tradingagents"
  - "ai-trader"
  - "clawwork"
  - "binance-spot"
  - "execution_gateway"
  - "pre_trade_validator"
  - "telegram"
  - "slack"
  - "policy-engine"
change_type: "nova-capacidade"
audit_rigor: "strict"
---

# PRD - OC-TRADING

> Origem: [INTAKE-OC-TRADING.md](PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md)
>
> Este PRD substitui o placeholder de scaffold por backlog real da vertical de
> trading governado do OpenClaw.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-OC-TRADING.md](PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-23
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: OC-TRADING
- **Tese em 1 frase**: transformar a vertical Trading em backlog proprio, governado por risco, onde o pipeline oficial permanece `signal_intent -> validator -> HITL -> execution_gateway`
- **Valor esperado em 3 linhas**:
  - isolar uma capacidade de alto risco estrutural do runtime generico
  - tornar auditavel o caminho oficial de validacao, aprovacao e execucao
  - manter enablement, capital ramp e expansao multiativos sob gates explicitos

## 2. Problema ou Oportunidade

- **Problema atual**: a vertical de trading ja possui documentos normativos ricos, mas ainda estava representada por um PRD placeholder de scaffold
- **Evidencia do problema**: `TRADING-PRD`, `TRADING-RISK-RULES`, `TRADING-ENABLEMENT-CRITERIA` e `SEC-POLICY` descrevem gates e contratos especificos que nao se confundem com backlog generico
- **Custo de nao agir**: trading corre o risco de virar apenas mais uma integracao do runtime, escondendo risco financeiro, `TRADING_BLOCKED` e enablement por estagio
- **Por que agora**: a auditoria do worktree atual separou Mission Control, Host Ops e Trading; a vertical precisa backlog proprio antes de qualquer execucao

## 3. Publico e Operadores

- **Usuario principal**: operador humano habilitado a supervisionar a vertical Trading
- **Usuario secundario**: engenharia de risco, arquitetura, seguranca e PM responsaveis por gates de enablement
- **Operador interno**: runtime de trading conectado ao backbone do Mission Control
- **Quem aprova ou patrocina**: mantenedor responsavel por risco/vertical Trading

## 4. Jobs to be Done

- **Job principal**: operar a vertical Trading com sinais, validacao, aprovacao e execucao sob controles hard de risco e auditoria
- **Jobs secundarios**: bloquear bypass de ordem direta; garantir que `pre_trade_validator` governe a entrada em live; promover capital e classes de ativo apenas com checklist e decisao formal
- **Tarefa atual que sera substituida**: deduzir a vertical de trading a partir de varios documentos normativos dispersos

## 5. Escopo

### Dentro

- pipeline oficial `signal_intent -> normalizacao/deduplicacao -> pre_trade_validator -> HITL -> execution_gateway`
- enablement por estagios `S0`, `S1` e `S2` com `TRADING_BLOCKED`, `capital_ramp_level` e checklist
- governanca das integracoes `TradingAgents`, `AI-Trader`, `ClawWork` e venues ativas da fase inicial
- risk rules, gates executaveis e bloqueio de bypass para side effects financeiros

### Fora

- toolkit host-side macOS e restore operacional do repo `openclaw`
- redefinicao do runtime core, router e memory plane alem do que Trading consome
- alavancagem, derivativos e qualquer execucao live sem enablement formal
- ativacao imediata de `equities_br`, `fii_br` ou `fixed_income_br`

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: tornar a vertical Trading um produto separado, auditavel e governado por risco
- **Metricas leading**:
  - `make eval-trading` cobre cenarios hard-risk bloqueantes
  - toda tentativa de ordem direta externa e rejeitada e auditada
  - `pre_trade_validator` bloqueia casos invalidos com motivo explicito
- **Metricas lagging**:
  - 7 dias verdes de gates obrigatorios antes do capital real
  - zero incidentes `SEV-1/SEV-2` nas janelas minimas de enablement
  - ausencia de bypass de `execution_gateway_only`
- **Criterio minimo para considerar sucesso**: o backlog consegue transformar trading em entregas observaveis sem perder a fronteira de risco

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: `execution_gateway_only`, `pre_trade_validator` obrigatorio, idempotencia de ordem e reconciliacao em falha parcial
- **Restricoes operacionais**: `paper/sandbox` antes de capital real; `capital_ramp_level=L0` na primeira entrada live; aprovacao humana explicita por ordem
- **Restricoes legais ou compliance**: credencial live sem saque; IP allowlist quando suportado; operadores autorizados para comandos criticos
- **Restricoes de prazo**: este PRD fecha backlog da vertical inicial; rollout multiativos detalhado fica para fases posteriores
- **Restricoes de design ou marca**: o foco e governanca de risco e execucao segura, nao dashboard dedicado

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: `OC-MISSION-CONTROL`, `execution_gateway`, `pre_trade_validator`, policy engine, canais HITL, trilhas de auditoria
- **Sistemas externos impactados**: venues, integradores de sinal e frameworks externos permitidos
- **Dados de entrada necessarios**: `signal_intent`, asset profiles, risk rules, enablement criteria, credenciais e allowlists governadas
- **Dados de saida esperados**: ordens aprovadas e executadas pelo gateway oficial, logs auditaveis e bloqueios explicitos quando necessario

## 9. Arquitetura Geral do Projeto

- **Backend**: pipeline de sinal, validacao, aprovacao e execucao governada
- **Frontend**: nao aplicavel; interfaces humanas entram via canais HITL e evidencias
- **Banco/migracoes**: nao aplicavel neste recorte documental
- **Observabilidade**: audit trail de sinais, validacoes, ordens, bloqueios e gates de enablement
- **Autorizacao/autenticacao**: canais confiaveis, allowlists, credenciais sem saque e gates de operador
- **Rollout**: paper -> micro-live -> escala, sempre com veredito humano

## 10. Riscos Globais

- **Risco de produto**: tratar trading como backlog generico e apagar fronteira de risco
- **Risco tecnico**: bypass de `execution_gateway_only` ou validator insuficiente
- **Risco operacional**: pressao para pular janelas minimas e checklists
- **Risco de dados**: vazamento de credenciais ou trilhas auditaveis incompletas
- **Risco de adocao**: habilitar live sem evidence refs suficientes

## 11. Nao-Objetivos

- misturar trading com toolkit host-side
- transformar Trading em backlog generico do Mission Control
- habilitar classes de ativo ou modos live fora dos gates definidos

## 12. Features do Projeto

### Feature 1: Ingerir `signal_intent` sem bypass

#### Objetivo de Negocio

Garantir que engines externas entreguem sinais, e nao ordens diretas, respeitando o caminho oficial da vertical.

#### Comportamento Esperado

`AI-Trader`, `TradingAgents` e integrações semelhantes so podem entrar pelo contrato `signal_intent`; payloads que tentem pular etapas sao rejeitados e auditados.

#### Criterios de Aceite

- `AI-Trader` opera apenas em `signal_only`
- payload de ordem direta externa e rejeitado e auditado
- a normalizacao e deduplicacao de sinais preserva trilha rastreavel

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T1 | Formalizar contratos de `signal_intent` e adapters permitidos | 3 | - |
| T2 | Validar rejeicao de bypass e evidencias de auditoria | 3 | T1 |

### Feature 2: Validar ordens com `pre_trade_validator`

#### Objetivo de Negocio

Impedir ordens invalidas antes de qualquer side effect financeiro.

#### Comportamento Esperado

Toda ordem elegivel passa por `pre_trade_validator`, que aplica risco por trade, stop obrigatorio, min notional, lot size, tick size, fees e slippage.

#### Criterios de Aceite

- risco por trade fica <= 1% do equity
- stoploss e obrigatorio
- regras por classe de ativo sao avaliadas antes da aprovacao humana

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T3 | Definir baseline do `pre_trade_validator` por classe inicial de ativo | 5 | T1 |
| T4 | Evidenciar bloqueios hard-risk e mensagens explicitas | 3 | T3 |

### Feature 3: Operar `execution_gateway_only` com HITL

#### Objetivo de Negocio

Manter o gateway oficial como unico ponto de side effect financeiro e preservar aprovacao humana por ordem.

#### Comportamento Esperado

So `execution_gateway` envia ordens live; cada ordem exige aprovacao humana e replay idempotente vira `no-op` auditavel.

#### Criterios de Aceite

- somente `execution_gateway` envia ordem live
- toda ordem com side effect financeiro tem aprovacao explicita por ordem
- replay de `client_order_id + idempotency_key` vira `no-op` auditavel

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T5 | Formalizar contrato do gateway e pontos de aprovacao HITL | 5 | T3 |
| T6 | Evidenciar idempotencia e reconciliacao de falha parcial | 3 | T5 |

### Feature 4: Promover `paper -> micro-live -> escala`

#### Objetivo de Negocio

Liberar capital real apenas quando gates, evidencias e janelas minimas estiverem verdes.

#### Comportamento Esperado

`S0` nao envia ordem real; `S1` inicia em `capital_ramp_level=L0`; `S2` so ocorre com checklist, gates e decisao formal.

#### Criterios de Aceite

- `TRADING_BLOCKED` permanece ativo enquanto qualquer gate obrigatorio falhar
- `pre_live_checklist` bloqueia capital real quando qualquer item falha
- promocoes de estagio e capital exigem evidence refs e decisao humana

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T7 | Formalizar checklist e janelas minimas de enablement | 3 | T5 |
| T8 | Amarrar `TRADING_BLOCKED` e capital ramp a evidence refs | 3 | T7 |

### Feature 5: Governar integracoes e expansao multiativos

#### Objetivo de Negocio

Expandir a vertical sem romper fail-closed nem misturar risco de novas classes de ativo ao MVP.

#### Comportamento Esperado

`crypto_spot` permanece classe inicial; novas classes entram apenas com `asset_profile`, `venue_adapter`, `validator_profile` e suites dedicadas.

#### Criterios de Aceite

- novas classes de ativo exigem contracts e evidencias dedicadas
- falha da engine primaria entra em `fail_closed`
- engines secundarias so degradam para modos permitidos explicitamente

#### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---|---|---|---|
| T9 | Definir criterio de entrada para nova classe de ativo | 3 | T8 |
| T10 | Formalizar fail-closed e single-engine mode das integracoes | 3 | T9 |

## 13. Estrutura de Fases

## Fase 1: Sinal e validacao

- **Objetivo**: fechar signal intake governado e baseline do `pre_trade_validator`.
- **Features incluidas**: Feature 1, Feature 2
- **Gate de saida**: sinais externos entram sem bypass e ordens invalidas sao bloqueadas antes do HITL.

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F1-01 | Feature 1, Feature 2 | todo | 14 |

## Fase 2: Gateway e enablement

- **Objetivo**: consolidar `execution_gateway_only` e rollout paper -> micro-live -> escala.
- **Features incluidas**: Feature 3, Feature 4
- **Gate de saida**: ordem live so flui pelo gateway oficial, com gates de enablement verdes.

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F2-01 | Feature 3, Feature 4 | todo | 14 |

## Fase 3: Integracoes e multiativos

- **Objetivo**: governar expansao externa e novas classes de ativo sem romper fail-closed.
- **Features incluidas**: Feature 5
- **Gate de saida**: criterio formal de entrada de nova classe e degradacao segura documentados.

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|---|---|---|---|
| EPIC-F3-01 | Feature 5 | todo | 6 |

## 14. Epicos

### Epico: Sinal governado e validator baseline

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1, Feature 2
- **Objetivo**: entregar a entrada oficial de sinais e a primeira malha de validacao hard-risk.
- **Resultado de Negocio Mensuravel**: nenhuma ordem chega ao HITL sem antes passar pelo contrato de sinal e pelo validator.
- **Definition of Done**:
  - [ ] contratos de `signal_intent` formalizados
  - [ ] bypass bloqueado e auditado
  - [ ] `pre_trade_validator` baseline definido para a classe inicial de ativo

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|---|---|---|---|---|
| ISSUE-F1-01-001 | Formalizar `signal_intent` e bloquear bypass externo | 6 | todo | Feature 1 |
| ISSUE-F1-01-002 | Definir baseline do `pre_trade_validator` | 8 | todo | Feature 2 |

## 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|---|---|---|---|---|
| Mission Control | runtime | OC-MISSION-CONTROL | Trading depende de HITL, policy e execution backbone | active |
| Trading integrations | integracoes externas | TradingAgents, AI-Trader, ClawWork, venues | alimentam sinais e execucao conforme gates | active |

## 16. Rollout e Comunicacao

- **Estrategia de deploy**: paper -> micro-live -> escala, sempre com checkpoint humano
- **Comunicacao de mudancas**: evidencias e decision refs precisam acompanhar qualquer gate de enablement
- **Treinamento necessario**: operadores precisam dominar risk rules, checklist e canal HITL autorizado
- **Suporte pos-launch**: backlog proprio em `PROJETOS/OC-TRADING/`

## 17. Revisoes e Auditorias

- **Auditorias planejadas**: ao fim de cada fase da vertical
- **Criterios de auditoria**: aderencia aos gates de risco, evidence refs e fail-closed
- **Threshold anti-monolito**: seguir `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md` quando a base de codigo crescer

## 18. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
- [x] Dependencias externas mapeadas
- [x] Riscos e guardrails documentados
- [x] Rollout planejado

## 19. Anexos e Referencias

- [Intake](PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md)
- [Audit Log](PROJETOS/OC-TRADING/AUDIT-LOG.md)
- [Decision de projetos](PROJETOS/_WORK-MIGRACAO-OPENCLAW/DECISAO-PROJETOS.md)
