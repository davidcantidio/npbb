---
doc_id: "PRD-LP-PREVIEW.md"
version: "0.1"
status: "draft"
intake_kind: "refactor"
owner: "PM"
last_updated: "2026-03-13"
origin_intake: "INTAKE.md"
delivery_surface: "frontend-web"
business_domain: "landing-pages, leads"
product_type: "platform-capability"
change_type: "refactor"
criticality: "baixa"
---

# PRD — LP-PREVIEW — Refatoração do Preview em Layout Side-by-Side Mobile

## Cabeçalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | refactor (remediação controlada) |
| Origem do intake | [INTAKE.md](./INTAKE.md) |
| Superfície afetada | frontend-web (páginas de configuração de leads e landing page) |
| Domínio | landing-pages, leads |
| Criticidade | baixa |

---

## 1. Objetivo e Contexto

Este PRD define a refatoração do preview presente nas páginas de configuração de formulário de leads e de landing page. O problema foi identificado no [INTAKE.md](./INTAKE.md): o preview ocupa hoje uma faixa horizontal intercalada entre blocos do formulário, fragmentando o fluxo de configuração e não representando a experiência real do usuário final (mobile).

O objetivo é reposicionar o preview em layout side-by-side (painel de configuração à esquerda, preview à direita), fixo e visível durante toda a sessão, com viewport simulando dispositivo móvel (~390px, referência iPhone 16), mantendo a reatividade existente.

---

## 2. Problema e Evidência Técnica

### 2.1 Sintoma observado

Preview disposto horizontalmente em faixa, intercalado entre blocos do formulário de configuração, fragmentando o fluxo de trabalho do operador e não representando a experiência real do usuário final (mobile).

### 2.2 Impacto operacional

Operador precisa rolar a tela para correlacionar configuração com resultado visual; preview não simula dispositivo móvel, levando a decisões de layout baseadas em viewport desktop que não correspondem à experiência de produção.

### 2.3 Evidência técnica

Comportamento visual observado diretamente na interface pelo PM. Nenhum bug tracker associado.

### 2.4 Componentes afetados

- Componente(s) de preview na página de configuração de formulário de leads
- Componente(s) de preview na página de configuração de landing page
- Sistema de layout da página de configuração (grid/flex atual)

**Lacunas conhecidas (a serem resolvidas na F1):**
- Nome exato do(s) componente(s) de preview no codebase: `nao_definido`
- Estrutura atual de layout da página (CSS Grid / Flexbox / outro): `nao_definido`
- Se o componente de preview é compartilhado entre os dois contextos ou são instâncias distintas: `nao_definido`

### 2.5 Riscos de não agir

Operadores continuarão tomando decisões de configuração com base em uma visualização não representativa, aumentando a probabilidade de retrabalho pós-publicação e de experiências inconsistentes para o usuário final.

---

## 3. Escopo

### 3.1 Dentro

- Converter layout da página de configuração para duas colunas (painel esquerdo + preview direito)
- Reposicionar o preview à direita, fixo e visível durante toda a sessão, sem necessidade de scroll
- Renderizar o preview em viewport de dispositivo móvel (largura-alvo: ~390px, referência iPhone 16), com frame visual de celular
- Manter reatividade existente (atualização em tempo real ao editar campos)
- Tratar breakpoint para viewports menores (desktop com resolução baixa ou tablets) — layout deve colapsar de forma controlada
- Compatibilidade obrigatória com os dois contextos (leads e landing page) na mesma entrega

### 3.2 Fora

- Alterar a lógica de configuração dos formulários em si
- Adicionar funcionalidades ao preview (zoom, troca de dispositivo, modo desktop) nesta fase
- Alterar contrato de API ou modelos de dados
- Introduzir nova dependência de biblioteca externa sem aprovação prévia

---

## 4. Restrições e Riscos

### 4.1 Restrições

- O preview não pode introduzir nova dependência de biblioteca externa sem aprovação prévia
- A reatividade existente (atualização ao editar campos) deve ser mantida
- Compatibilidade com os dois contextos (leads e landing page) obrigatória na mesma entrega

### 4.2 Riscos principais

| Risco | Mitigação |
|---|---|
| Componente de preview não isolado, dificultando reposicionamento | F1 Discovery: mapear acoplamentos antes de implementar |
| Layout de duas colunas colapsa em viewports menores | Tratamento de breakpoint; fallback para layout empilhado em telas pequenas |
| Reatividade acoplada ao posicionamento atual | F1 Discovery: validar fluxo de dados; F2: ajustar se necessário |
| Largura-alvo 390px não validada com design | F1: validar com design antes de implementar |

### 4.3 Rollback

- Reverter alterações de layout via deploy da versão anterior
- Sem migração de dados; alteração exclusivamente de UI

---

## 5. Fases Propostas

### F1 — Discovery Técnico

**Objetivo:** Levantar informações técnicas necessárias para implementação segura.

**Entregas:**
- Identificar nome exato do(s) componente(s) de preview no codebase
- Documentar estrutura atual de layout da página (CSS Grid / Flexbox / outro)
- Confirmar se o componente de preview é compartilhado entre leads e landing page ou são instâncias distintas
- Validar largura-alvo do frame mobile (390px) com design

**Critério de aceite:**
- Lacunas conhecidas do intake resolvidas e documentadas
- Decisão de arquitetura (componente compartilhado ou não) registrada

---

### F2 — Implementação

**Objetivo:** Implementar layout side-by-side e preview mobile.

**Entregas:**
- Converter layout da página de configuração para duas colunas (painel esquerdo + preview direito)
- Reposicionar preview à direita, fixo e visível
- Aplicar frame visual de celular com viewport ~390px
- Manter reatividade (atualização em tempo real)
- Implementar tratamento de breakpoint para viewports menores
- Aplicar alterações em ambos os contextos (leads e landing page)

**Critério de aceite:**
- Preview visível ao lado do painel durante toda a sessão
- Preview renderiza em viewport mobile com frame de celular
- Reatividade preservada em ambos os contextos
- Layout colapsa adequadamente em viewports menores

---

### F3 — Validação

**Objetivo:** Garantir ausência de regressão e aderência aos critérios de sucesso.

**Entregas:**
- Testes manuais em ambos os contextos (leads e landing page)
- Checklist de regressão de funcionalidade do preview
- Validação em diferentes viewports (desktop, tablet, mobile)

**Critério de aceite:**
- Zero bugs reportados relacionados ao preview
- Métricas de sucesso atendidas

---

## 6. Indicadores de Sucesso

- Eliminação de reclamações sobre preview não representativo (qualitativa, próximas sessões de uso interno)
- Nenhuma regressão de funcionalidade nos dois contextos (zero bugs reportados pós-deploy relacionados ao preview)
- [hipótese] Redução de iterações de reconfiguração pós-publicação

---

## 7. Referências

- **Intake de origem:** [INTAKE.md](./INTAKE.md)
- **Governança:** `PROJETOS/COMUM/GOV-INTAKE.md` — gate Intake → PRD
