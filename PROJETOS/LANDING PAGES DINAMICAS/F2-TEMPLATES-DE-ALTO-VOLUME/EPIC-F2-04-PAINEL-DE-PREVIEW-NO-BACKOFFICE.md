# EPIC-F2-04 — Painel de Preview no Backoffice
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Criar uma experiência de preview no backoffice NPBB para que operadores possam
validar o template resolvido e seus principais elementos antes do uso da URL na
ativação presencial.

## 2. Contexto Arquitetural
- O PRD prevê preview de template na F2
- O endpoint `template-config` da F1 foi desenhado para suportar esse caso
- O preview deve usar dados reais do evento, não mocks locais

## 3. Riscos e Armadilhas
- Preview divergir da landing real por usar outra fonte de dados
- Duplicar lógica de resolução de template no frontend administrativo

## 4. Definition of Done do Épico
- [ ] Backoffice exibe preview fiel do template resolvido por evento
- [ ] Operador consegue validar hero, CTA, paleta e blocos principais
- [ ] Preview trata estados de dados faltantes e fallback de categoria

---
## Issues

### LPD-F2-04-001 — Expor preview de template por evento no backoffice
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-003

**Descrição:**
Adicionar tela ou painel no backoffice que consulte a ativação (ou evento) e mostre
o template resolvido com os principais elementos visuais e de conteúdo.

**Critérios de Aceitação:**
- [ ] Operador consegue abrir preview a partir de uma ativação ou evento existente
- [ ] Preview usa os endpoints reais do projeto
- [ ] Estados de loading, erro e fallback são tratados

**Tarefas:**
- [ ] T1: Criar rota/componente de preview no backoffice
- [ ] T2: Integrar leitura de `template-config` e/ou `landing`
- [ ] T3: Exibir hero, CTA, título e principais tokens do template

---
### LPD-F2-04-002 — Comparar preview e landing usada na ativação
**tipo:** test | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-04-001

**Descrição:**
Criar verificação para garantir que o preview apresentado ao operador reflita a mesma
configuração aplicada à landing final do evento.

**Critérios de Aceitação:**
- [ ] Preview e landing compartilham a mesma categoria resolvida
- [ ] Diferenças de CTA, hero e paleta são detectáveis em teste
- [ ] Não existe lógica duplicada de resolução no backoffice

**Tarefas:**
- [ ] T1: Criar testes de integração entre preview e landing
- [ ] T2: Validar cenários com override e fallback
- [ ] T3: Documentar limites conhecidos do preview

---
### LPD-F2-04-003 — Sinalizar checklist mínimo de ativação
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-04-002

**Descrição:**
Adicionar ao preview sinais mínimos para o operador confirmar se a landing está pronta
para uso em campo: imagem, CTA, categoria, política e tagline.

**Critérios de Aceitação:**
- [ ] Preview sinaliza campos críticos ausentes ou inconsistentes
- [ ] Operador visualiza checklist mínimo antes de usar a URL na ativação
- [ ] Itens do checklist são alinhados ao PRD e ao guia operacional

**Tarefas:**
- [ ] T1: Definir lista mínima de validações do preview
- [ ] T2: Exibir estado ok/pendente para cada item
- [ ] T3: Cobrir casos com dados incompletos

## 5. Notas de Implementação Globais
- O preview não substitui a landing publicada, mas precisa ser fiel o suficiente para
  revisão operacional
