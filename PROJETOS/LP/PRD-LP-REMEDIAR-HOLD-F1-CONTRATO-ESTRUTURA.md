---
doc_id: "PRD-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md"
version: "0.1"
status: "draft"
intake_kind: "audit-remediation"
owner: "PM"
last_updated: "2026-03-13"
origin_intake: "INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md"
origin_audit: "auditoria_fluxo_ativacao.md"
delivery_surface: "fullstack-module"
---

# PRD — LP — Remediar Hold F1: Contrato Publico e Estrutura

## Cabecalho

| Campo | Valor |
|---|---|
| Status | draft |
| Tipo | audit-remediation |
| Origem do intake | `INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md` |
| Relatorio de origem | `auditoria_fluxo_ativacao.md` |
| PRD principal relacionado | `PRD-LP-QR-ATIVACOES.md` |
| Superficie afetada | backend submit/landing, frontend landing, governanca LP |

## 1. Objetivo e Contexto

Este PRD define a remediacao minima e controlada para retirar a F1 do projeto `LP` do estado de `hold` provisional. O foco e estritamente o conjunto de nao conformidades que ainda bloqueiam a fase no estado real do repositorio em `2026-03-13`: drift de contrato no submit publico, ausencia de `lead_reconhecido` no response de submit, dependencia do frontend no endpoint legado e arquivos estruturais fora dos thresholds de manutencao.

O PRD nao reabre o produto `LP`, nao altera a tese funcional do fluxo CPF-first e nao inclui a remediacao LGPD de CPF em repouso. O objetivo e restabelecer aderencia entre PRD principal, backend e frontend, preparando uma reauditoria independente da F1.

## 2. Problema e Evidencia

- `POST /leads` ja existe como endpoint publico com `ativacao_id`, mas `GET landing` ainda devolve `submit_url` legado via `/landing/ativacoes/{id}/submit`.
- O frontend da landing usa o `submit_url` retornado e, por isso, o caminho principal de fato ainda e o endpoint legado.
- `LandingSubmitResponse` nao inclui `lead_reconhecido`, embora o PRD principal espere esse sinal no submit.
- `backend/app/models/models.py` segue com `1364` linhas e excede o threshold bloqueante.
- `backend/app/routers/ativacao.py` segue com `421` linhas e excede o threshold de alerta.
- Nao existe evidencia automatizada especifica cobrindo metadata/migracao para `conversao_ativacao`, o indice `(ativacao_id, cpf)` e `lead_reconhecimento_token`.

## 3. Escopo

### Dentro

- canonizar `POST /leads` como endpoint principal de submit publico para landing com ou sem ativacao
- alterar o payload de submit para expor `lead_reconhecido`, `conversao_registrada`, `bloqueado_cpf_duplicado` e `token_reconhecimento`
- redefinir `lead_reconhecido` no submit como "a sessao termina com reconhecimento valido para o evento apos processar a submissao"
- manter `/landing/ativacoes/{ativacao_id}/submit` como wrapper temporario com response identico ao canônico
- alterar `submit_url` do GET landing para `/leads`
- atualizar frontend e testes para enviar `event_id` e `ativacao_id` no body canônico e remover hardcodes do endpoint legado no caminho principal
- particionar `backend/app/models/models.py` sem quebrar imports existentes
- reduzir `backend/app/routers/ativacao.py` abaixo do threshold de alerta
- adicionar validacoes automatizadas de paridade e metadata para os artefatos de fundacao

### Fora

- criptografia ou tokenizacao de CPF em repouso
- remocao definitiva do wrapper legado
- qualquer mudanca funcional alem do necessario para alinhar contrato e estrutura

## 4. Contrato Publico Remediado

### 4.1 Endpoint canônico

`POST /leads` passa a ser a unica URL canônica de submit publico.

**Request**

- `event_id`: obrigatorio quando `ativacao_id` nao vier resolvido
- `ativacao_id`: opcional; quando presente, identifica o fluxo por ativacao
- `cpf`: obrigatorio quando houver `ativacao_id`
- demais campos existentes do formulario permanecem inalterados

**Response**

- `lead_id`
- `event_id`
- `ativacao_id`
- `ativacao_lead_id`
- `mensagem_sucesso`
- `lead_reconhecido`
- `conversao_registrada`
- `bloqueado_cpf_duplicado`
- `token_reconhecimento`

### 4.2 Semantica de `lead_reconhecido`

- `true` quando, ao final do processamento, existe token/cookie valido para o evento retornado ao cliente
- `true` tanto em submit bem-sucedido com ativacao quanto em bloqueio por CPF duplicado quando o sistema consegue reconhecer o lead do evento e emitir token
- `false` apenas quando o submit nao termina com sessao reconhecida valida para o evento

### 4.3 Wrapper legado

`POST /landing/ativacoes/{ativacao_id}/submit` permanece temporariamente como adaptador compativel:

- aceita o mesmo schema de body
- injeta ou valida `ativacao_id` a partir da path
- delega para o mesmo fluxo canônico de submit
- responde com payload identico ao de `POST /leads`

### 4.4 GET landing

- `GET /eventos/{evento_id}/ativacoes/{ativacao_id}/landing` continua sem regressao funcional
- `formulario.submit_url` passa a retornar `/leads`
- `formulario.event_id` e `formulario.ativacao_id` permanecem obrigatorios no payload para que o frontend consiga chamar o endpoint canônico

## 5. Implementacao e Estrutura

### EPIC-RH1-01 — Paridade do Contrato Publico

**Objetivo:** eliminar o drift entre PRD principal, backend e frontend.

**Entregas:**

- `LandingSubmitResponse` expandido com `lead_reconhecido`
- fluxo de submit unificado entre `/leads` e o wrapper legado
- frontend enviando `event_id` e `ativacao_id` no body canônico
- fixtures e testes atualizados para `submit_url=/leads`

**Criterio de aceite:**

- o caminho principal do submit publico usa `/leads`
- o wrapper legado continua funcional sem comportamento divergente
- nenhum consumidor principal depende mais de `submit_url` legado

### EPIC-RH1-02 — Refatoracao Estrutural Minima

**Objetivo:** remover a nao conformidade estrutural que hoje bloqueia F1.

**Entregas:**

- `models.py` particionado em modulos coesos, mantendo reexport/import estavel
- `ativacao.py` reduzido via extracao de helpers/servicos administrativos

**Criterio de aceite:**

- `backend/app/models/models.py` fica abaixo de `600` linhas
- `backend/app/routers/ativacao.py` fica abaixo de `400` linhas
- imports existentes de `app.models.models` continuam funcionando

### EPIC-RH1-03 — Evidencia para Reauditoria

**Objetivo:** sustentar a nova rodada de auditoria com provas automatizadas.

**Entregas:**

- testes de paridade entre `POST /leads` e `/landing/ativacoes/{id}/submit`
- testes do payload `lead_reconhecido`
- validacoes de metadata para `conversao_ativacao`, `lead_reconhecimento_token` e o indice composto

**Criterio de aceite:**

- testes falham se o wrapper legado divergir do endpoint canônico
- testes falham se a metadata perder tabela, coluna ou indice critico

## 6. Riscos e Mitigacoes

| Risco | Mitigacao |
|---|---|
| Submit canônico quebrar por falta de `event_id`/`ativacao_id` no body | atualizar frontend, fixtures e testes no mesmo ciclo |
| Refatoracao de `models.py` quebrar imports amplos | manter `app.models.models` como camada de reexport estavel |
| Wrapper legado permanecer com comportamento distinto | adicionar testes de paridade de request/response |
| Escopo inflar com LGPD | registrar explicitamente o risco como follow-up separado e fora deste sibling |

## 7. Rollback

- se a migracao para `/leads` gerar regressao inesperada, o wrapper legado continua disponivel para rollback operacional imediato
- se a refatoracao estrutural quebrar imports, a remediacao deve priorizar restaurar `app.models.models` como fachada unica
- se algum requisito extra surgir fora do escopo minimo, o trabalho deve parar e abrir novo intake, nao expandir este PRD silenciosamente

## 8. Validacao e Cenarios

- `GET landing` por evento/ativacao retorna `submit_url=/leads` e preserva flags de reconhecimento
- `POST /leads` com `ativacao_id` responde com `lead_reconhecido=true` quando termina com sessao reconhecida valida
- bloqueio por CPF duplicado em ativacao unica ainda retorna payload coerente e pode reconhecer a sessao
- `/landing/ativacoes/{id}/submit` responde exatamente como `/leads` para o mesmo caso de uso
- metadata contem `conversao_ativacao`, `lead_reconhecimento_token` e o indice `ix_conversao_ativacao_ativacao_id_cpf`
- `models.py` e `ativacao.py` ficam abaixo dos thresholds aplicaveis antes da reauditoria

## 9. Assuncoes

- a auditoria `auditoria_fluxo_ativacao.md` e a fonte oficial do hold mesmo com status `provisional`
- nao existe `DECISION-PROTOCOL.md` local em `PROJETOS/LP`
- o endpoint legado so sera removido em remediacao posterior, apos nova rodada de compatibilidade
- a remediacao LGPD de CPF em repouso continua fora deste ciclo

## 10. Referencia de Intake

Este PRD deriva exclusivamente de `INTAKE-LP-REMEDIAR-HOLD-F1-CONTRATO-ESTRUTURA.md`, com contexto adicional de `PRD-LP-QR-ATIVACOES.md`, `AUDIT-LOG.md` e `auditoria_fluxo_ativacao.md`.
