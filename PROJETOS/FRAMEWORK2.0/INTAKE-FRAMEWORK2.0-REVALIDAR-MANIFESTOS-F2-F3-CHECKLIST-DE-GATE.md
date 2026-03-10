---
doc_id: "INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-10"
project: "FRAMEWORK2.0"
intake_kind: "audit-remediation"
source_mode: "audit-derived"
origin_project: "FRAMEWORK2.0"
origin_phase: "F1-HARMONIZACAO-E-RENOMEACAO"
origin_audit_id: "RELATORIO-AUDITORIA-F1-R01.md"
origin_report_path: "/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "PROJETOS/FRAMEWORK2.0/F2-ANTI-MONOLITH-ENFORCEMENT"
  - "PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO"
  - "PROJETOS/COMUM/GOV-ISSUE-FIRST.md"
change_type: "correcao-estrutural"
audit_rigor: "elevated"
---

# INTAKE - FRAMEWORK2.0 - REVALIDAR MANIFESTOS F2/F3 CHECKLIST DE GATE

## 0. Rastreabilidade de Origem

- projeto de origem: `FRAMEWORK2.0`
- fase de origem: `F1-HARMONIZACAO-E-RENOMEACAO`
- auditoria de origem: `RELATORIO-AUDITORIA-F1-R01.md`
- relatorio de origem: `/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- motivo da abertura deste intake: follow-up nao bloqueante da auditoria F1-R01 para revalidar os manifestos F2/F3 contra o checklist split `pending -> hold` / `pending -> approved` do template canonico e reduzir drift futuro

## 1. Resumo Executivo

- nome curto da iniciativa: `REVALIDACAO-F2-F3-GATE`
- tese em 1 frase: revalidar os manifestos das fases F2 e F3 contra o template canonico de gate para prevenir repeticao do drift documental identificado em F1
- valor esperado em 3 linhas:
  reduzir ambiguidade futura na leitura de `gate_atual`, `ultima_auditoria` e checklist de transicao
  antecipar correcao documental em F2/F3 antes que o mesmo tipo de drift reapareca em auditorias futuras
  manter o framework de fases coerente com o split canonico `pending -> hold` / `pending -> approved`

## 2. Problema ou Oportunidade

- problema atual: a auditoria F1-R01 mostrou que drift documental em manifesto e gate compromete a leitura confiavel da fase; por extensao, F2/F3 precisam ser revalidadas contra o checklist split vigente para evitar recorrencia
- evidencia do problema: follow-up nao bloqueante do `RELATORIO-AUDITORIA-F1-R01.md` recomenda explicitamente revalidar os manifestos F2/F3 contra o checklist split do template canonico
- custo de nao agir: fases futuras podem repetir ambiguidade de gate, descoberta errada de unidade elegivel e leitura historica inconsistente
- por que agora: o framework ja sofreu esse tipo de drift em F1 e F2/F3 ainda estao em estado anterior a suas auditorias formais

## 3. Publico e Operadores

- usuario principal: PM que mantem e opera o projeto `FRAMEWORK2.0`
- usuario secundario: agentes de IA que leem manifestos de fase para planejar, executar e auditar
- operador interno: engenharia de produto responsavel pela governanca documental do framework
- quem aprova ou patrocina: PM / engenharia

## 4. Jobs to be Done

- job principal: garantir que manifestos de fase futuros sejam lidos com gate e checklist sem ambiguidade
- jobs secundarios: prevenir drift entre template canonico e manifestos concretos; manter rastreabilidade de auditoria futura
- tarefa atual que sera substituida: revalidacao manual ad hoc de manifestos de fase apos achados de auditoria

## 5. Fluxo Principal Desejado

1. Ler o template canonico de fase e o follow-up de auditoria que motivou a remediacao
2. Comparar os manifestos F2 e F3 com o checklist split vigente
3. Identificar e corrigir drift estritamente documental, se houver
4. Deixar F2/F3 coerentes com o modelo canonico antes de suas futuras auditorias

## 6. Escopo Inicial

### Dentro

- revalidar os manifestos F2 e F3 contra o checklist split `pending -> hold` / `pending -> approved`
- confirmar coerencia de `gate_atual`, `ultima_auditoria` e checklist de transicao nesses manifestos
- corrigir drift documental estritamente necessario caso a revalidacao confirme divergencia

### Fora

- alterar o escopo funcional dos epicos ou issues de F2/F3
- criar nova rodada de auditoria para F2 ou F3 dentro deste intake
- redefinir o checklist canonico de gate alem do que ja esta estabelecido no template atual

## 7. Resultado de Negocio e Metricas

- objetivo principal: reduzir risco de drift futuro nos manifestos de fase de `FRAMEWORK2.0`
- metricas leading: manifestos F2/F3 aderentes ao checklist split vigente; ausencia de ambiguidade em `gate_atual` e `ultima_auditoria`
- metricas lagging: menor incidencia de achados de drift documental em auditorias futuras de F2/F3
- criterio minimo para considerar sucesso: F2 e F3 revalidadas contra o template canonico, com divergencias documentais corrigidas ou explicitamente descartadas com evidencia

## 8. Restricoes e Guardrails

- restricoes tecnicas: trabalho limitado a artefatos Markdown e governanca documental
- restricoes operacionais: nao tratar este intake como substituto da futura auditoria formal de F2/F3
- restricoes legais ou compliance: nao aplicavel
- restricoes de prazo: idealmente concluir antes das auditorias formais de F2 e F3
- restricoes de design ou marca: manter estilo e estrutura documental ja adotados pelo framework

## 9. Dependencias e Integracoes

- sistemas internos impactados: manifestos `F2_FRAMEWORK2_0_EPICS.md` e `F3_FRAMEWORK2_0_EPICS.md`, template de fase em `GOV-ISSUE-FIRST.md`
- sistemas externos impactados: nenhum
- dados de entrada necessarios: `RELATORIO-AUDITORIA-F1-R01.md`, template canonico de fase, manifestos atuais de F2 e F3
- dados de saida esperados: decisao rastreavel sobre aderencia ou drift dos manifestos F2/F3 e eventual remediacao documental correspondente

## 10. Arquitetura Afetada

- backend: nao aplicavel
- frontend: nao aplicavel
- banco/migracoes: nao aplicavel
- observabilidade: nao aplicavel
- autorizacao/autenticacao: nao aplicavel
- rollout: ajuste documental coordenado nos manifestos F2/F3 antes de novas rodadas de auditoria

## 11. Riscos Relevantes

- risco de produto: fases futuras parecerem mais prontas ou menos prontas do que realmente estao
- risco tecnico: drift entre template canonico e manifestos concretos persistir sem ser percebido
- risco operacional: agente ou PM interpretar gate de fase de forma errada em F2/F3
- risco de dados: nao aplicavel
- risco de adocao: operadores continuarem confiando em manifestos potencialmente desatualizados

## 12. Nao-Objetivos

- nao executar epicos ou issues de F2/F3
- nao abrir auditoria formal de F2/F3 neste fluxo
- nao redesenhar o modelo de gate alem da revalidacao contra o split canonico ja existente

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: a auditoria F1-R01 registrou drift documental material em gate e manifesto de fase e, como follow-up nao bloqueante, recomendou revalidar os manifestos F2/F3 contra o checklist split `pending -> hold` / `pending -> approved`
- impacto operacional: sem essa revalidacao, F2/F3 podem repetir ambiguidade de gate, leitura incorreta da proxima unidade elegivel e historico de fase inconsistente
- evidencia tecnica: `RELATORIO-AUDITORIA-F1-R01.md`, especialmente o follow-up nao bloqueante que recomenda revalidacao preventiva de F2/F3; o proprio relatorio tambem registra que o checklist split ja existe no template canonico
- componente(s) afetado(s): manifestos de fase F2 e F3 de `FRAMEWORK2.0` e sua aderencia ao template canonico de `GOV-ISSUE-FIRST.md`
- riscos de nao agir: recorrencia de drift documental em fases futuras, gate mal interpretado e necessidade de correcao reativa apenas durante auditoria

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: o relatorio nao informa se F2/F3 possuem alguma excecao deliberada ao template canonico
- dependencia ainda nao confirmada: o relatorio nao confirma se os manifestos F2/F3 ja estao totalmente aderentes ou se ha drift concreto a corrigir
- dado ainda nao disponivel: nao existe, no relatorio F1-R01, inventario detalhado das divergencias atuais de F2 e F3
- decisao de UX ainda nao fechada: nao aplicavel
- outro ponto em aberto: o downstream precisa decidir se a entrega sera apenas de revalidacao documental ou de revalidacao mais ajuste imediato caso o drift seja confirmado

## 15. Perguntas que o PRD Precisa Responder

- qual e o delta real entre os manifestos atuais de F2/F3 e o checklist split vigente do template canonico
- se houver drift, quais ajustes documentais minimos devem ser aplicados sem reabrir escopo das fases
- como registrar a revalidacao de F2/F3 de forma rastreavel sem simular auditoria formal antecipada

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
