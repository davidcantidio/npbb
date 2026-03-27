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

- TODO (T3): registar a estrategia de transicao aprovada para coexistencia entre legado e novo dominio.

## Gate por evento e criterio de activacao

- TODO (T3): documentar o mecanismo de activacao gradual por evento e o criterio verificavel para considerar um evento no novo fluxo.

## Impacto em rotas e clientes do baseline

- TODO (T3): mapear o impacto esperado nas rotas e clientes do baseline, preservando o comportamento legado para eventos nao migrados.

## Rollback e preservacao de dados reconciliados

- TODO (T3): alinhar rollback e preservacao de dados reconciliados ao `PRD-ATIVOS-INGRESSOS.md` sec. 8, sem prometer invariantes fora do PRD.

## Ponto de extensao para correlation_id

- TODO (T3): registar `correlation_id` (ou padrao equivalente) como ponto de extensao para fluxos futuros da FEATURE-2 em diante.

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
