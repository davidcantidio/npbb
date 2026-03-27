---
doc_id: "TASK-3.md"
user_story_id: "US-4-04-BLOQUEIO-POR-RECEBIMENTO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/services/ativos_recebimento_bloqueio.py"
  - "backend/app/services/"
tdd_aplicavel: false
---

# TASK-3 - Desbloqueio auditavel quando a conciliacao reconhece cobertura

## objetivo

Quando o recebimento correspondente existir e a **conciliacao** reconhecer cobertura (pos [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md)), levantar o bloqueio `bloqueado_por_recebimento` de forma **auditavel**, permitindo que o aumento prossiga conforme regras de saldo e teto ([US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md)).

## precondicoes

- TASK-2 `done`: bloqueio aplicado no pipeline com motivo persistido.
- Fluxo de registro/conciliacao da US-4-02 expõe hook, evento de dominio ou ponto de servico onde, apos persistencia de recebido e atualizacao de conciliacao, e seguro reavaliar pedidos bloqueados.
- Trilha auditavel da US-4-01 (ator, instante, natureza) utilizavel para registrar levantamento de bloqueio.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: incluir `backend/app/services/` apenas para o modulo concreto da US-4-02 que dispara reavaliacao *(substituir pelo path exato apos leitura do codigo)*.

## arquivos_a_ler_ou_tocar

- `backend/app/services/ativos_recebimento_bloqueio.py` *(funcoes de reavaliacao / clear bloqueio)*
- Modulo(s) de servico de recebimento/conciliacao entregues pela US-4-02 *(registro pos-commit ou use case equivalente)*
- Tabelas/campos de auditoria da US-4-01
- [FEATURE-4.md](../../FEATURE-4.md) sec. 2 e criterios de aceite item 3–4

## passos_atomicos

1. Identificar o ponto unico pos-conciliacao onde “cobertura reconhecida” e determinista (evitar N chamadas duplicadas sem idempotencia).
2. Implementar `reavaliar_bloqueios_por_recebimento` (ou nome alinhado ao projeto) que: lista candidatos bloqueados por este motivo no escopo evento/categoria/modo afetado; aplica a mesma regra de cobertura usada em T2; remove ou altera estado de bloqueio quando coberto.
3. Registrar trilha auditavel do desbloqueio (quem/quando/o que — conforme modelo US-4-01; se apenas sistema, usar actor sistema explicito).
4. Opcional nesta task: emitir evento de negocio correlacionavel com FEATURE-2 *(mesmo nome/correlation_id que o restante do dominio de ativos)* — apenas se o padrao de telemetria ja existir; caso contrario deixar nota em T4 para extensao sem bloquear a US.
5. Garantir que, apos desbloqueio, a continuacao do fluxo respeita US-4-03 (nao distribuir alem do recebido confirmado).

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/ -q -k recebimento_or_bloqueio` *(ajustar quando suite existir)*
- `cd backend && ruff check app/services/`

## resultado_esperado

- Cenario Given/When/Then 2 da US satisfeito: apos recebimento e conciliacao com cobertura, bloqueio levantado com registro auditavel e aumento pode seguir regras de saldo.

## testes_ou_validacoes_obrigatorias

- Teste ou roteiro manual: pedido bloqueado → registro recebido que cobre → apos conciliacao, estado deixa de ser bloqueado por recebimento e saldo reflete US-4-03.

## stop_conditions

- Parar e reportar `BLOQUEADO` se US-4-02 nao publicar um ponto de extensao claro (risco de race ou duplo desbloqueio) — definir transacao ou outbox com time antes de integrar.
- Parar se T2 nao estiver `done`.
