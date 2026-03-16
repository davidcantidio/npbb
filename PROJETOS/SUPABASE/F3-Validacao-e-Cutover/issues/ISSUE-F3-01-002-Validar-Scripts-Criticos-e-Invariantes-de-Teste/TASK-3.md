---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-01-002-Validar-Scripts-Criticos-e-Invariantes-de-Teste"
task_id: "T3"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-16"
tdd_aplicavel: false
---

# T3 - Consolidar evidencias minimas para a fase documental

## objetivo

Consolidar as evidencias minimas de scripts e testes para a fase documental final.

## precondicoes

- T2 concluida

## arquivos_a_ler_ou_tocar

- `backend/scripts/seed_common.py`
- `backend/app/db/database.py`
- `docs/TROUBLESHOOTING.md`

## passos_atomicos

1. resumir o estado dos scripts criticos e do fallback SQLite
2. registrar os bloqueios objetivos restantes, se existirem
3. sinalizar quais pontos precisam aparecer na issue documental final
4. liberar a issue somente se operacao e testes estiverem coerentes com o novo banco unico

## comandos_permitidos

- `rg -n "DIRECT_URL|DATABASE_URL|sqlite|TESTING" backend/scripts/seed_common.py backend/app/db/database.py docs/TROUBLESHOOTING.md`

## resultado_esperado

Evidencias minimas consolidadas para orientar a documentacao final do projeto.

## testes_ou_validacoes_obrigatorias

- confirmar que nao ha contradicao entre scripts de operacao e fallback de testes

## stop_conditions

- parar se a fase documental nao puder afirmar com seguranca o estado final de operacao e testes
