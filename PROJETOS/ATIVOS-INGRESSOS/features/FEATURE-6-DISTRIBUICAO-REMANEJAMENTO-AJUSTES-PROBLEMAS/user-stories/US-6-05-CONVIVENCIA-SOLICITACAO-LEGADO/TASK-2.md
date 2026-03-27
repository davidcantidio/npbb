---
doc_id: "TASK-2.md"
user_story_id: "US-6-05-CONVIVENCIA-SOLICITACAO-LEGADO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md"
tdd_aplicavel: false
---

# TASK-2 - Matriz novo vs legado, limites de dados e mapeamento de estados

## objetivo

Completar o corpo do ADR criado em T1: matriz de **operacoes** que usam fluxo novo
(FEATURE-6) versus fluxo legado (cotas agregadas + `SolicitacaoIngresso`);
explicitar **quais dados nao se misturam** sem migracao; documentar mapeamento de
estados `SolicitacaoIngresso` e invariantes face a distribuicao, remanejamento,
ajuste de previsao e problema operacional, alinhado ao primeiro criterio
Given/When/Then da US-6-05 e ao PRD 2.6 / 4.0.

## precondicoes

- T1 concluida: ficheiro ADR e esqueleto existem.
- Implementacao das US-6-01 a US-6-04 **disponivel no repositorio** (merged) para
  que os nomes de estados, endpoints e entidades novos citados no ADR correspondam
  ao codigo real — conforme texto da US («Execucao apos US-6-01 a US-6-04 para
  validar o conjunto contra o legado»). Se ainda nao houver implementacao,
  limitar o ADR ao baseline PRD 4.0 e marcar lacunas explicitas; nao inventar
  contratos.
- PRD sec. 2.6 e 4.0 relidos para nao contradizer guardrails nem baseline.

## orquestracao

- `depends_on`: `["T1"]`.
- `parallel_safe`: `false`.
- `write_scope`: mesmo ficheiro ADR que T1.

## arquivos_a_ler_ou_tocar

- `docs/adr/ATIVOS-INGRESSOS-feature6-convivencia-solicitacao-ingresso.md`
- `docs/adr/ATIVOS-INGRESSOS-coexistencia-legado-e-novo-dominio.md` *(se existir)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (2.6, 4.0, 4.1)
- `backend/app/models/models.py` — `SolicitacaoIngresso`, `SolicitacaoIngressoStatus`,
  `SolicitacaoIngressoTipo`, `CotaCortesia`
- `backend/app/routers/ingressos.py` — rotas legadas de solicitacao
- `backend/app/routers/ativos.py` — agregacao `usados` / cotas *(baseline PRD 4.0)*
- Rotas e modelos introduzidos por US-6-01..04 *(localizar apos implementacao)*
- `backend/tests/test_ingressos_endpoints.py`
- `backend/tests/test_ativos_endpoints.py`

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Preencher a seccao **matriz operacao nova vs legado** com uma tabela ou lista
   verificavel (ex.: colunas: operacao, superficie API/UI, modo legado, modo novo,
   notas de rollout por evento se aplicavel).
2. Documentar **limites de dados**: o que permanece em modelo agregado legado,
   o que exige novas entidades ou flags, e o que e proibido misturar ate migracao
   documentada (alinhado a PRD 4.0 lacunas e 2.6).
3. Documentar **mapeamento de estados** `SolicitacaoIngresso` (e cotas) face aos
   estados/ eventos de FEATURE-6, incluindo leituras separadas remanejado vs
   aumento/reducao quando o codigo existir (PRD 2.6).
4. Incluir **ponteiros concretos** para ficheiros e simbolos no repositorio
   (caminhos relativos ao root), para auditoria e para T3/T4 escreverem testes.
5. Registar **invariantes** que a suite de testes deve proteger (sem duplicar o
   texto inteiro dos testes — lista verificavel para T3).
6. Revisar consistencia com ADR de coexistencia geral (US-2-01), se existir;
   adicionar secao "Relacao com..." se necessario.

## comandos_permitidos

- `rg`, `grep`, leitura de ficheiros *(apenas documentacao; nao alterar codigo de
  aplicacao nesta task)*

## resultado_esperado

O ADR contem matriz novo/legado, limites de mistura de dados, mapeamento de
estados e invariantes testaveis, com referencias a ficheiros reais do repo.

## testes_ou_validacoes_obrigatorias

- Um revisor consegue, apenas com o ADR, saber qual fluxo usar para cada operacao
  e quais invariantes nao podem ser violados.
- Todas as afirmacoes sobre codigo legado batem com `models.py` / `ingressos.py`
  / testes citados.

## stop_conditions

- Parar se o codigo de US-6-01..04 nao existir e o produto exigir precisao nominal
  de endpoints novos: completar apenas parte legado + lacunas `TBD` e escalar para
  alinhar ordem de execucao com o PM.
