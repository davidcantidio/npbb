---
doc_id: "TASK-2.md"
user_story_id: "US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/ingressos.py"
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: false
---

# TASK-2 - Integrar teto distribuivel nos fluxos de listagem e solicitacao

## objetivo

Garantir que o calculo de ingressos **disponiveis** e a validacao ao **criar solicitacao** (ou fluxo equivalente de distribuicao externa) usem o **teto** derivado do servico de T1, de modo que nunca se permita distribuir acima do recebido confirmado quando a origem for ticketeira/modo externo, conforme primeiro e terceiro criterios Given/When/Then da US.

## precondicoes

- T1 `done`: `backend/app/services/ativos_ingressos_saldo.py` implementado e testes unitarios green.
- Dados de `recebido_confirmado` e `planejado` acessiveis na camada de persistencia ou via queries alinhadas ao modelo US-4-01/4-02.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false` (sobreposta evolucao do router de ingressos com T3 se esta tambem tocar o mesmo ficheiro; executar T2 antes de T3 se ambas alterarem `ingressos.py`).
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `backend/app/services/ativos_ingressos_saldo.py`
- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py`
- `backend/tests/test_ingressos_endpoints.py`
- `backend/app/models/models.py` *(ou modulos de cotas/recebimento entregues pela FEATURE-4)*

## passos_atomicos

1. Localizar os pontos que calculam `disponiveis` na listagem de ativos para ingressos e o check pre-POST em `criar_solicitacao`.
2. Para cotas/lotes em modo externo/ticketeira, obter planejado e recebido do banco e invocar o servico de T1 para obter o teto efetivo.
3. Substituir ou compor `cota.quantidade` com o teto quando aplicavel; manter comportamento de legado para modos nao cobertos por esta US (convivencia FEATURE-2/3).
4. Garantir mensagem ou codigo HTTP 409 coerente quando nao houver saldo distribuivel por teto zero.
5. Atualizar ou adicionar testes em `test_ingressos_endpoints.py` para pelo menos um cenario de teto abaixo do planejado.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingressos_endpoints.py`
- `cd backend && ruff check app/routers/ingressos.py app/schemas/ingressos.py`

## resultado_esperado

- Listagem e criacao de solicitacao respeitam o recebido confirmado como teto para origem externa.
- Testes de router atualizados ou novos casos cobrindo regressao do fluxo feliz e conflito por teto.

## testes_ou_validacoes_obrigatorias

- Pytest do modulo `test_ingressos_endpoints.py` relevante em green.
- Verificacao manual opcional: resposta JSON de listagem reflete disponiveis limitados pelo recebido.

## stop_conditions

- Parar com `BLOQUEADO` se T1 nao estiver concluida ou se o modelo de dados nao permitir distinguir modo externo/ticketeira no mesmo endpoint sem decisao de produto.
- Parar se a alteracao exigir mudanca de contrato publico sem versionamento acordado.
