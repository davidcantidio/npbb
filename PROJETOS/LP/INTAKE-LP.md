---
doc_id: "INTAKE-LP.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-11"
project: "LP"
intake_kind: "problem"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "campaign-experience"
delivery_surface: "fullstack-module"
business_domain: "landing-pages"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "eventos"
  - "formulario-lead"
change_type: "correcao-estrutural"
audit_rigor: "standard"
---

# INTAKE - LP

> Intake de correção de problemas na página de configuração do formulário de leads e no preview da landing page associada.

## 0. Rastreabilidade de Origem

- projeto de origem: LP
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: feedback direto do usuário na página `/eventos/:id/formulario-lead` identificando bugs de sincronização do preview e problemas de UX (mobile-first, contraste).

## 1. Resumo Executivo

- nome curto da iniciativa: Correção do preview e UX do formulário de leads
- tese em 1 frase: O preview da landing page na tela de configuração do formulário de leads deve refletir em tempo real todas as alterações (tema, contexto, campos) e garantir usabilidade mobile-first com contraste adequado.
- valor esperado em 3 linhas:
  - Configurador WYSIWYG funcional: o operador vê imediatamente o resultado das escolhas.
  - Landing pages legíveis em qualquer dispositivo e em qualquer template-override.
  - Redução de retrabalho e frustração ao publicar formulários com aparência inesperada.

## 2. Problema ou Oportunidade

- problema atual: Na página de formulário de leads (`/eventos/:id/formulario-lead`), o preview da landing page abaixo não reflete três tipos de alteração: (1) seleção do tema no dropdown; (2) seleção dos campos possíveis; (3) além disso, ao alterar "Contexto da Landing" o preview atualiza, mas há problemas de mobile-first e contraste em alguns template-overrides.
- evidencia do problema: Comportamento observado em http://127.0.0.1:5173/eventos/111/formulario-lead — dropdown tema sem efeito no preview; campos selecionados sem efeito no preview; templates com baixo contraste e layout não mobile-first.
- custo de nao agir: Operadores publicam formulários com aparência inesperada; risco de acessibilidade e usabilidade em mobile; perda de confiança no configurador.
- por que agora: Demanda explícita do usuário; impacto direto na experiência de configuração de eventos.

## 3. Publico e Operadores

- usuario principal: Operador interno que configura eventos e formulários de lead.
- usuario secundario: Visitante que preenche o formulário na landing page pública.
- operador interno: Equipe de marketing/eventos.
- quem aprova ou patrocina: nao_definido

## 4. Jobs to be Done

- job principal: Configurar tema, contexto e campos do formulário de lead e visualizar o resultado em tempo real antes de publicar.
- jobs secundarios: Garantir que a landing publicada seja legível em mobile e em todos os templates.
- tarefa atual que sera substituida: Configuração sem feedback visual confiável; templates com contraste inadequado.

## 5. Fluxo Principal Desejado

1. Operador abre a página de formulário de leads do evento.
2. Operador altera o tema no dropdown → preview atualiza imediatamente.
3. Operador altera o "Contexto da Landing" (template_override) → preview atualiza (já funciona) e exibe layout mobile-first com contraste adequado.
4. Operador seleciona/deseleciona campos possíveis → preview reflete os campos ativos em tempo real.
5. Operador salva → configuração persiste e preview permanece alinhado.

## 6. Escopo Inicial

### Dentro

- Sincronizar preview com alteração do dropdown tema.
- Sincronizar preview com alteração dos campos selecionados (sem exigir salvar).
- Garantir filosofia mobile-first na landing page e no preview.
- Corrigir template-overrides que geram formulários com contraste insuficiente.

### Fora

- Alteração da API pública de landing (manter contrato existente).
- Novos templates ou novos campos de customização além dos atuais.
- Refatoração ampla do sistema de templates.

## 7. Resultado de Negocio e Metricas

- objetivo principal: Preview WYSIWYG funcional e landing pages legíveis em todos os contextos.
- metricas leading: Preview atualiza em <500ms após alteração de tema, contexto ou campos.
- metricas lagging: Redução de reclamações sobre aparência inesperada; conformidade com critérios de contraste (WCAG AA mínimo).
- criterio minimo para considerar sucesso: (1) Tema, contexto e campos refletem no preview em tempo real; (2) Layout mobile-first; (3) Nenhum template-override homologado com contraste inaceitável.

## 8. Restricoes e Guardrails

- restricoes tecnicas: Manter compatibilidade com API `getLandingByEvento` e estrutura de dados existente; preview pode precisar de parâmetros adicionais para tema/campos locais.
- restricoes operacionais: nao_definido
- restricoes legais ou compliance: Contraste deve atender WCAG AA para texto.
- restricoes de prazo: nao_definido
- restricoes de design ou marca: Manter catálogo homologado da marca BB; customização controlada (template_override, cta_personalizado, descricao_curta).

## 9. Dependencias e Integracoes

- sistemas internos impactados: frontend (EventLeadFormConfig, LandingPageView), possivelmente API de landing para preview com parâmetros de override.
- sistemas externos impactados: nenhum
- dados de entrada necessarios: template_id (tema), template_override (contexto), campos ativos/obrigatórios — estado local e persistido.
- dados de saida esperados: Preview renderizado com tema, contexto e campos corretos.

## 10. Arquitetura Afetada

- backend: Possível endpoint ou parâmetros de preview para tema/campos locais (a confirmar).
- frontend: EventLeadFormConfig.tsx (lógica de preview), LandingPageView (renderização), componentes de template-override (cores/contraste).
- banco/migracoes: Nenhuma esperada.
- observabilidade: nao_definido
- autorizacao/autenticacao: Sem alteração.
- rollout: Deploy frontend; possível ajuste de API se necessário.

## 11. Riscos Relevantes

- risco de produto: Correção de contraste pode alterar aparência de templates já em uso.
- risco tecnico: Preview com estado local pode divergir temporariamente do persistido.
- risco operacional: baixo
- risco de dados: nenhum
- risco de adocao: baixo — melhoria de UX.

## 12. Nao-Objetivos

- Redesenho completo do sistema de templates.
- Novos tipos de template-override.
- Alteração do fluxo de salvamento (manter salvar explícito).

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: (1) Dropdown tema não atualiza preview; (2) Campos selecionados não refletem no preview; (3) "Contexto da Landing" atualiza preview, mas layout não é mobile-first e alguns template-overrides geram formulários ilegíveis por baixo contraste.
- impacto operacional: Operador não consegue validar visualmente a configuração antes de salvar; formulários publicados podem ser ilegíveis em mobile ou em certos templates.
- evidencia tecnica: Página `EventLeadFormConfig` usa `landingMeta.template_override` para o preview; `templateId` (tema) e `camposAtivos` não são passados ao `loadPreview`. Preview chama `getLandingByEvento(eventoId, { templateOverride })` — dados de tema e campos vêm do backend persistido, não do estado local.
- componente(s) afetado(s): `frontend/src/pages/EventLeadFormConfig.tsx`, `frontend/src/components/landing/LandingPageView.tsx`, estilos/CSS dos template-overrides.
- riscos de nao agir: Formulários publicados com aparência inesperada; problemas de acessibilidade; perda de confiança no configurador.

## 14. Lacunas Conhecidas

- Mapeamento exato tema (template_id) ↔ template_override: relação entre dropdown tema e "Contexto da Landing" precisa ser validada no código.
- Lista completa de template-overrides com problema de contraste: requer auditoria visual.
- Decisão sobre preview com estado local vs. chamada API com parâmetros: se backend suporta preview com tema/campos não persistidos.
- Critério de contraste exato (WCAG AA) para cada template-override.

## 15. Perguntas que o PRD Precisa Responder

- Como o tema (template_id) se relaciona com template_override no backend e no preview?
- O preview deve usar estado local (tema, campos) ou a API deve aceitar parâmetros de override para preview?
- Quais template-overrides específicos têm problema de contraste e qual paleta corrigir?
- Qual breakpoint e ordem de prioridade para mobile-first (mobile primeiro, desktop como enhancement)?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
