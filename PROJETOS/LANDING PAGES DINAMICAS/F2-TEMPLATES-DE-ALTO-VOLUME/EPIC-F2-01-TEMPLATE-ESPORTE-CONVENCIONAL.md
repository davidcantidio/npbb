# EPIC-F2-01 — Template Esporte Convencional
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Habilitar o template `esporte_convencional` com visual de alta energia, orgulho e
espírito competitivo, preservando a estrutura base criada na F1.

## 2. Contexto Arquitetural
- O template reaproveita a landing base e o catálogo central de tokens
- O PRD pede layout `split`, header azul e destaque para conquistas esportivas
- Eventos esportivos têm grande volume e serão um bom termômetro da solução

## 3. Riscos e Armadilhas
- Hero overload visual prejudicando leitura do formulário
- Quebra de contraste ao combinar azul escuro, amarelo e imagens vibrantes

## 4. Definition of Done do Épico
- [ ] Template `esporte_convencional` renderiza com tokens e layout corretos
- [ ] CTA e mensagens de sucesso refletem o tom esportivo definido no PRD
- [ ] Responsividade e contraste são validados nos breakpoints obrigatórios

---
## Issues

### LPD-F2-01-001 — Implementar hero e composição visual do template esportivo
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Adaptar hero, grafismos e hierarquia visual para o template `esporte_convencional`,
seguindo a especificação da seção 4.2 do PRD.

**Critérios de Aceitação:**
- [ ] Hero usa layout `split`
- [ ] Paleta principal respeita azul escuro, amarelo e branco
- [ ] Grafismos e acentos reforçam energia e conquista sem poluir a leitura

**Tarefas:**
- [ ] T1: Configurar tokens visuais do template no frontend
- [ ] T2: Ajustar `HeroSection` para o layout `split`
- [ ] T3: Validar contraste e legibilidade do conteúdo textual

---
### LPD-F2-01-002 — Ajustar CTA, sucesso e conteúdo contextual do template
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F2-01-001

**Descrição:**
Personalizar texto de CTA, tela de sucesso e detalhes contextuais para eventos
esportivos convencionais em cenários de captação durante a ativação.

**Critérios de Aceitação:**
- [ ] CTA padrão segue o tom "Cadastre-se na ação" / "Quero receber novidades"
- [ ] Mensagem de sucesso é específica da categoria
- [ ] Dados do evento continuam íntegros no fluxo de captação

**Tarefas:**
- [ ] T1: Atualizar cópias padrão da categoria
- [ ] T2: Ajustar `SuccessScreen` para o contexto esportivo
- [ ] T3: Cobrir o fluxo com testes frontend

---
### LPD-F2-01-003 — Validar template esportivo em cenários reais de evento
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-01-002

**Descrição:**
Executar validação funcional e visual do template com eventos de futebol, atletismo e
outras modalidades convencionais.

**Critérios de Aceitação:**
- [ ] Template funciona com pelo menos 3 exemplos de eventos esportivos
- [ ] Não há regressão no formulário e no footer compartilhados
- [ ] Evidência de review visual fica registrada

**Tarefas:**
- [ ] T1: Criar fixtures/mock de eventos esportivos
- [ ] T2: Validar breakpoints 375px, 768px e 1280px
- [ ] T3: Registrar checklist de review visual

## 5. Notas de Implementação Globais
- Priorizar reuso máximo da infraestrutura visual já criada na F1
