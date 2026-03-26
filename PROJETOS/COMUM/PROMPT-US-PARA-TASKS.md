---
doc_id: "PROMPT-US-PARA-TASKS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# Prompt Canonico - User Story para Tasks

## Como usar

Cole este prompt numa sessao com acesso ao repositorio e informe:

- o caminho do manifesto da User Story: `.../user-stories/US-<N>-<NN>-<NOME>/README.md`
- (opcional) restricoes do executor: stack, ramos, ou ordem desejada entre tasks

## Prompt

Voce e um engenheiro responsavel por decompor **uma User Story** em **Tasks** executaveis, como ficheiros `TASK-<N>.md` (ou checklist no proprio README apenas quando o projeto ainda usar formato legado explicitamente permitido).

Principios de trabalho:

- **task** e a menor unidade operacional para execucao; **instructions** atomicas seguem `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`
- respeite **no maximo 5 tasks por User Story** (`GOV-USER-STORY.md`)
- quando `task_instruction_mode: required`, cada task deve ter **ficheiro proprio** `TASK-N.md` com os campos minimos obrigatorios
- quando `optional`, ainda assim prefira `TASK-N.md` se houver mais de uma task ou qualquer risco de ambiguidade
- TDD: use `tdd_aplicavel` e `testes_red` conforme `TEMPLATE-TASK.md` e `SPEC-TASK-INSTRUCTIONS.md`

### Leitura obrigatoria

1. siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1 e 2, quando aplicavel
2. leia o `README.md` da User Story na integra (narrativa, criterios Given/When/Then, dependencias, `task_instruction_mode`)
3. leia o `FEATURE-<N>.md` de origem e trechos relevantes do `PRD-<PROJETO>.md` apenas para contexto — **nao** reabra escopo da US
4. use `PROJETOS/COMUM/GOV-USER-STORY.md` para limites e elegibilidade
5. use `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md` para modo `required`/`optional` e campos minimos por task
6. use `PROJETOS/COMUM/TEMPLATE-TASK.md` como estrutura obrigatoria de cada `TASK-N.md`
7. use `PROJETOS/COMUM/GOV-COMMIT-POR-TASK.md` se precisar alinhar expectativa de commit por task com o texto das tasks

### Passagem 1 - Prontidao da US

Antes de escrever tasks:

- confirme que a US tem criterios de aceite **testaveis ou verificaveis**
- confirme dependencias a outras USs: se uma US predecessora nao estiver `done`, declare `BLOQUEADO` em vez de assumir ordem
- se `task_instruction_mode: required` e a US ainda nao tiver espaco estruturado para tasks em ficheiros, planeie a criacao dos `TASK-*.md` correspondentes
- decida se cada task precisa de `tdd_aplicavel: true` com base nos fatores de risco em `SPEC-TASK-INSTRUCTIONS.md` e `GOV-USER-STORY.md`

Se a US estiver ambigua ou sem criterios suficientes:

- decisao: `BLOQUEADO`
- liste o que falta para desdobrar com seguranca

### Passagem 2 - Geracao das Tasks

So execute se a passagem 1 nao estiver bloqueada.

- crie `TASK-1.md` ... `TASK-K.md` (K <= 5) na mesma pasta que o `README.md` da US
- cada ficheiro deve seguir `TEMPLATE-TASK.md`, com `issue_id` / identificadores alinhados ao projeto (use o ID da US ou convencao local documentada no README)
- preencha `objetivo`, `precondicoes`, `arquivos_a_ler_ou_tocar`, `passos_atomicos`, `comandos_permitidos`, `resultado_esperado`, `testes_ou_validacoes_obrigatorias`, `stop_conditions`
- quando `tdd_aplicavel: true`, preencha `testes_red` **antes** de `passos_atomicos`
- atualize a secao **Tasks** do `README.md` da US com links relativos para cada `TASK-N.md`
- garanta ordem logica entre tasks (T1 antes de T2 quando houver dependencia) e que nenhuma task misture entregas de outra US

### Requisitos minimos da saida

- no maximo **5** tasks por US
- coerencia total entre o texto da US (Given/When/Then) e o somatorio das tasks
- `task_instruction_mode` respeitado: se `required`, **nenhuma** task pode ficar apenas como bullet vago no README sem `TASK-N.md`

### Regra final

Se uma task precisar de decisao de produto ou de escopo nao presente na US, **pare** e devolva `BLOQUEADO` com perguntas objetivas — nao alargue escopo silenciosamente.
