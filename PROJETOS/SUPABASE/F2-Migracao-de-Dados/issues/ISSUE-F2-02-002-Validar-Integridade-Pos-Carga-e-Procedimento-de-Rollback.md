---
doc_id: "ISSUE-F2-02-002-Validar-Integridade-Pos-Carga-e-Procedimento-de-Rollback.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Validar integridade pos-carga e procedimento de rollback

## User Story

Como responsavel pelo cutover, quero validar a integridade do Supabase apos a
recarga e confirmar que o rollback continua viavel, para liberar a fase final
sem perder o caminho de retorno.

## Contexto Tecnico

A recarga da issue anterior substitui o dataset do Supabase. Esta issue fecha a
fase de dados com verificacoes objetivas de consistencia e com a confirmacao de
que o backup do Supabase continua utilizavel caso a rodada precise ser desfeita.

## Plano TDD
- Red: falhar se o estado pos-carga ainda divergir do dataset local ou se o backup nao estiver utilizavel
- Green: validar o ambiente recarregado e manter o rollback viavel
- Refactor: consolidar um checklist simples e verificavel para liberar F3

## Criterios de Aceitacao
- Given a recarga concluida, When a validacao pos-carga roda, Then o Supabase apresenta sinais objetivos de que agora reflete os dados locais
- Given o backup previo do Supabase, When o procedimento de rollback e revisado, Then o caminho de retorno permanece viavel ate o fim da validacao
- Given a validacao pos-carga concluida, When F3 iniciar, Then o ambiente esta apto para validacao de runtime e cutover

## Definition of Done da Issue
- [ ] checklist de integridade pos-carga executado
- [ ] backup e procedimento de rollback ainda viaveis
- [ ] fase F2 pronta para liberar a validacao e o cutover

## Tasks Decupadas
- [ ] T1: definir e executar o checklist minimo de integridade pos-carga
- [ ] T2: revisar a viabilidade do rollback a partir do backup preservado
- [ ] T3: consolidar o veredito da fase de dados para liberar F3

## Instructions por Task

### T1
- objetivo: verificar se o estado pos-carga do Supabase ja e suficiente para liberar a fase final
- precondicoes: ISSUE-F2-02-001 concluida; ambiente recarregado acessivel
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `backend/.env.example`
  - `docs/SETUP.md`
  - `docs/TROUBLESHOOTING.md`
- passos_atomicos:
  1. definir um checklist minimo de integridade usando apenas verificacoes coerentes com o PRD e com o ambiente atual
  2. executar essas verificacoes no ambiente recarregado
  3. registrar qualquer divergencia objetiva que impeça a liberacao para F3
  4. manter o resultado vinculado ao dataset recarregado, sem voltar ao PostgreSQL local como fonte ativa
- comandos_permitidos:
  - `rg -n "DATABASE_URL|DIRECT_URL" backend/app/db/database.py backend/.env.example`
- resultado_esperado: checklist de integridade pos-carga executado com conclusao objetiva
- testes_ou_validacoes_obrigatorias:
  - confirmar que o ambiente recarregado responde de forma coerente ao contrato atual do backend
- stop_conditions:
  - parar se as verificacoes mostrarem que o Supabase ainda nao representa o estado local esperado

### T2
- objetivo: confirmar que o caminho de retorno ao backup continua operacionalmente viavel
- precondicoes: T1 concluida; backup do Supabase preservado
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/SUPABASE/PRD-SUPABASE.md`
  - `docs/TROUBLESHOOTING.md`
  - `docs/SETUP.md`
- passos_atomicos:
  1. revisar o procedimento de rollback definido no runbook aprovado
  2. confirmar que o backup ainda esta preservado e utilizavel para um restore, se necessario
  3. validar o caminho de retorno sem executar restore destrutivo quando nao houver falha material
  4. registrar os criterios objetivos que disparariam o rollback
- comandos_permitidos:
  - `pg_restore --help`
- resultado_esperado: procedimento de rollback confirmado como viavel ate o fim da validacao
- testes_ou_validacoes_obrigatorias:
  - confirmar que o backup pode ser inspecionado e permanece disponivel
- stop_conditions:
  - parar se o backup nao estiver mais disponivel ou se o caminho de restore nao puder ser sustentado

### T3
- objetivo: consolidar a saida da fase de dados e liberar a entrada em F3
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `backend/app/db/database.py`
  - `docs/TROUBLESHOOTING.md`
  - `docs/DEPLOY_RENDER_CLOUDFLARE.md`
- passos_atomicos:
  1. resumir o resultado do checklist de integridade e da revisao de rollback
  2. declarar se ha ou nao bloqueios objetivos para validar runtime e cutover em F3
  3. manter o backup preservado enquanto F3 nao concluir com sucesso
  4. liberar a issue apenas quando o Supabase puder ser tratado como fonte de verdade para a validacao final
- comandos_permitidos:
  - `rg -n "Supabase|DATABASE_URL|DIRECT_URL|health" docs/TROUBLESHOOTING.md docs/DEPLOY_RENDER_CLOUDFLARE.md backend/app/db/database.py`
- resultado_esperado: veredito claro de saida da F2 e entrada liberada para F3
- testes_ou_validacoes_obrigatorias:
  - confirmar que nao resta dependencia operacional do PostgreSQL local para validar o backend no Supabase
- stop_conditions:
  - parar se o ambiente ainda exigir retorno imediato ao backup ou se houver divergencia objetiva de integridade

## Arquivos Reais Envolvidos
- `PROJETOS/SUPABASE/PRD-SUPABASE.md`
- `backend/app/db/database.py`
- `backend/.env.example`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/DEPLOY_RENDER_CLOUDFLARE.md`

## Artifact Minimo

Checklist de integridade pos-carga concluido e viabilidade do rollback
confirmada para liberar F3.

## Dependencias
- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F2-02-001](./ISSUE-F2-02-001-Implementar-Recarga-Controlada-de-Dados-no-Supabase.md)
