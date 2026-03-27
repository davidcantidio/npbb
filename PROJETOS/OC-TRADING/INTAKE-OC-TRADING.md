---
doc_id: "INTAKE-OC-TRADING.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-20"
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

# INTAKE - OC-TRADING

> Intake retroativo da capacidade de trading governado de alto risco do OpenClaw.

## 0. Rastreabilidade de Origem

- projeto de origem: vertical Trading do OpenClaw com enablement progressivo e controles de risco/auditoria
- fase de origem: Fase 1 Trading e Fase 2 Expansao do roadmap, com integracoes governadas e criteria de capital real
- auditoria de origem: nao_aplicavel
- relatorio de origem: `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`, `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`
- motivo da abertura deste intake: traduzir o legado de trading para um projeto feature-first separado do Mission Control, preservando o alto risco estrutural e os gates proprios da vertical

### Fontes principais

- `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`
- `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`
- `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`
- `assistant-brain/PRD/ROADMAP.md`
- `assistant-brain/SEC/SEC-POLICY.md`
- `assistant-brain/INTEGRATIONS/README.md`
- `assistant-brain/INTEGRATIONS/AI-TRADER.md`
- `assistant-brain/INTEGRATIONS/CLAWWORK.md`
- `assistant-brain/INTEGRATIONS/OPENCLAW-UPSTREAM.md`

### Mapeamento de features prioritarias

- `Ingerir signal_intent de engines externas sem bypass`
  - actor: runtime de trading
  - fontes: `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/INTEGRATIONS/AI-TRADER.md`
- `Validar ordens com pre_trade_validator e regras hard`
  - actor: risk engine e operador
  - fontes: `assistant-brain/VERTICALS/TRADING/TRADING-RISK-RULES.md`, `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`
- `Operar execution_gateway_only com aprovacao humana por ordem`
  - actor: operador habilitado
  - fontes: `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`, `assistant-brain/SEC/SEC-POLICY.md`
- `Promover paper -> micro-live -> escala com checklist e gates`
  - actor: PM, risco e operador humano
  - fontes: `assistant-brain/VERTICALS/TRADING/TRADING-ENABLEMENT-CRITERIA.md`, `assistant-brain/PRD/ROADMAP.md`
- `Governar integracoes e expansao multiativos sem romper fail-closed`
  - actor: arquitetura e risco
  - fontes: `assistant-brain/INTEGRATIONS/README.md`, `assistant-brain/INTEGRATIONS/CLAWWORK.md`, `assistant-brain/VERTICALS/TRADING/TRADING-PRD.md`

## 1. Resumo Executivo

- nome curto da iniciativa: trading governado do OpenClaw
- tese em 1 frase: separar a vertical de trading em um projeto feature-first proprio, cujo MVP e operar sinais, validacao, aprovacao e execucao sob gates fortes de risco e enablement
- valor esperado em 3 linhas:
  - isolar uma capacidade de alto risco estrutural que nao pode ficar diluida dentro do runtime generico
  - deixar explicito o pipeline oficial `signal_intent -> validator -> HITL -> execution_gateway`
  - preparar um PRD posterior sem misturar trading com toolkit host ou backlog core de Mission Control

## 2. Problema ou Oportunidade

- problema atual: o legado de trading esta bem especificado em PRDs e politicas, mas aparece acoplado ao roadmap geral do OpenClaw; sem intake proprio, a vertical corre o risco de virar um apendice do runtime e perder a fronteira de risco, enablement e rollout financeiro
- evidencia do problema: `TRADING-PRD`, `TRADING-RISK-RULES`, `TRADING-ENABLEMENT-CRITERIA`, `SEC-POLICY` e `ROADMAP` descrevem contracts e bloqueios especificos que nao se confundem com o runtime geral
- custo de nao agir: backlog, PRD e execucao podem tratar trading como apenas mais uma integracao, reduzindo visibilidade do hard gate financeiro, do `TRADING_BLOCKED` e dos requisitos de reabilitacao
- por que agora: a migracao para feature-first precisa manter trading como projeto proprio antes de qualquer tentativa de gerar PRD e fases futuras

## 3. Publico e Operadores

- usuario principal: operador humano habilitado a supervisionar a vertical Trading
- usuario secundario: engenharia de risco, arquitetura, seguranca e PM responsaveis por gates de enablement e promote
- operador interno: runtime de trading conectado ao backbone do Mission Control
- quem aprova ou patrocina: mantenedor responsavel por risco/vertical Trading

## 4. Jobs to be Done

- job principal: operar a vertical Trading com sinais, validacao, aprovacao e execucao sob controles hard de risco e auditoria
- jobs secundarios:
  - bloquear qualquer bypass de ordem direta vindo de frameworks externos
  - garantir que `pre_trade_validator` e enablement gates governem a entrada em live
  - promover capital e classes de ativo somente com checklist, evidence refs e decisao formal
- tarefa atual que sera substituida: deduzir a vertical de trading a partir de varios documentos normativos espalhados pelo corpus

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. Engines externas produzem `signal_intent` governado e nunca enviam ordem direta para a venue.
2. O runtime normaliza o sinal, deduplica entradas e executa `pre_trade_validator` com regras hard da classe de ativo.
3. Toda ordem elegivel passa por HITL explicito e por `execution_gateway_only`, com idempotencia e trilha auditavel.
4. O ambiente evolui por estagios `S0 -> S1 -> S2`, mantendo `TRADING_BLOCKED` ate que checklist, evidencias e gates estejam verdes.
5. Promocoes de capital, de estagio ou de nova classe de ativo so ocorrem por decision e checkpoint humano.

### Features MVP priorizadas

#### Feature 1 - Ingerir `signal_intent` de engines externas sem bypass

- actor: runtime de trading
- DoD comportamental:
  - `AI-Trader` opera apenas em `signal_only`
  - `TradingAgents` aparece como engine primaria de sinal na Fase 1
  - payload que represente ordem direta externa e rejeitado e auditado
- dependencias: Mission Control, contratos de integracao e adapters de sinal
- riscos: framework externo conseguir burlar o caminho oficial de execucao

#### Feature 2 - Validar ordens com `pre_trade_validator` e regras hard

- actor: risk engine e operador
- DoD comportamental:
  - risco por trade fica <= 1% do equity
  - stoploss e obrigatorio
  - `min_notional`, `lot_size`, `tick_size`, fees e slippage sao validados antes da ordem
- dependencias: `pre_trade_validator`, `asset_profile`, regras da classe de ativo
- riscos: falsos negativos liberarem ordem invalida ou falsos positivos travarem a operacao sem contexto

#### Feature 3 - Operar `execution_gateway_only` com aprovacao humana por ordem

- actor: operador humano habilitado
- DoD comportamental:
  - somente `execution_gateway` pode enviar ordem live
  - toda ordem com side effect financeiro tem aprovacao explicita por ordem
  - replay de `client_order_id + idempotency_key` vira `no-op` auditavel
- dependencias: `OC-MISSION-CONTROL`, canais HITL, credenciais sem saque, allowlists
- riscos: canal critico indisponivel ou credenciais fora da politica

#### Feature 4 - Promover `paper -> micro-live -> escala` com checklist e gates

- actor: PM, risco e operador
- DoD comportamental:
  - `S0` nao envia ordem real e qualquer tentativa live mantem `TRADING_BLOCKED`
  - `S1` inicia em `capital_ramp_level=L0` e exige aprovacao humana por ordem
  - `pre_live_checklist` e gates de CI bloqueiam capital real quando qualquer item falha
- dependencias: `make eval-trading`, `pre_live_checklist`, evidence refs, backup operator
- riscos: pressao para pular janelas minimas ou checklist de enablement

#### Feature 5 - Governar integracoes e expansao multiativos sem romper fail-closed

- actor: arquitetura e risco
- DoD comportamental:
  - `crypto_spot` permanece classe inicial
  - novas classes so entram com `asset_profile`, `venue_adapter`, `validator_profile` e suites dedicadas
  - falha da engine primaria entra em `fail_closed`; engine secundaria so pode cair para `single_engine_mode`
- dependencias: integracoes externas, allowlists de dominio, backlog fase 2
- riscos: expandir classe de ativo ou modulo externo sem contracts nem evidencias suficientes

## 6. Escopo Inicial

### Dentro

- pipeline oficial de `signal_intent -> normalizacao/deduplicacao -> pre_trade_validator -> HITL -> execution_gateway`
- enablement por estagios `S0`, `S1` e `S2` com `TRADING_BLOCKED`, `capital_ramp_level` e checklist
- governanca das integracoes `TradingAgents`, `AI-Trader`, `ClawWork` e venues ativas da fase inicial
- risk rules, gates executaveis e bloqueio de bypass para side effects financeiros

### Fora

- toolkit host-side macOS e restore operacional do repo `openclaw`
- redefinicao do runtime core, router, memory plane e policy engine alem do que Trading consome
- alavancagem, derivativos e qualquer execucao live sem enablement formal
- ativacao imediata de `equities_br`, `fii_br` ou `fixed_income_br`

## 7. Resultado de Negocio e Metricas

- objetivo principal: tornar a vertical Trading um produto separado, auditavel e governado por risco, em vez de uma extensao generica do runtime
- metricas leading:
  - `make eval-trading` cobre 100% dos cenarios hard-risk bloqueantes
  - toda tentativa de ordem direta externa e rejeitada e auditada
  - `pre_trade_validator` bloqueia casos invalidos e explicita motivo do bloqueio
- metricas lagging:
  - 7 dias verdes de gates obrigatorios antes do capital real
  - zero incidentes `SEV-1/SEV-2` durante as janelas minimas de enablement
  - ausencia de bypass de `execution_gateway_only` e de ordens live em `S0`
- criterio minimo para considerar sucesso: o PRD posterior consegue transformar a vertical em backlog por comportamento observavel, mantendo trading isolado do runtime generico

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - `execution_gateway_only`
  - `pre_trade_validator` obrigatorio
  - idempotencia de ordem e reconciliacao em falha parcial
- restricoes operacionais:
  - `paper/sandbox` obrigatorio antes de capital real
  - `capital_ramp_level=L0` na primeira entrada live
  - aprovacao humana explicita por ordem em todos os estagios
- restricoes legais ou compliance:
  - credencial live sem saque
  - IP allowlist quando suportado
  - canais confiaveis e operadores autorizados para comandos criticos
- restricoes de prazo: este intake formaliza o recorte; nao resolve nesta fase o rollout multiativos nem o detalhamento completo do PRD
- restricoes de design ou marca: nao ha dashboard dedicado como driver; o foco e governanca de risco e execucao segura

## 9. Dependencias e Integracoes

- sistemas internos impactados:
  - `OC-MISSION-CONTROL`
  - `execution_gateway`
  - `pre_trade_validator`
  - `SEC/allowlists/*`
  - `artifacts/evals/trading/*`
- sistemas externos impactados:
  - Binance Spot
  - `TradingAgents`
  - `AI-Trader`
  - `ClawWork`
  - canais HITL Telegram/Slack
- dados de entrada necessarios:
  - `signal_intent`
  - `order_intent`
  - `market_state`
  - `asset_profile`
  - `capital_ramp_level`
  - checklist de prontidao
- dados de saida esperados:
  - `execution_report`
  - eventos de bloqueio/risco
  - artifacts de enablement e de `pre_live_checklist`

Dependencia cruzada declarada:

- este projeto depende do backbone de `OC-MISSION-CONTROL`
- este projeto nao redefine toolkit host-side nem restore local de `OC-HOST-OPS`

## 10. Arquitetura Afetada

- backend: risk engine, `pre_trade_validator`, `execution_gateway`, integracoes de sinal e flows de enablement
- frontend: nao ha painel dedicado como parte do MVP; aprovacao ocorre por HITL governado
- banco/migracoes: trilha auditavel de ordens, eventos de risco, checklists e artifacts de eval/enablement
- observabilidade: `make eval-trading`, artifacts `summary.json`, `failures.jsonl`, `pre_live_checklist` e incidentes de bloqueio
- autorizacao/autenticacao: operadores allowlisted, canais HITL validados, credenciais live sem saque e IP allowlist quando suportado
- rollout: `S0 -> S1 -> S2` com `TRADING_BLOCKED` como estado seguro default e desbloqueio somente por decision formal

## 11. Riscos Relevantes

- risco de produto: a vertical perder sua fronteira propria e ser tratada como extensao simplificada do runtime geral
- risco tecnico: bypass de ordem direta ou validacao incompleta de `pre_trade_validator`
- risco operacional: canais HITL ou backup operator nao estarem prontos no momento de promover capital real
- risco de dados: vazamento de credenciais, payloads sensiveis ou eventos financeiros sem trilha minima
- risco de adocao: friccao operacional levar a tentativas de pular `paper/sandbox`, checklist ou gates de CI

## 12. Nao-Objetivos

- nao misturar o backlog de trading com o runtime core de Mission Control
- nao incluir toolkit host-side e restore local macOS
- nao habilitar multiativos alem de `crypto_spot` como parte do MVP
- nao permitir qualquer caminho de ordem live sem `execution_gateway_only` e HITL por ordem

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: peso operacional final entre `TradingAgents`, `AI-Trader` e modulos futuros de `AgenticTrading`
- dependencia ainda nao confirmada: operadores habilitados, `backup_operator` e fallback Slack totalmente prontos para trading live
- dado ainda nao disponivel: evidencias completas da janela minima de `paper/sandbox` no bundle atual de artifacts
- decisao de UX ainda nao fechada: nao existe painel dedicado de trading assumido no MVP; a experiencia continua centrada em HITL e artifacts
- outro ponto em aberto:
  - `asset_profiles`, `venue_adapters` e `validator_profiles` das classes alem de `crypto_spot` ainda nao estao publicados no repo-alvo
  - detalhes finais de broker adapter para `equities_br`, `fii_br` e `fixed_income_br`

## 15. Perguntas que o PRD Precisa Responder

- Quais fases separam de forma segura o MVP `crypto_spot` dos refinamentos multiativos sem diluir o hard gate financeiro?
- Qual backlog minimo fecha `execution_gateway`, `pre_trade_validator`, checklist de capital real e integracoes de sinal sem reabrir o runtime core?
- Quais evidencias bloqueiam ou liberam promote entre `S0`, `S1` e `S2` no estado real do repositorio?

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
