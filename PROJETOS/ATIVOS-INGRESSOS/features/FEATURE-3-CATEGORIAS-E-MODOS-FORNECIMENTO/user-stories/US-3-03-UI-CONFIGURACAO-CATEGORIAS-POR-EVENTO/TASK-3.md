---
doc_id: "TASK-3.md"
user_story_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/pages/AtivosList.tsx"
  - "frontend/src/store/auth.tsx"
tdd_aplicavel: false
---

# TASK-3 - RBAC e feedback de erro na UI de configuracao

## objetivo

Garantir que utilizadores sem permissao para alterar configuracao nao tenham acoes de gravacao disponiveis de forma clara, ou que tentativas resultem em mensagem compreensivel alinhada a API (403/401 e detalhes), cumprindo o segundo criterio Given/When/Then da US e a coerencia com [US-3-02](../../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md).

## precondicoes

- T2 concluida: fluxo de configuracao e chamadas a API funcionais para utilizadores autorizados.
- Contrato US-3-02 documentando quem pode escrever (ou comportamento exclusivamente via 403 na gravacao).

## orquestracao

- `depends_on`: ["T2"].
- `parallel_safe`: false.
- `write_scope`: UI de ativos; `auth.tsx` apenas se for necessario expor um campo ja existente no `LoginUser` para decisao de UI — evitar alargar o modelo de auth sem necessidade; preferir desabilitar com base em flag da API ou em `tipo_usuario` ja exposto, se o projeto assim documentar.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/AtivosList.tsx`
- `frontend/src/services/auth.ts` *(interface `LoginUser`)*
- `frontend/src/store/auth.tsx` *(hook `useAuth`)*
- `frontend/src/services/ativos.ts` *(tratamento de erro nas chamadas da T1)*

## passos_atomicos

1. Confirmar com o contrato US-3-02 se existe sinal previo de permissao (ex. campo no `LoginUser` ou endpoint GET que indica `can_configure`) ou se a UI deve confiar apenas na resposta 403 na gravacao.
2. Se houver sinal previo: ocultar ou desabilitar botoes de gravacao e exibir texto explicativo para utilizadores sem permissao.
3. Se nao houver sinal previo: manter leitura visivel se permitida pela API; na gravacao, mapear 403/401 para mensagem amigavel reutilizando ou estendendo `getFriendlyErrorMessage` em `AtivosList.tsx` quando o erro vier das novas chamadas.
4. Garantir que erros 4xx de validacao (subset invalido) tambem aparecam de forma legivel, sem vazar detalhes internos desnecessarios.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## resultado_esperado

Utilizador sem permissao nao consegue alterar configuracao de forma ambigua; falhas de autorizacao e validacao sao claras na UI.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run build`
- Teste manual com perfil sem permissao (ou simulacao de 403) e com perfil autorizado.

## stop_conditions

- Parar se a US-3-02 nao definir comportamento de permissao testavel (falta de criterio objetivo).
- Parar se for necessario novo endpoint exclusivamente para descoberta de permissao — tratar como dependencia de produto/backend antes de implementar.
