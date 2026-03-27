---
doc_id: "TASK-5.md"
user_story_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T4"
parallel_safe: false
write_scope: []
tdd_aplicavel: false
---

# TASK-5 - Validacao final da US (build, regressao minima, checklist de aceite)

## objetivo

Fechar a US com validacoes objetivas: compilacao, lint/typecheck, execucao opcional da suite de testes do frontend se existir cobertura relevante, e checklist manual cobrindo os tres Given/When/Then do `README.md` da US, sem alargar escopo funcional.

## precondicoes

- T1 a T4 concluidas ou justificativas documentadas para qualquer cancelamento parcial inaceitavel (nao aplicavel se a US exige entrega completa).

## orquestracao

- `depends_on`: ["T4"].
- `parallel_safe`: false.
- `write_scope`: vazio — apenas comandos e revisao; correcoes minimas descobertas nesta task devem limitar-se a bugs que impedem criterios de aceite.

## arquivos_a_ler_ou_tocar

- `README.md` desta user story *(criterios de aceite)*
- Ficheiros alterados nas tasks T1-T4 *(apenas se correcao pontual for necessaria)*

## passos_atomicos

1. Executar `npm run typecheck` e `npm run lint` no diretorio `frontend/`.
2. Executar `npm run build` no diretorio `frontend/`.
3. Se existirem testes Vitest que cubram modulos tocados, executar `npm run test -- --run` com filtro adequado; caso nao existam testes para ativos, registar "nao aplicavel" na evidencia e nao bloquear por ausencia de suite dedicada.
4. Percorrer checklist manual: (a) persistencia e refresco do subset; (b) utilizador sem permissao; (c) distincao categoria/modo.
5. Preparar notas breves para o handoff de revisao na US (commits, limitacoes).

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- `cd frontend && npm run test -- --run` *(opcional, com filtro se aplicavel)*

## resultado_esperado

Suite de validacoes documentada com resultados; US pronta para `SESSION-REVISAR-US.md` conforme fluxo do projeto.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- Checklist manual dos criterios Given/When/Then no `README.md` da US

## stop_conditions

- Parar se build ou typecheck falharem — corrigir apenas regressoes introduzidas pelo conjunto FEATURE-3/US-3-03; se falha for pre-existente, documentar e isolar.
