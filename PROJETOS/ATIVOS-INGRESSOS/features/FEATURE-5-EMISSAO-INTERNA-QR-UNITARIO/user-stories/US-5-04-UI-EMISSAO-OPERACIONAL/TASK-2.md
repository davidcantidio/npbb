---
doc_id: "TASK-2.md"
user_story_id: "US-5-04-UI-EMISSAO-OPERACIONAL"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/pages/IngressosPortal.tsx"
  - "frontend/src/app/AppRoutes.tsx"
tdd_aplicavel: false
---

# TASK-2 - Entrada do fluxo operador e gating RBAC na superficie `/ingressos`

## objetivo

Garantir que utilizadores **com** permissao de operador acedem ao fluxo de emissao interna com QR na superficie acordada (`/ingressos` ou sub-rota/modulo dedicado alinhado ao PRD 4.0), e que utilizadores **sem** permissao nao veem controlos de emissao nem entram em estados ambiguos — cumprindo o terceiro Given/When/Then da US (erro ou ausencia de UI consistente).

## precondicoes

- T1 concluida: funcoes de emissao disponiveis no servico para ligacao nas tasks seguintes.
- [US-5-02](../../US-5-02-SERVICO-E-API-EMISSAO/README.md) define ou implica semantica de autorizacao (403/401) reutilizavel na UI.
- Criterio de “operador” ou papel equivalente identificavel no frontend (token, claims, ou endpoint de contexto ja existente no portal).

## orquestracao

- `depends_on`: ["T1"] *(o cliente de emissao deve existir antes de acoplar o fluxo completo; o gating visual pode ser esbocado antes, mas esta task fecha a entrada integrada)*.
- `parallel_safe`: false.
- `write_scope`: rotas e shell do portal de ingressos; nao duplicar logica de auth — reutilizar padroes de `IngressosPortal` (BB vs admin).

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/IngressosPortal.tsx`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/ingressos_admin.ts` *(consumo futuro; apenas leitura se necessario para papel)*
- `README.md` desta US *(criterios RBAC)*

## passos_atomicos

1. Definir o ponto de entrada UX: secao, separador ou rota (ex. `?tab=` ou `Route` filho) para “Emissao interna / QR” visivel apenas ao perfil operador.
2. Implementar renderizacao condicional: sem permissao, nao mostrar botoes/formulario de emissao; em tentativas de navegacao directa, mostrar estado vazio ou mensagem alinhada ao design system existente no portal.
3. Tratar respostas 403/401 das chamadas de contexto ou listagens relacionadas de forma consistente com o restante `IngressosPortal` (mensagem amigavel, sem detalhes internos).
4. Nao introduzir scanner nem validacao no portao (criterio explicito da US).

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Superficie clara para o operador iniciar o fluxo; superficie sem controlos de emissao para quem nao tem permissao.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck`
- Verificacao manual: utilizador sem permissao nao ve controlos de emissao; operador ve entrada para o fluxo.

## stop_conditions

- Parar se o criterio de papel operador nao estiver definido no frontend nem derivavel do token — escalar decisao de produto antes de inventar heuristica.
