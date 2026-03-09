---
doc_id: "INTAKE-LANDING-PAGE-FORM-FIRST.md"
version: "1.1"
status: "backfilled"
owner: "PM"
last_updated: "2026-03-08"
project: "LANDING-PAGE-FORM-FIRST"
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "LANDING-PAGE-FORM-FIRST"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "campaign-experience"
delivery_surface: "fullstack-module"
business_domain: "landing-pages"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "landing public API"
  - "template visual tokens"
  - "backoffice preview"
  - "gamificacao block"
change_type: "evolucao"
audit_rigor: "standard"
---

# INTAKE - LANDING-PAGE-FORM-FIRST

> Artefato retrospectivo. Este arquivo foi reconstruido a partir do PRD vigente para formalizar a etapa `Intake -> PRD` sem alegar que este foi o registro original da descoberta.

## 0. Rastreabilidade de Origem

- projeto de origem: LANDING-PAGE-FORM-FIRST
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: backfill documental da origem da iniciativa

## 1. Resumo Executivo

- nome curto da iniciativa: simplificacao form-only para landing pages dinamicas
- tese em 1 frase: remover distracoes e reduzir a landing a uma unica tela de formulario melhora conversao no contexto de evento presencial
- valor esperado em 3 linhas: reduzir atrito acima da dobra, reforcar o contexto visual via tema do template e preservar o formulario atual sem retrabalho estrutural no payload publico

## 2. Problema ou Oportunidade

- problema atual: a landing publica ainda exibe header, hero e bloco descritivo que competem com a unica acao relevante, o cadastro
- evidencia do problema: o usuario acessa via QR code ja presente no evento e nao precisa de contextualizacao longa para concluir a acao
- custo de nao agir: menor velocidade de preenchimento, maior dispersao visual e uso ineficiente do viewport em mobile
- por que agora: a infraestrutura de tokens visuais ja existe e permite simplificar a view sem reescrever a base do formulario

## 3. Publico e Operadores

- usuario principal: participante presencial de evento que acessa a landing pelo celular
- usuario secundario: operador do backoffice que precisa validar preview e contexto visual
- operador interno: time de marketing/ativacoes que configura a landing
- quem aprova ou patrocina: produto/marketing da trilha de landing pages dinamicas

## 4. Jobs to be Done

- job principal: cadastrar rapidamente um lead durante o evento
- jobs secundarios: reforcar o territorio visual da ativacao e manter gamificacao acessivel apos o submit
- tarefa atual que sera substituida: jornada com hero contextual, sobre o evento e outros blocos informativos redundantes

## 5. Fluxo Principal Desejado

1. participante abre a landing via QR code em mobile
2. o fundo tematico contextualiza o evento sem exigir leitura adicional
3. o card do formulario aparece imediatamente como elemento principal
4. o usuario preenche, aceita LGPD, envia e, quando aplicavel, segue para gamificacao

## 6. Escopo Inicial

### Dentro

- simplificar a landing publica para layout form-only
- reaproveitar tema, overlay e derivacao de conteudo ja existentes
- ajustar preview/backoffice para o novo layout
- validar regressao visual e acessibilidade nos templates

### Fora

- mudar os campos ou regras do formulario
- introduzir fluxo multi-step
- redesenhar o payload backend da landing alem do necessario para o preview atual

## 7. Resultado de Negocio e Metricas

- objetivo principal: aumentar foco no formulario e reduzir atrito de cadastro em contexto presencial
- metricas leading: tempo para primeira interacao no formulario, visibilidade above-the-fold do card, ausencia de scroll horizontal
- metricas lagging: taxa de conclusao do formulario e reducao de abandono no topo da jornada
- criterio minimo para considerar sucesso: formulario funcional sem regressao, layout responsivo em breakpoints canonicos e ausencia de blocos legados na view publica

## 8. Restricoes e Guardrails

- restricoes tecnicas: preservar `buildLandingTheme`, `renderGraphicOverlay`, derivacoes de conteudo e fluxo de submit existente
- restricoes operacionais: preview deve continuar funcionando para o operador interno
- restricoes legais ou compliance: LGPD e link de politica permanecem obrigatorios
- restricoes de prazo: fatiamento em 3 fases com F1 publica, F2 preview/backoffice e F3 QA
- restricoes de design ou marca: manter conformidade BB, contraste minimo WCAG AA e uso dos tokens do template

## 9. Dependencias e Integracoes

- sistemas internos impactados: view publica da landing, componentes de preview, bloco de gamificacao
- sistemas externos impactados: nenhum sistema externo novo; consumo do payload publico atual permanece
- dados de entrada necessarios: `ativacao`, `evento`, `template`, `formulario`, `marca`, `gamificacoes`
- dados de saida esperados: landing publica simplificada e preview consistente com o novo layout

## 10. Arquitetura Afetada

- backend: sem alteracoes estruturais obrigatorias nesta iniciativa alem do payload ja existente para a landing
- frontend: `LandingPageView` e componentes correlatos da trilha de landing
- banco/migracoes: nenhuma nesta iniciativa especifica
- observabilidade: regressao funcional e visual deve ser coberta por testes direcionados
- autorizacao/autenticacao: sem impacto para a view publica; preview segue regras atuais do backoffice
- rollout: implementar por fases sem quebrar templates existentes

## 11. Riscos Relevantes

- risco de produto: simplificar demais e perder contexto minimo para determinadas ativacoes
- risco tecnico: regressao visual nos 7 templates e nos estados de gamificacao
- risco operacional: preview ficar desalinhado da view publica
- risco de dados: nenhum novo dado sensivel alem do formulario ja existente
- risco de adocao: operadores estranharem a remocao da hero image e dos blocos antigos

## 12. Nao-Objetivos

- criar novo sistema de templates
- alterar logica de validacao dos campos do formulario
- introduzir hero image como fundo da pagina

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: nenhuma lacuna critica remanescente no PRD atual
- dependencia ainda nao confirmada: nenhuma
- dado ainda nao disponivel: metricas reais de conversao dependem de instrumentacao posterior
- decisao de UX ainda nao fechada: opacidade exata do card por template pode continuar tokenizada e refinada em execucao
- outro ponto em aberto: este documento e retrospectivo e serve como fonte canonica daqui para frente

## 15. Perguntas que o PRD Precisa Responder

- quais blocos devem ser removidos da view publica e quais devem ser preservados
- como o fundo tematico full-page deve reutilizar os tokens visuais existentes
- como o preview/backoffice devem refletir o novo layout sem reintroduzir o hero antigo

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
