---
doc_id: "TASK-N.md"
user_story_id: "US-<N>-<NN>-<slug>"
task_id: "T<N>"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "YYYY-MM-DD"
depends_on: []
parallel_safe: false
write_scope: []
tdd_aplicavel: false
---

# TASK-N - <titulo breve da task>

## objetivo

## precondicoes

## orquestracao

- `depends_on`: liste `T<N>` que precisam estar `done` antes desta task
- `parallel_safe`: use `true` apenas quando a task puder rodar em paralelo sem
  conflito documental ou de codigo
- `write_scope`: liste caminhos, modulos ou superfícies concretas tocadas pela
  task; se `parallel_safe: true`, esta lista deve ser especifica o suficiente
  para detectar conflito

> Regras canônicas:
> - task com qualquer item de `depends_on` ainda aberto e `BLOQUEADO`
> - `parallel_safe: true` com `write_scope: []`, generico ou ambiguo e
>   `BLOQUEADO`

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
