---
doc_id: "ISSUE-F3-01-001-Validar-Runtime-do-Backend-com-Supabase.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-001 - Validar runtime do backend com Supabase

## User Story

Como operador do backend, quero validar a API usando o Supabase como banco de
runtime, para confirmar que o cutover do banco suporta o fluxo real da
aplicacao.

## Contexto Tecnico

`backend/app/db/database.py` define o contrato de runtime da aplicacao e
`scripts/dev_backend.sh` e o launcher oficial a partir da raiz do repo. Depois
da recarga de dados em F2, esta issue confirma que a API sobe e responde usando
`DATABASE_URL` do Supabase, mantendo `DIRECT_URL` reservada para operacoes
sensiveis de banco.

## Plano TDD
- Red: falhar se a API subir apontando para um banco local ou com contrato de URL incoerente
- Green: levantar o backend com as URLs do Supabase e validar o fluxo basico de runtime
- Refactor: consolidar os bloqueios objetivos que restarem antes da documentacao final

## Criterios de Aceitacao
- Given `DATABASE_URL` e `DIRECT_URL` do Supabase configuradas, When a API e iniciada, Then o backend sobe usando o Supabase como banco de runtime
- Given a API em execucao, When os checks basicos de disponibilidade forem feitos, Then os endpoints minimos respondem como esperado
- Given a validacao de runtime concluida, When a documentacao final for ajustada, Then o estado operacional validado esta claro

## Definition of Done da Issue
- [ ] backend iniciado com `DATABASE_URL` do Supabase
- [ ] checks minimos de disponibilidade executados com sucesso
- [ ] bloqueios objetivos de runtime registrados, se existirem

## Tasks Decupadas
- [ ] T1: preparar o ambiente de runtime e conferir o contrato de URLs
- [ ] T2: iniciar a API e executar os checks basicos de disponibilidade
- [ ] T3: consolidar o resultado da validacao de runtime para liberar a documentacao final

## Instructions por Task

### T1
- objetivo: garantir que o backend sera validado contra o Supabase e nao contra um banco local residual
- precondicoes: F2 concluida; credenciais validas de `DATABASE_URL` e `DIRECT_URL`
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `backend/.env.example`
  - `scripts/dev_backend.sh`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- passos_atomicos:
  1. revisar em `backend/app/db/database.py` a ordem de resolucao de `DATABASE_URL` e o fallback de testes
  2. revisar em `scripts/dev_backend.sh` como o backend e iniciado a partir da raiz do repo
  3. conferir se o ambiente de validacao esta apontando para o Supabase e nao para PostgreSQL local
  4. bloquear a rodada se houver qualquer indicio de que o runtime ainda usara o banco local
- comandos_permitidos:
  - `rg -n "DATABASE_URL|TESTING|sqlite" backend/app/db/database.py backend/.env.example scripts/dev_backend.sh docs/DEPLOY_RENDER_CLOUDFLARE.md`
- resultado_esperado: ambiente de runtime preparado para validar a API diretamente contra o Supabase
- testes_ou_validacoes_obrigatorias:
  - confirmar que `DATABASE_URL` do ambiente aponta para o Supabase antes do boot
- stop_conditions:
  - parar se o ambiente ainda estiver configurado para um PostgreSQL local

### T2
- objetivo: validar o boot da API e os checks basicos de disponibilidade com o Supabase como banco de runtime
- precondicoes: T1 concluida; ambiente apontando para o Supabase
- arquivos_a_ler_ou_tocar:
  - `scripts/dev_backend.sh`
  - `backend/app/db/database.py`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- passos_atomicos:
  1. iniciar a API com o launcher oficial da raiz do repo ou comando equivalente suportado
  2. validar pelo menos os checks basicos de disponibilidade do backend em execucao
  3. confirmar que a aplicacao nao caiu em fallback SQLite ou dependencia de PostgreSQL local
  4. registrar qualquer erro objetivo de conexao, timeout ou incompatibilidade de runtime
- comandos_permitidos:
  - `source backend/.venv/bin/activate && ./scripts/dev_backend.sh`
  - `curl -sf http://127.0.0.1:8000/health`
- resultado_esperado: backend iniciado e respondendo com o Supabase como banco de runtime
- testes_ou_validacoes_obrigatorias:
  - `curl -sf http://127.0.0.1:8000/health`
- stop_conditions:
  - parar se a API nao subir, se usar banco incorreto ou se os checks minimos falharem

### T3
- objetivo: consolidar o resultado da validacao de runtime para liberar a etapa documental final
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. resumir o comportamento observado no boot e nos checks de disponibilidade
  2. explicitar se o runtime esta pronto para ser tratado como estado final do projeto
  3. registrar os bloqueios objetivos restantes, se houver, antes da issue documental
  4. liberar a issue somente se o backend tiver sido validado contra o Supabase
- comandos_permitidos:
  - `rg -n "health|DATABASE_URL|DIRECT_URL|Supabase" docs/DEPLOY_RENDER_CLOUDFLARE.md docs/TROUBLESHOOTING.md backend/app/db/database.py`
- resultado_esperado: resultado da validacao de runtime consolidado para orientar a configuracao final
- testes_ou_validacoes_obrigatorias:
  - confirmar que o backend foi validado sem depender do PostgreSQL local
- stop_conditions:
  - parar se o resultado nao permitir afirmar que o runtime do backend usa o Supabase com seguranca

## Arquivos Reais Envolvidos
- `backend/app/db/database.py`
- `backend/.env.example`
- `scripts/dev_backend.sh`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- `docs/TROUBLESHOOTING.md`

## Artifact Minimo

Backend validado em runtime com o Supabase como banco de aplicacao.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F3-01-Validar-Backend-e-Scripts-Criticos-contra-Supabase.md)
- [Fase](../F3_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [F2](../../F2-Migracao-de-Dados/F2_SUPABASE_EPICS.md)
