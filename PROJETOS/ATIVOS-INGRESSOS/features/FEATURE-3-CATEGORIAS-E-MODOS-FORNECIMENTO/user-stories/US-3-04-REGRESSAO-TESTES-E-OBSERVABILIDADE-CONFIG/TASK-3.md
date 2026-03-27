---
doc_id: "TASK-3.md"
user_story_id: "US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/schemas/ativos.py"
  - "backend/app/services/"
  - "backend/tests/test_ativos_config_audit.py"
tdd_aplicavel: true
---

# TASK-3 - Trilha minima de auditoria em mutacoes de configuracao

## objetivo

Implementar **trilha minima** (log estruturado ou registro auditavel persistido,
conforme decisao ja tomada ou padrao do repo) para **alteracoes de
configuracao por evento** por utilizador autorizado, alinhada a FEATURE-3 sec. 7
e ao PRD 2.6, e cobrir com testes que provem **presenca e campos minimos**
(evento, actor, acao, timestamp ou equivalente acordado).

## precondicoes

- **TASK-2** (`T2`) em `done`.
- Pontos de mutacao de configuracao (PUT/PATCH/POST) entregues pela US-3-02
  identificados no router ou servico correspondente.
- Se nao existir mutacao consolidada ainda, **BLOQUEADO** ate US-3-02 entregar
  superficie de escrita.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false` (mexe em fluxo de escrita e testes).
- `write_scope`: routers/schemas/servicos de configuracao de ativos +
  testes dedicados; ajustar lista se a US-3-02 tiver criado ficheiros novos
  (manter caminhos concretos na execucao).

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) desta US
- [FEATURE-3.md](../../FEATURE-3.md) *(sec. 7 Observabilidade)*
- `backend/app/routers/ativos.py`
- `backend/app/schemas/ativos.py` *(ou schemas criados para configuracao)*
- `backend/app/services/` *(casos de uso de configuracao, se existirem)*
- Padroes existentes: `backend/app/utils/log_sanitize.py` ou logging do projeto
- `backend/tests/test_ativos_config_audit.py` *(criar)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API (ou de servico com session injetada) que executa uma mutacao
    de configuracao autorizada e **falha** enquanto nao houver evidencia da
    trilha (ex.: `caplog` com marcador/nivel, ou linha em tabela de auditoria
    consultavel na mesma transacao/sessao de teste).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_config_audit.py`
- criterio_red:
  - Falha antes da instrumentacao; depois do green, o teste deve continuar a
    detectar remocao acidental da trilha.

## passos_atomicos

1. Escrever o teste de `testes_red`.
2. Confirmar red.
3. Adicionar logging estruturado ou persistencia auditavel **apenas** nos
   caminhos de mutacao de configuracao por evento (sem dados sensiveis em claro;
   alinhar a politicas LGPD do PRD).
4. Confirmar green no pytest.
5. Refatorar extraindo helper de auditoria se reduzir duplicacao sem alargar
   escopo.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_config_audit.py`
- `ruff check` / `ruff format` nos ficheiros tocados

## resultado_esperado

Terceiro criterio Given/When/Then satisfeito: alteracao concluida implica trilha
minima verificavel; testes protegem regressao.

## testes_ou_validacoes_obrigatorias

- `pytest` em `test_ativos_config_audit.py` verde.
- Revisao de que campos logados nao violam restricoes do PRD 2.6.

## stop_conditions

- Parar se nao existir endpoint de escrita de configuracao para instrumentar.
- Parar se produto exigir modelo de auditoria diferente (fora da US) sem PRD
  atualizado.
