# Épicos — Ajuste Fino Landing Pages Dinâmicas / F3 — Gamificação Integrada
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F3
**prd:** ../PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md
**status:** aprovado

---
## Objetivo da Fase
Implementar o componente `GamificacaoBlock` com máquina de estados
(`PRESENTING → ACTIVE → COMPLETED`), integrar ao `LandingPageView` com
gerenciamento de estado `leadSubmitted` / `ativacaoLeadId`, e conectar ao endpoint
de conclusão de gamificação do backend.

Ao final da fase, a landing page exibe o bloco de gamificação desde o carregamento
(quando disponível), habilita participação após submit do formulário, registra
conclusão via API e suporta reset completo para nova pessoa.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Componente GamificacaoBlock e Máquina de Estados | Criar componente com estados PRESENTING/ACTIVE/COMPLETED, props tipadas e transições controladas. | nenhuma | 🔲 | `EPIC-F3-01-COMPONENTE-GAMIFICACAO-BLOCK.md` |
| EPIC-F3-02 | Integração Gamificação no LandingPageView | Integrar GamificacaoBlock ao LandingPageView, gerenciar estado leadSubmitted/ativacaoLeadId, conectar ao endpoint de gamificação e implementar reset. | EPIC-F3-01 | 🔲 | `EPIC-F3-02-INTEGRACAO-GAMIFICACAO-LANDING-VIEW.md` |

## Dependências entre Épicos
`EPIC-F3-01` → `EPIC-F3-02`

O EPIC-F3-02 depende do componente `GamificacaoBlock` criado no EPIC-F3-01.
Ambos dependem da F2 estar concluída (endpoint de gamificação disponível).

## Definition of Done da Fase
- [ ] Componente `GamificacaoBlock` renderiza card com nome, descrição e prêmio da gamificação
- [ ] Botão "Quero participar" desabilitado antes do submit, com texto de orientação visível
- [ ] Botão habilitado após submit bem-sucedido do formulário
- [ ] Transição `PRESENTING → ACTIVE` funcional (requer `leadSubmitted=true` + clique)
- [ ] Transição `ACTIVE → COMPLETED` funcional (clique em "Concluí" + chamada API)
- [ ] `POST /ativacao-leads/{id}/gamificacao` disparado ao concluir
- [ ] Feedback (`titulo_feedback` + `texto_feedback`) exibido no estado COMPLETED
- [ ] Reset completo ("Nova pessoa") limpa formulário e retorna bloco para PRESENTING
- [ ] Bloco não renderizado quando `data.gamificacoes.length === 0`
- [ ] Serviço `completeGamificacao()` implementado no frontend
- [ ] Tipos `GamificacaoCompletePayload` e `GamificacaoCompleteResponse` definidos

## Notas e Restrições
- O componente é montado pelo pai apenas quando `gamificacoes.length > 0` — sem estado `IDLE` interno
- Modelo 1:1 ativação-gamificação — bloco exibe card único, sem dropdown
- O endpoint de gamificação é público — frontend não precisa de token
- `ativacao_lead_id` vem da response do submit e é passado ao serviço de conclusão
