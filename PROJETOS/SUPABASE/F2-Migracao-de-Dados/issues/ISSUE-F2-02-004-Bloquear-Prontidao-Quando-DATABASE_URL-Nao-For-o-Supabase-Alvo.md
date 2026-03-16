---
doc_id: "ISSUE-F2-02-004-Bloquear-Prontidao-Quando-DATABASE_URL-Nao-For-o-Supabase-Alvo.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-004 - Bloquear prontidao quando DATABASE_URL nao for o Supabase alvo

## User Story

Como operador da migracao, quero que a consolidacao da recarga valide que o
contrato de runtime aponta para o mesmo Supabase alvo da rodada, para evitar
falso positivo de prontidao quando `DATABASE_URL` estiver remota, conectavel e
ainda assim divergente do ambiente recarregado.

## Contexto Tecnico

Esta issue nasce da revisao pos-issue da
`ISSUE-F2-02-003-Endurecer-Contratos-e-Atomicidade-da-Recarga-no-Supabase.md`.

- issue de origem: `ISSUE-F2-02-003`
- evidencia usada na revisao:
  - diff dos commits `890c7cf`, `29fc745`, `7078887`, `f13c035`, `c986162`
  - leitura de `backend/scripts/recarga_migracao.py`
  - leitura de `backend/tests/test_migracao_scripts.py`
  - execucao de `backend/.venv/bin/python -m py_compile backend/scripts/backup_export_migracao.py backend/scripts/recarga_migracao.py`
  - execucao de `cd backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
  - simulacao controlada de `run_consolidacao()` com `DATABASE_URL=postgresql://u:p@db.example.com:5432/otherdb` e `DIRECT_URL` do Supabase, resultando em mensagem de prontidao indevida
- sintoma observado:
  - a consolidacao atual bloqueia apenas `DATABASE_URL` ausente ou local
  - qualquer `DATABASE_URL` remota e conectavel pode ser aceita como "apta para Supabase", mesmo sem apontar para o alvo recarregado
  - a suite atual nao cobre explicitamente o caso de runtime remoto divergente
- risco de nao corrigir:
  - a `ISSUE-F2-02-002` pode iniciar validacao pos-carga sobre um banco diferente do Supabase recarregado
  - o runbook pode induzir o operador a confiar em um sinal de prontidao falso
  - o cutover de F3 pode herdar um contrato de runtime incoerente com o ambiente validado

## Plano TDD

- Red: reproduzir em teste o falso positivo quando `DATABASE_URL` estiver remota e divergente do alvo Supabase
- Green: endurecer a consolidacao para aceitar apenas runtime coerente com o alvo recarregado
- Refactor: consolidar helper(s) de comparacao/normalizacao sem ampliar o escopo do epico

## Criterios de Aceitacao

- Given uma rodada de recarga concluida com `SUPABASE_DIRECT_URL` ou `DIRECT_URL`, When a consolidacao validar `DATABASE_URL`, Then ela so libera a proxima etapa se o runtime apontar para o mesmo alvo Supabase da rodada
- Given uma `DATABASE_URL` remota, conectavel, mas divergente do host/projeto alvo, When a consolidacao rodar, Then ela bloqueia com mensagem objetiva em vez de declarar prontidao
- Given o follow-up concluido, When os testes locais rodarem, Then existe cobertura automatizada para o caso de divergencia entre runtime e manutencao
- Given a documentacao operacional atualizada, When o operador consultar o runbook e o `.env.example`, Then o criterio de prontidao deixa claro que conectividade remota isolada nao basta

## Definition of Done da Issue

- [x] a consolidacao nao aceita `DATABASE_URL` apenas por ser remota e conectavel
- [x] o critero de alinhamento entre runtime e alvo recarregado esta implementado com mensagem de bloqueio objetiva
- [x] testes automatizados cobrem o caso remoto divergente e o caminho de sucesso coerente
- [x] runbook e comentarios minimos nao fazem overclaim sobre prontidao

## Tasks Decupadas

- [x] T1: reproduzir o falso positivo de runtime remoto divergente em teste automatizado
- [x] T2: endurecer a consolidacao para validar alinhamento entre `DATABASE_URL` e o Supabase alvo
- [x] T3: sincronizar runbook e comentarios minimos com o contrato corrigido

## Instructions por Task

### T1
- objetivo: transformar o falso positivo observado na review em teste reproduzivel
- precondicoes: `ISSUE-F2-02-003` concluida; modulo de testes atual compreendido; sem acesso a banco real
- arquivos_a_ler_ou_tocar:
  - `backend/tests/test_migracao_scripts.py`
  - `backend/scripts/recarga_migracao.py`
- passos_atomicos:
  1. adicionar um teste que simule `DATABASE_URL` remota, conectavel e diferente do alvo Supabase usado na recarga
  2. configurar o teste para evidenciar que o comportamento atual libera prontidao indevida
  3. manter o teste isolado por mocks, sem credenciais reais nem operacao destrutiva
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- resultado_esperado: existe um teste vermelho que captura o falso positivo remanescente
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- stop_conditions:
  - parar se a reproducao depender de conexao real ao Supabase ou de heuristica nao deterministica sobre DNS/ambiente

### T2
- objetivo: impedir liberacao quando o runtime nao corresponder ao alvo recarregado
- precondicoes: T1 concluida; criterio de comparacao definido de forma objetiva e local ao script
- arquivos_a_ler_ou_tocar:
  - `backend/scripts/recarga_migracao.py`
  - `backend/tests/test_migracao_scripts.py`
  - `backend/.env.example`
- passos_atomicos:
  1. introduzir normalizacao/comparacao objetiva entre o alvo de manutencao e o alvo de runtime, usando informacao suficiente para distinguir Supabase correto de destino remoto divergente
  2. bloquear a consolidacao quando `DATABASE_URL` nao corresponder ao alvo esperado, mesmo que a conexao responda `SELECT 1`
  3. preservar o caminho de sucesso apenas para runtime coerente com o Supabase recarregado
  4. atualizar ou expandir os testes para cobrir bloqueio por divergencia e sucesso coerente
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
  - `backend/.venv/bin/python -m py_compile backend/scripts/recarga_migracao.py`
- resultado_esperado: a prontidao depende de coerencia real entre runtime e alvo recarregado, nao apenas de conectividade
- testes_ou_validacoes_obrigatorias:
  - `backend/.venv/bin/python -m py_compile backend/scripts/recarga_migracao.py`
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- stop_conditions:
  - parar se a comparacao exigir rediscutir o contrato global de URLs de F3 ou alterar componentes fora do escopo da automacao de migracao

### T3
- objetivo: alinhar a documentacao minima ao contrato corrigido de prontidao
- precondicoes: T2 concluida; criterio final de bloqueio validado pelos testes
- arquivos_a_ler_ou_tocar:
  - `docs/RUNBOOK-MIGRACAO-SUPABASE.md`
  - `backend/.env.example`
  - `backend/scripts/recarga_migracao.py`
- passos_atomicos:
  1. ajustar o runbook para explicitar que `DATABASE_URL` precisa estar alinhada ao mesmo alvo Supabase da recarga
  2. revisar comentarios e mensagens do script para evitar linguagem ambigua sobre "apta para Supabase"
  3. manter a documentacao minima consistente com o comportamento efetivo do script
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- resultado_esperado: documentacao e mensagens refletem o contrato corrigido sem overclaim
- testes_ou_validacoes_obrigatorias:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_migracao_scripts.py`
- stop_conditions:
  - parar se a sincronizacao documental exigir redefinir o runbook completo de F2 ou alterar escopo fora do epico atual

## Arquivos Reais Envolvidos

- `backend/scripts/recarga_migracao.py`
- `backend/tests/test_migracao_scripts.py`
- `backend/.env.example`
- `docs/RUNBOOK-MIGRACAO-SUPABASE.md`

## Artifact Minimo

Consolidacao da recarga bloqueando `DATABASE_URL` remota divergente do
Supabase alvo, com cobertura automatizada local e documentacao minima coerente.

## Dependencias

- [Intake](../../INTAKE-SUPABASE.md)
- [Epic](../EPIC-F2-02-Recarregar-o-Supabase-com-os-Dados-Locais.md)
- [Fase](../F2_SUPABASE_EPICS.md)
- [PRD](../../PRD-SUPABASE.md)
- [ISSUE-F2-02-003](./ISSUE-F2-02-003-Endurecer-Contratos-e-Atomicidade-da-Recarga-no-Supabase.md)
