---
doc_id: "TASK-4.md"
user_story_id: "US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/recebimento_ingresso_models.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# T4 - Validacao final, downgrade multiplo e registo LGPD

## objetivo

Fechar a US com **evidencia executavel** de migrations (cadeia completa T1+T2), confirmar que os modelos permanecem alinhados apos um ciclo de aplicacao de schema, e **documentar** o placeholder LGPD (referencia externa + metadados; sem binario obrigatorio) de forma rastreavel para auditoria — sem criar novos ficheiros em `docs/` salvo ja existir convenção explícita no PR/handoff.

## precondicoes

- T3 concluida: modelos importados e migrations presentes no branch.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: false.
- `write_scope`: repeticao de comandos sobre artefactos ja tocados; **nao** alterar DDL nesta task salvo correcao minima para corrigir falha de validacao (nesse caso, preferir nova task ou revisao de escopo).

## arquivos_a_ler_ou_tocar

- Revisoes Alembic T1 e T2
- `backend/app/models/recebimento_ingresso_models.py`
- `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md`

## passos_atomicos

1. Em base limpa de desenvolvimento, executar `alembic upgrade head` desde a revisao anterior a T1 ate head.
2. Executar `alembic downgrade` ate a revisao **anterior** a T1 (dois passos de downgrade se T1 e T2 forem revisoes separadas), confirmando que o schema remove apenas o esperado.
3. Subir novamente com `alembic upgrade head`.
4. Repetir import de modelos (`from app.models import models`) apos o upgrade final.
5. Se a documentacao LGPD ainda nao estiver explicita nos comentarios do topo das migrations T2 (artefatos), acrescentar **comentario SQLAlchemy** ou docstring curta na revisao T2 **sem** mudar comportamento — apenas se ainda faltar texto; caso contrario, registar no handoff da US que o comentario ja cumpre o requisito.
6. Preparar **commit** isolado desta US conforme `GOV-COMMIT-POR-TASK` (mensagem com `ATIVOS-INGRESSOS US-4-01 T4: ...`).

## comandos_permitidos

- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1` *(repetir conforme necessario ate base pre-T1)*
- `cd backend && .venv/bin/alembic current`
- `cd backend && PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -c "from app.models import models; print('ok')"`

## resultado_esperado

Evidencia de que a cadeia de migrations e reversivel além de um unico passo; modelos carregam com schema atual; decisao de placeholder LGPD visivel para revisores.

## testes_ou_validacoes_obrigatorias

- Pelo menos um ciclo completo: `upgrade head` apos `downgrade` multiplo ate pre-T1.
- Import dos modelos com exit code 0 apos schema no head.
- Mensagem de commit com projeto, US e task conforme governanca.

## stop_conditions

- Parar se downgrade destruir dados ou tabelas fora do escopo T1/T2 — investigar ordem de dependencias FK antes de continuar.
- Parar se for necessario reescrever migrations ja mergeadas em main — escalar para estrategia de revisao nova em vez de editar historico publicado.
