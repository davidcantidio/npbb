---
doc_id: "TASK-3.md"
user_story_id: "US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "frontend/src/components/dashboard/DashboardLayout.tsx"
  - "frontend/src/components/dashboard/DashboardSidebar.tsx"
  - "frontend/src/store/auth.tsx"
  - "frontend/src/services/auth.ts"
  - "frontend/src/app/AppRoutes.tsx"
tdd_aplicavel: false
---

# T3 - RBAC: visibilidade na sidebar e bloqueio de rota direta

## objetivo

Cumprir os critérios da US: utilizador **sem** permissão para o dashboard de ativos **não** vê a entrada no menu; ao aceder diretamente à URL da rota de ativos, o sistema **nega** acesso de forma consistente com o módulo Dashboard (sem vazar dados agregados — mensagem genérica ou redirect como no resto da app). Utilizador **com** permissão mantém navegação e shell.

## precondicoes

- T2 `done`: rota e página shell existem.
- Mapear critério de autorização: alinhar a **utilizador interno NPBB** (espelho de `UsuarioTipo.NPBB` / `require_npbb_user` no backend) salvo regra já documentada noutro módulo do frontend para o Dashboard. Ler `frontend/src/services/auth.ts` (`LoginUser`, `tipo_usuario`) e padrões de guarda em rotas internas (ex.: comparação de string com valor API).

## orquestracao

- `depends_on`: `["T2"]`
- `parallel_safe`: false
- `write_scope`: componentes de dashboard, auth se precisar de helper partilhado, e rota guardada em `AppRoutes` se a estratégia for wrapper de `Route`.

## arquivos_a_ler_ou_tocar

- [README.md](README.md)
- `frontend/src/components/dashboard/DashboardLayout.tsx`
- `frontend/src/components/dashboard/DashboardSidebar.tsx`
- `frontend/src/config/dashboardManifest.ts` *(leitura — filtrar entradas em runtime, não duplicar manifesto)*
- `frontend/src/store/auth.tsx`, `frontend/src/services/auth.ts`
- `frontend/src/app/AppRoutes.tsx`
- Referência backend: `backend/app/platform/security/rbac.py` *(apenas critério conceitual; endpoints de ativos podem vir na US-8-01)*

## passos_atomicos

1. Definir função pura ou hook (ex.: `canAccessDashboardAtivos(user: LoginUser | null): boolean`) com regra explícita documentada num comentário curto (ex.: apenas `tipo_usuario === "npbb"` — **ajustar ao valor real** devolvido pela API).
2. Filtrar entradas passadas ao `DashboardSidebar`: ou filtrar `DASHBOARD_MANIFEST` no `DashboardLayout` antes de `createPortal`, ou ler `useAuth` dentro do sidebar e ocultar entradas do domínio `ativos` quando não autorizado.
3. Proteger rota direta: wrapper `Navigate` para `/dashboard` ou página “acesso negado” já existente no projeto — **reutilizar** padrão encontrado com `rg`/leitura de `AppRoutes` e páginas similares; nunca renderizar a shell de ativos nem disparar fetch de dados para utilizador não autorizado.
4. Garantir que `enabled: false` no manifesto **não** seja a única defesa (link oculto mas URL acessível falha o critério da US).
5. Documentar no PR de implementação a regra escolhida para revisão de produto.

## comandos_permitidos

- `cd frontend && npm run build`
- `rg`, `git diff`

## resultado_esperado

Comportamento de autorização alinhado à US: menu condicional + deep link bloqueado sem leak de conteúdo sensível.

## testes_ou_validacoes_obrigatorias

- Testes automatizados ficam na T4; aqui validar manualmente dois utilizadores (ou mocks): autorizado vê entrada e shell; não autorizado não vê entrada e URL de ativos redireciona/nega.

## stop_conditions

- **Parar** se não existir valor estável em `LoginUser` para distinguir quem pode ver o dashboard de ativos além do texto da US — pedir decisão explícita de PM/PO antes de codificar.
- Parar se a única opção for inventar permissão nova no backend fora de escopo desta US — documentar dependência e bloquear.
