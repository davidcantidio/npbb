---
doc_id: "ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md"
version: "1.0"
status: "proposed"
last_updated: "2026-03-27"
user_story_id: "US-2-01-ADR-E-COEXISTENCIA"
feature_key: "FEATURE-2"
---

# ADR - ATIVOS-INGRESSOS: coexistencia entre legado e novo dominio

Este ADR fixa o artefato canonico de convivencia para a FEATURE-2 e parte explicitamente do baseline descrito em `PRD-ATIVOS-INGRESSOS.md` sec. 4.0; o seu escopo e documentar a separacao entre legado e novo dominio ate ao corte de rollout gradual por evento.

## Contexto e Baseline

- Baseline de referencia: `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` sec. 4.0.
- O baseline atual do produto permanece a fonte factual inicial para a convivencia entre o fluxo agregado legado e a evolucao prevista para o novo dominio.
- Hoje o dominio de ativos e ingressos e agregado por evento e diretoria: a operacao trabalha com cotas e solicitacoes associadas a esse par, sem categorias de ingresso, sem conciliacao `planejado x recebido`, sem rastreio de artefatos por lote, sem emissao unitaria com QR e sem `Dashboard > Ativos` analitico como parte do comportamento corrente.
- Este ADR usa o PRD 4.0 como contrato de baseline e os anexos `ATIVOS_STATE_NOW.md` e `RESTORE_ATIVOS_SUMMARY.md` como evidencia observavel do estado atual, sem transformar o PRD em backlog e sem congelar detalhes de implementacao fora do que permanece relevante para a convivencia.

## Convivencia ate ao Rollout

- Este documento descreve a convivencia entre o modelo agregado atual e o novo dominio apenas ate ao rollout acordado no projeto.
- Eventos nao migrados devem continuar interpretados pelo comportamento legado ate existir criterio explicito de activacao por evento.
- Ate ao corte de rollout, o limite de convivencia e simples: o legado continua sendo a referencia operacional para eventos nao migrados, enquanto o novo dominio permanece alvo de evolucao descrito no PRD 4.1 e na FEATURE-2.
- Capacidades do novo dominio nao devem ser tratadas como baseline ja activo enquanto nao estiverem implementadas e activadas por evento; por isso, este ADR separa claramente o que continua obrigatorio no agregado actual do que ainda pertence ao alvo futuro.

## Modelo agregado legado

- `CotaCortesia` permanece como o registo agregado de stock por par `evento_id + diretoria_id`, com unicidade desse par e quantidade controlada nesse nivel, sem desdobramento em categorias de ingresso no baseline.
- A rota `/ativos` continua a representar esse modelo agregado: lista cotas com filtros, permite atribuir quantidade ao par evento-diretoria, excluir a cota quando permitido e exportar CSV, preservando o comportamento observavel descrito no PRD 4.0.
- `SolicitacaoIngresso` permanece como o artefato de pedido vinculado a uma `CotaCortesia`, distinguindo pedido para o proprio solicitante (`SELF`) ou para terceiro (`TERCEIRO`) e mantendo os estados `SOLICITADO` e `CANCELADO` do fluxo legado.
- A rota `/ingressos` continua a operar sobre a mesma base agregada: lista ativos disponiveis para solicitacao, cria solicitacoes vinculadas a uma cota existente e expõe a listagem administrativa de solicitacoes, sem introduzir inventario unitario ou contratos novos de categoria.
- No comportamento actual, o consumo de uma cota continua a ser lido de forma agregada: o total de "usados" deriva das solicitacoes em estado `SOLICITADO`, preservando a logica operacional por evento e diretoria para eventos nao migrados.

## Novo dominio em transicao

- O novo dominio em transicao introduz, como alvo e nao como baseline actual, configuracao de categorias por evento e modos canonicos de fornecimento para superar a limitacao do modelo agregado unico.
- Tambem passa a prever conciliacao entre `planejado` e `recebido_confirmado`, com leitura operacional capaz de distinguir disponibilidade real, bloqueios por recebimento e divergencias que hoje nao existem no fluxo legado.
- Para ingressos internos, o alvo futuro inclui emissao unitaria por destinatario com QR unico e identidade suficiente para validacao posterior, substituindo a ausencia de inventario unitario do baseline actual.
- O mesmo dominio futuro prepara leitura operacional mais rica para dashboard, remanejamentos, aumentos, reducoes, problemas e trilhas correlacionadas entre operacoes, incluindo `correlation_id` ou padrao equivalente como ponto de extensao.
- Ate esse conjunto estar implementado e activado por evento, todas essas capacidades devem ser tratadas como fora do comportamento actual do baseline e nao como expectativa valida para eventos nao migrados.

## Ate ao corte de rollout

- O corte de rollout significa o momento em que um evento especifico deixa de depender exclusivamente do fluxo agregado legado e pode operar sob o novo dominio sem quebrar a operacao acordada no PRD.
- Enquanto esse corte nao existir para um evento, continua obrigatorio que o legado suporte cadastro agregado de cotas, atribuicao de quantidade, leitura de disponibilidade, criacao de solicitacoes e exportacao nos contratos ja existentes de `/ativos` e `/ingressos`.
- Em termos operacionais, eventos nao migrados continuam a ter como fonte de verdade a combinacao "cota agregada por evento e diretoria + solicitacoes vinculadas", e nao categorias, conciliacao detalhada, emissao unitaria ou leituras analiticas do novo dominio.
- Esta task fixa apenas o limite de convivencia ate ao rollout; criterio de activacao por evento, tactica de transicao e rollback detalhado permanecem decididos nas secoes de T3.

## Estrategia de Transicao

- A transicao e controlada por **evento**, nao por troca global de rotas ou de modelo de dados para todos os eventos ao mesmo tempo.
- O estado padrao continua a ser "evento no legado" ate existir um mecanismo explicito de activacao por evento, como feature flag ou equivalente documental/operacional alinhado ao PRD sec. 8.
- Quando um evento entra no novo fluxo, o novo dominio passa a ser a referencia para capacidades que o baseline nao possui, como categorias, conciliacao e emissao unitaria; ainda assim, a superficie legada de `/ativos` e `/ingressos` deve continuar funcional como contrato de compatibilidade durante a transicao.
- **Dual-read** e tratado apenas como tatica **condicional** de transicao, nunca como invariante do dominio: pode ser activado para comparar leituras entre legado e novo dominio em eventos ja colocados no novo fluxo, quando isso for necessario para validar paridade operacional ou concluir backfill/reconciliacao.
- A desactivacao do dual-read e elegivel quando o evento ja opera com gate activo, a leitura canonica no novo dominio foi validada para o caso operacional daquele evento, e nao resta dependencia do agregado legado para interpretar saldo ou distribuicao desse evento.
- Este ADR nao fixa **dual-write** como obrigatorio e nao desenha implementacao; a decisao aqui limita-se a explicitar que a convivencia e gradual, por evento, e pode recorrer a leituras paralelas apenas enquanto isso reduzir risco de corte.

## Gate por evento e criterio de activacao

- "Evento apenas legado" significa que o evento continua a ser operado integralmente pelo baseline do PRD sec. 4.0: `CotaCortesia`, `SolicitacaoIngresso`, rotas actuais e leitura agregada por `evento + diretoria`.
- "Evento no novo fluxo" significa que existe uma activacao explicita por evento para permitir que capacidades do novo dominio sejam usadas sem alterar o comportamento dos eventos nao migrados.
- O criterio minimo de activacao e verificavel em tres pontos:
  - existe gate por evento activo, por flag ou mecanismo equivalente, para aquele evento especifico
  - o corte operacional desse evento foi validado no escopo descrito pelo PRD sec. 4.1 e 8, sem exigir activacao global do projeto
  - o evento ja tem as estruturas minimas do novo fluxo necessarias para operar sem reclassificar eventos nao migrados como se ja estivessem no novo dominio
- Se qualquer um desses pontos falhar, o evento permanece no legado por definicao arquitetural, mesmo que existam partes do novo dominio ja implementadas no codigo.

| Estado do evento | Criterio de activacao | Impacto em rotas legadas | Comportamento se rollback |
| --- | --- | --- | --- |
| Evento apenas legado | Gate por evento ausente ou desligado | `/ativos` e `/ingressos` preservam integralmente o comportamento baseline | Nao aplicavel; o evento ja esta no legado |
| Evento no novo fluxo sem dual-read | Gate por evento activo e corte validado para esse evento | Rotas legadas permanecem como superficie de compatibilidade; eventos nao migrados nao sofrem alteracao | Desligar o gate do evento e retomar interpretacao operacional pelo legado, preservando dados reconciliados quando possivel |
| Evento no novo fluxo com dual-read condicional | Gate activo mais necessidade temporaria de comparar leituras entre legado e novo dominio | Contratos externos de `/ativos` e `/ingressos` nao mudam por causa do dual-read; a diferenca fica interna a decisao de leitura | Desligar dual-read e/ou o gate do evento de forma controlada; nao descartar dados reconciliados sem decisao posterior documentada |

## Impacto em rotas e clientes do baseline

- As rotas **`/ativos`** e **`/ingressos`** continuam sendo contratos existentes do baseline durante a transicao; esta task nao autoriza quebrar payloads, semantica ou disponibilidade para eventos nao migrados.
- Para eventos nao migrados, o impacto esperado e **nenhum**: `frontend/src/pages/AtivosList.tsx`, `frontend/src/pages/IngressosPortal.tsx` e os routers/backend do baseline continuam a operar sobre o modelo agregado actual.
- Para eventos migrados, o impacto permitido e interno a decisao de roteamento/leitura: a implementacao pode passar a usar o novo dominio por tras do gate daquele evento ou expor extensoes futuras documentadas noutras user stories, mas sem assumir nesta task novos endpoints, novos contratos publicos ou uma troca global de UX.
- Em particular, este ADR fixa que "evento nao migrado" continua a significar comportamento legado preservado, mesmo que outros eventos do mesmo sistema ja estejam no novo fluxo.
- Clientes e automacoes que hoje dependem de `/ativos` e `/ingressos` devem continuar a receber comportamento compatível para o baseline enquanto o evento correspondente nao tiver gate activo e corte validado.

## Rollback e preservacao de dados reconciliados

- O rollback e orientado por **evento**: se um evento activado no novo fluxo precisar regressar ao comportamento legado, a primeira acao e retirar ou desactivar o gate daquele evento, e nao reverter o projeto inteiro.
- Em linha com o PRD sec. 8, o rollback deve **preservar dados reconciliados quando possivel**. Isso significa que reconciliacoes, artefatos e trilhas ja produzidos no novo dominio nao devem ser descartados automaticamente apenas para voltar a operar o evento pelo legado.
- Este ADR nao promete reversao perfeita de todas as escritas nem sincronizacao retroactiva completa entre modelos. Qualquer garantia mais forte do que "preservar quando possivel" exigira decisao posterior em features de implementacao e migracao.
- Quando dual-read estiver activo, ele pode ser mantido por janela curta e controlada para apoiar diagnostico e retorno ao legado; quando nao estiver, o rollback continua possivel via desactivacao do gate por evento.

## Ponto de extensao para correlation_id

- `correlation_id` (ou padrao equivalente) fica registado como **ponto de extensao** entre previsao, recebimento, conciliacao, emissao, distribuicao, bloqueios e ocorrencias que as features seguintes vao materializar.
- A exigencia deste ADR e apenas semantica: eventos que entrarem no novo fluxo devem poder propagar um identificador correlacionavel entre operacoes e logs, sem mudar por isso os contratos publicos desta task.
- Para eventos que permanecerem no legado, a ausencia desse identificador nao altera o comportamento baseline; quando existir, ele deve ser tratado como metadado aditivo de rastreabilidade, nao como precondicao para manter `/ativos` e `/ingressos` funcionais.

## Rastreabilidade e Referencias

- Referencia primaria de baseline: `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` sec. 4.0.
- Referencia de rollout: `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` sec. 8.
- TODO (T4): consolidar a rastreabilidade final entre PRD, FEATURE-2, anexos de auditoria e seccoes deste ADR.

## Leituras obrigatorias

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/FEATURE-2.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md`
- `backend/docs/auditoria_eventos/ATIVOS_STATE_NOW.md`
- `docs/auditoria_eventos/RESTORE_ATIVOS_SUMMARY.md`

## Checklist de aceite (US-2-01)

- TODO (T4): mapear o primeiro Given/When/Then a seccoes concretas do ADR.
- TODO (T4): mapear o segundo Given/When/Then a referencias cruzadas e rastreabilidade do ADR.
- TODO (T4): mapear o terceiro Given/When/Then a transicao, activacao por evento e impacto em rotas.
