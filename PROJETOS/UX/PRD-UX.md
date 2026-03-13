---
doc_id: "PRD-UX.md"
version: "0.1"
status: "draft"
intake_kind: "refactor"
owner: "PM"
last_updated: "2026-03-13"
origin_intake: "INTAKE-UX.md"
delivery_surface: "frontend-web"
business_domain: "landing-pages, leads, eventos"
product_type: "platform-capability"
change_type: "refactor"
criticality: "media"
---

# PRD — UX — Refatoração do Wizard de Configuração de Evento

## Cabeçalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | refactor (remediação controlada) |
| Origem do intake | [INTAKE-UX.md](./INTAKE-UX.md) |
| Superfície afetada | frontend-web (wizard de 5 etapas) |
| Domínio | landing-pages, leads, eventos |
| Criticidade | media |

---

## 1. Objetivo e Contexto

Este PRD define a refatoração do wizard de configuração de evento (5 etapas: Evento, Formulário de Lead, Gamificação, Ativações, Questionário) para eliminar ruído visual, redundâncias e inconsistências que prejudicam a experiência do operador.

O problema foi identificado no [INTAKE-UX.md](./INTAKE-UX.md): campos excessivamente largos, preview fragmentado, dropdown de "Tema" duplicado, box informativo redundante, seção "Governança e performance" desnecessária, texto descritivo sem valor, lista de campos em 2 colunas sem drag-and-drop, densidade visual desproporcional e falta de harmonia entre etapas.

O objetivo é estabelecer um padrão visual consistente em duas colunas (configuração à esquerda, contexto à direita), com respiro visual e sem informações redundantes, para que o operador configure com eficiência e confiança.

---

## 2. Problema e Evidência Técnica

### 2.1 Sintoma observado

Interface do wizard com múltiplas camadas de ruído visual: campos excessivamente largos, elementos redundantes (dropdown duplicado, box informativo, texto descritivo sem valor), preview fragmentado sem coluna fixa, lista de campos em 2 colunas com reordenação apenas textual, densidade desproporcional e inconsistência visual entre etapas.

### 2.2 Impacto operacional

Operador enfrenta fricção desnecessária em cada etapa: precisa ignorar informações redundantes, não consegue correlacionar configuração com resultado visual sem scroll, e não pode reordenar campos de forma intuitiva. A inconsistência entre etapas aumenta a carga cognitiva e reduz a confiança na configuração.

### 2.3 Evidência técnica

Screenshots da interface atual fornecidos pelo PM em sessão de intake (2026-03-13), cobrindo as etapas Formulário de Lead, Gamificação e Ativações. Problemas identificados diretamente na interface em produção local (localhost).

### 2.4 Componentes afetados

- Páginas das 5 etapas do wizard
- Componente de preview de landing (nome exato: `nao_definido` — F1)
- Componente de preview de ativação (nome exato: `nao_definido` — F1)
- Componente de seleção/reordenação de campos possíveis
- Sistema de layout/grid do wizard

### 2.5 Riscos de não agir

A inconsistência visual e a densidade de informação continuarão gerando fricção operacional crescente à medida que novas funcionalidades forem adicionadas. O padrão atual, se não corrigido, tende a ser replicado em novas etapas, aumentando o custo de refatoração futura.

---

## 3. Escopo

### 3.1 Dentro

**Layout geral (todas as 5 etapas):**
- Dividir tela em duas colunas fixas: painel de configuração à esquerda, conteúdo contextual à direita
- Aplicar padrão visual consistente: respiro, fontes, espaçamentos
- Tratar breakpoint para viewports menores (colapso para coluna única — breakpoint a definir na F1)

**Etapa Formulário de Lead:**
- Coluna esquerda: seletor único de template ("Contexto da landing"), CTA personalizado, Descrição curta, seleção de campos
- Coluna direita: preview da landing em frame mobile (~390px), sem texto descritivo acima
- Remover dropdown "Tema" redundante (confirmar na F1 que "Contexto da landing" cobre 100% dos valores)
- Remover box informativo azul redundante
- Remover seção "Governança e performance"
- Campos possíveis em 1 coluna; CPF, Nome, Sobrenome e Data de nascimento pré-selecionados e visíveis por padrão (CPF não desmarcável)
- Demais campos acessíveis via botão "+"
- Reordenação por drag-and-drop (em vez de indicação textual)

**Etapa Gamificação:**
- Coluna esquerda: formulário de configuração
- Coluna direita: lista das gamificações criadas (comportamento atual mantido)

**Etapa Ativações:**
- Coluna esquerda: formulário de configuração
- Coluna direita: preview da página de ativação em frame mobile

**Etapas Evento e Questionário:**
- Padrão de duas colunas aplicado; conteúdo da coluna direita a definir na F1 (discovery)

**Restrições preservadas:**
- Manter reatividade do preview (atualização em tempo real)
- Nenhuma alteração de contrato de API ou modelo de dados
- CPF obrigatório e não desmarcável

### 3.2 Fora

- Novas funcionalidades de configuração (novos campos, novos tipos de gamificação)
- Redesign do sistema de design global da plataforma
- Alteração de comportamento de publicação ou salvamento
- Preview interativo (permanece somente-leitura)
- Nova dependência de biblioteca externa sem aprovação prévia

---

## 4. Restrições e Riscos

### 4.1 Restrições

- Nenhuma alteração de contrato de API ou modelo de dados
- CPF deve permanecer obrigatório e não desmarcável
- Reatividade do preview (atualização em tempo real) deve ser mantida
- Padrão de duas colunas deve ser responsivo (breakpoint a definir)
- Nenhuma nova dependência de biblioteca externa sem aprovação prévia

### 4.2 Riscos principais

| Risco | Mitigação |
|---|---|
| Componente de preview acoplado ao posicionamento atual | F1: mapear acoplamentos; F2: refatorar se necessário |
| Nova lib de drag-and-drop aumenta bundle | F1: avaliar dnd-kit ou similar; aprovar antes de introduzir |
| Layout colapsa mal em tablets/laptops pequenos | F1: definir breakpoint; F2: testar em resoluções intermediárias |
| Superfície de regressão em 5 etapas | F3: checklist manual por etapa antes do deploy |
| Seletor "Contexto da landing" não cobre valores do "Tema" removido | F1: confirmar cobertura 100% antes de remover |

### 4.3 Rollback

- Reverter alterações de layout via deploy da versão anterior
- Sem migração de dados; alteração exclusivamente de UI

---

## 5. Fases Propostas

### F1 — Discovery Técnico

**Objetivo:** Resolver lacunas conhecidas e validar premissas antes da implementação.

**Entregas:**
- Identificar nomes exatos dos componentes de preview (landing e ativação) no codebase
- Documentar estrutura atual de layout do wizard (CSS Grid / Flexbox / outro)
- Verificar se existe biblioteca de drag-and-drop no codebase; se não, recomendar e obter aprovação
- Definir breakpoint de colapso para coluna única
- Definir conteúdo da coluna direita nas etapas Evento e Questionário
- Confirmar que o seletor "Contexto da landing" cobre todos os valores do dropdown "Tema" removido

**Critério de aceite:**
- Todas as lacunas `nao_definido` do intake resolvidas e documentadas
- Decisões de arquitetura registradas (componentes compartilhados, lib de dnd, breakpoint)

---

### F2 — Implementação

**Objetivo:** Implementar layout side-by-side, limpeza de redundâncias e drag-and-drop.

**Entregas:**
- Converter layout do wizard para duas colunas em todas as 5 etapas
- Etapa Formulário de Lead: remover redundâncias (Tema, box azul, Governança e performance, texto descritivo); aplicar preview mobile ~390px; implementar campos em 1 coluna com visibilidade progressiva e drag-and-drop
- Etapa Gamificação: aplicar layout; manter lista à direita
- Etapa Ativações: aplicar layout; preview da ativação em frame mobile à direita
- Etapas Evento e Questionário: aplicar layout conforme definido na F1
- Implementar tratamento de breakpoint para viewports menores

**Critério de aceite:**
- Layout de duas colunas visível em todas as etapas
- Zero elementos listados como removidos no escopo
- Reatividade do preview preservada
- Drag-and-drop funcional para reordenação de campos
- Layout colapsa adequadamente em viewports menores

---

### F3 — Validação

**Objetivo:** Garantir ausência de regressão e aderência aos critérios de sucesso.

**Entregas:**
- Checklist de regressão manual por etapa (Evento, Formulário, Gamificação, Ativações, Questionário)
- Validação em múltiplos viewports (desktop, tablet, mobile)
- Validação interna pelo PM de limpeza e harmonia visual

**Critério de aceite:**
- Zero regressão funcional nas 5 etapas
- PM aprova interface antes do deploy

---

## 6. Indicadores de Sucesso

- Nenhuma regressão funcional nas 5 etapas do wizard
- Eliminação de 100% dos elementos listados como removidos no escopo
- Validação interna pelo PM de que a interface atende aos critérios de limpeza e harmonia visual antes do deploy
- [hipótese] Redução de dúvidas operacionais sobre função dos controles, observável em próximas sessões de uso

---

## 7. Referências

- **Intake de origem:** [INTAKE-UX.md](./INTAKE-UX.md)
- **Governança:** `PROJETOS/COMUM/GOV-INTAKE.md` — gate Intake → PRD
