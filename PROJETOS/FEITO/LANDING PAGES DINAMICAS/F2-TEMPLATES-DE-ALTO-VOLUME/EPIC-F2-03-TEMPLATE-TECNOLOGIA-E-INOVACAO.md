# EPIC-F2-03 — Template Tecnologia e Inovação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Entregar o template `tecnologia` com identidade de inovação, comunidade tech e
otimismo tecnológico, aplicável a hackathons, demo days e eventos de startups.

## 2. Contexto Arquitetural
- O PRD define fundo escuro com gradiente azul-verde e elementos de grid/circuito
- O template deve compartilhar estrutura com os anteriores, variando tokens e composição

## 3. Riscos e Armadilhas
- Excesso de efeitos visuais afetando performance e legibilidade
- Estética "tech" genérica demais, sem aderência à marca BB

## 4. Definition of Done do Épico
- [ ] Template `tecnologia` está funcional e visualmente aderente ao PRD
- [ ] Efeitos visuais não degradam a meta de performance da landing
- [ ] CTA e sucesso reforçam cadastro na ativação e vínculo com inovação

---
## Issues

### LPD-F2-03-001 — Implementar identidade visual do template tecnologia
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Criar a variação visual do template tecnologia com gradientes, grid e linguagem de
comunidade tech, mantendo contraste e performance sob controle.

**Critérios de Aceitação:**
- [ ] Hero usa a composição prevista para tecnologia
- [ ] Paleta azul-claro, verde-claro e azul-escuro é respeitada
- [ ] Elementos gráficos não comprometem legibilidade nem carregamento

**Tarefas:**
- [ ] T1: Configurar tokens do template tecnologia
- [ ] T2: Aplicar grafismos e background coerentes com o PRD
- [ ] T3: Verificar contraste e custo visual do template

---
### LPD-F2-03-002 — Adaptar CTA e mensagem de sucesso para eventos tech
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-03-001

**Descrição:**
Ajustar os textos de ação e resposta pós-envio para o contexto de eventos de inovação,
hackathons e encontros de comunidade, assumindo que o participante já está no local.

**Critérios de Aceitação:**
- [ ] CTA padrão usa tom "Cadastre-se para acompanhar" / "Quero receber novidades"
- [ ] Mensagem de sucesso reforça empoderamento e continuidade do relacionamento
- [ ] Overrides de CTA por evento continuam respeitados

**Tarefas:**
- [ ] T1: Atualizar catálogo textual da categoria tecnologia
- [ ] T2: Validar fluxo de sucesso com eventos de exemplo
- [ ] T3: Cobrir comportamento com testes frontend

---
### LPD-F2-03-003 — Validar template tecnologia com foco em responsividade
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-03-002

**Descrição:**
Executar validação funcional e visual do template em diferentes breakpoints e perfis
de evento de tecnologia.

**Critérios de Aceitação:**
- [ ] Template funciona com hackathon, demo day e meetup tech
- [ ] Layout mantém leitura e CTA visível em 375px, 768px e 1280px
- [ ] Evidência de review visual fica registrada

**Tarefas:**
- [ ] T1: Criar fixtures para eventos de tecnologia
- [ ] T2: Validar responsividade e contraste
- [ ] T3: Registrar resultado do review visual

## 5. Notas de Implementação Globais
- Preservar a assinatura BB; "tech" não pode virar um tema desconectado da marca
