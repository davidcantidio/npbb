---
doc_id: "TASK-5.md"
user_story_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T4"
parallel_safe: false
write_scope: []
tdd_aplicavel: true
---

# TASK-5 - Testes automatizados e validacao final da US

## objetivo

Adicionar cobertura automatizada onde o risco o justifique (componente de fluxo, servico mockado, ou E2E Playwright leve) e fechar a US com `typecheck`, `lint`, `build` e checklist manual dos quatro Given/When/Then do `README.md`, **sem** introduzir scanner/validador no portao.

## precondicoes

- T1 a T4 concluidas ou justificativas documentadas para qualquer desvio inaceitavel.
- Ambiente ou mocks permitem simular sucesso/403 na camada de servico se testes forem isolados.

## orquestracao

- `depends_on`: ["T4"].
- `parallel_safe`: false.
- `write_scope`: vazio por omissao — preferir novos ficheiros de teste sob `frontend/src/**/__tests__/` ou `frontend/e2e/`; correcoes minimas na implementacao apenas se bloquearem criterios de aceite.

## arquivos_a_ler_ou_tocar

- `README.md` desta US
- Modulos tocados em T1-T4
- `frontend/package.json` *(scripts `test`, `test:e2e`)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de componente ou de servico: utilizador sem permissao nao renderiza controlos de emissao **ou** mock de chamada devolve 403 e a UI apresenta estado tratado *(escolher uma estrategia alinhada ao que for mais estavel no repo)*.
  - Opcional: teste que assegura ausencia de rotas/textos que impliquem “scanner no portao” no modulo do fluxo *(assertiva simples em strings ou ausencia de componente)*.
- comando_para_rodar:
  - `cd frontend && npm run test -- --run` *(com filtro de ficheiro se aplicavel)*
- criterio_red:
  - Antes da implementacao de suporte aos testes, o cenario acima deve falhar ou nao compilar ate existir o comportamento coberto.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red) ou falha de compilacao esperada.
3. Ajustar implementacao ou mocks o minimo necessario para green.
4. Rodar `npm run typecheck`, `npm run lint`, `npm run build` no `frontend/`.
5. Se a suite E2E existir e o custo for aceitavel, acrescentar um cenario minimo opcional; caso contrario, registar “E2E nao aplicavel neste corte” na evidencia com justificativa.
6. Percorrer checklist manual dos quatro criterios Given/When/Then no `README.md` da US.

## comandos_permitidos

- `cd frontend && npm run test -- --run`
- `cd frontend && npm run test:e2e` *(opcional)*
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## resultado_esperado

Testes relevantes passando; build verde; US pronta para `SESSION-REVISAR-US.md`.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run` *(com filtro se necessario)*
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- Checklist manual dos criterios no `README.md` da US

## stop_conditions

- Parar se a suite de testes exigir backend indisponivel — preferir testes com `msw` ou mocks de `fetch` ja usados no projeto; se nao existir padrao, documentar e limitar a testes de componente puros.
- Parar se build/typecheck falharem por regressoes pre-existentes nao causadas por T1-T4 — isolar e documentar.
