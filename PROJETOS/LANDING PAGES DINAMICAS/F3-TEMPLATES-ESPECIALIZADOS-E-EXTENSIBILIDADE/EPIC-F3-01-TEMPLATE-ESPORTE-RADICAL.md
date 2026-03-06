# EPIC-F3-01 — Template Esporte Radical
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Entregar o template `esporte_radical` para skate, surfe, BMX e modalidades afins, com
expressão visual de movimento, autenticidade e alta energia.

## 2. Contexto Arquitetural
- O PRD define paleta vibrante, splash visual e hero full-bleed
- Este template exige equilíbrio entre ousadia visual e legibilidade do formulário

## 3. Riscos e Armadilhas
- Exagero de elementos gráficos dificultando leitura e performance
- Visual "radical" conflitando com a identidade institucional BB

## 4. Definition of Done do Épico
- [ ] Template `esporte_radical` respeita a especificação visual do PRD
- [ ] Hero, CTA e sucesso comunicam entusiasmo máximo sem perder clareza
- [ ] Review visual valida o uso da identidade BB no território radical

---
## Issues

### LPD-F3-01-001 — Implementar hero full-bleed do template radical
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Criar a composição hero do template radical com imagem full-bleed, texto sobreposto e
grafismos dinâmicos alinhados ao PRD.

**Critérios de Aceitação:**
- [ ] Hero usa imagem full-bleed com boa legibilidade do texto
- [ ] Paleta vibrante rosa/amarelo/azul é respeitada
- [ ] Badge/modalidade pode ser exibido sem comprometer o CTA

**Tarefas:**
- [ ] T1: Configurar tokens e layout do hero radical
- [ ] T2: Implementar tratamento de sobreposição e contraste
- [ ] T3: Validar performance visual em mobile

---
### LPD-F3-01-002 — Ajustar grafismos e tom de voz do template radical
**tipo:** feature | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-01-001

**Descrição:**
Refinar CTA, mensagem de sucesso e elementos gráficos para comunicar atitude,
comunidade e celebração de performance.

**Critérios de Aceitação:**
- [ ] CTA padrão segue o território radical
- [ ] Mensagem de sucesso comunica entusiasmo e pertencimento
- [ ] Grafismos dinâmicos permanecem consistentes entre hero e blocos de apoio

**Tarefas:**
- [ ] T1: Ajustar catálogo textual da categoria radical
- [ ] T2: Refinar grafismos de apoio no layout
- [ ] T3: Cobrir o fluxo com testes e revisão visual

---
### LPD-F3-01-003 — Validar template radical com eventos de skate e surfe
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-01-002

**Descrição:**
Executar validação funcional e visual do template com eventos representativos de
esporte radical.

**Critérios de Aceitação:**
- [ ] Template funciona com eventos de skate e surfe
- [ ] Layout preserva conversão e responsividade
- [ ] Evidência de aceite visual fica registrada

**Tarefas:**
- [ ] T1: Criar fixtures de eventos radicais
- [ ] T2: Validar breakpoints obrigatórios
- [ ] T3: Registrar aceite visual

## 5. Notas de Implementação Globais
- Reutilizar a estrutura base; especialização deve vir de tema e composição, não de
  nova árvore de componentes
