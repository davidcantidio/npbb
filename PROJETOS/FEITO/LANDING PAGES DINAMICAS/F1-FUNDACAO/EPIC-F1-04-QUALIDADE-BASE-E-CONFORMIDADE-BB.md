# EPIC-F1-04 — Qualidade Base e Conformidade BB
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Garantir que a experiência base entregue na F1 já nasce aderente aos requisitos
mínimos de acessibilidade, privacidade, performance e identidade de marca.

Este épico fecha a fundação com critérios verificáveis antes da expansão para os
templates de alto volume da F2.

## 2. Contexto Arquitetural
- O PRD impõe WCAG 2.1 AA, consentimento LGPD e metas de performance
- Os elementos invariáveis da landing devem ser compatíveis com todos os templates
- O checklist de marca BB é gate de aceite antes do deploy

## 3. Riscos e Armadilhas
- Ajustar acessibilidade apenas no fim e acumular retrabalho nos templates seguintes
- Consentimento LGPD tratado apenas visualmente, sem bloqueio real de envio
- Otimizações de performance dependerem de decisões tardias de arquitetura

## 4. Definition of Done do Épico
- [ ] Formulário atende requisitos mínimos de acessibilidade e consentimento
- [ ] Baseline de performance do template base é mensurada
- [ ] Checklist de marca BB está operacional para review do time de marca

---
## Issues

### LPD-F1-04-001 — Acessibilidade e LGPD no formulário base
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-03-002

**Descrição:**
Adequar o formulário de leads aos requisitos mínimos de acessibilidade e privacidade,
incluindo labels visíveis, navegação por teclado e consentimento LGPD obrigatório.

**Critérios de Aceitação:**
- [ ] Todos os campos têm label visível e atributos acessíveis adequados
- [ ] Fluxo completo do formulário é navegável por teclado
- [ ] Checkbox de consentimento LGPD bloqueia submissão quando não marcado
- [ ] CPF e telefone não são persistidos em `localStorage` ou `sessionStorage`

**Tarefas:**
- [ ] T1: Revisar markup e estados de foco do formulário
- [ ] T2: Adicionar bloco de consentimento com link para política de privacidade
- [ ] T3: Validar navegação por teclado e mensagens de erro acessíveis
- [ ] T4: Criar testes de interação/accessibility smoke tests

**Notas técnicas:**
Priorizar mensagens de erro claras e associadas semanticamente aos campos.

---
### LPD-F1-04-002 — Baseline de performance da landing base
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-03-003

**Descrição:**
Aplicar otimizações iniciais de carregamento e definir a estratégia executável para
atingir os requisitos de LCP, CLS e code splitting da landing.

**Critérios de Aceitação:**
- [ ] Hero image usa estratégia responsiva compatível com WebP/lazy loading quando aplicável
- [ ] Bundle da landing é separado do bundle principal
- [ ] Existe evidência mensurável do baseline de LCP/CLS para o template base
- [ ] Estratégia de SSR/SSG fica registrada como implementada ou formalmente decidida

**Tarefas:**
- [ ] T1: Configurar code splitting da rota de landing
- [ ] T2: Ajustar carregamento de imagens do hero
- [ ] T3: Executar medição inicial de performance com Lighthouse
- [ ] T4: Registrar decisão técnica sobre SSR/SSG para as landings

**Notas técnicas:**
Se SSR/SSG não entrar nesta issue, registrar decisão aprovada para viabilizar a F2
sem ambiguidade arquitetural.

---
### LPD-F1-04-003 — Checklist de marca e aceite visual da fase
**tipo:** docs | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F1-04-001, LPD-F1-04-002

**Descrição:**
Converter o checklist de conformidade do PRD em um artefato operacional para validar
os templates base com design/brand antes do encerramento da fase.

**Critérios de Aceitação:**
- [ ] Checklist contempla todos os itens obrigatórios da seção 07 do PRD
- [ ] Existe evidência de review para `generico` e `corporativo`
- [ ] Critérios reusáveis ficam preparados para os templates futuros

**Tarefas:**
- [ ] T1: Criar checklist operacional de revisão visual
- [ ] T2: Validar `generico` e `corporativo` contra o checklist
- [ ] T3: Registrar pendências ou ajustes de marca, se houver

**Notas técnicas:**
Este artefato deve ser reutilizado na F2 e F3, evitando interpretação subjetiva por
template.

## 5. Notas de Implementação Globais
- A fase só fecha após evidência objetiva de qualidade, não apenas com os componentes
  renderizando
- Qualquer desvio de marca ou privacidade exige registro formal de decisão
