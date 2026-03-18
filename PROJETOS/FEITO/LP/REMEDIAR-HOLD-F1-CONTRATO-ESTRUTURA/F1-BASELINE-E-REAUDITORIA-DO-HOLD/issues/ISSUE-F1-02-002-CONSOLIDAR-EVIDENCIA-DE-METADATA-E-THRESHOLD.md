---
doc_id: "ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
task_instruction_mode: "required"
decision_refs:
  - "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md / secoes 2, 5 e 8"
  - "auditoria_fluxo_ativacao.md / F1-NAO03, F1-NAO04 e F1-NAO08"
  - "SPEC-ANTI-MONOLITO.md / thresholds por arquivo"
---

# ISSUE-F1-02-002 - Consolidar evidencia de metadata e threshold

## User Story

Como mantenedor do sibling `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`, quero
consolidar evidencia executavel de metadata critica, migration rastreavel e
threshold estrutural para que a reauditoria da F1 consiga verificar a fundacao
por fatos e relacionar cada prova aos achados estruturais do hold.

## Contexto Tecnico

O repositorio ja possui teste focal de schema contract
(`test_lp_ativacao_schema_contract.py`), migration rastreavel
`c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py` e baseline
estrutural recente de `models.py` e `ativacao.py`. Esta issue consolida essas
provas, liga cada uma aos achados `F1-NAO03`, `F1-NAO04` e `F1-NAO08` e torna
explicito que `backend/app/routers/leads.py` permanece fora do sibling como
risco residual.

## Plano TDD

- Red: validar se a metadata critica e os thresholds ainda podem ser provados pelo estado atual
- Green: consolidar a evidencia executavel de schema contract, revision e medidas estruturais
- Refactor: vincular cada prova aos achados estruturais da auditoria F1

## Criterios de Aceitacao

- Given o teste focal de metadata, When o comando exato aprovado for executado, Then existe evidencia objetiva das tabelas, campos e indice criticos da fundacao
- Given a migration `c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`, When ela for lida junto com o teste focal, Then a rastreabilidade de revision fica explicita
- Given as metricas atuais de `models.py` e `ativacao.py`, When elas forem registradas, Then a leitura contra `SPEC-ANTI-MONOLITO.md` fica objetiva
- Given qualquer ausencia de tabela, indice, revision ou threshold esperado, When ela surgir, Then a issue responde `BLOQUEADO`

## Definition of Done da Issue

- [x] evidencia de metadata critica consolidada
- [x] evidencia de revision/migration rastreavel consolidada
- [x] evidencia de threshold dos alvos originais do hold consolidada
- [x] provas vinculadas aos achados `F1-NAO03`, `F1-NAO04` e `F1-NAO08`

## Tasks Decupadas

- [x] T1: consolidar a evidencia de metadata critica e da revision rastreavel
- [x] T2: registrar a evidencia de threshold dos alvos estruturais originais do hold
- [x] T3: mapear cada prova aos achados estruturais da auditoria F1

## Instructions por Task

### T1
- objetivo: produzir evidencia repetivel de metadata critica e de revision rastreavel da fundacao da F1
- precondicoes:
  - baseline estrutural de `ISSUE-F1-01-002` concluida
  - nenhuma alteracao nova em models ou migrations sendo introduzida por este sibling
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_lp_ativacao_schema_contract.py`
  - `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. executar o comando focal aprovado de metadata
  2. ler a migration `c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`
  3. registrar quais tabelas, colunas e indices criticos ficam provados por teste e por leitura da revision
- comandos_permitidos:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_lp_ativacao_schema_contract.py`
  - `sed -n`
- resultado_esperado: evidencia objetiva de metadata e revision rastreavel da fundacao consolidada
- testes_ou_validacoes_obrigatorias:
  - `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_lp_ativacao_schema_contract.py`
- stop_conditions:
  - parar se o teste focal falhar
  - parar se a migration rastreavel nao puder ser associada aos objetos criticos da fundacao

### T2
- objetivo: registrar a leitura de threshold dos alvos estruturais originais do hold
- precondicoes:
  - T1 concluida
  - metadata critica consolidada
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
  - `backend/app/models/models.py`
  - `backend/app/routers/ativacao.py`
  - `backend/app/routers/leads.py`
- passos_atomicos:
  1. revisar os thresholds de `warn` e `block` do spec
  2. registrar as linhas atuais de `models.py`, `ativacao.py` e `leads.py`
  3. explicitar a leitura normativa: `models.py` e `ativacao.py` como alvos remediados do hold; `leads.py` como risco residual fora do sibling
- comandos_permitidos:
  - `sed -n`
  - `wc -l`
  - `apply_patch`
- resultado_esperado: quadro objetivo de threshold registrado na issue
- testes_ou_validacoes_obrigatorias:
  - `wc -l backend/app/models/models.py backend/app/routers/ativacao.py backend/app/routers/leads.py`
- stop_conditions:
  - parar se `models.py` ou `ativacao.py` voltarem a cruzar threshold aplicavel
  - parar se o quadro estrutural passar a exigir refactor de `leads.py` neste sibling

### T3
- objetivo: vincular cada prova consolidada aos achados estruturais e de metadata da auditoria F1
- precondicoes:
  - T1 e T2 concluidas
  - evidencias de metadata e threshold registradas
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/LP/auditoria_fluxo_ativacao.md`
  - `PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md`
- passos_atomicos:
  1. mapear a evidencia de schema contract e revision para `F1-NAO08`
  2. mapear a evidencia de `models.py` para `F1-NAO03` e de `ativacao.py` para `F1-NAO04`
  3. registrar que `leads.py` permanece como risco fora deste sibling e nao como follow-up silencioso
- comandos_permitidos:
  - `apply_patch`
  - `rg -n`
- resultado_esperado: issue pronta para leitura de auditoria com mapeamento explicito `achado -> prova`
- testes_ou_validacoes_obrigatorias:
  - `rg -n "F1-NAO03|F1-NAO04|F1-NAO08|leads.py" PROJETOS/LP/REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA/F1-BASELINE-E-REAUDITORIA-DO-HOLD/issues/ISSUE-F1-02-002-CONSOLIDAR-EVIDENCIA-DE-METADATA-E-THRESHOLD.md`
- stop_conditions:
  - parar se alguma prova nao puder ser vinculada a um achado material do hold
  - parar se o mapeamento exigir atualizar `AUDIT-LOG.md`

## Arquivos Reais Envolvidos

- `backend/tests/test_lp_ativacao_schema_contract.py`
- `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py`
- `backend/app/models/models.py`
- `backend/app/routers/ativacao.py`
- `backend/app/routers/leads.py`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
- `PROJETOS/LP/auditoria_fluxo_ativacao.md`

## Artifact Minimo

- quadro consolidado `prova -> comando ou leitura -> achado da auditoria`, registrado na propria issue

## Evidencia Consolidada

### T1 - Metadata Critica e Revision Rastreavel

| Prova | Comando ou leitura | Objetos provados | Achado vinculado |
|---|---|---|---|
| teste focal de metadata | `PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q backend/tests/test_lp_ativacao_schema_contract.py` | `conversao_ativacao` com colunas `id`, `ativacao_id`, `lead_id`, `cpf`, `created_at`; indice `ix_conversao_ativacao_ativacao_id_cpf`; `lead_reconhecimento_token` com colunas `token_hash`, `lead_id`, `evento_id`, `expires_at` | `F1-NAO08` |
| leitura da revision | `backend/alembic/versions/c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py` | `revision = c5a8d2e1f4b6`; criacao de `conversao_ativacao`; criacao de `lead_reconhecimento_token`; criacao de `ix_conversao_ativacao_ativacao_id_cpf` | `F1-NAO08` |

Resultado objetivo do comando aprovado em `2026-03-13`: `2 passed in 0.12s`.

Leitura objetiva da prova:

- o teste focal exige a presenca das tabelas e do indice criticos da fundacao no metadata carregado do backend
- a revision `c5a8d2e1f4b6` preserva rastreabilidade explicita entre a prova automatizada e a migration que cria os objetos auditados
- para esta issue, `F1-NAO08` fica coberto por duas camadas complementares de evidencia: teste executavel e leitura direta da migration

### T2 - Threshold Estrutural dos Alvos Originais do Hold

Leitura executada contra `SPEC-ANTI-MONOLITO.md`, usando o threshold de arquivo
`warn > 400` e `block > 600`.

| Arquivo | Linhas atuais | Threshold aplicavel | Leitura normativa | Escopo no sibling |
|---|---:|---|---|---|
| `backend/app/models/models.py` | `549` | `warn (> 400)` e abaixo de `block (> 600)` | `warn`; alvo estrutural remediado da F1 e fora do threshold bloqueante | dentro |
| `backend/app/routers/ativacao.py` | `394` | abaixo de `warn (> 400)` | `ok`; alvo estrutural remediado da F1 e abaixo do threshold de atencao | dentro |
| `backend/app/routers/leads.py` | `1649` | `block (> 600)` | `block`; risco estrutural residual explicito e fora do escopo deste sibling | fora |

Resultado objetivo do comando aprovado em `2026-03-13`:

- `backend/app/models/models.py`: `549`
- `backend/app/routers/ativacao.py`: `394`
- `backend/app/routers/leads.py`: `1649`

Leitura objetiva da prova:

- `models.py` e `ativacao.py` correspondem aos alvos estruturais originais do hold e ja nao reproduzem o retrato historico descrito na auditoria de origem.
- `leads.py` continua muito acima do threshold `block`, mas este arquivo nao pertence aos alvos remediados desta trilha e deve permanecer como risco residual fora do sibling.
- o sibling usa esse quadro apenas para prestar contas do estado estrutural atual, nao para absorver silenciosamente um novo refactor de `leads.py`.

### T3 - Mapeamento Explicito dos Achados da Auditoria F1

| Achado | Prova consolidada | Leitura de fechamento |
|---|---|---|
| `F1-NAO03` | baseline estrutural de `backend/app/models/models.py` com `549` linhas, medida contra `SPEC-ANTI-MONOLITO.md` | o arquivo deixa de reproduzir o estado bloqueante historico (`1364` linhas) e fica registrado como alvo estrutural remediado da F1, ainda em `warn` mas fora de `block` |
| `F1-NAO04` | baseline estrutural de `backend/app/routers/ativacao.py` com `394` linhas, medida contra `SPEC-ANTI-MONOLITO.md` | o arquivo deixa de reproduzir o estado historico de alerta (`421` linhas) e fica registrado abaixo de `warn` como alvo estrutural remediado da F1 |
| `F1-NAO08` | teste focal `test_lp_ativacao_schema_contract.py` + leitura da revision `c5a8d2e1f4b6_add_conversao_ativacao_and_reconhecimento_token.py` | a reauditoria recebe prova executavel e rastreabilidade direta para tabelas, colunas e indice criticos da fundacao |

Registro explicito de risco residual:

- `backend/app/routers/leads.py` permanece fora deste sibling como risco estrutural residual, mesmo cruzando `block`, e nao deve ser reinterpretado como follow-up silencioso desta issue.
- o mapeamento acima fecha a prestacao de contas dos achados estruturais e de metadata sem exigir atualizacao de `AUDIT-LOG.md` nem reclassificacao do `hold` original.

## Dependencias

- [Issue de Baseline Estrutural](./ISSUE-F1-01-002-VALIDAR-BASELINE-ESTRUTURAL-DA-F1.md)
- [Auditoria de Origem](../../../auditoria_fluxo_ativacao.md)
- [Epic](../EPIC-F1-02-EVIDENCIA-OBJETIVA-PARA-REAUDITORIA.md)
- [Fase](../F1_REMEDIAR_HOLD_F1_CONTRATO_ESTRUTURA_EPICS.md)
