---
doc_id: "ISSUE-F2-01-003-Validar-Artefatos-e-Cobrir-a-Automacao-de-Backup-Export.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-003 - Validar artefatos e cobrir a automacao de backup/export

## User Story

Como operador da migracao, quero que a automacao valide objetivamente os
artefatos gerados e tenha cobertura automatizada para seus cenarios criticos,
para que a F2-02 nao consuma dumps invalidos nem dependa de comportamento sem
prova executavel.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue de `ISSUE-F2-01-002`.

- issue de origem: `ISSUE-F2-01-002`
- evidencia usada na revisao: diff dos commits `1a95361`, `46f094c` e `671308c`;
  leitura de `backend/scripts/backup_export_migracao.py`, `backend/.env.example`,
  `docs/RUNBOOK-MIGRACAO-SUPABASE.md`, `docs/SETUP.md`,
  `docs/TROUBLESHOOTING.md`; validacao sintatica com `py_compile`; busca de
  testes no repo; execucao de `pytest -k backup_export_migracao` sem casos
  selecionados
- sintoma observado: a automacao declara os artefatos prontos para a recarga
  controlada sem validar a legibilidade do dump gerado antes da mensagem final
  de sucesso, e nao ha teste automatizado dedicado cobrindo precondicoes, ordem
  `backup -> export` e falhas do fluxo
- risco de nao corrigir: a F2-02 pode partir de artefatos corrompidos ou nao
  verificaveis; regressao em precondicoes e ordem critica pode passar sem
  deteccao e comprometer a seguranca operacional da migracao

## Plano TDD

- Red: materializar em testes os cenarios de precondicao, ordem critica e falha
  de validacao dos artefatos
- Green: fazer a automacao validar os dumps antes de anunciar prontidao para
  F2-02
- Refactor: consolidar verificacoes de tooling e mensagens de erro sem alterar o
  carater nao destrutivo do fluxo

## Criterios de Aceitacao

- Given backup e export gerados em formato custom, When a automacao conclui,
  Then ela valida os artefatos de forma objetiva antes de anunciar sucesso para
  F2-02
- Given dump ilegivel, ausente ou invalido, When a etapa de validacao roda,
  Then o fluxo falha sem declarar os artefatos prontos para a recarga
- Given falta de credencial, `pg_dump` ou tooling adicional exigido pela
  validacao, When a automacao e iniciada, Then a falha ocorre antes de qualquer
  mensagem de sucesso
- Given o fluxo principal da automacao, When os testes dedicados forem
  executados, Then eles comprovam a ordem `backup -> export -> validacao final`
  e cobrem os cenarios criticos de falha

## Definition of Done da Issue

- [x] a automacao valida objetivamente os artefatos antes da mensagem final de
      prontidao
- [x] existe cobertura automatizada dedicada para precondicoes, ordem critica e
      falhas de validacao
- [x] a documentacao operacional reflete qualquer tooling adicional exigido pela
      validacao dos artefatos

## Tasks Decupadas

- [x] T1: fechar o contrato de validacao dos artefatos e das precondicoes da
      automacao
- [x] T2: implementar a validacao objetiva dos dumps antes da liberacao para
      F2-02
- [x] T3: adicionar testes dedicados e alinhar a documentacao operacional

## Instructions por Task

### T1

- objetivo: definir exatamente quais validacoes finais a automacao deve fazer e
  quais ferramentas passam a ser precondicao do fluxo
- precondicoes: `ISSUE-F2-01-002` revisada; runbook atual lido; entendimento
  claro de que o escopo continua nao destrutivo
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/backup_export_migracao.py`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. localizar o ponto em que a automacao declara os artefatos prontos para
     F2-02
  2. definir a validacao minima obrigatoria para os dumps gerados, sem incluir
     qualquer limpeza, import ou alteracao no Supabase
  3. fechar se a validacao exigira `pg_restore`, checagem de existencia/tamanho
     do arquivo, ou ambas, mantendo aderencia ao formato custom ja produzido
  4. atualizar o contrato operacional para que a automacao so anuncie sucesso
     depois da validacao final dos artefatos
- comandos_permitidos:
  - `rg -n "pg_dump|pg_restore|Artefatos prontos|backup|export" backend/scripts/backup_export_migracao.py docs/RUNBOOK-MIGRACAO-SUPABASE.md docs/SETUP.md docs/TROUBLESHOOTING.md`
  - `pg_restore --help`
- resultado_esperado: contrato de validacao final e de tooling fechado, sem
  ambiguidade e sem ampliar escopo para import/recarga
- testes_ou_validacoes_obrigatorias:
  - confirmar que o fluxo continua apenas com backup, export e validacao dos
    artefatos
- stop_conditions:
  - parar se a validacao pretendida exigir passo destrutivo ou redefinir o
    escopo da F2-02

### T2

- objetivo: materializar no script a validacao objetiva dos artefatos antes da
  mensagem final de prontidao
- precondicoes: T1 concluida; regras de validacao e tooling definidas
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/backup_export_migracao.py`
- passos_atomicos:
  1. adicionar as verificacoes de tooling exigidas pela validacao final no mesmo
     bloco de precondicoes do fluxo
  2. implementar validadores explicitos para os dumps gerados, preservando a
     ordem `backup -> export -> validacao final`
  3. fazer o script falhar com erro objetivo quando algum artefato nao puder ser
     validado, sem imprimir a mensagem final de sucesso
  4. manter intacta a restricao de nao executar qualquer passo destrutivo no
     Supabase
- comandos_permitidos:
  - `pg_dump --help`
  - `pg_restore --help`
- resultado_esperado: automacao so libera F2-02 quando os dumps gerados passam
  pelas validacoes finais definidas em T1
- testes_ou_validacoes_obrigatorias:
  - confirmar no codigo que a mensagem final de prontidao nao aparece em caminho
    de falha
  - confirmar que a ordem continua sendo backup antes de export
- stop_conditions:
  - parar se a implementacao exigir mudar o formato dos artefatos ou alterar o
    runbook alem da validacao local

### T3

- objetivo: criar cobertura automatizada para os cenarios criticos e alinhar a
  documentacao ao comportamento corrigido
- precondicoes: T2 concluida; fluxo final do script estabilizado
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/backup_export_migracao.py`
  - `backend/tests/`
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. adicionar teste dedicado para falha antecipada em ausencia de credenciais ou
     tooling obrigatorio
  2. adicionar teste dedicado para a ordem `backup -> export -> validacao final`
     e para o bloqueio da mensagem de sucesso quando a validacao falhar
  3. atualizar runbook, setup e troubleshooting apenas no necessario para
     refletir a validacao final e o tooling exigido
  4. executar os testes dedicados da automacao e registrar qualquer limitacao
     objetiva de ambiente encontrada
- comandos_permitidos:
  - `cd backend && TESTING=true SECRET_KEY=ci-secret-key PYTHONPATH=.. python3 -m pytest -q tests/test_backup_export_migracao.py`
  - `cd backend && python3 -m py_compile scripts/backup_export_migracao.py`
- resultado_esperado: cobertura automatizada dedicada e documentacao coerente
  com o comportamento corrigido da automacao
- testes_ou_validacoes_obrigatorias:
  - `cd backend && TESTING=true SECRET_KEY=ci-secret-key PYTHONPATH=.. python3 -m pytest -q tests/test_backup_export_migracao.py`
  - `cd backend && python3 -m py_compile scripts/backup_export_migracao.py`
- stop_conditions:
  - parar se os testes dependerem de conexao real com Supabase ou PostgreSQL
    local em vez de doubles/mocks controlados

## Arquivos Reais Envolvidos

- `backend/scripts/backup_export_migracao.py`
- `backend/tests/test_backup_export_migracao.py`
- `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Automacao que valida objetivamente os artefatos gerados antes da mensagem final
de prontidao, com teste dedicado cobrindo precondicoes, ordem critica e falhas
de validacao.

**Artifact gerado:** `backend/scripts/backup_export_migracao.py` e
`backend/tests/test_backup_export_migracao.py`

## Dependencias

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F2-01-002](./ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md)
