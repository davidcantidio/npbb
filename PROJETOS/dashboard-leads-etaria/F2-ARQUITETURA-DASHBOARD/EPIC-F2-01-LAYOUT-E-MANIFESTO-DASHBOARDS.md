# EPIC-F2-01 — Layout e Manifesto de Dashboards
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Criar a infraestrutura frontend do módulo Dashboard: um manifesto declarativo de análises
disponíveis, o componente de layout com sidebar de navegação, a página seletora
(`DashboardHome`) com cards visuais e o roteamento protegido por autenticação. O design
segue o princípio de extensibilidade zero-change: novos dashboards são adicionados apenas
via manifesto + componente de página.

## 2. Contexto Arquitetural
- Frontend React + Vite com Tailwind CSS
- Roteamento via React Router (padrão do projeto)
- Autenticação JWT existente — reusar guards/hooks já implementados
- Estrutura de páginas em `frontend/src/pages/`
- Componentes reutilizáveis em `frontend/src/components/`
- Novo módulo: `frontend/src/components/dashboard/` e `frontend/src/pages/dashboard/`

## 3. Riscos e Armadilhas
- Sidebar de navegação do dashboard pode conflitar com sidebar/menu global da aplicação
- Cards "Em breve" devem ser visualmente distintos sem parecer "quebrados"
- Roteamento aninhado (`/dashboard/*`) deve coexistir com rotas existentes sem conflito

## 4. Definition of Done do Épico
- [ ] Manifesto tipado com entradas para análises (ativa + "Em breve")
- [ ] `DashboardLayout` com sidebar funcional baseada no manifesto
- [ ] `DashboardHome` com grid de cards clicáveis/não-clicáveis
- [ ] Rotas `/dashboard` e `/dashboard/leads/analise-etaria` protegidas e funcionais
- [ ] Extensibilidade validada: nova entrada no manifesto = novo card sem alterar layout

---
## Issues

### DLE-F2-01-001 — Criar manifesto de dashboards no frontend
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Definir o manifesto declarativo de dashboards como array tipado em TypeScript. Cada
entrada define: id, rota, domínio, nome da análise, ícone, descrição curta e flag
`enabled`. O manifesto é a fonte de verdade para navegação, cards e sidebar.

**Critérios de Aceitação:**
- [ ] Tipo `DashboardManifestEntry` definido com campos: `id`, `route`, `domain`, `name`, `icon`, `description`, `enabled`
- [ ] Array `DASHBOARD_MANIFEST` com ao menos 3 entradas: Análise Etária (enabled), Fechamento de Evento (disabled), Conversão por Evento (disabled)
- [ ] Manifesto exportado de módulo dedicado (`frontend/src/config/dashboardManifest.ts`)
- [ ] Tipo e array cobertos por teste unitário de shape

**Tarefas:**
- [ ] T1: Criar tipo `DashboardManifestEntry` em `frontend/src/types/dashboard.ts`
- [ ] T2: Criar manifesto em `frontend/src/config/dashboardManifest.ts`
- [ ] T3: Popular manifesto com entradas conforme PRD (seção 1.1)
- [ ] T4: Escrever teste de shape do manifesto

**Notas técnicas:**
O ícone pode ser string referenciando componente de ícone (Lucide, Heroicons) ou
nome de ícone — seguir padrão do projeto.

---
### DLE-F2-01-002 — Implementar DashboardLayout com sidebar de navegação
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F2-01-001

**Descrição:**
Criar o componente `DashboardLayout` que envolve todas as páginas do módulo dashboard.
Inclui sidebar de navegação renderizada a partir do manifesto, com links para análises
habilitadas e itens desabilitados para análises futuras.

**Critérios de Aceitação:**
- [ ] Componente `DashboardLayout` renderiza sidebar + área de conteúdo (Outlet)
- [ ] Sidebar lista todas as entradas do manifesto com ícone e nome
- [ ] Entradas com `enabled: true` são links navegáveis com destaque de rota ativa
- [ ] Entradas com `enabled: false` aparecem esmaecidas com tooltip "Em breve"
- [ ] Layout responsivo: sidebar colapsa em mobile (hambúrguer ou drawer)
- [ ] Componente não conflita com a navegação global da aplicação

**Tarefas:**
- [ ] T1: Criar componente `frontend/src/components/dashboard/DashboardLayout.tsx`
- [ ] T2: Implementar sidebar com iteração sobre manifesto
- [ ] T3: Implementar destaque de rota ativa via `useLocation()`
- [ ] T4: Implementar comportamento responsivo (mobile)
- [ ] T5: Estilizar com Tailwind seguindo padrão visual do projeto

---
### DLE-F2-01-003 — Implementar DashboardHome (seletor visual de análises)
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F2-01-001

**Descrição:**
Criar a página `DashboardHome` que renderiza na rota `/dashboard`. Exibe cards
clicáveis em grid de 3 colunas, um por entrada no manifesto. Cards habilitados
navegam para a análise; cards desabilitados exibem badge "Em breve" e são
não-clicáveis.

**Critérios de Aceitação:**
- [ ] Página renderiza na rota `/dashboard`
- [ ] Grid de 3 colunas com cards para cada entrada do manifesto
- [ ] Cards habilitados: clicáveis, com ícone, nome, descrição e hover effect
- [ ] Cards desabilitados: badge "Em breve", opacidade reduzida, cursor default
- [ ] Grid responsivo: 1 coluna em mobile, 2 em tablet, 3 em desktop
- [ ] Título da página: "Dashboard" ou "Painel de Análises"

**Tarefas:**
- [ ] T1: Criar página `frontend/src/pages/dashboard/DashboardHome.tsx`
- [ ] T2: Criar componente de card `DashboardCard.tsx`
- [ ] T3: Implementar grid responsivo com Tailwind
- [ ] T4: Implementar estados de card (enabled/disabled) com badge "Em breve"
- [ ] T5: Conectar click dos cards à navegação via React Router

---
### DLE-F2-01-004 — Configurar rotas /dashboard/* e proteção de autenticação
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** DLE-F2-01-002, DLE-F2-01-003

**Descrição:**
Configurar o roteamento aninhado para o módulo dashboard (`/dashboard/*`), integrar
com o `DashboardLayout` e aplicar guard de autenticação JWT para proteger todas as
rotas do módulo.

**Critérios de Aceitação:**
- [ ] Rota `/dashboard` renderiza `DashboardHome` dentro de `DashboardLayout`
- [ ] Rota `/dashboard/leads/analise-etaria` renderiza componente placeholder (até F3)
- [ ] Rotas do dashboard protegidas por guard de autenticação existente
- [ ] Acesso sem autenticação redireciona para login
- [ ] Rota inexistente dentro de `/dashboard/*` exibe 404 ou redireciona para `/dashboard`
- [ ] Link para "Dashboard" adicionado ao menu/navegação principal da aplicação

**Tarefas:**
- [ ] T1: Configurar rotas aninhadas em `frontend/src/App.tsx` ou arquivo de rotas
- [ ] T2: Aplicar guard de autenticação ao grupo `/dashboard/*`
- [ ] T3: Criar componente placeholder para `/dashboard/leads/analise-etaria`
- [ ] T4: Adicionar link "Dashboard" ao menu de navegação principal
- [ ] T5: Testar navegação: autenticado e não-autenticado

**Notas técnicas:**
Reusar o guard de autenticação existente no projeto (verificar implementação atual
em `frontend/src/`). Não criar novo mecanismo de auth.

## 5. Notas de Implementação Globais
- A arquitetura deve ser genérica o suficiente para acomodar dashboards de qualquer
  domínio (leads, eventos, publicidade) sem alteração no layout
- Evitar acoplamento entre o manifesto e componentes específicos de análise
- O manifesto é configuração estática — não vem da API nesta versão
