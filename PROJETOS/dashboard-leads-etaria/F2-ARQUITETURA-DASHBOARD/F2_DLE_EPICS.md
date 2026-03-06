# Épicos — Dashboard Leads Etária / F2 — Arquitetura Dashboard
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** DASHBOARD-LEADS-ETARIA | **fase:** F2
**prd:** ../PRD_Dashboard_Portfolio.md
**status:** aprovado

---
## Objetivo da Fase
Implementar a arquitetura de navegação do módulo Dashboard no frontend: manifesto de
dashboards, componente `DashboardLayout` com sidebar, `DashboardHome` com seletor
visual de análises (cards) e roteamento protegido por autenticação.

Ao final da fase, o usuário pode acessar `/dashboard`, ver os cards de análises
disponíveis (com "Em breve" para análises futuras) e navegar para o subpainel da
análise etária. A extensibilidade garante que novos dashboards sejam adicionados
apenas inserindo uma entrada no manifesto + componente de página.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Layout e Manifesto de Dashboards | Criar o manifesto, DashboardLayout, DashboardHome e roteamento protegido para o módulo de dashboards. | F1 (backend pronto) | 🔲 | `EPIC-F2-01-LAYOUT-E-MANIFESTO-DASHBOARDS.md` |

## Dependências entre Épicos
`EPIC-F2-01` não tem dependência interna — depende apenas de F1 estar concluída.

## Definition of Done da Fase
- [ ] Manifesto de dashboards definido com ao menos 1 entrada ativa (Análise Etária) e entradas "Em breve"
- [ ] `DashboardLayout` renderiza sidebar de navegação baseada no manifesto
- [ ] `DashboardHome` exibe cards clicáveis em grid de 3 colunas
- [ ] Cards "Em breve" visualmente distintos e não-clicáveis
- [ ] Rota `/dashboard` acessível e protegida por autenticação
- [ ] Rota `/dashboard/leads/analise-etaria` acessível (pode renderizar placeholder até F3)
- [ ] Adicionar nova entrada ao manifesto renderiza card sem alteração de layout
- [ ] Responsividade testada em desktop e mobile

## Notas e Restrições
- Não introduzir biblioteca de state management adicional (usar o que já existe no projeto)
- Seguir padrão visual existente do frontend (Tailwind/componentes do projeto)
- Rotas futuras (`/dashboard/eventos/fechamento`) devem ser reservadas mas não implementadas
