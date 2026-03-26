---
doc_id: "INTAKE-ATIVOS-INGRESSOS.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-26"
project: "ATIVOS-INGRESSOS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "workflow-improvement"
delivery_surface: "fullstack-module"
business_domain: "eventos"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "ativos"
  - "ingressos"
  - "dashboard"
  - "internal/registry"
  - "internal/ingestao-inteligente"
  - "internal/revisao-humana"
  - "email"
change_type: "evolucao"
audit_rigor: "elevated"
---

# INTAKE - ATIVOS-INGRESSOS

> Evolucao do produto para operar ativos e ingressos fim a fim: previsao,
> recebimento, conciliacao, emissao interna com QR, distribuicao,
> acompanhamento operacional e analytics no dashboard.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: substituir o scaffold inicial por um projeto real de operacao de ativos e ingressos, usando o PDF operacional externo `Acompanhamento Alceu.pdf` apenas como referencia de metricas e graficos

## 1. Resumo Executivo

- nome curto da iniciativa: operacao de ativos e ingressos
- tese em 1 frase: criar a capacidade operacional para prever, receber, conciliar, emitir, distribuir e analisar ingressos internos e de ticketeiras em um fluxo auditavel
- valor esperado em 3 linhas:
  - receber ativos internos e externos em formatos heterogeneos com rastreabilidade de origem, quantidade e categoria
  - emitir ingressos internos unitarios com QR unico por destinatario e preparar o dominio para validacao futura de uso unico
  - acompanhar planejado, recebido, distribuido, bloqueado, remanejado, aumentado, reduzido e problemas em um dashboard operacional aderente ao padrao ja existente do modulo Dashboard

## 2. Problema ou Oportunidade

- problema atual: o dominio atual de ativos controla apenas cotas agregadas por `evento + diretoria`, sem categorias de ingresso, sem reconciliacao `planejado x recebido`, sem inventario unitario por destinatario e sem camada de QR para ingressos internos
- evidencia do problema: o backend atual usa `CotaCortesia` e `SolicitacaoIngresso` como controle agregado; nao ha modelagem para `pista`, `pista premium` e `camarote`, nao ha suporte a divergencia entre quantidade cadastrada e quantidade recebida da ticketeira, e os ingressos internos ainda nao contam com mecanismo de autenticidade por limitacao tecnologica
- custo de nao agir: a operacao continua dependente de email, drive e planilhas paralelas, com risco de enviar categoria errada, distribuir acima do recebido, perder rastreabilidade de problemas e operar sem base confiavel para dashboard gerencial
- por que agora: a equipe vai assumir a distribuicao efetiva dos ingressos e precisa suportar eventos reais com ativos mistos, conciliacao entre previsao e recebimento, emissao interna segura e visibilidade operacional

## 3. Publico e Operadores

- usuario principal: equipe operacional NPBB responsavel por receber, preparar e distribuir ativos dos eventos
- usuario secundario: diretorias, gestores e patrocinadores internos que acompanham saldo, distribuicao, bloqueios, remanejamentos e problemas
- operador interno: operacao NPBB no sistema e skill externa do OpenClaw que pode ler emails de ticketeiras e alimentar o banco via API
- quem aprova ou patrocina: PM e lideranca operacional de eventos

## 4. Jobs to be Done

- job principal: transformar recebimentos heterogeneos de ingressos em inventario distribuivel, auditavel e visivel para a operacao
- jobs secundarios: configurar categorias por evento, conciliar divergencias de quantidade, emitir ingressos internos com QR, bloquear distribuicao quando houver dependencia de recebimento externo, registrar problemas e gerar leitura executiva no dashboard
- tarefa atual que sera substituida: controle manual em email, drive e planilhas para entender o que foi recebido, para quem deve ser enviado, o que foi remanejado e onde houve erro operacional

## 5. Fluxo Principal Desejado

Estados e conceitos canonicos que devem orientar o dominio:

- `planejado`: quantidade prevista no cadastro operacional por evento, diretoria e categoria
- `recebido_confirmado`: quantidade ou artefato efetivamente entregue e conciliado no sistema
- `disponivel`: saldo apto a ser distribuido
- `bloqueado_por_recebimento`: aumento cadastrado que ainda nao pode ser distribuido porque depende de entrega da ticketeira
- `distribuido`: ingresso ou ativo efetivamente vinculado e enviado ao destinatario
- `remanejado`: realocacao entre areas, categorias ou destinatarios ja registrados
- `aumentado`: incremento de previsao ou estoque, sem confundir com remanejamento
- `reduzido`: reducao de previsao ou estoque, sem confundir com remanejamento
- `problema_registrado`: ocorrencia operacional documentada para acompanhamento e dashboard
- `qr_emitido`: ingresso interno gerado com QR unico por destinatario
- `qr_validado`: estado futuro, fora do v1, previsto para suportar semantica de uso unico

Descreva o fluxo ponta a ponta em etapas curtas:

1. Operador cadastra a previsao de ativos por evento, diretoria, categoria e modo de fornecimento.
2. O sistema registra o que foi efetivamente recebido, concilia divergencias e, para origem ticketeira, considera o recebido confirmado como fonte de verdade para o estoque distribuivel.
3. Para ingressos internos, o sistema emite um ingresso unitario por destinatario a partir do layout da categoria, adiciona QR unico e persiste identidade suficiente para validacao futura; para ativos externos, libera distribuicao somente ate o limite confirmado como recebido.
4. A operacao distribui, remaneja, registra aumentos, reducoes, bloqueios, reenviios e problemas; o dashboard consolida KPIs, graficos, acompanhamento por data e painel de ocorrencias.

## 6. Escopo Inicial

### Dentro

- configuracao por evento das categorias iniciais `pista`, `pista premium` e `camarote`, com suporte a eventos que usem apenas parte do catalogo
- dois modos canonicos de fornecimento: `interno_emitido_com_qr` e `externo_recebido`
- conciliacao entre quantidade planejada e quantidade recebida
- regra de prevalencia do recebido confirmado para ativos originados em ticketeira
- bloqueio operacional para aumentos dependentes de ticketeira ate o recebimento correspondente
- emissao de ingressos internos unitarios com QR unico por destinatario
- persistencia e rastreabilidade de arquivos compartilhados, ingressos unitarios externos, links de drive e instrucoes textuais recebidas
- fluxo de distribuicao, remanejamento, aumento, reducao e registro de problemas operacionais
- dashboard de ativos dentro do modulo Dashboard, seguindo o padrao visual e estrutural ja adotado em dashboard de leads
- contratos de API e dados suficientes para integracao com skill externa de leitura de emails

### Fora

- leitura direta de caixa de email dentro do NPBB
- desenvolvimento da skill OpenClaw neste repositorio
- implementacao completa do validador/scanner de QR no v1
- conciliacao financeira de bilheteria ou integracao completa com venda de ingressos
- redesign do modulo Dashboard fora do padrao ja homologado no produto

## 7. Resultado de Negocio e Metricas

- objetivo principal: reduzir erro operacional e tempo de distribuicao de ingressos, aumentando a confiabilidade do estoque operacional e a visibilidade executiva sobre ativos
- metricas leading: percentual de eventos com categorias configuradas; percentual de lotes com origem e artefatos rastreados; tempo entre recebimento e disponibilidade; percentual de distribuicoes com status registrado; percentual de ingressos internos emitidos com QR unico
- metricas lagging: taxa de reenvio ou erro operacional; tempo medio entre recebimento e envio final; quantidade de bloqueios por falta de recebimento; quantidade de problemas operacionais por evento; uso recorrente do dashboard pela operacao
- criterio minimo para considerar sucesso: um evento real consegue ser operado ponta a ponta com previsao, recebimento, conciliacao, emissao/distribuicao e acompanhamento no dashboard sem depender de planilha paralela como fonte de verdade

## 8. Restricoes e Guardrails

- restricoes tecnicas: a evolucao deve conviver com o modelo atual de `CotaCortesia` e `SolicitacaoIngresso` durante a transicao, sem quebrar operacoes existentes antes do rollout controlado
- restricoes operacionais: para origem `externo_recebido`, a quantidade distribuivel deve refletir o `recebido_confirmado`, mesmo quando divergir do `planejado`
- restricoes operacionais: aumentos dependentes de ticketeira ficam em estado `bloqueado_por_recebimento` ate o recebimento correspondente
- restricoes operacionais: `remanejado` significa apenas realocacao efetiva; aumento, reducao e saldo nao distribuido devem aparecer como leituras separadas
- restricoes operacionais: para v1, a dimensao `Area` do painel sera tratada como equivalente a `Diretoria` ate decisao documentada em contrario
- restricoes legais ou compliance: arquivos de ingresso, links, emails de destinatarios e QR codes devem ser tratados como dados sensiveis sob LGPD, com controle de acesso e trilha auditavel
- restricoes de prazo: priorizar um corte operacional real para ao menos um evento antes de expandir automacoes adicionais
- restricoes de design ou marca: o PDF de referencia orienta informacao e graficos, nao layout ou arte; a implementacao visual deve seguir o padrao ja usado pelo dashboard de leads

## 9. Dependencias e Integracoes

- sistemas internos impactados: modulo de `ativos`, modulo de `ingressos`, `dashboard`, catalogo de fontes em `internal/registry`, contratos de `internal/ingestao-inteligente`, workbench de `internal/revisao-humana`, servico atual de email e o dominio de eventos
- sistemas externos impactados: ticketeiras, links de drive recebidos por email, provedores de email de saida e skill operacional do OpenClaw
- dados de entrada necessarios: evento, diretoria, categoria, modo de fornecimento, quantidade planejada, quantidade recebida, arquivos ou links, instrucoes do emissor, destinatarios, status de envio, motivo de remanejamento, aumento/reducao e ocorrencias
- dados de saida esperados: inventario reconciliado, historico de distribuicao, bloqueios por recebimento, trilha de remanejamentos, registro de problemas, dashboard operacional e contratos consumiveis por integracoes externas

## 10. Arquitetura Afetada

- backend: ampliar o dominio atual para suportar configuracao de categorias por evento, dois modos canonicos de fornecimento, conciliacao `planejado x recebido`, bloqueios por recebimento, emissao interna com QR unitario, distribuicao, remanejamento, aumento, reducao e incidentes operacionais
- frontend: evoluir as telas operacionais de ativos/ingressos e adicionar `Dashboard > Ativos` com leituras separadas para planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido e problemas
- banco/migracoes: criar ou adaptar entidades para categorias por evento, previsao, recebimento, divergencia de conciliacao, artefatos de ingresso, emissao interna com QR unico, distribuicao por destinatario, eventos de ajuste e ocorrencias
- observabilidade: correlation_id e rastreabilidade entre previsao, recebimento, conciliacao, emissao, envio, bloqueio, remanejamento e problema operacional
- autorizacao/autenticacao: manter RBAC atual e endurecer acesso a artefatos sensiveis e operacoes de distribuicao
- rollout: ativacao gradual por evento, com convivencia controlada com o fluxo agregado atual ate que o corte operacional esteja validado

## 11. Riscos Relevantes

- risco de produto: tentar fechar operacao, analitico e preparacao para automacao no mesmo ciclo e diluir a entrega do primeiro evento real
- risco tecnico: formatos heterogeneos de ticketeiras e necessidade de coexistir com o modelo agregado atual aumentam a complexidade do dominio e das migracoes
- risco operacional: classificacao errada, divergencia nao conciliada ou envio duplicado pode gerar distribuicao acima do recebido, categoria incorreta ou destinatario inadequado
- risco de dados: arquivos, links e QR codes podem expor acessos indevidos se storage, expiracao e auditoria nao forem definidos cedo
- risco de adocao: a operacao pode manter planilhas paralelas se o produto nao reduzir trabalho manual de forma tangivel no primeiro evento real

## 12. Nao-Objetivos

- construir integracao nativa de inbox IMAP/Gmail/Outlook no NPBB
- desenvolver a skill OpenClaw dentro deste repositorio
- entregar o scanner/validador final de QR no v1
- usar o PRD como backlog de features, user stories ou tasks

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

- regra de negocio ainda nao definida: catalogo de categorias alem do trio inicial e politica de expansao futura
- dependencia ainda nao confirmada: estrategia final de storage, expiracao e retencao para arquivos, links e ingressos emitidos com QR
- dado ainda nao disponivel: SLA operacional de envio, retry, bounce e reenvio
- decisao de UX ainda nao fechada: drill-downs e detalhamento do painel de problemas no dashboard
- outro ponto em aberto: UX e contrato do futuro validador de QR com semantica de uso unico, previsto como etapa posterior no mesmo projeto

## 15. Perguntas que o PRD Precisa Responder

- qual e o modelo canonico de conciliacao entre `planejado`, `recebido_confirmado`, `bloqueado_por_recebimento`, `disponivel` e `distribuido`
- como representar aumento e reducao sem misturar esses estados com `remanejado`
- como persistir artefatos externos e ingressos internos emitidos com QR mantendo rastreabilidade e compliance
- qual e o contrato minimo para que a emissao com QR ja nasca preparada para validacao futura de uso unico
- quais recortes, filtros, tabelas e graficos do dashboard de ativos sao obrigatorios no v1 para operar um evento real

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
