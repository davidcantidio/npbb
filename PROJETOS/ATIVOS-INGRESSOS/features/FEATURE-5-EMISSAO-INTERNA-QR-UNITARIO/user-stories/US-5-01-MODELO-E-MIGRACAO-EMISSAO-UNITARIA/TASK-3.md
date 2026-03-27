---
doc_id: "TASK-3.md"
user_story_id: "US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/models/emissao_interna_models.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# T3 - Modelos SQLModel para emissao interna unitaria

## objetivo

Espelhar em SQLModel a tabela criada na revisao T2, com `Field(foreign_key=...)` e `Relationship` opcionais apenas onde fizer sentido imediato (`Evento`, `Diretoria`, entidades FEATURE-3, destinatario), **sem** implementar servicos, routers ou regras de emissao da US-5-02.

## precondicoes

- T2 concluida: migration aplicada localmente ou schema inspecionavel a partir do ficheiro de revisao.
- Tipos de coluna, nullability e `__table_args__` (unicidades) conferidos contra o SQL da migration T2 e o ADR.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: false.
- `write_scope`: novo modulo de modelos + import em `models.py` para registo no metadata SQLModel.

## arquivos_a_ler_ou_tocar

- Revisao Alembic produzida na T2
- [ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md](./ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md)
- `backend/app/db/metadata.py`
- `backend/app/models/models.py` *(padrao de import de submodulos no final do ficheiro)*
- `backend/app/models/event_support_models.py` *(estilo de FKs e relacionamentos)*
- `backend/app/models/recebimento_ingresso_models.py` *(se existir no branch: referencia de organizacao por dominio ativos/ingressos)*

## passos_atomicos

1. Criar `backend/app/models/emissao_interna_models.py` com classe `SQLModel, table=True` para a tabela nova; `__tablename__` **igual** ao definido na migration T2.
2. Declarar campos espelhando a revisao, incluindo `public_id` com tipo UUID alinhado ao restante do backend (usar padrao do repo: `uuid.UUID` com `Field`/`Column` conforme exemplos existentes).
3. Replicar `UniqueConstraint` ou equivalente em `__table_args__` se a migration usar constraint nomeada que o SQLModel deva refletir para testes/metadata.
4. Adicionar `Relationship` apenas evitando ciclos de import (forward refs ou imports locais como no repo).
5. Em `backend/app/models/models.py`, importar a(s) nova(s) classe(s) no final do ficheiro, no mesmo padrao de `event_support_models` / `tmj_analytics_models`.
6. Validar import: `cd backend && PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -c "from app.models import models; print('ok')"` substituindo `<raiz_do_repo>` pelo path absoluto do clone.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -c "from app.models import models; print('ok')"`

## resultado_esperado

Modelo(s) registado(s) no metadata, importavel sem erro, alinhados ao DDL da T2 e ao ADR.

## testes_ou_validacoes_obrigatorias

- Comando de import acima com exit code 0.
- Conferencia visual entre classe SQLModel e migration (nomes de coluna e FK strings).

## stop_conditions

- Parar se a migration T2 tiver sido alterada apos merge publico — preferir nova revisao Alembic em vez de editar historico.
- Parar se surgir import circular nao resolvivel sem ADR — escalar.
