---
doc_id: "TASK-1.md"
user_story_id: "US-4-04-BLOQUEIO-POR-RECEBIMENTO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/models.py"
  - "backend/app/models/event_support_models.py"
tdd_aplicavel: false
---

# TASK-1 - Contrato persistido para bloqueio por recebimento

## objetivo

Garantir que o dominio possa persistir o estado ou motivo `bloqueado_por_recebimento` (ou equivalente alinhado ao PRD 2.3 / FEATURE-4) na entidade correta do pipeline de **aumentos dependentes de ticketeira**, reutilizando ao maximo o modelo entregue pela [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) e sem duplicar tabelas de recebimento ou conciliacao.

## precondicoes

- [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) concluida (`done`): estruturas de recebimento/conciliacao e vinculos a evento, categoria e modo externo disponiveis no codigo e migracoes aplicaveis.
- PRD e [FEATURE-4.md](../../FEATURE-4.md) lidos para nomenclatura de estados (`bloqueado_por_recebimento` vs codigo interno).

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false` (modelo base para T2–T4).
- `write_scope`: conforme frontmatter; ajustar caminhos exatos se a US-4-01 introduzir modulo dedicado (substituir `models.py` / `event_support_models.py` pelo modulo real).

## arquivos_a_ler_ou_tocar

- `backend/alembic/versions/` *(nova revisao se faltar coluna/enum/tabela de bloqueio)*
- `backend/app/models/models.py` *(enums `SolicitacaoIngressoTipo` / `SolicitacaoIngressoStatus` ou equivalentes de ajuste)*
- `backend/app/models/event_support_models.py` *(se o aumento for modelado em `SolicitacaoIngresso` ou entidade adjacente)*
- Artefatos de modelo entregues pela US-4-01 *(tabelas de bloqueio ou ligacao a recebimento)*
- [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md), [FEATURE-4.md](../../FEATURE-4.md)

## passos_atomicos

1. Mapear onde o produto persistira o bloqueio (coluna em linha de ajuste, linha em tabela de bloqueios, ou campo em entidade da US-4-01) com base no desenho ja mergeado da US-4-01.
2. Se faltar representacao, adicionar migracao Alembic minima (enum/campos/tabela) com nome e semantica alinhados ao PRD; evitar escopo de conciliacao completa (pertence a US-4-01/4-02).
3. Atualizar modelos SQLModel/Pydantic para refletir o contrato persistido e valores canonicos do motivo `bloqueado_por_recebimento`.
4. Documentar em comentario curto no modelo ou no docstring do pacote o mapeamento PRD estado → persistencia, para consumo por T2/T3.

## comandos_permitidos

- `cd backend && alembic upgrade head` *(apos revisao de migracao)*
- `cd backend && ruff check app/models/`

## resultado_esperado

- Existe representacao persistivel e versionada do bloqueio por recebimento associada ao fluxo de aumento dependente de ticketeira, coerente com US-4-01.
- Nenhuma regra de negocio de avaliacao ou desbloqueio implementada nesta task (fica para T2/T3).

## testes_ou_validacoes_obrigatorias

- Migracao aplica e reverte (upgrade/downgrade) em ambiente de desenvolvimento sem erro.
- Modelo carrega no metadata da aplicacao sem quebra de import circular.

## stop_conditions

- Parar e reportar `BLOQUEADO` se US-4-01 nao tiver entregue ponto de extensao claro para “linha de ajuste” ou bloqueio — exigir alinhamento de modelo antes de inventar entidade paralela.
- Parar se o PRD exigir nome de estado diferente do acordado na FEATURE-4 sem decisao registada.
