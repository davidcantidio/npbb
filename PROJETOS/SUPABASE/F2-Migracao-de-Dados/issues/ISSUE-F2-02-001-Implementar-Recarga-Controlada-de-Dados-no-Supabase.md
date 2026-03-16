---
doc_id: "ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Implementar recarga controlada de dados no Supabase

## User Story

Como operador da migracao, quero recarregar o Supabase com os dados do
PostgreSQL local de forma controlada, para substituir o dataset desatualizado do
alvo sem perder o caminho de retorno.

## Contexto Tecnico

F1 valida o schema e F2-01 entrega o runbook, o backup e o export local. Esta
issue executa a etapa mais sensivel: limpar o alvo na ordem segura, importar os
dados locais com `psql` ou `pg_restore` conforme o runbook aprovado e encerrar a
rodada somente quando a recarga estiver completa.

## Plano TDD
- Red: bloquear a execucao se faltarem backup, export ou ordem segura de recarga
- Green: executar a limpeza controlada e a importacao no Supabase
- Refactor: consolidar a rodada para suportar a validacao pos-carga e o rollback

## Criterios de Aceitacao
- Given backup do Supabase e export local disponiveis, When a recarga roda, Then os dados antigos do Supabase sao substituidos pelos dados locais
- Given dependencias entre tabelas, When a limpeza e a importacao ocorrem, Then a ordem operacional respeita o runbook aprovado
- Given a recarga concluida, When a validacao pos-carga for iniciada, Then o Supabase ja esta pronto para as verificacoes de integridade

## Definition of Done da Issue
- [x] precondicoes de backup, export e ordem de recarga verificadas antes da execucao
- [x] limpeza e importacao executadas sem improviso no Supabase
- [x] resultado da recarga pronto para a validacao pos-carga

## Tasks Decupadas
- [x] T1: validar precondicoes e selecionar o caminho de recarga aprovado no runbook
- [x] T2: preparar a limpeza controlada do Supabase na ordem segura
- [x] T3: executar a importacao dos dados locais no Supabase
- [x] T4: consolidar o estado final da recarga para a etapa de validacao

## Instructions por Task

### T1
- objetivo: garantir que a recarga so comeca com todos os insumos criticos validados
- precondicoes: EPIC-F2-01 concluido; backup do Supabase e export local disponiveis
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/PRD-SUPABASE.md`
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. revisar o runbook aprovado e confirmar qual caminho sera usado para a recarga: `psql` ou `pg_restore`
  2. confirmar que o backup do Supabase existe e que o export local esta disponivel para a importacao
  3. conferir se `DIRECT_URL` do Supabase e o acesso ao PostgreSQL local estao validos para a rodada
  4. bloquear a execucao se qualquer um desses insumos estiver ausente
- comandos_permitidos:
  - `pg_restore --help`
  - `psql --help`
- resultado_esperado: recarga autorizada apenas com todos os insumos e o caminho operacional definidos
- testes_ou_validacoes_obrigatorias:
  - confirmar que backup e export existem antes do primeiro passo destrutivo
- stop_conditions:
  - parar se faltar backup, export local ou definicao objetiva do caminho de recarga

### T2
- objetivo: executar a limpeza controlada do ambiente alvo na ordem segura aprovada
- precondicoes: T1 concluida; ordem de recarga definida
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
  - `backend/scripts/seed_common.py`
- passos_atomicos:
  1. preparar a conexao direta ao Supabase para a etapa de limpeza
  2. aplicar a limpeza do dataset alvo conforme a ordem segura definida no runbook
  3. interromper imediatamente se surgir erro de FK, erro transacional ou qualquer indicio de que a ordem de limpeza esta incorreta
  4. preservar o backup do Supabase como caminho de retorno ate o fim da F3
- comandos_permitidos:
  - `psql --help`
  - `pg_restore --help`
- resultado_esperado: ambiente alvo pronto para receber os dados locais sem resquicio operacional do dataset antigo
- testes_ou_validacoes_obrigatorias:
  - confirmar que a limpeza executada corresponde exatamente ao runbook aprovado
- stop_conditions:
  - parar se a ordem segura da limpeza nao puder ser garantida ou se houver risco nao previsto de perda de dados fora do backup

### T3
- objetivo: importar no Supabase o dataset atual do PostgreSQL local usando o formato aprovado
- precondicoes: T2 concluida; ambiente alvo pronto para importacao
- arquivos_a_ler_ou_tocar:
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. executar a importacao com `psql` ou `pg_restore`, conforme o caminho aprovado no runbook
  2. observar o progresso e interromper a rodada se houver falha estrutural durante a carga
  3. garantir que a importacao nao altere schema fora do historico Alembic ja validado em F1
  4. registrar o resultado bruto da carga para a issue de validacao pos-carga
- comandos_permitidos:
  - `psql --help`
  - `pg_restore --help`
- resultado_esperado: dados locais carregados no Supabase sem alterar o schema validado em F1
- testes_ou_validacoes_obrigatorias:
  - confirmar que a importacao concluiu sem erro antes de iniciar a validacao
- stop_conditions:
  - parar se a importacao falhar no meio da carga ou exigir ajuste de schema fora do escopo aprovado

### T4
- objetivo: preparar o ambiente recarregado para a etapa de integridade pos-carga
- precondicoes: T3 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `backend/.env.example`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. confirmar que o Supabase ficou acessivel com o dataset recarregado
  2. consolidar os dados minimos da rodada: caminho usado, resultado da carga e bloqueios objetivos, se existirem
  3. manter o backup do Supabase preservado ate o encerramento da validacao da F3
  4. liberar a issue somente quando o ambiente estiver pronto para a validacao pos-carga
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL" backend/app/db/database.py backend/.env.example`
- resultado_esperado: ambiente recarregado e pronto para a validacao de integridade
- testes_ou_validacoes_obrigatorias:
  - confirmar que a proxima etapa pode acessar o Supabase sem depender do PostgreSQL local
- stop_conditions:
  - parar se o ambiente recarregado ainda nao estiver apto para a validacao pos-carga

## Arquivos Reais Envolvidos
- `PROJETOS/SUPABASE/PRD-SUPABASE.md`
- `backend/.env.example`
- `backend/app/db/database.py`
- `backend/scripts/seed_common.py`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Rodada de recarga executada no Supabase com o dataset local pronta para a
validacao de integridade.

**Artifact gerado:** [backend/scripts/recarga_migracao.py](../../../../backend/scripts/recarga_migracao.py) — executa validacao, limpeza, import e consolidacao.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [EPIC-F2-01](../EPIC-F2-01-Preparar-Backup-e-Export-do-PostgreSQL-Local.md)
- [ISSUE-F2-01-002](./ISSUE-F2-01-002-Automatizar-Backup-do-Supabase-e-Export-do-PostgreSQL-Local.md)
