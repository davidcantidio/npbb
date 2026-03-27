---
doc_id: "INTAKE-OC-MISSION-CONTROL.md"
version: "1.0"
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

# INTAKE - OC-MISSION-CONTROL

> Intake retroativo do backbone operacional do OpenClaw, reexpresso no paradigma feature-first.

## 0. Rastreabilidade de Origem

- projeto de origem: OpenClaw Agent OS document-first com baseline operacional local ativo
- fase de origem: consolidacao de F0/F10/F11, com backlog B0 remanescente e controles normativos transversais
- auditoria de origem: nao_aplicavel
- relatorio de origem: `assistant-brain/PRD/PRD-MASTER.md`, `assistant-brain/PRD/ROADMAP.md`, `assistant-brain/ARC/ARC-CORE.md`
- motivo da abertura deste intake: rebater o legado plataforma-first em um projeto feature-first para o backbone operacional do Mission Control, sem misturar toolkit host ou rollout financeiro

### Fontes principais

- `assistant-brain/README.md`
- `assistant-brain/PRD/PRD-MASTER.md`
- `assistant-brain/PRD/ROADMAP.md`
- `assistant-brain/ARC/ARC-CORE.md`
- `assistant-brain/SEC/SEC-POLICY.md`
- `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`
- `assistant-brain/apps/control-plane/README.md`
- `assistant-brain/apps/ops-api/README.md`
- `assistant-brain/platform/policy-engine/README.md`
- `assistant-brain/PM/PHASES/F10-CONVERGENCIA-PRD-RUNTIME-SEM-REGRESSAO/EPIC-F10-02-CONVERGENCIA-PRD-SEM-PERDA-DE-ESTADO.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-03-BUDGET-PRIVACIDADE-A2A-E-HOOKS-GOVERNADOS.md`
- `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-04-INTEGRACAO-PROMOCAO-E-EVIDENCIA-OPERACIONAL.md`

### Mapeamento de features prioritarias

- `Operar runtime governado com estado preservado`
  - actor: operador de runtime
  - fontes: `assistant-brain/PRD/PRD-MASTER.md`, `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/PM/PHASES/F10-CONVERGENCIA-PRD-RUNTIME-SEM-REGRESSAO/EPIC-F10-02-CONVERGENCIA-PRD-SEM-PERDA-DE-ESTADO.md`
- `Decidir roteamento de modelos com trilha requested/effective`
  - actor: runtime e operadores internos
  - fontes: `assistant-brain/apps/control-plane/README.md`, `assistant-brain/apps/ops-api/README.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md`
- `Persistir memoria, runs e budget por trace_id`
  - actor: operador, auditoria e analytics operacional
  - fontes: `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/PRD/ROADMAP.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-02-CATALOGO-ROUTER-E-MEMORY-OPERACIONAIS.md`
- `Executar HITL seguro em canais confiaveis`
  - actor: operador humano habilitado
  - fontes: `assistant-brain/README.md`, `assistant-brain/SEC/SEC-POLICY.md`, `assistant-brain/DEV/DEV-OPENCLAW-SETUP.md`, `assistant-brain/PM/PHASES/F9-ONBOARDING-CREDENCIAIS-E-CANAIS-AUTOMATIZADOS/EPIC-F9-02-BOOTSTRAP-TELEGRAM-E-SLACK-SOCKET-MANIFEST.md`
- `Governar A2A e hooks com allowlist, assinatura e idempotencia`
  - actor: seguranca e orquestrador
  - fontes: `assistant-brain/ARC/ARC-CORE.md`, `assistant-brain/platform/policy-engine/README.md`, `assistant-brain/PM/PHASES/F11-RUNTIME-FIRST-B0-REMANESCENTE/EPIC-F11-03-BUDGET-PRIVACIDADE-A2A-E-HOOKS-GOVERNADOS.md`

## 1. Resumo Executivo

- nome curto da iniciativa: Mission Control governado do OpenClaw
- tese em 1 frase: transformar o legado do OpenClaw em um produto operacional claro, cujo valor MVP e executar runtime governado com roteamento, memoria, budget, HITL e integracoes seguras como um backbone unico auditavel
- valor esperado em 3 linhas:
  - consolidar em um unico projeto o backbone operacional hoje espalhado entre PRD, ARC, SEC, DEV, fases F10/F11 e READMEs de apps
  - priorizar features demonstraveis de runtime em vez de organizar o trabalho por camada tecnica
  - preparar o gate canonico para um PRD posterior sem misturar toolkit host ou trading

## 2. Problema ou Oportunidade

- problema atual: o legado descreve Mission Control por componentes, backlog B0 e fases arquiteturais, mas nao existe um intake feature-first que feche claramente o que o backbone operacional precisa entregar como produto auditavel
- evidencia do problema: `PRD-MASTER`, `ROADMAP`, `ARC-CORE`, `SEC-POLICY` e epicos F10/F11 descrevem runtime, router, budget, privacidade, HITL e hooks em documentos separados, enquanto o repo `openclaw` atual expõe apenas parte da realidade implantavel host-side
- custo de nao agir: o PRD posterior tendera a virar monolito documental, misturando runtime core, operacao host e trading; isso piora priorizacao, rastreabilidade e definicao de fronteiras
- por que agora: a base normativa do framework ja exige `Intake -> PRD`, e o OpenClaw precisa ser rebaseado para o paradigma feature-first antes de novas fases de entrega

## 3. Publico e Operadores

- usuario principal: operador responsavel por manter o runtime OpenClaw funcional, governado e auditavel
- usuario secundario: PM, arquitetura, seguranca e engenharia que precisam promover backlog, gates e rollout sem perder estado
- operador interno: runtime OpenClaw, `control-plane`, `ops-api` e policy engine
- quem aprova ou patrocina: mantenedor do produto/plataforma OpenClaw

## 4. Jobs to be Done

- job principal: operar o OpenClaw como Mission Control governado, com roteamento, memoria, budget, canais HITL e integracoes seguras funcionando como backbone unico
- jobs secundarios:
  - preservar estado operacional ao convergir configuracao e runtime
  - decidir modelo/provider com trilha explicavel e persistente
  - aplicar budget, privacidade, allowlists e idempotencia antes de side effects
  - manter auditoria por `trace_id` e promover mudancas com evidencia operacional
- tarefa atual que sera substituida: navegar entre varios documentos de produto/arquitetura/fase para deduzir o que o backbone realmente precisa entregar

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. O operador sobe um runtime governado com configuracao canônica, estado preservado e `gateway.bind=loopback`.
2. Uma solicitacao entra por canal ou cliente interno e o runtime calcula `router_decision` com `requested_model`, `effective_model`, `fallback_step` e motivo.
3. A execucao persiste `llm_run`, `router_decision`, snapshots de budget e contexto de privacidade em um read model correlacionado por `trace_id`.
4. Aprovacoes humanas criticas passam por Telegram primario ou Slack fallback controlado, sempre com allowlist, challenge e trilha auditavel.
5. Delegacoes A2A, hooks e side effects so avancam quando policy, assinatura, idempotencia e allowlists forem satisfeitas.

### Features MVP priorizadas

#### Feature 1 - Operar runtime governado com estado preservado

- actor: operador de runtime
- DoD comportamental:
  - runtime inicia com contratos minimos e `gateway.bind=loopback`
  - convergencia de configuracao nao apaga paths preservados
  - existe `dry-run` e rollback para ajustes estruturais
- dependencias: `assistant-brain/ARC/ARC-CORE.md`, backlog F10, config de runtime
- riscos: drift entre configuracao alvo e estado preservado

#### Feature 2 - Decidir roteamento de modelos com trilha requested/effective

- actor: runtime e arquitetura
- DoD comportamental:
  - `/router/decide` aceita `router_request` e devolve `router_decision` calculada no dominio
  - filtro por policy, risco e sensibilidade e aplicado antes de escolher provider
  - fallback e motivo ficam persistidos de forma explicavel
- dependencias: model catalog, router schemas, `ops-api`
- riscos: decisao ficar dependente de payload pronto ou perder explicabilidade

#### Feature 3 - Persistir memoria, runs e budget por `trace_id`

- actor: operador, auditoria e analytics operacional
- DoD comportamental:
  - `trace_snapshot` correlaciona run, decisao e contexto financeiro
  - historico/versionamento de catalogo e consultavel
  - budget snapshots e politicas aparecem no contexto do trace efetivo
- dependencias: `postgres`, read models, schemas `llm_run` e `credits_snapshot`
- riscos: paridade incompleta entre backends `memory` e `postgres`

#### Feature 4 - Executar HITL seguro em canais confiaveis

- actor: operador habilitado
- DoD comportamental:
  - Telegram continua como canal primario confiavel
  - Slack so atua como fallback validado, sem bypass de gates
  - comandos criticos carregam challenge, identidade valida e evidence ref
- dependencias: allowlists de operadores, bootstrap de canais, `ops-api` interno HITL
- riscos: roster de operadores e IDs de fallback ainda nao fechados

#### Feature 5 - Governar A2A e hooks com allowlist, assinatura e idempotencia

- actor: seguranca e orquestrador
- DoD comportamental:
  - A2A respeita `tools.agentToAgent.allow[]`
  - webhook com assinatura invalida ou replay nao produz side effect
  - duplicate replay vira `NO_OP_DUPLICATE` com trilha auditavel
- dependencias: runtime config, policy engine, schemas A2A/webhook
- riscos: confiar em flags precomputadas pelo payload em vez de validacao real

## 6. Escopo Inicial

### Dentro

- runtime governado do OpenClaw como backbone operacional unico
- roteamento de modelos, persistencia de catalogo, `llm_runs`, `trace_snapshot` e budget baseline
- HITL multi-canal governado, A2A permitido por allowlist e hooks/webhooks validados
- evidencias operacionais de promote, rollback e cobertura executavel das claims centrais

### Fora

- toolkit macOS `nemoclaw-host`, `LaunchAgents` e restore local do host
- rollout financeiro, `execution_gateway` e gates de capital real da vertical trading
- dashboard dedicado alem das superficies operacionais minimas
- migracao para microservices alem do necessario para o backbone atual

## 7. Resultado de Negocio e Metricas

- objetivo principal: deixar explicito o backbone que faz o OpenClaw operar como Mission Control governado e auditavel
- metricas leading:
  - toda decisao de roteamento exibe `requested_model`, `effective_model`, `fallback_step` e motivo
  - toda run critica carrega contexto de budget e privacidade por `trace_id`
  - todo side effect sensivel e bloqueado quando allowlists, budget ou assinatura falham
- metricas lagging:
  - gates obrigatorios do backbone permanecem verdes por ciclos consecutivos
  - reducao de backlog ambiguo entre PRD, ARC, PM e SEC sobre o que pertence ao runtime core
  - promocao/rollback do runtime deixa de depender de edicao manual ad-hoc
- criterio minimo para considerar sucesso: o PRD posterior consegue organizar o produto por features operacionais observaveis, sem reabrir a discussao de fronteira com host ou trading

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - runtime canonico com `gateway.bind=loopback`
  - chamadas programaticas a providers passam pelo OpenClaw Gateway
  - control-plane, router e memoria precisam manter trilha auditavel e compatibilidade com schemas
- restricoes operacionais:
  - claims centrais exigem gate executavel antes de promote
  - fallback humano critico depende de canais confiaveis e operador allowlisted
  - automacoes com side effect exigem idempotencia e rollback
- restricoes legais ou compliance:
  - politica de menor privilegio
  - `public/internal/sensitive` com provider allowlist e ZDR quando aplicavel
  - email nao e canal confiavel para comando
- restricoes de prazo: rebasear o legado em intake agora, sem tentar resolver todo o backlog B0/F11 nesta fase
- restricoes de design ou marca: nao ha UI de marca como driver principal; a prioridade e a operacao segura do runtime

## 9. Dependencias e Integracoes

- sistemas internos impactados:
  - `control-plane`
  - `ops-api`
  - `policy-engine`
  - `workspaces/main`
  - `SEC/allowlists/*`
  - `PM/TRACEABILITY/*`
- sistemas externos impactados:
  - Telegram
  - Slack
  - providers roteados por LiteLLM/OpenRouter
  - infraestrutura de banco operacional (`postgres` + `pgvector` ou equivalente funcional)
- dados de entrada necessarios:
  - `router_request`
  - runtime config
  - payloads de canais/hook
  - snapshots de budget
  - catalogo de modelos/provedores
- dados de saida esperados:
  - `router_decision`
  - `llm_run`
  - `trace_snapshot`
  - eventos HITL/A2A/hook persistidos com `trace_id`

Dependencia cruzada declarada:

- este projeto e upstream de `OC-TRADING`
- este projeto nao inclui o toolkit de `OC-HOST-OPS`, embora dependa de um host funcional para operacao local

## 10. Arquitetura Afetada

- backend: `control-plane`, `ops-api`, services de router/catalog/memory/budget/privacy/A2A/webhook
- frontend: nao ha painel dedicado como escopo MVP; as superficies de comando sao canais confiaveis e clientes internos
- banco/migracoes: memoria operacional, `llm_runs`, `router_decisions`, `credits_snapshots` e demais read models do runtime
- observabilidade: `trace_id`, artifacts de fase, bundles de canary/promocao/rollback e suites `eval-*`
- autorizacao/autenticacao: operators allowlisted, challenge de segundo fator, assinatura HMAC/anti-replay para Slack e hooks
- rollout: promover o backbone por gates executaveis, preservando baseline F10 e fechando deltas F11 sem perda de estado

## 11. Riscos Relevantes

- risco de produto: o projeto continuar descrito como soma de componentes tecnicos e nao como backbone operacional testavel
- risco tecnico: paridade incompleta entre runtime documentado e estado real do codigo/infra hoje implementado
- risco operacional: promote/rollback dependerem de passos manuais ou de canais sem fallback validado
- risco de dados: vazamento ou retenção inadequada em fluxos `sensitive` se provider allowlist/ZDR nao forem aplicados fim a fim
- risco de adocao: backlog permanecer acoplado a uma linguagem arquitetural-first e dificultar priorizacao por valor

## 12. Nao-Objetivos

- nao cobrir o toolkit host-side macOS
- nao definir rollout financeiro nem regras de `execution_gateway` de trading
- nao substituir o PRD posterior por backlog completo nesta fase
- nao forcar migracao arquitetural para microservices como objetivo do intake

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: recorte final entre estado canonico em `Convex` e estado canonico em `postgres` para o control-plane de produto
- dependencia ainda nao confirmada: roster final de operadores, `slack_user_ids`, `slack_channel_ids` e `backup_operator` habilitado no fallback critico
- dado ainda nao disponivel: bundle unico de evidencias do estado real do runtime fora do corpus documental lido
- decisao de UX ainda nao fechada: existe mencao a dashboard opcional, mas o intake nao assume painel dedicado como parte do MVP
- outro ponto em aberto:
  - cadence final de revisao de compatibilidade com OpenClaw upstream
  - criterio operacional exato para promote quando `Convex` e control-plane completo ainda estiverem parciais

## 15. Perguntas que o PRD Precisa Responder

- Qual e o recorte de fases que transforma as cinco features MVP em backlog executavel sem reabrir arquitetura-first?
- Qual contrato canônico de persistencia e leitura sera tratado como fonte de verdade para promote no control-plane completo?
- Quais evidencias minimas bloqueiam promote quando Telegram, Slack fallback, budget ou privacy gates estiverem degradados?

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
