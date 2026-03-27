---
doc_id: "TASK-4.md"
user_story_id: "US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_emissao_interna_unitaria_models.py"
  - "backend/alembic/versions/"
  - "backend/app/models/emissao_interna_models.py"
  - "backend/app/models/models.py"
tdd_aplicavel: true
---

# T4 - Testes de invariantes e validacao executavel da cadeia migration

## objetivo

Fechar a US com **evidencia automatizada** dos invariantes acordados no ADR (unicidade de negocio e unicidade/imutabilidade logica de `public_id` na camada persistida) e com **validacao** da revisao Alembic (`upgrade` / `downgrade`), sem implementar API nem UI.

## precondicoes

- T3 concluida: classe(s) em `emissao_interna_models.py` importada(s) via `app.models.models`.
- ADR e migration T2 disponiveis para consulta dos nomes de constraint e colunas.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: false.
- `write_scope`: novo ficheiro de testes; repeticao de comandos alembic; **correcoes minimas** apenas em modelos ou migration se falha de validacao for bug obvio introduzido em T2/T3 (preferir task corretiva separada se a correcao for ambigua).

## arquivos_a_ler_ou_tocar

- [ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md](./ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md)
- Revisao Alembic T2
- `backend/app/models/emissao_interna_models.py`
- `backend/tests/test_lead_constraints.py` *(padrao IntegrityError + sqlite in-memory)*
- `backend/tests/test_ativacao_url_validation.py` *(seed minimo de `StatusEvento` + `Evento`)*
- `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md`

## testes_red

- testes_a_escrever_primeiro:
  - caso que insere duas emissoes no **mesmo escopo de unicidade** definido no ADR e espera `IntegrityError` na segunda confirmacao;
  - caso que insere duas linhas com o **mesmo `public_id`** (se aplicavel ao desenho) e espera `IntegrityError`, **ou** caso que verifica que o metadata/SQLModel expoe o constraint UNIQUE esperado sobre `public_id` — escolher a variante coerente com o ADR e documentar no nome do teste.
- comando_para_rodar:
  - `cd backend && TESTING=true SECRET_KEY=ci-secret-key PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -m pytest -q tests/test_emissao_interna_unitaria_models.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao de dados de suporte/fixtures ou antes do modelo/migration estarem completos; se passarem sem ter implementado T2/T3, parar e rever o criterio do teste.

## passos_atomicos

1. Escrever os testes listados em `testes_red` em `backend/tests/test_emissao_interna_unitaria_models.py`, usando motor SQLite in-memory (`StaticPool`) e `SQLModel.metadata.create_all` **apenas** com o subconjunto de tabelas necessario (incluir tabelas referenciadas por FKs: `evento`, `diretoria`, `status_evento`, entidade FEATURE-3 conforme existir no metadata, `convidado` ou equivalente do ADR, e a tabela de emissao).
2. Semear dados minimos (status, evento, diretoria, categoria por evento, destinatario) com valores validos; usar padroes de `test_ativacao_url_validation.py` e estender para `Diretoria` e demais FKs.
3. Rodar o comando red e confirmar falha inicial coerente (ou green apenas apos implementacao completa de T2/T3 — entao o red foi satisfeito na ordem canónica TDD desta task).
4. Ajustar fixtures/modelos apenas o minimo para atingir green mantendo significado dos asserts.
5. Executar `cd backend && .venv/bin/alembic upgrade head` e `alembic downgrade -1` em base de desenvolvimento com Postgres (ou fluxo do projeto) para confirmar reversibilidade da revisao T2; repetir `upgrade head`.
6. Rodar a suite alvo: `cd backend && TESTING=true SECRET_KEY=ci-secret-key PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -m pytest -q tests/test_emissao_interna_unitaria_models.py`.
7. Preparar **commit** isolado desta task conforme `GOV-COMMIT-POR-TASK` (mensagem com `ATIVOS-INGRESSOS US-5-01 T4: ...`).

## comandos_permitidos

- `cd backend && TESTING=true SECRET_KEY=ci-secret-key PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -m pytest -q tests/test_emissao_interna_unitaria_models.py`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic current`
- `cd backend && PYTHONPATH=<raiz_do_repo>:<raiz_do_repo>/backend .venv/bin/python -c "from app.models import models; print('ok')"`

## resultado_esperado

Testes protegendo duplicidade e identidade conforme ADR; ciclo alembic verificavel; mensagem de commit alinhada à governanca.

## testes_ou_validacoes_obrigatorias

- `pytest` do ficheiro alvo em green com `TESTING=true`.
- Pelo menos um ciclo `upgrade head` apos `downgrade -1` na revisao T2 em ambiente com URL real (quando disponivel no ambiente do executor).
- Import `from app.models import models` com exit code 0 apos alteracoes.

## stop_conditions

- Parar se o grafo de FKs impedir `create_all` em SQLite sem carregar metade do monolito — reduzir escopo do teste para assert sobre `__table_args__` e um unico cenario de IntegrityError documentado, e registrar limitacao no handoff da US.
- Parar se downgrade destruir objetos fora da revisao T2 — investigar ordem de FKs antes de continuar.
- Parar se FEATURE-3 ainda nao estiver no metadata — manter teste em skip com motivo explicito ate merge, e nao declarar US concluida sem estrategia acordada com PM.
