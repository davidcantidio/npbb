---
doc_id: "TASK-4.md"
user_story_id: "US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_leituras_canonicas.py"
tdd_aplicavel: true
---

# TASK-4 - Testes e consistencia com US-4-03 e US-4-04

## objetivo

Adicionar **testes automatizados** que provem separacao de **remanejado** versus **aumento/reducao** na resposta da API (e, se util, no servico), e produzir **checklist documental** que amarre o ADR e as consultas de saldo/bloqueio as narrativas da [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) e [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md), sem contradicao silenciosa (criterio 3 da US).

## precondicoes

- [TASK-3.md](./TASK-3.md) concluida (`done`): rota e schemas disponiveis.
- ADR da TASK-1 e READMEs US-4-03/US-4-04 disponiveis para comparacao textual.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; incluir `tests/test_ativos_endpoints.py` apenas se testes forem colocados la em vez de ficheiro novo (atualizar entao este frontmatter na revisao).

## arquivos_a_ler_ou_tocar

- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md`
- `backend/tests/test_ativos_leituras_canonicas.py` *(criar)*
- `backend/tests/test_ativos_endpoints.py` *(padrao de cliente/fixtures)*
- [US-4-03/README.md](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md)
- [US-4-04/README.md](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md)

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API: fixture com evento que tenha movimento de remanejamento e movimento de aumento/reducao no mesmo recorte; resposta GET das leituras canonicas expoe **valores em campos distintos** e remanejado **nao** aparece apenas dentro do campo de aumento ou reducao (conforme ADR).
  - Teste de regressao minimo: resposta continua a respeitar autenticacao e visibilidade por agencia (403/404/401 conforme padrao existente).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_leituras_canonicas.py -q`
- criterio_red:
  - Os testes acima devem **falhar** antes da implementacao de dados/fixtures ou do endpoint; se ja passarem no primeiro run, parar e rever escopo do teste (devem assertar comportamento ainda nao garantido).

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Ajustar fixtures/seeds de teste e asserts ate refletirem o contrato TASK-3 e o ADR; completar implementacao minima apenas se algum gap restar (preferir que TASK-3 ja tenha entregue endpoint).
4. Rodar os testes e confirmar sucesso (green).
5. Refatorar fixtures compartilhadas se necessario mantendo a suite green.
6. Preencher checklist em comentario no topo do ficheiro de teste ou em secao `## Checklist consistencia` no proprio `TASK-4.md` apos execucao:
   - item ADR: cada leitura exposta pela API tem linha no ADR;
   - item US-4-03: totais de saldo/disponivel nao reinterpretam remanejado como ajuste de previsao;
   - item US-4-04: indicadores de bloqueio por recebimento nao somam remanejado como se fosse aumento dependente.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_leituras_canonicas.py -q`
- `cd backend && ruff check tests/test_ativos_leituras_canonicas.py`

## resultado_esperado

- Suite pytest verde para o novo modulo de testes.
- Checklist de consistencia preenchida (sim/nao/N/A com nota) referenciando ADR + US-4-03 + US-4-04.

## testes_ou_validacoes_obrigatorias

- `pytest tests/test_ativos_leituras_canonicas.py -q` sem falhas.
- Revisao manual: nenhuma contradicao evidente entre texto do ADR e asserts dos testes.

## stop_conditions

- Parar e reportar `BLOQUEADO` se nao for possivel construir dados de teste sem US-4-01/4-02 entregues — documentar dependencia e reduzir testes a contrato esquematico (smoke) apenas com aprovacao do gate.
- Parar se US-4-03/US-4-04 ainda nao tiverem implementacao no codigo: limitar checklist a **risco documentado** e testes de contrato JSON estatico ate as USs estarem disponiveis.
