---
doc_id: "PRD-ATIVOS-INGRESSOS.md"
version: "2.1"
status: "approved"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "workflow-improvement"
delivery_surface: "fullstack-module"
business_domain: "eventos"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "ativos"
  - "ingressos"
  - "dashboard"
  - "internal/registry"
  - "internal/ingestao-inteligente"
  - "internal/revisao-humana"
  - "email"
change_type: "evolucao"
audit_rigor: "elevated"
---

# PRD - ATIVOS-INGRESSOS

> Principio **delivery-first**. Este documento cobre produto, escopo, restricoes, riscos, metricas,
> arquitetura geral e rollout. A decomposicao em Features, User Stories e Tasks e etapa **posterior**
> (`SESSION-DECOMPOR-PRD-EM-FEATURES.md`, `PROMPT-PRD-PARA-FEATURES.md`).
>
> **Especificacao Funcional** = fonte autoritativa do o que e por que. **Plano Tecnico** = como derivado;
> em conflito, a Especificacao Funcional prevalece.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-ATIVOS-INGRESSOS.md](./INTAKE-ATIVOS-INGRESSOS.md)
- **Versao do intake**: 1.0
- **Data de criacao deste PRD**: 2026-03-26
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: operacao de ativos e ingressos (ATIVOS-INGRESSOS)
- **Tese em 1 frase**: criar a capacidade operacional para prever, receber, conciliar, emitir, distribuir e analisar ingressos internos e de ticketeiras em um fluxo auditavel
- **Valor esperado em 3 linhas**:
  - receber ativos internos e externos em formatos heterogeneos com rastreabilidade de origem, quantidade e categoria
  - emitir ingressos internos unitarios com identificador unico por destinatario (QR) e preparar o dominio para validacao futura de uso unico
  - acompanhar planejado, recebido, distribuido, bloqueado, remanejado, aumentado, reduzido e problemas em um dashboard operacional aderente ao padrao ja existente do modulo Dashboard

## 2. Especificacao Funcional

> Descreve **o que** precisa ser entregue e **por que**. Nao usa stack, framework, endpoint, esquema
> fisico ou ferramenta como eixo da especificacao.

### 2.1 Problema ou Oportunidade

- **Problema atual**: o dominio atual de ativos controla apenas cotas agregadas por evento e diretoria, sem categorias de ingresso, sem reconciliacao planejado versus recebido, sem inventario unitario por destinatario e sem camada de autenticidade (QR) para ingressos internos
- **Evidencia do problema**: o produto hoje usa controle agregado (por exemplo cotas e solicitacoes agregadas); nao ha modelagem para categorias como pista, pista premium e camarote; nao ha suporte consistente a divergencia entre quantidade cadastrada e quantidade recebida da ticketeira; ingressos internos ainda nao contam com mecanismo de autenticidade por limitacao tecnologica
- **Custo de nao agir**: a operacao continua dependente de email, armazenamento compartilhado e planilhas paralelas, com risco de enviar categoria errada, distribuir acima do recebido, perder rastreabilidade de problemas e operar sem base confiavel para dashboard gerencial
- **Por que agora**: a equipe vai assumir a distribuicao efetiva dos ingressos e precisa suportar eventos reais com ativos mistos, conciliacao entre previsao e recebimento, emissao interna segura e visibilidade operacional

### 2.2 Publico e Operadores

- **Usuario principal**: equipe operacional NPBB responsavel por receber, preparar e distribuir ativos dos eventos
- **Usuario secundario**: diretorias, gestores e patrocinadores internos que acompanham saldo, distribuicao, bloqueios, remanejamentos e problemas
- **Operador interno**: operacao NPBB no produto e automacao externa (por exemplo skill OpenClaw) que pode consumir emails de ticketeiras e alimentar o sistema via contratos expostos pelo backend
- **Quem aprova ou patrocina**: PM e lideranca operacional de eventos

### 2.3 Jobs to be Done

- **Job principal**: transformar recebimentos heterogeneos de ingressos em inventario distribuivel, auditavel e visivel para a operacao
- **Jobs secundarios**: configurar categorias por evento; conciliar divergencias de quantidade; emitir ingressos internos com identificador unico por destinatario; bloquear distribuicao quando houver dependencia de recebimento externo; registrar problemas; gerar leitura executiva no dashboard
- **Tarefa atual que sera substituida**: controle manual em email, armazenamento compartilhado e planilhas para entender o que foi recebido, para quem enviar, o que foi remanejado e onde houve erro operacional

Fluxo desejado e estados canonicos (orientam o dominio e as leituras de saldo; o desenho exato de entidades e transicoes fica no Plano Tecnico e nos manifestos de feature posteriores):

- **planejado**: quantidade prevista no cadastro operacional por evento, diretoria e categoria
- **recebido_confirmado**: quantidade ou artefato efetivamente entregue e conciliado no sistema
- **disponivel**: saldo apto a ser distribuido
- **bloqueado_por_recebimento**: aumento cadastrado que ainda nao pode ser distribuido porque depende de entrega da ticketeira
- **distribuido**: ingresso ou ativo efetivamente vinculado e enviado ao destinatario
- **remanejado**: realocacao entre areas, categorias ou destinatarios ja registrados (somente realocacao efetiva)
- **aumentado**: incremento de previsao ou estoque, distinto de remanejamento
- **reduzido**: reducao de previsao ou estoque, distinto de remanejamento
- **problema_registrado**: ocorrencia operacional documentada para acompanhamento e dashboard
- **qr_emitido**: ingresso interno gerado com identificador unico por destinatario (QR)
- **qr_validado**: estado futuro, fora do escopo inicial do produto, para semantica de uso unico na entrada do evento

Fluxo ponta a ponta em etapas:

1. Operador cadastra a previsao de ativos por evento, diretoria, categoria e modo de fornecimento.
2. O sistema registra o que foi efetivamente recebido, concilia divergencias e, para origem ticketeira, trata o recebido confirmado como fonte de verdade para o estoque distribuivel.
3. Para ingressos internos, o sistema emite um ingresso unitario por destinatario a partir do layout da categoria, associa identificador unico (QR) e persiste identidade suficiente para validacao futura; para ativos externos, libera distribuicao somente ate o limite confirmado como recebido.
4. A operacao distribui, remaneja, registra aumentos, reducoes, bloqueios, reenvios e problemas; o dashboard consolida indicadores, graficos, acompanhamento por data e painel de ocorrencias.

### 2.4 Escopo

#### Dentro

- configuracao por evento das categorias iniciais pista, pista premium e camarote, com suporte a eventos que usem apenas parte do catalogo
- dois modos canonicos de fornecimento: interno emitido com QR e externo recebido
- conciliacao entre quantidade planejada e quantidade recebida
- regra de prevalencia do recebido confirmado para ativos originados em ticketeira
- bloqueio operacional para aumentos dependentes de ticketeira ate o recebimento correspondente
- emissao de ingressos internos unitarios com identificador unico por destinatario (QR)
- persistencia e rastreabilidade de arquivos compartilhados, ingressos unitarios externos, links de armazenamento e instrucoes textuais recebidas
- fluxo de distribuicao, remanejamento, aumento, reducao e registro de problemas operacionais
- dashboard de ativos dentro do modulo Dashboard, seguindo o padrao visual e estrutural ja adotado no dashboard de leads
- exposicao de contratos de dados e operacoes suficientes para integracao com automacao externa que le emails de ticketeiras (sem inbox nativo no produto)

#### Fora

- leitura direta de caixa de email dentro do NPBB
- desenvolvimento da skill OpenClaw neste repositorio
- implementacao completa do validador ou scanner de QR no primeiro corte de produto descrito neste PRD
- conciliacao financeira de bilheteria ou integracao completa com venda de ingressos
- redesign do modulo Dashboard fora do padrao ja homologado no produto

### 2.5 Resultado de Negocio e Metricas

- **Objetivo principal**: reduzir erro operacional e tempo de distribuicao de ingressos, aumentando a confiabilidade do estoque operacional e a visibilidade executiva sobre ativos
- **Metricas leading**: percentual de eventos com categorias configuradas; percentual de lotes com origem e artefatos rastreados; tempo entre recebimento e disponibilidade; percentual de distribuicoes com status registrado; percentual de ingressos internos emitidos com identificador unico (QR)
- **Metricas lagging**: taxa de reenvio ou erro operacional; tempo medio entre recebimento e envio final; quantidade de bloqueios por falta de recebimento; quantidade de problemas operacionais por evento; uso recorrente do dashboard pela operacao
- **Criterio minimo para considerar sucesso**: um evento real consegue ser operado ponta a ponta com previsao, recebimento, conciliacao, emissao ou distribuicao e acompanhamento no dashboard sem depender de planilha paralela como fonte de verdade

### 2.6 Restricoes e Guardrails

- **Restricoes tecnicas**: a evolucao deve conviver com o modelo atual de cotas e solicitacoes agregadas durante a transicao, sem quebrar operacoes existentes antes do rollout controlado
- **Restricoes operacionais**: para origem externa recebida, a quantidade distribuivel deve refletir o recebido confirmado, mesmo quando divergir do planejado; aumentos dependentes de ticketeira ficam bloqueados por recebimento ate o recebimento correspondente; remanejado significa apenas realocacao efetiva; aumento, reducao e saldo nao distribuido devem aparecer como leituras separadas; no primeiro release operacional, a dimensao Area do painel sera tratada como equivalente a Diretoria ate decisao documentada em contrario
- **Restricoes legais ou compliance**: arquivos de ingresso, links, emails de destinatarios e QR codes devem ser tratados como dados sensiveis sob LGPD, com controle de acesso e trilha auditavel
- **Restricoes de prazo**: priorizar um corte operacional real para ao menos um evento antes de expandir automacoes adicionais
- **Restricoes de design ou marca**: o documento operacional externo de referencia (por exemplo metricas e graficos de acompanhamento) orienta informacao e leituras, nao layout ou arte final; a implementacao visual deve seguir o padrao ja usado pelo dashboard de leads

### 2.7 Dependencias e Integracoes

- **Sistemas internos impactados**: modulo de ativos, modulo de ingressos, dashboard, catalogo de fontes em registro interno, contratos de ingestao inteligente, workbench de revisao humana, servico atual de email e dominio de eventos
- **Sistemas externos impactados**: ticketeiras, links de armazenamento recebidos por email, provedores de email de saida e automacao operacional externa (OpenClaw)
- **Dados de entrada necessarios**: evento, diretoria, categoria, modo de fornecimento, quantidade planejada, quantidade recebida, arquivos ou links, instrucoes do emissor, destinatarios, status de envio, motivo de remanejamento, aumento ou reducao e ocorrencias
- **Dados de saida esperados**: inventario reconciliado, historico de distribuicao, bloqueios por recebimento, trilha de remanejamentos, registro de problemas, dashboard operacional e contratos consumiveis por integracoes externas

## 3. Hipoteses Congeladas

> Resultado do gate Intake para clarificacao pre-PRD; decisoes fechadas sem inventar regra de negocio ausente no intake.

- **Lacunas resolvidas na clarificacao**:
  - nenhuma lacuna adicional foi fechada em sessao separada; o intake 1.0 e a base factual; incertezas permanecem listadas abaixo como pendentes ou hipoteses
- **Hipoteses congeladas** (ate revisao de PRD ou decisao documentada):
  - o trio inicial de categorias (pista, pista premium, camarote) e suficiente para o primeiro evento real; expansao de catalogo segue politica a definir
  - Area equivalente a Diretoria no painel v1, conforme restricao operacional do intake
  - emissao com QR nasce com identidade persistida suficiente para um validador futuro de uso unico, sem comprometer o escopo fora do validador neste corte
- **Dependencias externas pendentes**:
  - estrategia final de armazenamento, expiracao e retencao para arquivos, links e ingressos emitidos com QR
  - SLA operacional de envio, retentativas, bounce e reenvio
  - formatos concretos e estabilidade das entregas das ticketeiras (impacta ingestao e conciliacao)
- **Riscos de interpretacao** (exigem decisao em desenho ou em manifestos de feature):
  - modelo canonico exato de conciliacao entre planejado, recebido_confirmado, bloqueado_por_recebimento, disponivel e distribuido
  - representacao de aumento e reducao sem misturar com remanejado nas leituras e relatorios
  - persistencia de artefatos externos e emissoes internas com QR com rastreabilidade e compliance plenos
  - contrato minimo da emissao com QR para validacao futura de uso unico
  - recortes, filtros, tabelas e graficos obrigatorios do dashboard de ativos no v1 para operar um evento real (incluindo drill-down do painel de problemas)

## 4. Plano Tecnico

> Descreve **como** viabilizar a especificacao. Se houver conflito com a secao 2, esta secao deve ser revista.

### 4.0 Baseline do produto (implementacao atual no repositorio)

Ponto de partida verificavel para evolucao e migracao; caminhos relativos ao root do monolito NPBB.

- **Frontend**
  - **`/ativos`**: `frontend/src/pages/AtivosList.tsx` — grid de cards por **evento + diretoria**, filtros (evento, diretoria, data), atribuicao de quantidade (`atribuirCota`), exclusao de cota quando permitido, exportacao CSV, link para o fluxo de ingressos; cliente HTTP em `frontend/src/services/ativos.ts`.
  - **`/ingressos`**: `frontend/src/pages/IngressosPortal.tsx` — listagem de cotas disponiveis para solicitacao, criacao de solicitacao e visao administrativa de solicitacoes; clientes em `frontend/src/services/ingressos.ts` e `frontend/src/services/ingressos_admin.ts` conforme uso na pagina.
- **Backend**
  - **`/ativos`** (`backend/app/routers/ativos.py`): `GET /ativos` e `GET /ativos/` (lista paginada, filtros, cabecalho `X-Total-Count`), `POST /ativos/{evento_id}/{diretoria_id}/atribuir`, `DELETE /ativos/{cota_id}`, `GET /ativos/export/csv`; filtro de visibilidade para usuario agencia por `agencia_id` do evento.
  - **`/ingressos`** (`backend/app/routers/ingressos.py`): `GET /ingressos/ativos`, `GET /ingressos/solicitacoes` (admin), `POST /ingressos/solicitacoes` (vincula a cota e a diretoria do perfil BB).
- **Modelo de dados (SQLModel)** em `backend/app/models/models.py`: entidade **CotaCortesia** com quantidade por par **evento_id + diretoria_id** (unicidade da combinacao); entidade **SolicitacaoIngresso** com status e tipo. Na listagem de ativos, **usados** agrega solicitacoes em status `SOLICITADO` por `cota_id` (subqueries em `ativos.py`).
- **Testes e contratos**: cobertura de rotas em `backend/tests/test_ativos_endpoints.py` e `backend/tests/test_ingressos_endpoints.py` (ajustar quando o dominio evoluir).
- **Documentacao de apoio no repo**: `docs/tela-inicial/menu/Ativos/ativos.md`, `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md`, `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`.

**Lacuna em relacao ao alvo deste PRD**: o baseline opera **cota agregada** sem categorias de ingresso (pista, premium, camarote), sem conciliacao **planejado versus recebido** de ticketeira, sem rastreio de artefatos por lote, sem emissao **unitaria** com QR, sem estados operacionais completos (bloqueio por recebimento, remanejamento formal, problemas) e **sem** `Dashboard > Ativos` analitico. Qualquer desenho de feature deve explicitar convivencia, migracao de dados e compatibilidade com estes endpoints e telas ate o corte de rollout.

### 4.1 Arquitetura Geral do Projeto

- **Backend**: ampliar o dominio atual para suportar configuracao de categorias por evento, dois modos canonicos de fornecimento, conciliacao planejado versus recebido, bloqueios por recebimento, emissao interna com identificador unico por destinatario (QR), distribuicao, remanejamento, aumento, reducao e incidentes operacionais; manter convivencia controlada com cotas e solicitacoes agregadas existentes durante a transicao
- **Frontend**: evoluir telas operacionais de ativos e ingressos; adicionar visao Dashboard maior Ativos com leituras separadas para planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido e problemas, alinhadas ao padrao do dashboard de leads
- **Banco/migracoes**: criar ou adaptar entidades para categorias por evento, previsao, recebimento, divergencia de conciliacao, artefatos de ingresso, emissao interna com identificador unico, distribuicao por destinatario, eventos de ajuste e ocorrencias
- **Observabilidade**: correlation_id e rastreabilidade entre previsao, recebimento, conciliacao, emissao, envio, bloqueio, remanejamento e problema operacional
- **Autorizacao/autenticacao**: manter RBAC atual e endurecer acesso a artefatos sensiveis e operacoes de distribuicao
- **Rollout**: ativacao gradual por evento, com convivencia controlada com o fluxo agregado atual ate validacao do corte operacional

### 4.2 Decisoes Tecnicas e Contratos Relevantes

- **Contratos de API / integracoes**: expor operacoes e payloads que permitam a automacao externa registrar recebimentos e artefatos oriundos de email de ticketeiras, alinhados a registry, ingestao inteligente e revisao humana onde aplicavel; documentar limites de idempotencia e autenticacao para integradores
- **Persistencia / migracoes**: priorizar modelo que suporte reconciliacao e auditoria; decisoes de storage de binarios e politicas de retencao seguem dependencia externa pendente na secao 3
- **Observabilidade e operacao**: trilhas correlacionadas para investigacao de divergencias e incidentes; metricas alinhadas as leading e lagging da especificacao funcional
- **Trade-offs tecnicos assumidos**: complexidade de dominio e migracao elevadas pela coexistencia com modelo agregado legado e pela heterogeneidade de ticketeiras; primeiro corte favorece operacao ponta a ponta em um evento real sobre automacao completa e validacao de QR na entrada

## 5. Riscos Globais

- **Risco de produto**: tentar fechar operacao, analitico e preparacao para automacao no mesmo ciclo e diluir a entrega do primeiro evento real
- **Risco tecnico**: formatos heterogeneos de ticketeiras e necessidade de coexistir com o modelo agregado atual aumentam a complexidade do dominio e das migracoes
- **Risco operacional**: classificacao errada, divergencia nao conciliada ou envio duplicado pode gerar distribuicao acima do recebido, categoria incorreta ou destinatario inadequado
- **Risco de dados**: arquivos, links e QR codes podem expor acessos indevidos se armazenamento, expiracao e auditoria nao forem definidos cedo
- **Risco de adocao**: a operacao pode manter planilhas paralelas se o produto nao reduzir trabalho manual de forma tangivel no primeiro evento real

## 6. Nao-Objetivos

- construir integracao nativa de inbox no NPBB
- desenvolver a skill OpenClaw dentro deste repositorio
- entregar o scanner ou validador final de QR no mesmo corte descrito como dentro do escopo inicial deste PRD
- usar este PRD como catalogo de features, lista de user stories ou planejamento de tasks

---

> **Pos-PRD:** backlog estruturado segue `GOV-FEATURE.md`, `GOV-USER-STORY.md`, `GOV-SCRUM.md` e sessoes de decomposicao.

## 7. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| Ticketeiras e formatos de entrega | Dados / processo | Externo | Conciliacao e recebido confirmado | pending |
| Armazenamento compartilhado (links, arquivos) | Armazenamento | Externo | Artefatos e rastreabilidade | pending |
| Provedor de email de saida | Servico | Externo | Distribuicao e notificacoes | active (existente) |
| Automacao OpenClaw (leitura de email) | Integracao | Externo ao repo | Carga de recebimentos via API | pending |
| Estrategia de storage, expiracao e retencao (LGPD) | Politica / infra | Interno | Artefatos sensiveis e QR | pending |

---

## 8. Rollout e Comunicacao

- **Estrategia de deploy**: liberacao gradual por evento; feature flags ou equivalente para nao interromper operacao legada ate corte validado; rollback preservando dados reconciliados quando possivel
- **Comunicacao de mudancas**: alinhamento com operacao e diretorias sobre novos estados de saldo, bloqueios por recebimento e leituras do dashboard; registro de dependencias com automacao externa
- **Treinamento necessario**: fluxo ponta a ponta no modulo de ativos e ingressos e interpretacao do dashboard de ativos
- **Suporte pos-launch**: canal para incidentes de conciliacao, bloqueios indevidos e problemas operacionais registrados

---

## 9. Revisoes e Auditorias

- **Gates e auditorias em nivel de projeto**: auditorias de feature apos decomposicao e execucao, conforme ciclo do projeto; revisao de PRD quando hipoteses congeladas forem desbloqueadas ou quando o corte operacional real alterar escopo
- **Criterios de auditoria**: ver `PROJETOS/COMUM/GOV-AUDITORIA.md`
- **Threshold anti-monolito**: ver `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

---

## 10. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
- [x] `Especificacao Funcional` e `Plano Tecnico` estao separados com precedencia explicita
- [x] `Hipoteses Congeladas` esta preenchido com lacunas resolvidas, hipoteses aceitas, dependencias pendentes e riscos de interpretacao
- [x] Arquitetura geral e rollout descritos **sem** catalogo de Features nem tabelas de User Stories neste PRD
- [x] Dependencias externas mapeadas
- [x] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

---

## 11. Anexos e Referencias

- [Intake ATIVOS-INGRESSOS](./INTAKE-ATIVOS-INGRESSOS.md)
- Documento operacional externo de referencia para metricas e graficos (ex.: acompanhamento operacional tipo Alceu): uso apenas informativo, nao como especificacao de layout
- Baseline implementado (monolito): `docs/tela-inicial/menu/Ativos/ativos.md`, `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md`, `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`
- `PROJETOS/COMUM/GOV-PRD.md`, `PROJETOS/COMUM/GOV-AUDITORIA.md`, `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

---

> **Frase Guia (pipeline):** PRD direciona; Feature organiza; User Story fatia; Task executa; Teste valida.
