---
doc_id: "TASK-3.md"
user_story_id: "US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/models/recebimento_ingresso_models.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# T3 - Modelos SQLModel alinhados ao schema FEATURE-4

## objetivo

Espelhar em SQLModel as tabelas introduzidas nas revisoes T1 e T2, com `Relationship` apenas onde fizer sentido imediato (`Evento`, `Diretoria`, `Usuario`, entidades FEATURE-3), **sem** implementar servicos, routers ou regras de negocio de US-4-02 em diante.

## precondicoes

- T2 concluida e migrations aplicadas localmente (schema visivel).
- Tipos de coluna e nullability conferidos contra o SQL gerado nas revisoes T1/T2.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: false.
- `write_scope`: novo modulo de modelos + import em `models.py` para registo no metadata SQLModel.

## arquivos_a_ler_ou_tocar

- Revisoes Alembic das tasks T1 e T2
- `backend/app/db/metadata.py`
- `backend/app/models/models.py` *(padrao de import de submodulos)*
- `backend/app/models/event_support_models.py` *(estilo de FKs e relacionamentos)*

## passos_atomicos

1. Criar `backend/app/models/recebimento_ingresso_models.py` com classes `SQLModel, table=True` para cada tabela nova, nomes de `__tablename__` **iguais** aos criados nas migrations.
2. Declarar `Field(foreign_key=...)` alinhados as strings de FK das migrations (incl. `evento.id`, `diretoria.id`, `usuario.id` se usados, e FKs FEATURE-3).
3. Adicionar `Relationship` opcional apenas para leitura/desenvolvimento futuro, evitando import circular (seguir padrao do repo: tipos forward ou imports locais).
4. Em `backend/app/models/models.py`, importar as novas classes no final do ficheiro (mesmo padrao que `event_support_models` / `tmj_analytics_models`) para garantir que o metadata as regista.
5. Arrancar interpretador ou comando rapido de import: `python -c "from app.models import models"` a partir de `backend/` com `PYTHONPATH` do projeto, confirmando ausencia de erro de import.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -c "from app.models import models; print('ok')"`
- *(substituir `<raiz_do_repo>` pelo path absoluto do clone; equivale ao que `scripts/dev_backend.sh` documenta)*

## resultado_esperado

Modelos Python consistentes com o DDL; aplicacao continua a importar o pacote de modelos sem regressao de import.

## testes_ou_validacoes_obrigatorias

- Comando de import acima (ou equivalente documentado no handoff) com exit code 0.
- Conferencia visual entre nomes de colunas no modelo e no ficheiro Alembic.

## stop_conditions

- Parar se for necessario autogerar migration a partir dos modelos que diverge do DDL manual — preferir alinhar modelo ao DDL ja mergeado, nao o contrario, salvo decisao explicita.
- Parar se aparecer ciclo de imports irresolvevel — extrair tipos base ou mover relacionamentos para modulo separado conforme convencao do repo.
