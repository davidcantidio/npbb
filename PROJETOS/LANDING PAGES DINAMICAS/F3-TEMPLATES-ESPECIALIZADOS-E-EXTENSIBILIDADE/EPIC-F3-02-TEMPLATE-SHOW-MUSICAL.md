# EPIC-F3-02 — Template Show Musical
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Entregar o template `show_musical` com atmosfera noturna, vibrante e emocional para
shows, concertos e festivais.

## 2. Contexto Arquitetural
- O PRD define gradiente roxo, partículas e destaque de título em fundo dark
- Este template precisa equilibrar espetáculo visual e ação clara de cadastro

## 3. Riscos e Armadilhas
- Hero excessivamente escuro prejudicando contraste do CTA
- Efeitos de partículas degradando performance

## 4. Definition of Done do Épico
- [ ] Template `show_musical` aplica o visual noturno previsto
- [ ] CTA e sucesso reforçam emoção e captação durante a experiência no evento
- [ ] Performance e acessibilidade permanecem dentro do baseline aceitável

---
## Issues

### LPD-F3-02-001 — Implementar visual dark-overlay do template musical
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Construir o hero e a identidade visual do template musical com fundo escuro, gradiente
roxo e elementos visuais inspirados em palco e luz.

**Critérios de Aceitação:**
- [ ] Hero usa composição dark-overlay
- [ ] Paleta roxo/rosa/amarelo é respeitada
- [ ] CTA permanece visualmente destacado no cenário noturno

**Tarefas:**
- [ ] T1: Configurar tokens do template musical
- [ ] T2: Implementar background e hierarquia do hero
- [ ] T3: Validar contraste e legibilidade

---
### LPD-F3-02-002 — Ajustar CTA e sucesso para contexto de espetáculo
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-02-001

**Descrição:**
Personalizar mensagens de ação e sucesso para o contexto de shows e festivais,
mantendo tom acolhedor e entusiasmado para um público já presente no evento.

**Critérios de Aceitação:**
- [ ] CTA padrão segue "Cadastre-se na experiência" / "Quero receber novidades"
- [ ] Mensagem de sucesso é coerente com o contexto musical
- [ ] Overrides por evento continuam funcionando

**Tarefas:**
- [ ] T1: Atualizar textos padrão da categoria musical
- [ ] T2: Validar fluxo de sucesso do template
- [ ] T3: Cobrir cenários com CTA default e personalizado

---
### LPD-F3-02-003 — Validar template musical em eventos de show e festival
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-02-002

**Descrição:**
Executar testes e review visual com exemplos reais de concertos e festivais para
garantir aderência da experiência.

**Critérios de Aceitação:**
- [ ] Template funciona com show, concerto e festival
- [ ] Layout preserva clareza do formulário em todos os breakpoints
- [ ] Evidência de aceite visual fica registrada

**Tarefas:**
- [ ] T1: Criar fixtures para eventos musicais
- [ ] T2: Validar responsividade do template
- [ ] T3: Registrar review visual

## 5. Notas de Implementação Globais
- O template deve transmitir atmosfera, mas sem virar uma exceção técnica fora da
  biblioteca de temas
