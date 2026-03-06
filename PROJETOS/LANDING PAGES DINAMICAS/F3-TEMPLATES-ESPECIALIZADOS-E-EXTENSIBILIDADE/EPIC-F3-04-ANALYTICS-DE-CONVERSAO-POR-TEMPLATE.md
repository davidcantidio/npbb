# EPIC-F3-04 — Analytics de Captação por Template
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Instrumentar a jornada da landing para medir visualizações, submissões e taxa de
captação por categoria/template, suportando análise contínua de performance.

## 2. Contexto Arquitetural
- O PRD cita integração com GA4 e métricas de conversão por template
- Os dados precisam distinguir categoria, evento e variante de CTA quando aplicável
- No contexto operacional, a métrica representa captação de lead durante a ativação

## 3. Riscos e Armadilhas
- Capturar eventos demais e poluir análise
- Violação de privacidade ao enviar dados pessoais para analytics

## 4. Definition of Done do Épico
- [ ] Visualizações e submissões são rastreadas por evento e template
- [ ] Taxa de captação por categoria fica consultável
- [ ] Instrumentação respeita LGPD e não envia dados sensíveis

---
## Issues

### LPD-F3-04-001 — Definir plano de eventos de analytics da landing
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Definir o plano mínimo de eventos e propriedades necessárias para medir desempenho da
landing sem excesso de ruído analítico.

**Critérios de Aceitação:**
- [ ] Eventos de page view, início de preenchimento e submit são definidos
- [ ] Propriedades incluem categoria/template e identificador do evento
- [ ] Dados sensíveis do lead não entram no payload analítico

**Tarefas:**
- [ ] T1: Listar eventos e propriedades necessárias
- [ ] T2: Revisar aderência a LGPD
- [ ] T3: Registrar plano analítico para implementação

---
### LPD-F3-04-002 — Implementar instrumentação de analytics na landing
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F3-04-001

**Descrição:**
Adicionar a instrumentação na landing para registrar eventos do funil de captação por
template usando a solução analítica definida para o projeto.

**Critérios de Aceitação:**
- [ ] Page view, submit e sucesso são enviados com propriedades corretas
- [ ] Falhas de analytics não quebram o fluxo de captura
- [ ] Eventos são disparados uma única vez por interação relevante

**Tarefas:**
- [ ] T1: Integrar camada de tracking ao frontend da landing
- [ ] T2: Disparar eventos nas etapas relevantes do funil
- [ ] T3: Validar instrumentação em ambiente de teste

---
### LPD-F3-04-003 — Consolidar visão de captação por template
**tipo:** feature | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F3-04-002

**Descrição:**
Disponibilizar uma visão inicial que permita comparar desempenho por template/categoria
para orientar otimizações futuras.

**Critérios de Aceitação:**
- [ ] Captação por categoria/template pode ser consultada
- [ ] Métricas distinguem visualizações, envios e taxa resultante
- [ ] Time de produto consegue identificar templates com melhor e pior desempenho

**Tarefas:**
- [ ] T1: Definir onde a visão será consultada (dashboard, relatório ou painel)
- [ ] T2: Consolidar métricas mínimas por template
- [ ] T3: Validar leitura com stakeholders de produto

## 5. Notas de Implementação Globais
- Começar pelo essencial do funil; evitar tentar resolver analytics completo em uma
  única iteração
