---
doc_id: "TASK-1.md"
user_story_id: "US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/services/ativos_ingressos_saldo.py"
  - "backend/tests/test_ativos_ingressos_saldo.py"
tdd_aplicavel: true
---

# TASK-1 - Servico de dominio: prevalencia do recebido e teto distribuivel

## objetivo

Centralizar em um modulo de servico as regras de **prevalencia do recebido confirmado** sobre o planejado para origem ticketeira / modo externo, o calculo do **teto** do saldo distribuivel e o **delta** (planejado vs recebido) para leituras auditaveis, alinhado ao PRD 2.4 e aos criterios Given/When/Then da US-4-03.

## precondicoes

- [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) e [US-4-02](../US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md) concluidas no codigo: existem entidades ou fontes de dados consultaveis para `planejado` e `recebido_confirmado` por eixo evento/diretoria/categoria/modo externo (ou equivalente acordado no modelo). Se ainda nao existirem, parar com `BLOQUEADO`.
- Nenhuma ambiguidade sobre politica quando nao ha recebido: a US exige saldo distribuivel **nao superior a zero** salvo excecao ja documentada; implementar o caso zero por omissao.

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false` (base para T2/T3).
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `backend/app/services/ativos_ingressos_saldo.py` *(criar)*
- `backend/tests/test_ativos_ingressos_saldo.py` *(criar)*
- Modelos ou repositorios entregues por US-4-01/US-4-02 *(somente leitura para desenhar assinaturas)*
- [FEATURE-4.md](../../FEATURE-4.md) *(sec. 2, 7)*
- [README.md](./README.md) *(criterios de aceitacao)*

## testes_red

- testes_a_escrever_primeiro:
  - planejado maior que recebido: teto distribuivel igual ao recebido confirmado (nao ao planejado).
  - recebido maior que planejado: teto segue recebido confirmado (prevalencia do recebido; delta reflete divergencia).
  - ausencia total de recebido confirmado: teto distribuivel para fornecimento externo e zero (salvo excecao documentada na US/PRD).
  - funcao ou estrutura de saida expoe `planejado`, `recebido`, `delta` de forma deterministica para reuso pela API (T3).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_saldo.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao do servico; se passarem sem codigo novo, parar e revisar a task.

## passos_atomicos

1. Escrever os testes listados em `testes_red` contra funcoes puras ou facades finas que recebam `planejado` e `recebido` (e flags de modo externo/ticketeira se necessario).
2. Rodar o comando red e confirmar falha inicial.
3. Implementar em `ativos_ingressos_saldo.py` o calculo minimo do teto e do delta, sem acoplar HTTP.
4. Rodar o pytest alvo e confirmar green.
5. Refatorar nomes e limites de responsabilidade mantendo a suite green.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_saldo.py`
- `cd backend && ruff check app/services/ativos_ingressos_saldo.py`

## resultado_esperado

- Servico de dominio testado cobrindo os tres cenarios da US no nivel de regra numerica.
- Contrato de entrada/saida documentado no codigo (tipos ou dataclasses) consumivel por routers nas tasks seguintes.

## testes_ou_validacoes_obrigatorias

- `pytest` no ficheiro da suite acima em green.
- Revisao manual dos valores de delta face aos exemplos numericos da US.

## stop_conditions

- Parar com `BLOQUEADO` se US-4-01/US-4-02 nao tiverem fontes de verdade para recebido/planejado no repositorio.
- Parar se o PRD ou um ADR exigir formula de delta diferente da US sem atualizacao documental.
