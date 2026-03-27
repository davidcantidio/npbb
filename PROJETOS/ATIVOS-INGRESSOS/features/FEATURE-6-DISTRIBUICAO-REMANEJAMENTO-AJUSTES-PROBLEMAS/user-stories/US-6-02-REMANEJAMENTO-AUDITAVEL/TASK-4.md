---
doc_id: "TASK-4.md"
user_story_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/pages/IngressosPortal.tsx"
  - "frontend/src/services/ingressos.ts"
  - "frontend/src/services/ingressos_admin.ts"
tdd_aplicavel: false
---

# T4 - UI operacional: remanejamento e auditoria

## objetivo

Evoluir a superficie do portal/admin de ingressos para o operador **executar remanejamento** com rotulagem clara que **nao confunda** com fluxo de aumento/reducao de previsao (risco do manifesto FEATURE-6), capturar **motivo** quando a API indicar obrigatoriedade (422/400 da T2 ou metadados de configuracao expostos por endpoint de politica, se existir), e **listar/navegar** historico de remanejamentos consumindo a API da T3.

## precondicoes

- TASK-2 e TASK-3 `done`: contratos JSON e codigos de erro estaveis documentados no OpenAPI.
- Padroes de UI existentes em `IngressosPortal` e servicos `ingressos.ts` / `ingressos_admin.ts` lidos pelo executor.

## orquestracao

- `depends_on`: `["T2", "T3"]`.
- `parallel_safe`: `false`.
- `write_scope`: apenas ficheiros listados no frontmatter (componentes extraidos sob o mesmo diretorio `pages/` se necessario, declarar no PR da task).

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/IngressosPortal.tsx`
- `frontend/src/services/ingressos.ts`
- `frontend/src/services/ingressos_admin.ts`
- Rotas e layout existentes do modulo de ativos *(para navegacao coerente)*
- OpenAPI gerada a partir do backend apos T2/T3

## passos_atomicos

1. Mapear endpoints e tipos TypeScript para POST de remanejamento e GET de listagem (alinhados a T2/T3).
2. Implementar formulario ou fluxo em passos com labels explicitas **Remanejamento** (nao “ajuste de previsao”).
3. Exibir campo motivo condicionalmente: obrigatorio quando configuracao/politica assim exigir; mostrar erros da API de forma acessivel.
4. Implementar painel ou tabela de historico com colunas origem, destino, quantidade, data/hora, ator, motivo; linkagem ou detalhe expandivel para navegacao da cadeia conforme payload da T3.
5. Garantir estados de carregamento e vazio; respeitar RBAC (desabilitar acoes se 403).

## comandos_permitidos

- `cd frontend && npm run build`
- `cd frontend && npm run lint` *(se configurado no repo)*

## resultado_esperado

Operador consegue registrar remanejamento auditavel pela UI e revisar historico no mesmo contexto de evento, alinhado aos criterios de aceitacao da US.

## testes_ou_validacoes_obrigatorias

- `npm run build` sem erro.
- Teste manual: fluxo feliz, fluxo bloqueado sem motivo quando politica ativa, listagem apos registo.

## stop_conditions

- Parar se API nao expuser campo ou header que permita ao front saber se motivo e obrigatorio — retornar T2/T3 para contrato minimo antes de UI condicional.
- Parar se design system nao tiver padrao para fluxos destrutivos — escalar UX sem improvisar padroes fora do restante portal.
