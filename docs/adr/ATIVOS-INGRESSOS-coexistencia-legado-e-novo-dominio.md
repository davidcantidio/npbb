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
- TODO (T2): detalhar o que permanece no baseline em termos de entidades, rotas e comportamento observavel.

## Convivencia ate ao Rollout

- Este documento descreve a convivencia entre o modelo agregado atual e o novo dominio apenas ate ao rollout acordado no projeto.
- Eventos nao migrados devem continuar interpretados pelo comportamento legado ate existir criterio explicito de activacao por evento.
- TODO (T2): explicitar os limites entre legado e novo dominio sem transformar o ADR em backlog do PRD.

## Modelo agregado legado

- TODO (T2): documentar `CotaCortesia`, `SolicitacaoIngresso`, rotas `/ativos` e `/ingressos`, e o comportamento legado que continua valido para eventos nao migrados.

## Novo dominio em transicao

- TODO (T2): documentar as capacidades alvo do novo dominio em transicao, alinhadas ao PRD sec. 4.1 e ao manifesto da FEATURE-2.

## Ate ao corte de rollout

- TODO (T2): definir o significado operacional do corte de rollout e o que continua obrigatoriamente funcional no legado para eventos nao migrados.

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
