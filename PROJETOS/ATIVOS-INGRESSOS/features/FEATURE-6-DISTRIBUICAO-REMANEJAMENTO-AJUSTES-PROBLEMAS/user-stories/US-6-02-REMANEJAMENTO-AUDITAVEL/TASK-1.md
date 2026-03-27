---
doc_id: "TASK-1.md"
user_story_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/"
tdd_aplicavel: false
---

# T1 - Modelo persistido e migracao para historico de remanejamento

## objetivo

Introduzir revisao Alembic e modelos SQLModel (ou equivalente do repo) para **historico de remanejamento** auditavel: origem, destino, quantidade, instante, ator; campo **motivo** persistido quando o PRD exigir captura (PRD sec. 2.6 e dados de entrada — motivo de remanejamento). A estrutura deve permitir consultas por evento e, quando aplicavel, por lote/linha operacional sem antecipar a logica de negocio das tasks seguintes.

## precondicoes

- **US-6-01** `done` no branch (ou mergeada): existem entidades de **distribuicao / alocacao** acordadas para referenciar como origem e destino do remanejamento; **parar** se ainda nao houver tabelas ou PKs estaveis para FK — nao inventar nomes fora do que US-6-01 entregou.
- `cd backend && alembic heads` executado; um unico head ou merges resolvidos antes de criar nova revisao.
- Leitura do manifesto FEATURE-6 e da US-6-02 para nao alargar escopo a **aumentado** / **reduzido** (US-6-03).

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false (fila de revisoes Alembic e modelos acoplados).
- `write_scope`: novos ficheiros sob `backend/alembic/versions/` e alteracoes pontuais em `backend/app/models/` (ou modulo de modelos alinhado ao padrao do repo).

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/FEATURE-6.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-02-REMANEJAMENTO-AUDITAVEL/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md` *(e artefatos de modelo entregues)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 2.3, 2.6)*
- `backend/alembic/env.py` *(apenas se convencao exigir)*
- `backend/app/models/models.py` e/ou modulos de dominio de ativos/ingressos existentes

## passos_atomicos

1. Confirmar `alembic heads` e definir `down_revision` para o head atual.
2. Desenhar tabela (ou par cabecalho/linha) de **evento de remanejamento** com: referencias a origem e destino (areas/categorias/destinatarios conforme modelo US-6-01), `quantidade`, `created_at` ou instante equivalente, `actor_user_id` ou FK para ator, `motivo` texto nullable ou com constraint alinhada a **politica configurada** (a validacao obrigatoria fica na T2).
3. Declarar FKs apenas para entidades que ja existam no branch; indices para listagem por `evento_id` e ordenacao temporal.
4. Implementar `upgrade()` / `downgrade()` simetricos.
5. Registar modelos SQLModel espelhando a revisao, seguindo convencao de imports do projeto.
6. Rodar `alembic upgrade head` e `alembic downgrade -1` em ambiente de desenvolvimento com `DATABASE_URL` valido.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Schema reversivel e modelos importaveis que materializam a trilha minima de remanejamento alinhada ao primeiro criterio Given/When/Then da US (origem, destino, quantidade, instante, ator; motivo persistivel).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` e `alembic downgrade -1` sem erro.
- Verificacao manual ou query de existencia dos indices e FKs declarados.

## stop_conditions

- Parar se US-6-01 nao tiver entregue alvos de FK para origem/destino.
- Parar se `alembic heads` reportar multiplos heads nao resolvidos.
- Parar se for necessario criar tabelas de **aumentado/reduzido** nesta task — pertence a US-6-03.
