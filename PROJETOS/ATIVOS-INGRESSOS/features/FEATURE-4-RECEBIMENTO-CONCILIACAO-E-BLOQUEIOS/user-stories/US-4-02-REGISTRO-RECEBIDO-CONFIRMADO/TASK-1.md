---
doc_id: "TASK-1.md"
user_story_id: "US-4-02-REGISTRO-RECEBIDO-CONFIRMADO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/services/recebimento_confirmado_service.py"
tdd_aplicavel: false
---

# TASK-1 - Servico de dominio: lote recebido confirmado, artefatos e trilha

## objetivo

Implementar o caso de uso que persiste `recebido_confirmado` por lote (ou
registro equivalente) com vinculo a evento, diretoria, categoria e modo
externo; aceitar metadados de artefato (ficheiro, link ou nota textual) no
formato previsto pelo modelo da US-4-01; e gravar trilha minima (instante,
ator) em cada registo, alinhado ao manifesto FEATURE-4 sec. 2 e aos criterios
Given/When/Then da US-4-02.

## precondicoes

- [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) concluida:
  migrations aplicaveis e entidades SQLModel/tabelas de recebimento e trilha
  disponiveis no codigo (caminhos exactos definidos na execucao da US-4-01).
- Eixos FEATURE-2/FEATURE-3 (evento, diretoria, categoria, modo externo)
  resolviveis no backend conforme contrato existente.
- Leitura do `README.md` desta US e de [FEATURE-4.md](../../FEATURE-4.md) sec. 2.

## orquestracao

- `depends_on`: `[]` (primeira task da US; dependencia de **US-4-01** e externa e
  tratada em precondicoes).
- `parallel_safe`: `false`.
- `write_scope`: ficheiro de servico listado no frontmatter; modelos SQLModel de
  recebimento sao entrega da US-4-01 — nao criar migrations de esquema novo
  aqui salvo gap formal da US-4-01 aprovado em gate.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-02-REGISTRO-RECEBIDO-CONFIRMADO/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` (sec. 5 contrato minimo,
  sec. 7 placeholder LGPD apenas como limite)
- Modelos e migrations entregues pela US-4-01 *(caminhos concretos apos merge)*
- `backend/app/db/database.py` *(padrao de sessao)*
- `backend/app/services/recebimento_confirmado_service.py` *(criar ou renomear
  conforme convencao do modulo)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Localizar no codigo as entidades de recebimento e campos de trilha/artefato
   introduzidos na US-4-01; confirmar indices ou FKs necessarios para consulta
   por evento, diretoria, categoria e modo externo.
2. Definir funcoes ou classe de servico que validam existencia e coerencia dos
   eixos (erros de dominio claros, sem vazar detalhes internos indevidos).
3. Implementar operacao de escrita de lote: persistir quantidade
   `recebido_confirmado` (ou agregado definido no modelo) e associar artefato
   quando presente (referencia externa, URL ou texto conforme placeholder
   LGPD).
4. Preencher em cada persistencia os campos de trilha acordados (ator corrente
   ou identificador de integracao, timestamp); reutilizar utilitarios existentes
   de `created_at`/`updated_at` apenas se forem semanticamente equivalentes.
5. Expor API interna (funcoes puras Python) consumivel pelo router na TASK-2,
   sem acoplar a HTTP nesta task.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(smoke opcional; ver `AGENTS.md`)*
- `cd backend && ruff check app/services/recebimento_confirmado_service.py`

## resultado_esperado

Servico de dominio utilizavel pela camada API que persiste lote de
`recebido_confirmado` com eixos validos, artefato opcional e trilha minima,
sem endpoints HTTP nesta task.

## testes_ou_validacoes_obrigatorias

- Teste manual ou REPL: criar sessao, chamar servico com dados minimos validos e
  confirmar linha(s) na base de teste com eixos e trilha preenchidos *(ou
  delegar verificacao integral a TASK-3 com pytest)*.
- Confirmar que nenhuma migration nova foi adicionada sem alinhamento com US-4-01.

## stop_conditions

- Parar e escalar se o modelo da US-4-01 nao existir ou nao suportar lote,
  artefato ou trilha conforme os criterios da US-4-02 — abrir gap na US-4-01 ou
  ADR antes de improvisar esquema.
- Parar se os eixos categoria/modo externo nao tiverem resolucao canonica no
  backend (dependencia FEATURE-3 nao satisfeita).
