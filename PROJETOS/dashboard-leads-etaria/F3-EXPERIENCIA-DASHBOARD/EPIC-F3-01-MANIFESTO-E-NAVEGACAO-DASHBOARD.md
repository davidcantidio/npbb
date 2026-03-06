---
doc_id: "EPIC-F3-01-MANIFESTO-E-NAVEGACAO-DASHBOARD"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F3-01 - Manifesto e Navegacao Dashboard

## Objetivo

Criar o manifesto configuravel de dashboards, a Home do portfolio em `/dashboard` e a reserva de rotas futuras, permitindo adicionar novas analises sem alterar o layout raiz.

## Resultado de Negocio Mensuravel

O produto ganha um portfolio de dashboards extensivel, com descoberta visual das analises disponiveis e preparacao explicita para trilhas futuras como fechamento e conversao.

## Definition of Done

- Existe um manifesto frontend que descreve dominio, rota, nome, icone e `enabled` de cada dashboard.
- `/dashboard` deixa de redirecionar diretamente para `/dashboard/leads` e passa a renderizar a Home com cards.
- Cards `enabled=false` aparecem como "Em breve" e nao navegam.
- O menu superior do layout consegue apontar para a Home do portfolio e para a analise etaria ativa.

## Issues

### DLE-F3-01-001 - Introduzir manifesto configuravel do portfolio
Status: todo

**User story**
Como pessoa desenvolvedora do frontend, quero um manifesto unico de dashboards para cadastrar novas analises sem reabrir o layout raiz a cada entrega.

**Plano TDD**
1. `Red`: usar `frontend/src/test/setup.ts` com o padrao de `frontend/src/pages/__tests__/EventoPages.smoke.test.tsx` para falhar quando o portfolio nao conseguir renderizar uma lista de cards a partir de configuracao declarativa.
2. `Green`: criar o manifesto e ligar `frontend/src/main.tsx` e `frontend/src/components/layout/AppLayout.tsx` a essa fonte unica de navegacao.
3. `Refactor`: extrair icones, labels e flags `enabled` para um modulo de configuracao de dashboard desacoplado das paginas concretas.

**Criterios de aceitacao**
- Given uma nova entrada ativa no manifesto, When a Home do dashboard e renderizada, Then um novo card clicavel aparece sem alteracao estrutural do layout.
- Given uma entrada desabilitada, When a Home e exibida, Then o card mostra "Em breve" e nao dispara navegacao.

### DLE-F3-01-002 - Criar a Home do portfolio em `/dashboard`
Status: todo

**User story**
Como pessoa usuaria autenticada, quero entrar em `/dashboard` e ver as analises disponiveis em um painel visual para escolher o recorte que desejo explorar.

**Plano TDD**
1. `Red`: ajustar a montagem de rotas em `frontend/src/main.tsx` para falhar enquanto `/dashboard` continuar redirecionando automaticamente para `/dashboard/leads`.
2. `Green`: criar a Home do portfolio e substituir o redirect por uma pagina com cards, mantendo `ProtectedRoute` e `AppLayout`.
3. `Refactor`: alinhar a estrutura da Home com os componentes e espacos do layout atual para permitir novas linhas de cards sem redesign.

**Criterios de aceitacao**
- Given usuario autenticado, When acessa `/dashboard`, Then a interface mostra ao menos o card ativo "Analise Etaria por Evento".
- Given cards futuros cadastrados, When a Home carrega, Then eles aparecem em grade de tres colunas ou layout responsivo equivalente.

### DLE-F3-01-003 - Reservar rotas futuras sem expor implementacoes incompletas
Status: todo

**User story**
Como pessoa dona do produto, quero manter as trilhas futuras visiveis no portfolio sem entregar paginas quebradas ou clicaveis antes da hora.

**Plano TDD**
1. `Red`: ampliar a configuracao de `frontend/src/main.tsx` e a navegacao de `frontend/src/components/layout/AppLayout.tsx` para falhar quando rotas futuras ficarem acessiveis como se estivessem prontas.
2. `Green`: reservar as rotas futuras com componentes de placeholder coerentes ou bloqueio por `enabled=false`, sem quebrar a navegacao principal.
3. `Refactor`: padronizar a representacao de status de disponibilidade para que Home e menu usem a mesma logica.

**Criterios de aceitacao**
- Given a trilha `dashboard/eventos/fechamento` marcada como futura, When o usuario olha o portfolio, Then ela aparece como indisponivel e sem promessa falsa de dado carregavel.
- Given a analise etaria ativa, When o usuario navega pelo menu, Then a rota funcional continua destacada independentemente das trilhas reservadas.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f3/epic-f3-01-manifesto-e-navegacao-dashboard.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
