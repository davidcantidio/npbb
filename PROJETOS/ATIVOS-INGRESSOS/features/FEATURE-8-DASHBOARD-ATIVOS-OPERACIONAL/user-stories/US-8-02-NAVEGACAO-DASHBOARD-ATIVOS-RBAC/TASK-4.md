---
doc_id: "TASK-4.md"
user_story_id: "US-8-02-NAVEGACAO-DASHBOARD-ATIVOS-RBAC"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/pages/dashboard/__tests__/US802DashboardAtivosNavigation.test.tsx"
  - "frontend/src/components/dashboard/__tests__/DashboardLayout.test.tsx"
tdd_aplicavel: true
---

# T4 - Testes automatizados: navegação, RBAC e layout

## objetivo

Cobrir por testes RTL (ou extensão dos testes existentes do módulo dashboard) os critérios Given/When/Then da US: entrada **Ativos** visível com href correto para utilizador autorizado; utilizador não autorizado **não** vê o item; acesso direto à rota de ativos resulta em negativa (redirect ou view de acesso negado) **sem** renderizar o conteúdo da shell de ativos; presença da região principal do dashboard quando autorizado (alinhamento estrutural ao padrão leads).

## precondicoes

- T3 `done`: regra `canAccessDashboardAtivos` (ou equivalente) e guard de rota implementados.
- Ler `frontend/src/components/dashboard/__tests__/DashboardLayout.test.tsx` e `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx` para providers (`MemoryRouter`, `AuthProvider` mock, etc.).

## orquestracao

- `depends_on`: `["T3"]`
- `parallel_safe`: false
- `write_scope`: ficheiros de teste listados; ajustar segundo ficheiro apenas se a estratégia for estender testes existentes em vez de novo ficheiro.

## arquivos_a_ler_ou_tocar

- [TASK-3.md](./TASK-3.md)
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `frontend/src/components/dashboard/__tests__/DashboardLayout.test.tsx`
- `frontend/src/components/ProtectedRoute.tsx` *(padrão de auth em rotas)*

## testes_red

- **testes_a_escrever_primeiro**:
  - Com utilizador **autorizado** mockado: renderizar árvore com `DashboardLayout` + manifesto contendo ativos; assert de link/navegação com `href` igual ao `route` da entrada de ativos.
  - Com utilizador **não autorizado**: assert de que o link para a rota de ativos **não** está presente (queryByRole ou ausência de href).
  - Com utilizador **não autorizado** e rota inicial na URL de ativos: assert de que o conteúdo da shell de ativos (ex.: título ou testid definido na T2) **não** aparece; assert de redirect ou texto de acesso negado conforme implementação da T3.
- **comando_para_rodar**:
  - `cd frontend && npm run test -- US802DashboardAtivosNavigation.test.tsx --run`
  - *(se o ficheiro tiver outro nome, ajustar o padrão do comando)*
- **criterio_red**:
  - Os testes novos falham antes da implementação T3 estar completa; se a T3 já estiver feita, falham até os testes existirem e estarem corretos. Se passarem sem cobrir os critérios, parar e rever asserts.

## passos_atomicos

1. Escrever os testes listados em `testes_red` no ficheiro dedicado (ou estender `DashboardModule.test.tsx` se reduzir duplicação).
2. Rodar o comando red e confirmar falha inicial (ou green se implementação já completa — então validar que os asserts são estritos).
3. Ajustar mocks de `useAuth` / provider para refletir `LoginUser` real (campos mínimos: `tipo_usuario` ou o que a T3 usar).
4. Iterar até green; refatorar helpers de render compartilhados se duplicar muito código com testes existentes.
5. Rodar `cd frontend && npm run test -- --run` se o projeto exigir regressão completa do frontend antes de merge.

## comandos_permitidos

- `cd frontend && npm run test -- US802DashboardAtivosNavigation.test.tsx --run`
- `cd frontend && npm run test -- DashboardModule.test --run`
- `cd frontend && npm run test -- DashboardLayout.test --run`

## resultado_esperado

Suite de testes documenta e protege os critérios de aceite da US-8-02 para navegação e RBAC.

## testes_ou_validacoes_obrigatorias

- Comando(s) de teste acima em verde.
- Nenhum teste a depender de rede ou backend real.

## stop_conditions

- Parar se não for possível mockar auth de forma estável — documentar bloqueio e alinhar com padrão do `AuthProvider` nos testes existentes.
- Parar se os selectors forem frágeis (texto livre) sem `data-testid` acordado — adicionar testid mínimo na shell (T2) com escopo restrito.
