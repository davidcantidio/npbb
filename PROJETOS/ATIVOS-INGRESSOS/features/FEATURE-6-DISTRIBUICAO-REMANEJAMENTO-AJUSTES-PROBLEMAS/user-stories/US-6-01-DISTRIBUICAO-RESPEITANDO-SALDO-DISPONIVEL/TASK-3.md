---
doc_id: "TASK-3.md"
user_story_id: "US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/pages/IngressosPortal.tsx"
  - "frontend/src/services/ingressos.ts"
  - "frontend/src/services/ingressos_admin.ts"
tdd_aplicavel: false
---

# TASK-3 - UI portal e admin: confirmar distribuicao e erros de saldo

## objetivo

Expor ao operador o fluxo de **confirmacao de distribuicao** consumindo a API da
TASK-2: em caso de saldo insuficiente, mostrar mensagem clara (AC1); em sucesso,
refletir estado alinhado ao contrato (`distribuido` / feedback de conclusao)
(AC2), reutilizando padroes de erro ja presentes em
`IngressosPortal.tsx` (`getFriendlyErrorMessage` / `parseErrorDetail`).

## precondicoes

- [TASK-2](./TASK-2.md) `done`: endpoint e payloads estaveis *(documentar path
  e shape no corpo desta task na execucao)*.
- Build frontend existente (`npm run dev`) validado localmente.

## orquestracao

- `depends_on`: `["T2"]`.
- `parallel_safe`: `false`.
- `write_scope`: pagina portal e clientes HTTP de ingressos; evitar tocar em
  rotas nao relacionadas.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md)
- `frontend/src/pages/IngressosPortal.tsx`
- `frontend/src/services/ingressos.ts`
- `frontend/src/services/ingressos_admin.ts` *(se o fluxo operacional for na
  superficie admin)*
- Contrato OpenAPI ou tipos TypeScript gerados se existirem

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Definir com base na TASK-2 o verbo, URL e payload do cliente HTTP em
   `ingressos.ts` ou `ingressos_admin.ts` *(funcao dedicada, ex.\
   `confirmarDistribuicao`)*.
2. Integrar na UI: formulario ou passo de confirmacao com quantidade e
   destinatario conforme API; desabilitar envio durante request; tratar 4xx com
   mensagem amigavel.
3. Em sucesso, invalidar caches locais ou refetch de listas que mostram saldo /
   estado para o operador ver consistencia.
4. Ajustar copy e acessibilidade (labels, `aria-*`) no minimo aceitavel do
   projeto.
5. Verificar regressao visual rapida nos fluxos existentes de solicitacao de
   ingressos na mesma pagina.

## comandos_permitidos

- `cd frontend && npm run build`
- `cd frontend && npm run lint` *(se configurado)*

## resultado_esperado

Operador consegue concluir ou ver bloqueio de distribuicao pela UI, coerente
com os tres criterios da US ao nivel de experiencia.

## testes_ou_validacoes_obrigatorias

- Teste manual: caminho feliz e caminho saldo insuficiente contra backend local.
- `npm run build` sem erros de TypeScript.

## stop_conditions

- Parar se a API da TASK-2 nao expuser erro estruturado consumivel pelo
  frontend — retornar TASK-2 para ajuste de contrato.
- Parar se o fluxo de distribuicao for exclusivamente admin e ainda nao existir
  rota/superficie — alinhar com PM antes de criar pagina nova fora do escopo da
  US.
