---
doc_id: "TASK-4.md"
user_story_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingestao_externa.py"
  - "backend/app/services/ingestao_externa_orquestracao.py"
  - "backend/tests/test_ingestao_externa_fluxo_operacional.py"
tdd_aplicavel: true
---

# TASK-4 - Orquestracao com FEATURE-4: recebido confirmado vs revisao humana

## objetivo

Conectar o endpoint de ingestao externa aos casos de uso de recebimento ja
definidos em FEATURE-4 de forma que: (1) cargas sem pendencia de revisao
conduzam a estado observavel equivalente a `recebido_confirmado`; (2) cargas
que exijam revisao humana entrem na fila ou estado alinhado ao **workbench
existente** no produto, sem inbox nativo no NPBB.

## precondicoes

- [TASK-3](./TASK-3.md) concluida: idempotencia aplicada antes ou em torno da
  escrita de negocio *(ordem exata conforme desenho da US-7-01)*.
- [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md) e
  [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md) concluidas conforme
  README desta US.
- Identificar servicos/routers FEATURE-4 de registro de recebimento e fluxos de
  revisao *(ex.: `recebimento_confirmado_service.py`, superficies de
  conciliacao US-4-06, conforme codigo real)*.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: orquestrador + alteracoes pontuais no router + testes de
  fluxo; nao alterar `FEATURE-7.md` nem PRD nesta sessao documental.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md`
- `backend/app/services/recebimento_confirmado_service.py` *(ou equivalente
  entregue por FEATURE-4)*
- Modulos de revisao humana / fila ja existentes no repositorio *(grep/arvore
  apos estado do codigo)*
- `backend/app/routers/ingestao_externa.py`
- `backend/app/services/ingestao_externa_orquestracao.py` *(criar: fachada fina
  que chama FEATURE-4)*
- `backend/tests/test_ingestao_externa_fluxo_operacional.py` *(criar)*

## testes_red

- testes_a_escrever_primeiro:
  - cenario feliz sem revisao: POST valido resulta em persistencia coerente com
    FEATURE-4 e resposta indica sucesso / estado `recebido_confirmado` ou campo
    espelhando o dominio.
  - cenario revisao: quando regras de negocio exigirem revisao, resposta ou
    estado persistido reflete fila/workbench *(assert sobre registos ou status
    retornado, conforme API real)*.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_fluxo_operacional.py`
- criterio_red:
  - falha ate a orquestracao chamar os servicos corretos; se passar sem
    implementacao, investigar mocks.

## passos_atomicos

1. Escrever os testes em `testes_red` com fixtures alinhadas ao modelo de dados
   FEATURE-4.
2. Confirmar red.
3. Implementar `ingestao_externa_orquestracao`: mapear payload validado para
   chamadas aos servicos FEATURE-4; propagar identidade do integrador como ator
   de trilha quando o modelo o suportar.
4. Integrar no router apos camada de idempotencia (T3) e validacao (T2).
5. Green; refatorar extraindo helpers se necessario sem mudar semantica.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_fluxo_operacional.py`
- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(regressao alvo se rapida)*
- `cd backend && ruff check app/services/ingestao_externa_orquestracao.py app/routers/ingestao_externa.py`

## resultado_esperado

Fluxo operacional da US verificavel por testes automatizados: sucesso com
`recebido_confirmado` (ou equivalente) ou encaminhamento a revisao conforme
FEATURE-4/PRD.

## testes_ou_validacoes_obrigatorias

- `pytest` do modulo de fluxo operacional em green.
- Releitura dos criterios Given/When/Then do `README.md` da US com checklist
  mental contra os asserts dos testes.

## stop_conditions

- Parar se servicos FEATURE-4 ainda nao existirem no repositorio — documentar
  lacuna e bloquear ate US FEATURE-4 correspondente.
- Parar se nao houver workbench/fila implementada para revisao: nao inventar
  UI; limitar a estado persistido acordado com PM ou ADR.
- Parar se registry/ingestao inteligente exigir contratos nao descritos na
  US-7-03 — escalar a intake/PRD sem implementar escopo novo.
