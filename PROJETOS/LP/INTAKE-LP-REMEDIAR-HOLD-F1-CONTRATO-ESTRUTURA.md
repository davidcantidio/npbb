---
doc_id: "INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-13"
project: "LP"
intake_kind: "audit-remediation"
source_mode: "audit-derived"
origin_project: "LP"
origin_phase: "F1-FUNDACAO-MODELO-BACKEND"
origin_audit_id: "auditoria_fluxo_ativacao.md"
origin_report_path: "/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/LP/auditoria_fluxo_ativacao.md"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "landing-pages"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend/app/routers/leads.py"
  - "backend/app/routers/landing_public.py"
  - "backend/app/services/landing_pages.py"
  - "frontend/src/pages/EventLandingPage.tsx"
  - "backend/app/models/models.py"
change_type: "correcao-estrutural"
audit_rigor: "strict"
---

# INTAKE - LP - REMEDIAR HOLD F1 CONTRATO E ESTRUTURA

## 0. Rastreabilidade de Origem

- projeto de origem: `LP`
- fase de origem: `F1-FUNDACAO-MODELO-BACKEND`
- auditoria de origem: `auditoria_fluxo_ativacao.md`
- relatorio de origem: `/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/LP/auditoria_fluxo_ativacao.md`
- motivo da abertura deste intake: regularizar o hold provisional de F1 e abrir uma remediacao controlada para o drift de contrato do submit publico, a ausencia de `lead_reconhecido` no response e o monolitismo estrutural identificado na auditoria

## 1. Resumo Executivo

- nome curto da iniciativa: `REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA`
- tese em 1 frase: alinhar o submit publico ao contrato canônico `POST /leads`, remover drift entre backend e frontend e reduzir o monolitismo estrutural minimo necessario para permitir a reauditoria de F1
- valor esperado em 3 linhas:
  eliminar o motivo material do hold em contrato publico e payload de submit
  restaurar rastreabilidade entre PRD, endpoint real e frontend da landing
  reduzir risco de manutencao imediata ao retirar `models.py` e `ativacao.py` da zona de nao conformidade estrutural

## 2. Problema ou Oportunidade

- problema atual: o projeto `LP` implementa `POST /leads` para submit publico com `ativacao_id`, mas o `GET landing` e o frontend ainda apontam para `/landing/ativacoes/{id}/submit`; alem disso o response publico nao expoe `lead_reconhecido` e a base estrutural segue com `models.py` acima do threshold bloqueante e `ativacao.py` acima do threshold de alerta
- evidencia do problema: auditoria `auditoria_fluxo_ativacao.md`; verificado no repo em `2026-03-13` que `backend/app/services/landing_pages.py` ainda gera `submit_url` legado, `backend/app/schemas/landing_public.py` nao inclui `lead_reconhecido` em `LandingSubmitResponse`, `frontend` e testes consomem `/landing/ativacoes/{id}/submit`, `backend/app/models/models.py` possui `1364` linhas e `backend/app/routers/ativacao.py` possui `421`
- custo de nao agir: o gate F1 permanece em hold, o frontend continua acoplado a um contrato divergente do PRD, a reauditoria volta a encontrar drift funcional e a manutencao segue arriscada por arquivos monoliticos
- por que agora: a fase F1 ja foi marcada como hold provisional e precisa de remediacao objetiva antes de qualquer nova rodada de auditoria

## 3. Publico e Operadores

- usuario principal: equipe de engenharia que mantem o fluxo publico de landing e submit de leads
- usuario secundario: auditoria tecnica e PM responsavel pelo gate de F1
- operador interno: time de produto/engenharia do NPBB
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: tirar F1 de hold corrigindo o contrato publico de submit e a nao conformidade estrutural minima sem reabrir o escopo funcional do projeto `LP`
- jobs secundarios: manter compatibilidade temporaria do endpoint legado; aumentar a evidência automatizada de metadata/migracao; permitir nova auditoria com rastreabilidade clara
- tarefa atual que sera substituida: conviver com drift entre PRD, landing e endpoint de submit e com arquivos monoliticos fora do spec

## 5. Fluxo Principal Desejado

1. O `GET landing` continua montando o contexto de landing por evento/ativacao, mas passa a apontar `submit_url` para `POST /leads`
2. O frontend envia `event_id` e `ativacao_id` no submit publico usando o contrato canônico
3. `POST /leads` passa a responder com `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado` e `token_reconhecimento`
4. O endpoint legado `/landing/ativacoes/{id}/submit` permanece apenas como wrapper temporario e com payload de resposta identico ao canônico
5. A estrutura do backend e particionada para remover `models.py` da zona bloqueante e reduzir `ativacao.py` abaixo do alerta
6. A base de testes valida paridade de contrato e a existencia de tabelas/indice criticos da fundacao

## 6. Escopo Inicial

### Dentro

- canonizar `POST /leads` como submit publico para fluxo com ativacao
- incluir `lead_reconhecido` no response publico e alinhar sua semantica
- manter wrapper legado apenas por compatibilidade temporaria
- trocar `submit_url` das landings para o endpoint canônico
- atualizar frontend, fixtures e testes para remover hardcode do endpoint legado
- particionar `backend/app/models/models.py`
- reduzir `backend/app/routers/ativacao.py`
- adicionar validacoes automatizadas de metadata/paridade para `conversao_ativacao`, indice `(ativacao_id, cpf)` e `lead_reconhecimento_token`

### Fora

- redesenho funcional do fluxo CPF-first ou da UX da landing
- remediacao LGPD de CPF em repouso
- mudanca de regras de reconhecimento entre eventos
- remocao imediata do endpoint legado antes da migracao completa dos consumidores

## 7. Resultado de Negocio e Metricas

- objetivo principal: destravar a reauditoria de F1 com aderencia de contrato e saude estrutural minima
- metricas leading: `submit_url` emitido como `/leads`; response publico com `lead_reconhecido`; nenhum arquivo acima dos thresholds aplicaveis na area remediada; testes novos de paridade e metadata passando
- metricas lagging: fase F1 reapresentada em auditoria sem reincidencia dos achados materiais de contrato e monolitismo
- criterio minimo para considerar sucesso: frontend e backend convergem em `/leads`, wrapper legado permanece com comportamento identico, `models.py` e `ativacao.py` saem da nao conformidade e a fase volta a estar apta para nova auditoria

## 8. Restricoes e Guardrails

- restricoes tecnicas: nao quebrar imports publicos de `app.models.models`; a compatibilidade do endpoint legado deve ser mantida ate a migracao de consumidores; a remediacao deve ser minima e rastreavel
- restricoes operacionais: o gate de F1 permanece `hold` ate nova auditoria; o intake nao deve inflar o escopo com LGPD em repouso
- restricoes legais ou compliance: CPF continua sendo dado sensivel e o risco deve ser explicitamente mantido fora deste sibling
- restricoes de prazo: concluir no mesmo ciclo de remediacao do hold para permitir reauditoria
- restricoes de design ou marca: nao aplicavel

## 9. Dependencias e Integracoes

- sistemas internos impactados: landing publica, submit de leads, roteamento backend, schemas publicos, testes backend/frontend, manifestos `LP`
- sistemas externos impactados: nenhum
- dados de entrada necessarios: payload atual das landings, endpoint `POST /leads`, endpoint legado `/landing/ativacoes/{id}/submit`, estrutura atual de `models.py` e `ativacao.py`
- dados de saida esperados: contrato canônico unificado, response com `lead_reconhecido`, `submit_url` ajustado, arquivos estruturais particionados e evidencias automatizadas para reauditoria

## 10. Arquitetura Afetada

- backend: `routers/leads.py`, `routers/landing_public.py`, `services/landing_pages.py`, `services/landing_page_submission.py`, `schemas/landing_public.py`, `models/`
- frontend: `pages/EventLandingPage.tsx`, `services/landing_public.ts`, fixtures e testes de landing
- banco/migracoes: sem nova tabela obrigatoria; validar tabelas `conversao_ativacao` e `lead_reconhecimento_token` e o indice `ix_conversao_ativacao_ativacao_id_cpf`
- observabilidade: nao aplicavel nesta remediacao
- autorizacao/autenticacao: sem mudanca de superficie; manter cookie/token de reconhecimento e compatibilidade do wrapper
- rollout: backend e frontend devem sair juntos para eliminar dependencias do endpoint legado no caminho principal

## 11. Riscos Relevantes

- risco de produto: migrar `submit_url` sem enviar `event_id`/`ativacao_id` no payload quebraria o submit publico
- risco tecnico: particionar `models.py` sem preservar export estavel pode quebrar imports amplos do backend
- risco operacional: manter dois endpoints sem testes de paridade perpetua drift
- risco de dados: CPF em claro continua existindo e deve permanecer documentado como follow-up fora deste escopo
- risco de adocao: se fixtures e testes nao forem migrados, a equipe continua lendo o contrato legado como principal

## 12. Nao-Objetivos

- nao resolver criptografia/tokenizacao do CPF neste ciclo
- nao remover o endpoint legado no mesmo passo em que o frontend migra
- nao redesenhar outras fases de `LP`
- nao introduzir novos requisitos funcionais para landing, operador ou metricas

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: a auditoria F1 detectou que o submit publico real do fluxo por ativacao esta ancorado em `/landing/ativacoes/{id}/submit`, enquanto o PRD declara `POST /leads`; o payload publico nao expoe `lead_reconhecido`; `models.py` e `ativacao.py` excedem os thresholds aplicaveis
- impacto operacional: reauditoria da fase falha, frontend e testes continuam acoplados ao contrato legado e o backend permanece mais dificil de auditar e manter
- evidencia tecnica: `backend/app/routers/leads.py` ja implementa `POST /leads` com `ativacao_id`; `backend/app/services/landing_pages.py` ainda constroi `submit_url` legado; `backend/app/schemas/landing_public.py` nao inclui `lead_reconhecido` em `LandingSubmitResponse`; `frontend/src/pages/EventLandingPage.tsx` submete para o `submit_url` retornado; `frontend` e `backend/tests/test_landing_public_endpoints.py` seguem fixados em `/landing/ativacoes/{id}/submit`; `backend/app/models/models.py` tem `1364` linhas e `backend/app/routers/ativacao.py` tem `421`
- componente(s) afetado(s): contrato de landing publica, submit publico de leads, schemas de resposta, frontend de landing, testes de contrato e arquivos estruturais `models.py` e `ativacao.py`
- riscos de nao agir: nova auditoria reencontra os mesmos blockers, o endpoint legado permanece sendo o caminho principal de fato e o monolitismo segue sem controle

## 14. Lacunas Conhecidas

- a auditoria original nao traz commit SHA nem frontmatter canônico completo; a regularizacao assume o filename `auditoria_fluxo_ativacao.md` como identificador de origem
- a remediacao LGPD de CPF em claro ainda nao tem intake proprio aberto
- a retirada definitiva do wrapper legado depende de uma rodada posterior de limpeza apos a migracao dos consumidores

## 15. Perguntas que o PRD Precisa Responder

- qual semantica final de `lead_reconhecido` deve valer para submit com sucesso e submit bloqueado por CPF duplicado
- como manter compatibilidade do endpoint legado sem preservar drift no caminho principal
- como particionar `models.py` mantendo imports estaveis e sem regressao de metadata
- quais testes minimos comprovam paridade entre `/leads` e o wrapper legado e validam metadata/migracao da fundacao

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
