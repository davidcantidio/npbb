# EPIC-F1-02 — Resolução de Template e Tokens Visuais
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Implementar a lógica central que decide qual categoria visual deve ser usada para
cada evento e traduz essa decisão em tokens de tema consumíveis pelo frontend.

Este épico é o núcleo de extensibilidade do projeto: novas categorias devem poder ser
adicionadas sem modificar a orquestração principal da landing page.

## 2. Contexto Arquitetural
- O PRD define prioridade de resolução: override, subtipo, tipo, keywords, fallback
- O frontend precisa consumir um objeto de tema, não regras de negócio
- Templates futuros da F2/F3 dependem do mesmo catálogo de tokens

## 3. Riscos e Armadilhas
- Regras de categorização espalhadas em múltiplos arquivos dificultando manutenção
- Keywords ambíguas gerando classificação inesperada
- Tokens incompletos levando a inconsistências visuais entre templates

## 4. Definition of Done do Épico
- [ ] Serviço central resolve categoria e tema com as 5 prioridades do PRD
- [ ] Registro de templates expõe tokens visuais e textos padrão por categoria
- [ ] Cobertura automatizada valida fallback e extensibilidade

---
## Issues

### LPD-F1-02-001 — Criar serviço de resolução de categoria do evento
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-001

**Descrição:**
Implementar serviço de domínio responsável por resolver a categoria visual do evento
com base no fluxo de prioridade especificado na seção 5.1 do PRD.

**Critérios de Aceitação:**
- [ ] Respeita a prioridade `template_override` -> `subtipo_evento` -> `tipo_evento` -> keywords -> `generico`
- [ ] Eventos com dados incompletos ainda resolvem uma categoria válida
- [ ] Regras ficam centralizadas em um único serviço reutilizável

**Tarefas:**
- [ ] T1: Definir enum ou type-safe registry para categorias suportadas
- [ ] T2: Implementar mapeamentos de subtipo e tipo
- [ ] T3: Implementar heurística simples por keywords no `nome_evento`
- [ ] T4: Cobrir cenários de sucesso e fallback com testes unitários

**Notas técnicas:**
Evitar NLP pesado; a heurística deve ser simples, determinística e fácil de ajustar.

---
### LPD-F1-02-002 — Criar registro central de tokens e mensagens por template
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-02-001

**Descrição:**
Definir uma fonte de verdade única para tokens visuais, layout hero, variante de CTA
e mensagens padrão de sucesso por categoria.

**Critérios de Aceitação:**
- [ ] Existe um registro central para todas as categorias previstas no PRD
- [ ] Cada categoria expõe cores, `heroLayout`, `graphicsStyle`, `toneOfVoice` e CTA padrão
- [ ] `generico` cobre eventos não classificados sem campos nulos críticos

**Tarefas:**
- [ ] T1: Criar estrutura de dados para tokens de tema
- [ ] T2: Popular tokens para `generico`, `corporativo`, `esporte_convencional`, `evento_cultural`, `tecnologia`, `esporte_radical` e `show_musical`
- [ ] T3: Definir mensagem de sucesso e CTA default por categoria
- [ ] T4: Expor helper para consumo pelos endpoints de landing

**Notas técnicas:**
Mesmo categorias entregues em fases futuras devem estar registradas desde já para
evitar condicionais espalhadas no código.

---
### LPD-F1-02-003 — Validar extensibilidade e consistência da resolução
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F1-02-002

**Descrição:**
Criar suíte de testes que congele o comportamento da engine e reduza regressão ao
adicionar novas categorias ou alterar palavras-chave.

**Critérios de Aceitação:**
- [ ] Testes cobrem todos os fluxos de prioridade do PRD
- [ ] Testes falham quando uma categoria registrada não possui tokens completos
- [ ] Adição de nova categoria exige alterar apenas o registro central e os testes

**Tarefas:**
- [ ] T1: Criar matriz de casos para override, subtipo, tipo, keyword e fallback
- [ ] T2: Criar teste de integridade do registro de templates
- [ ] T3: Documentar ponto único de extensão para novas categorias

**Notas técnicas:**
Esses testes serão a base para as entregas de F2 e F3, quando novos templates forem
efetivamente habilitados no frontend.

## 5. Notas de Implementação Globais
- Resolver categoria é regra de negócio; renderizar tokens é responsabilidade de
  camada de apresentação
- Não permitir lógica de categorização diretamente em componentes React
