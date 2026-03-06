# EPIC-F1-03 — Experiência Base e Templates Iniciais
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Construir a página de landing dinâmica com seus blocos obrigatórios e habilitar os
dois primeiros templates visuais da solução: `generico` e `corporativo`.

Este épico entrega a primeira experiência ponta a ponta visível ao participante já
presente no evento.

## 2. Contexto Arquitetural
- O PRD define a árvore base de componentes React para a landing
- Todos os templates compartilham blocos invariáveis: hero, form, sobre, footer e sucesso
- O frontend deve enviar leads usando a API existente, associando `event_id` e `ativacao_id`
- A URL pode ser `/landing/ativacoes/{id}` (preferencial) ou `/landing/eventos/{id}` (fallback)

## 3. Riscos e Armadilhas
- Misturar layout base com regras específicas de template e dificultar evolução
- Duplicar componentes entre `generico` e `corporativo`
- Introduzir dependência frágil do backend antes do contrato estabilizar

## 4. Definition of Done do Épico
- [ ] `EventLandingPage` busca dados do evento e seleciona template dinamicamente
- [ ] Template `generico` cobre fallback completo do sistema
- [ ] Template `corporativo` aplica identidade visual e CTA do contexto institucional
- [ ] Submit de lead e tela de sucesso funcionam nas duas variações

---
## Issues

### LPD-F1-03-001 — Construir orquestração da landing page dinâmica
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-002, LPD-F1-02-002

**Descrição:**
Criar a página principal de landing que consome o payload do backend, injeta tokens
de tema e monta os componentes invariáveis definidos no PRD.

**Critérios de Aceitação:**
- [ ] `EventLandingPage` busca dados por `ativacao_id` (rota `/landing/ativacoes/:id`) ou `event_id` (fallback)
- [ ] `ThemeProvider` ou equivalente injeta tokens do template resolvido
- [ ] Componentes base `HeroSection`, `LeadForm`, `EventDetails`, `BrandFooter` e `SuccessScreen` existem e recebem props tipadas

**Tarefas:**
- [ ] T1: Criar rota/página da landing dinâmica
- [ ] T2: Integrar consumo de `GET /ativacoes/{id}/landing` e fallback `GET /eventos/{id}/landing`
- [ ] T3: Criar contexto/adapter de tema para os tokens retornados pela API
- [ ] T4: Implementar estados de carregamento, erro e evento inexistente
- [ ] T5: Escrever testes de renderização básica da página

**Notas técnicas:**
Centralizar a escolha do componente de template na página orquestradora, não dentro
dos blocos compartilhados.

---
### LPD-F1-03-002 — Entregar template genérico com blocos obrigatórios
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-03-001

**Descrição:**
Implementar o fallback visual `generico` com identidade BB neutra, formulário de
captação, seção sobre a ativação/evento e tela de sucesso contextual.

**Critérios de Aceitação:**
- [ ] Hero exibe nome, data, local, imagem e CTA padrão orientado a cadastro/captação
- [ ] Formulário envia para a API existente com `event_id` e `ativacao_id` (quando disponível)
- [ ] Footer exibe links de política/contato e assinatura BB
- [ ] Tela de sucesso usa mensagem da categoria `generico`

**Tarefas:**
- [ ] T1: Implementar layout `generico` com header BB e formulário centralizado
- [ ] T2: Conectar `LeadForm` ao endpoint de submissão existente
- [ ] T3: Implementar estado de sucesso pós-envio
- [ ] T4: Cobrir fluxo feliz e erro de submit com testes frontend

**Notas técnicas:**
O template `generico` é o baseline de todos os demais; priorizar reutilização dos
componentes e estilos compartilhados.

---
### LPD-F1-03-003 — Entregar template corporativo e overrides por evento
**tipo:** feature | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F1-03-002

**Descrição:**
Adicionar a variação `corporativo` com sua paleta e layout hero próprios, respeitando
CTA customizado e hero image específicos do evento quando informados.

**Critérios de Aceitação:**
- [ ] Template `corporativo` possui layout distinto do `generico`
- [ ] `cta_personalizado` substitui CTA padrão quando presente
- [ ] `hero_image_url` do evento prevalece sobre imagem default do tema

**Tarefas:**
- [ ] T1: Implementar variante visual `corporativo`
- [ ] T2: Adaptar `HeroSection` para aceitar override de CTA e imagem
- [ ] T3: Adicionar testes cobrindo defaults e overrides

**Notas técnicas:**
Se a imagem do evento não estiver presente, usar o fallback definido no catálogo do
template, sem quebra visual.

## 5. Notas de Implementação Globais
- Componentes compartilhados devem receber dados prontos para renderização
- Não criar bifurcações de formulário por template nesta fase
