---
doc_id: "TASK-2.md"
user_story_id: "US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# T2 - Migration: bloqueio, referencias a artefatos e colunas de auditoria

## objetivo

Estender o schema com estruturas para **bloqueio** associado ao fluxo de recebimento (base para US-4-04), **referencias a artefatos** sem binario obrigatorio no core (placeholder LGPD: URI/ref externa + metadados), e campos ou tabela(s) de **auditoria minima** (ator, instante, natureza da alteracao) consumiveis pelas US seguintes, conforme segundo e terceiro criterios de aceitacao da US.

## precondicoes

- T1 concluida: revisao Alembic da T1 mergeada no branch e `alembic upgrade head` verde.
- Head Alembic aponta para a revisao criada na T1 (ou cadeia linear correta).

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: false.
- `write_scope`: novo ficheiro sob `backend/alembic/versions/` (segunda revisao apos T1).

## arquivos_a_ler_ou_tocar

- Revisao Alembic produzida na T1
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 7 LGPD — apenas contexto; nao ampliar escopo)*
- `README.md` desta US (criterios de artefato / auditoria)

## passos_atomicos

1. Confirmar `down_revision` = revisao final da T1.
2. Criar tabela (ou extensao coerente) de **bloqueio por recebimento** com FKs apenas para entidades ja criadas na T1 ou tabelas existentes (`evento`, `diretoria`, etc.), sem codificar ainda a maquina de estados de US-4-04.
3. Criar tabela de **referencia a artefato** com: identificador; FK opcional para linha de recebimento ou entidade pai definida na T1; campos para **referencia externa** (URL ou chave logica) e **metadados** (ex. JSON ou texto); **nao** exigir coluna de blob/binario obrigatoria — documentar no comentario da migration que o storage definitivo aguarda decisao LGPD.
4. Incluir **auditoria minima**: preferir colunas nas tabelas de dominio criadas em T1/T2 (`created_at`/`updated_at` ja existentes no repo como padrao) **e** campos para `ator` (ex. `usuario_id` nullable com FK para `usuario.id` se aplicavel) e **natureza da alteracao** (string curta ou enum em texto); **ou** tabela de log append-only referenciando entidade alvo — escolher uma abordagem e manter consistencia com o restante do backend.
5. Implementar `upgrade()` / `downgrade()` simetricos para esta revisao apenas.
6. Validar `alembic upgrade head` e `alembic downgrade -1` em sequencia (subir tudo, descer um nivel, subir de novo se necessario para confirmar idempotencia local).

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic downgrade <revision_da_T1>` *(apenas para diagnostico se downgrade -1 nao bastar)*

## resultado_esperado

Schema preparado para bloqueios, anexos logicos externos e trilha auditavel minima, cumprindo os criterios 2 e 3 da US sem antecipar logica de API/UI.

## testes_ou_validacoes_obrigatorias

- Ciclo `upgrade head` + `downgrade -1` + `upgrade head` sem erro.
- Revisar comentarios na migration: mencionar explicitamente **placeholder LGPD** e ausencia de binario obrigatorio no core.

## stop_conditions

- Parar se T1 nao estiver aplicada ou se o downgrade da T2 deixar objetos orfaos.
- Parar se surgir necessidade de armazenar conteudo binario obrigatorio — reprovar escopo e alinhar PRD sec. 7 antes de continuar.
