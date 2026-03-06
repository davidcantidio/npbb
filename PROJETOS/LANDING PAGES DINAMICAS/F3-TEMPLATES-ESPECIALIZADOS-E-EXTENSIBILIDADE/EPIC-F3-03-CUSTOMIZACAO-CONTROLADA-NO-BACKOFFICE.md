# EPIC-F3-03 — Customização Controlada no Backoffice
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Permitir customizações controladas de hero, CTA e conteúdo no backoffice, mantendo a
governança de marca e evitando deriva visual entre eventos.

## 2. Contexto Arquitetural
- O PRD prevê interface de criação de template customizado no backoffice
- O projeto já possui `template_override`, `cta_personalizado` e `hero_image_url`
- É preciso distinguir customização segura de editor visual irrestrito

## 3. Riscos e Armadilhas
- Transformar o backoffice em construtor livre e quebrar o framework visual
- Permitir combinações de cores/elementos que violem marca BB

## 4. Definition of Done do Épico
- [ ] Operador consegue customizar campos permitidos sem alterar a estrutura do template
- [ ] Regras de governança impedem combinações fora do catálogo homologado
- [ ] Preview reflete imediatamente a customização aplicada

---
## Issues

### LPD-F3-03-001 — Definir superfície permitida de customização
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Formalizar e implementar quais aspectos do template podem ser customizados por evento
sem aprovação extraordinária: imagem hero, CTA, descrição curta e seleção de template.

**Critérios de Aceitação:**
- [ ] Campos customizáveis são explicitamente definidos
- [ ] Não é possível alterar tokens fora do catálogo homologado
- [ ] Restrições ficam visíveis no backoffice

**Tarefas:**
- [ ] T1: Mapear campos liberados para customização
- [ ] T2: Implementar validações de backend/frontend
- [ ] T3: Exibir orientações de uso no backoffice

---
### LPD-F3-03-002 — Implementar fluxo de customização com preview imediato
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F3-03-001

**Descrição:**
Adicionar ao backoffice um fluxo seguro para editar os campos permitidos e revisar o
resultado no preview antes do uso da landing na ativação.

**Critérios de Aceitação:**
- [ ] Operador altera CTA, hero e descrição curta sem sair do fluxo
- [ ] Preview reflete as alterações persistidas
- [ ] Regras inválidas são bloqueadas com feedback claro

**Tarefas:**
- [ ] T1: Criar formulário de customização no backoffice
- [ ] T2: Persistir alterações via API de eventos
- [ ] T3: Revalidar preview após salvar
- [ ] T4: Cobrir fluxo com testes de integração

---
### LPD-F3-03-003 — Registrar trilha de governança das customizações
**tipo:** docs | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-03-002

**Descrição:**
Garantir rastreabilidade das customizações aplicadas e documentar o processo para
auditoria operacional.

**Critérios de Aceitação:**
- [ ] Existe registro dos campos customizados por evento
- [ ] Guia operacional indica quando a customização exige aprovação adicional
- [ ] Mudanças ficam auditáveis para revisão futura

**Tarefas:**
- [ ] T1: Definir quais alterações precisam ficar registradas
- [ ] T2: Expor log ou histórico mínimo no backoffice/documentação
- [ ] T3: Atualizar guia operacional com regras de governança

## 5. Notas de Implementação Globais
- Customização controlada não é sinônimo de liberdade total; o catálogo visual segue
  sendo a fonte de verdade
