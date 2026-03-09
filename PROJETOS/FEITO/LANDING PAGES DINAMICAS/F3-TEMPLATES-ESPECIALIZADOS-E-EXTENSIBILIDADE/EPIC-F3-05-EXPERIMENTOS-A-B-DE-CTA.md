# EPIC-F3-05 — Experimentos A/B de CTA
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Habilitar experimentos A/B controlados de CTA por categoria para otimizar captação de
leads nas ativações sem perder aderência ao tom de voz e à governança da marca BB.

## 2. Contexto Arquitetural
- O PRD prevê testes A/B entre variações de CTA por categoria
- Analytics da F3 fornece a base para leitura dos resultados
- CTAs precisam continuar restritos a variantes homologadas e orientadas a cadastro

## 3. Riscos e Armadilhas
- Randomização inconsistente entre sessões e eventos
- Variantes não homologadas prejudicarem marca, clareza ou contexto de ativação

## 4. Definition of Done do Épico
- [ ] É possível ativar variantes homologadas de CTA por categoria
- [ ] Exposição e captação por variante são mensuráveis
- [ ] Governança impede testes com mensagens fora do tom aprovado

---
## Issues

### LPD-F3-05-001 — Definir catálogo homologado de variantes de CTA
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Formalizar quais CTAs podem participar de experimentos por categoria, preservando tom
de voz, clareza de cadastro e aderência à marca BB.

**Critérios de Aceitação:**
- [ ] Cada categoria possui variantes aprovadas de CTA
- [ ] Não é possível cadastrar texto arbitrário para experimento A/B
- [ ] Catálogo fica disponível para consumo do experimento

**Tarefas:**
- [ ] T1: Consolidar variantes homologadas por categoria
- [ ] T2: Registrar restrições de uso por template
- [ ] T3: Expor catálogo para frontend/backoffice

---
### LPD-F3-05-002 — Implementar distribuição e tracking de variantes
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F3-05-001, LPD-F3-04-002

**Descrição:**
Implementar a lógica que seleciona uma variante de CTA elegível e registra exposição e
resultado para posterior comparação no contexto da captação em evento.

**Critérios de Aceitação:**
- [ ] Variantes são distribuídas de forma determinística ou controlada
- [ ] Evento analítico de exposição da variante é registrado
- [ ] Submit de lead preserva a informação da variante exibida

**Tarefas:**
- [ ] T1: Definir estratégia de randomização/segmentação
- [ ] T2: Aplicar variante ao CTA renderizado
- [ ] T3: Registrar exposição e captação por variante

---
### LPD-F3-05-003 — Disponibilizar leitura comparativa dos experimentos
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-05-002

**Descrição:**
Oferecer visão comparativa básica para que produto e marketing identifiquem qual CTA
performou melhor em cada categoria durante as ativações.

**Critérios de Aceitação:**
- [ ] Captação por variante pode ser comparada
- [ ] Resultado é segmentável por categoria/template
- [ ] Encerramento de experimento pode ser baseado em evidência disponível

**Tarefas:**
- [ ] T1: Consolidar métrica comparativa por variante
- [ ] T2: Exibir ou documentar leitura do resultado
- [ ] T3: Validar interpretação com stakeholders

## 5. Notas de Implementação Globais
- Experimento A/B deve ser o menor incremento possível sobre a base de analytics da F3
