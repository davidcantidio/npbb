# EPIC-F2-05 — Documentação Operacional para Marketing
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2 | **status:** 🔲

---
## 1. Resumo do Épico
Criar a documentação operacional do produto para orientar marketing e operação de
eventos no cadastro, revisão e uso em campo de landing pages dinâmicas.

## 2. Contexto Arquitetural
- O PRD prevê documentação de uso na F2
- O backoffice passa a ter preview e campos novos no cadastro do evento
- A qualidade do uso depende de instruções claras para times não técnicos

## 3. Riscos e Armadilhas
- Dependência excessiva de engenharia para configurar campanhas simples
- Time de marketing divulgar eventos sem validar categoria ou CTA

## 4. Definition of Done do Épico
- [ ] Existe guia operacional cobrindo cadastro, preview, overrides e ativação
- [ ] Documentação inclui checklist mínimo de revisão antes do uso em campo
- [ ] Linguagem é adequada para público não técnico

---
## Issues

### LPD-F2-05-001 — Documentar fluxo operacional de cadastro e preview
**tipo:** docs | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F2-04-001

**Descrição:**
Descrever passo a passo como cadastrar evento e ativação, revisar a categoria resolvida,
usar o preview e disponibilizar QR code / URL alternativa antes do uso em campo.

**Critérios de Aceitação:**
- [ ] Guia cobre preenchimento dos campos relevantes do evento
- [ ] Guia mostra como validar o template resolvido no backoffice
- [ ] Passos são claros para usuários não técnicos

**Tarefas:**
- [ ] T1: Mapear o fluxo operacional ponta a ponta
- [ ] T2: Escrever o guia em formato reutilizável pela operação
- [ ] T3: Revisar linguagem e clareza do material

---
### LPD-F2-05-002 — Formalizar checklist de ativação e governança de override
**tipo:** docs | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F2-05-001

**Descrição:**
Documentar o checklist de revisão final e explicitar quando o uso de
`template_override` é permitido, recomendado ou proibido.

**Critérios de Aceitação:**
- [ ] Checklist cobre hero, CTA, categoria, LGPD, política e tagline
- [ ] Regras de override ficam claras e rastreáveis
- [ ] Material aponta quando acionar design/engenharia

**Tarefas:**
- [ ] T1: Consolidar checklist mínimo de ativação
- [ ] T2: Definir diretrizes de uso do override
- [ ] T3: Validar material com stakeholders internos

---
### LPD-F2-05-003 — Publicar referência rápida por categoria de template
**tipo:** docs | **sp:** 1 | **prioridade:** baixa | **status:** 🔲
**depende de:** LPD-F2-05-002

**Descrição:**
Criar um resumo operacional por categoria para facilitar o entendimento rápido dos
territórios visuais e CTAs padrão disponíveis.

**Critérios de Aceitação:**
- [ ] Documento lista categorias entregues e seus usos recomendados
- [ ] Cada categoria traz exemplo de CTA e orientação de tom de voz
- [ ] Referência é curta o suficiente para consulta rápida

**Tarefas:**
- [ ] T1: Consolidar quadro resumo por categoria
- [ ] T2: Validar exemplos de CTA e mensagem
- [ ] T3: Publicar referência junto ao guia principal

## 5. Notas de Implementação Globais
- A documentação deve refletir o comportamento real do sistema, não a intenção do PRD
