# EPIC-F2-02 — Template Evento Cultural
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Entregar o template `evento_cultural` para exposições, teatro, cinema e experiências
CCBB, com caráter editorial e tom mais contemplativo.

## 2. Contexto Arquitetural
- O PRD define paleta clara, tipografia marcante e layout editorial
- Eventos culturais exigem mais ênfase em conteúdo, programação e imagem do acervo

## 3. Riscos e Armadilhas
- Excesso de estética editorial comprometer conversão do formulário
- Conteúdo cultural longo quebrar a hierarquia de leitura no mobile

## 4. Definition of Done do Épico
- [ ] Template `evento_cultural` aplica o layout editorial previsto
- [ ] Hero, detalhes e CTA mantêm equilíbrio entre informação e captação
- [ ] Seção sobre o evento suporta conteúdo cultural mais rico sem regressão

---
## Issues

### LPD-F2-02-001 — Implementar layout editorial do template cultural
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Criar a variação visual do template cultural com tipografia destacada, paleta clara e
composição adequada para eventos de exposição, teatro e CCBB.

**Critérios de Aceitação:**
- [ ] Hero usa layout `editorial`
- [ ] Paleta segue roxo claro, verde e branco conforme PRD
- [ ] Conteúdo principal preserva legibilidade e contraste AA

**Tarefas:**
- [ ] T1: Configurar tokens do template cultural
- [ ] T2: Ajustar estilos do hero e títulos com enfoque editorial
- [ ] T3: Testar legibilidade em mobile e desktop

---
### LPD-F2-02-002 — Adaptar bloco "Sobre o Evento" para agenda cultural
**tipo:** feature | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-02-001

**Descrição:**
Adequar o bloco de detalhes para suportar descrição expandida, programação resumida e
chamadas mais curatoriais sem perder o foco em captação.

**Critérios de Aceitação:**
- [ ] Bloco suporta descrição curta e programação resumida do evento
- [ ] CTA permanece visível sem competir com o conteúdo
- [ ] Template acomoda diferentes volumes de texto sem quebrar layout

**Tarefas:**
- [ ] T1: Ajustar `EventDetails` para conteúdos culturais mais extensos
- [ ] T2: Definir comportamento responsivo para blocos textuais
- [ ] T3: Cobrir cenários com descrição curta e longa

---
### LPD-F2-02-003 — Validar tom de voz e sucesso do template cultural
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-02-002

**Descrição:**
Garantir que CTA, mensagem de sucesso e revisão visual expressem atenção e simpatia,
em linha com a escala de serotonina prevista para o contexto cultural.

**Critérios de Aceitação:**
- [ ] CTA padrão segue o posicionamento "Cadastre-se para saber mais" / "Quero receber novidades"
- [ ] Mensagem de sucesso é coerente com o território cultural
- [ ] Review visual aprova o uso do template em contexto CCBB

**Tarefas:**
- [ ] T1: Ajustar cópias padrão e mensagens do template
- [ ] T2: Executar validação visual com eventos culturais de exemplo
- [ ] T3: Registrar evidências de aceite

## 5. Notas de Implementação Globais
- O template cultural deve privilegiar clareza e elegância sem introduzir novos
  componentes exclusivos se a base puder ser reutilizada
