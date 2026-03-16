---
doc_id: "TASK-N.md"
issue_id: "ISSUE-F<N>-<NN>-<MMM>-<slug>"
task_id: "T<N>"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
tdd_aplicavel: false
---

# TASK-N - <titulo breve da task>

## objetivo

## precondicoes

## arquivos_a_ler_ou_tocar

- `caminho/para/arquivo`

## testes_red

> Preencher esta secao apenas quando `tdd_aplicavel: true`.

- testes_a_escrever_primeiro:
  - teste ou cenario que deve falhar antes da implementacao
- comando_para_rodar:
  - `comando de teste red`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

> Se `tdd_aplicavel: true`, use a ordem abaixo.
> Se `tdd_aplicavel: false`, substitua por passos especificos da task.

1. Escrever os testes listados em `testes_red`
2. Rodar os testes e confirmar falha inicial (red)
3. Implementar o codigo minimo necessario para passar
4. Rodar os testes e confirmar sucesso (green)
5. Refatorar se necessario mantendo a suite green

## comandos_permitidos

- `comando permitido`

## resultado_esperado

## testes_ou_validacoes_obrigatorias

- validacao final obrigatoria

## stop_conditions

- parar se ...
