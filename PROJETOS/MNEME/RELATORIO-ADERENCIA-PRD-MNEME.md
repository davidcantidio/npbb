# Varredura de Aderência — PRD-MNEME

## Objetivo

Avaliar o `PRD-MNEME.md` em dois eixos:

1. aderência à linha conceitual original defendida na proposta anterior;
2. aderência ao plano consolidado pelas equipes especialistas na proposta `mneme_v2` e nas críticas da banca.

## Escala usada

- **Alta aderência**: o PRD cobre explicitamente o comportamento ou o transforma em feature/componente claro.
- **Aderência parcial**: o PRD cobre o tema, mas sem a granularidade ou formalização exigida.
- **Baixa aderência**: o PRD toca tangencialmente no tema ou o deixa implícito.
- **Gap**: o tema relevante no plano de referência não aparece de forma operacional suficiente no PRD.

---

## Resumo executivo

### Veredito geral

O PRD está **fortemente aderente ao framework de governança e ao eixo feature-first**.  
Ele também está **bem aderente à nossa tese original**: memória operacional em substrate transacional, retrieval híbrido, governança explícita e memória como fonte de dataset para fine-tuning.

Onde ele ainda perde aderência é justamente nas partes em que a `mneme_v2` ficou mais afiada:

- falta **Fase 0 explícita de observabilidade**;
- falta **propagação de mudança** como capacidade própria, não só como risco genérico;
- falta **incerteza epistêmica de segunda ordem** como dado de primeira classe;
- falta explicitar **compressão semântica / esquecimento construtivo** como comportamento operável;
- falta uma seção formal de **o que o sistema deliberadamente não resolve**.

### Nota de aderência

- **Governança / framework**: 9,2
- **Aderência à nossa proposta anterior**: 8,8
- **Aderência à proposta `mneme_v2`**: 8,1
- **Aderência às críticas da banca**: 7,9

**Média prática**: **8,5 / 10**

---

## Matriz de aderência por tema

| Tema | Nossa ideia original | HTML `mneme_v2` / banca | Situação no PRD | Veredito |
|---|---|---|---|---|
| Substrate transacional | central | mantido | explícito | Alta |
| Feature-first / delivery-first | central para governança | compatível | explícito | Alta |
| Ingestão canônica idempotente | implícito | explícito | explícito | Alta |
| Entity resolution | crítica antiga | pipeline NER/coreference/provisório | feature dedicada | Alta |
| Candidate facts vs facts consolidados | central | central | explícito | Alta |
| Supersessão tipada com justificativa | desejável | explícito | parcial | Parcial |
| Quórum / governança do estado canônico | desejável | explícito | parcial | Parcial |
| Retrieval híbrido | central | central | explícito | Alta |
| Exploration bonus / anti-echo | desejável | explícito | parcial | Parcial |
| Inibição por recuperação | ausente no PRD inicial | explícito | parcial | Parcial |
| Compressão semântica / esquecimento construtivo | ausente no PRD inicial | explícito | Gap | Gap |
| Janela de labilidade | sugerida | explícita | parcial | Parcial |
| Propagação de mudança | crítica antiga | explícita | apenas implícita em risco/rollback | Gap |
| Garantia de entrega + WAL | importante | explícito | parcial | Parcial |
| Fase 0 de observabilidade | não explícita | explícita | ausente como fase | Gap |
| Memória como dataset | central | central | explícito | Alta |
| Curadoria / elegibilidade de exemplos | central | central | explícito | Alta |
| Incerteza epistêmica de segunda ordem | não estava madura antes | explícita | ausente | Gap |
| Declaração formal de limites do sistema | recomendada pela banca | explícita | parcial via não-objetivos | Parcial |

---

## Aderência ao framework e governança

### O que está muito correto

1. O PRD usa **Features do Projeto** como eixo principal, e arquitetura aparece como impacto por feature, exatamente como o framework reformulado exige.
2. A cadeia `Intake -> PRD -> Features -> User Stories -> Tasks` está preservada.
3. O PRD respeita a ideia de que fundação compartilhada é **exceção documentada**, não eixo do projeto.
4. A decomposição em US pequenas e rastreabilidade mínima `feature -> fase -> épico -> issue` está alinhada ao framework.

### O que ainda falta

1. O PRD ainda não referencia o `INTAKE-MNEME.md` porque ele não existia; isso agora deixa de ser desculpa.
2. O PRD deveria sair em versão seguinte copiando do intake as taxonomias e a rastreabilidade de origem, em vez de manter `a criar` em `Intake de origem`.
3. O projeto ainda não traduziu as features em manifestos de feature / épicos / issues conforme o modelo operacional canônico.

### Veredito

**Aderência alta ao framework.**  
O desvio restante é de estado do artefato, não de filosofia.

---

## Aderência à nossa proposta anterior

### Cobertura alta

O PRD cobre bem os pilares que tínhamos defendido:

- memória episódica, semântica e procedural;
- substrate em Postgres;
- retrieval híbrido;
- governança, auditoria e rollback;
- learning loop com `training_examples`;
- separação entre registro, consolidação, recuperação e treino.

### Cobertura parcial

A proposta anterior já pressionava por:
- governança mais explícita da verdade;
- reconsolidação/repriorização;
- dataset lineage;
- rollback epistemológico completo.

O PRD absorveu bastante disso, mas ainda de forma desigual: o arcabouço está lá, porém alguns temas ainda estão “embutidos” em features genéricas quando deveriam aparecer como capacidades nomeadas.

### Veredito

**Alta aderência conceitual.**  
O PRD honra a tese central.

---

## Aderência à proposta `mneme_v2`

### 1. Sofia — esquecimento construtivo, RII e labilidade

`mneme_v2` introduz:
- `semantic_compression_jobs`
- `retrieval_inhibition_log`
- estado `labile`
- argumento forte de que “esquecer é feature”【referência: mneme_v2, slide de Sofia】

#### No PRD
- há menção a labilidade e saliência;
- há menção a `retrieval_inhibition_log` na Feature 4;
- **não existe feature ou comportamento nomeado para compressão semântica / esquecimento construtivo**.

#### Veredito
**Aderência parcial.**  
O PRD pegou a metade operacional e deixou a metade cognitiva no vácuo.

#### Delta recomendado
Criar uma **Feature 3B ou subcomportamento explícito**:

- compressão semântica programada;
- redução controlada de detalhe episódico;
- medição de `quality_delta`;
- policy de promoção/redução entre episódio, fact e summary.

---

### 2. René — supersessão tipada, justificativa e quórum

`mneme_v2` explicita:
- `reason_type` em supersessão;
- `justification not null`;
- `evidence_ids`;
- quórum para fatos críticos;
- `confidence_variance` e `source_agreement`【referência: mneme_v2, slide de René】

#### No PRD
- supersessão justificada existe;
- aprovação/quórum aparece de forma genérica;
- **não aparecem explicitamente `confidence_variance` nem `source_agreement`**.

#### Veredito
**Aderência parcial-alta.**

#### Delta recomendado
Adicionar nos critérios de aceite da consolidação:

- suporte explícito a `reason_type`;
- campo obrigatório de justificativa;
- suporte a `source_agreement`;
- suporte a incerteza de segunda ordem (`confidence_variance`).

---

### 3. Yuki — entity resolution e anti-echo

`mneme_v2` resolve:
- NER + normalização + coreference;
- entidades provisórias com review;
- `exploration_bonus(days_since_last_access)` para evitar eco mnemônico【referência: mneme_v2, slide de Yuki】

#### No PRD
- entity resolution foi coberto bem;
- existe feature dedicada e entidades provisórias;
- risco de câmara de eco foi citado;
- **exploration bonus ainda não é critério de aceite explícito**.

#### Veredito
**Aderência alta em entity resolution; parcial em anti-echo.**

#### Delta recomendado
Amarrar na Feature 4:

- fórmula de ranking com componente de exploração;
- teste de regressão contra dominância excessiva de fatos quentes.

---

### 4. Rafael — propagação, idempotência, WAL e fase 0

`mneme_v2` explicitou:
- `fact_dependencies`
- `propagation_queue`
- `idempotency_key`
- `write_ahead_log`
- `memory_metrics`
- fase 0 de observabilidade【referência: mneme_v2, slide de Rafael】

#### No PRD
- `fact_dependencies` aparece;
- idempotência aparece na ingestão;
- observabilidade existe como feature posterior;
- **propagação de mudança não virou feature operacional explícita**;
- **WAL não aparece explicitamente**;
- **fase 0 não existe**.

#### Veredito
**Aderência parcial. Aqui está a maior lacuna.**

#### Delta recomendado
1. Adicionar **Fase 0 — Instrumentação e Baseline de Observabilidade**.
2. Quebrar propagação de mudança em comportamento explícito:
   - enfileirar propagação;
   - recalcular derivados;
   - rastrear tentativas/falhas;
   - invalidar sumários e sinalizar conflitos.
3. Tornar WAL / fila segura / garantias de entrega parte dos critérios da ingestão e consolidação.

---

### 5. Laila — memória como currículo

`mneme_v2` formaliza `training_examples` com:
- `context_snapshot`
- `query_text`
- `retrieved_fact_ids`
- `agent_response`
- `outcome_quality`
- `quality_source`
- `task_type`
- `curated`
- `split`【referência: mneme_v2, slide de Laila】

#### No PRD
- a Feature 6 está bastante aderente;
- elegibilidade, versionamento e export foram contemplados;
- ainda falta explicitar melhor:
  - lineage entre memory/facts/examples/datasets;
  - critérios negativos de exclusão;
  - avaliação de regressão pós-fine-tuning.

#### Veredito
**Aderência alta.**

#### Delta recomendado
Tornar obrigatório na Feature 6:
- `dataset lineage graph`;
- política de exclusão negativa;
- benchmark mínimo pós-export.

---

## Aderência às críticas da banca

### Críticas já cobertas pelo PRD

- entity resolution como problema real;
- necessidade de rollback;
- necessidade de governança;
- necessidade de dataset curado;
- necessidade de declarar limites do sistema.

### Críticas só parcialmente cobertas

- substituição da analogia frouxa de reconsolidação;
- política concreta de esquecimento construtivo;
- modelo explícito de propagação de mudança;
- governança do estado canônico com justificativa forte;
- fase 0 de observabilidade;
- seção formal “o que o sistema deliberadamente não resolve”.

### Veredito

**O PRD responde ao espírito da banca, mas não cobre integralmente o plano corretivo que a própria banca consolidou depois.**

---

## Gaps prioritários para corrigir no PRD

### Gap 1 — Fase 0 de Observabilidade
**Prioridade:** crítica

Sem instrumentação inicial, o projeto nasce operando no escuro.  
Hoje o PRD só coloca observabilidade na fase final.

### Gap 2 — Propagação de Mudança Explícita
**Prioridade:** crítica

Hoje está implícita em `fact_dependencies` e rollback.  
Precisa virar feature/comportamento operacional, com fila, status e idempotência.

### Gap 3 — Compressão Semântica / Esquecimento Construtivo
**Prioridade:** alta

Sem isso, o PRD ainda descreve memória que registra muito bem e abstrai pouco.

### Gap 4 — Incerteza Epistêmica de Segunda Ordem
**Prioridade:** alta

Falta modelar não só “confiança no fato”, mas “confiança na confiança”.

### Gap 5 — Limites Deliberados do Sistema
**Prioridade:** média-alta

O PRD tem não-objetivos, mas ainda não tem uma seção direta com:
- verdade do mundo real;
- viés de origem;
- catastrophic forgetting do modelo;
- latência entre evento e fato canônico.

---

## Deltas recomendados no PRD

### Delta A — Inserir Fase 0
Antes da Fase 1, incluir:

- baseline de observabilidade;
- métricas mínimas;
- alertas iniciais;
- event tracing.

### Delta B — Quebrar propagação em feature própria
Opções:
- **Feature 3B: Propagação de Mudança e Recomputação Derivada**
ou
- expandir Feature 5 com comportamento explícito e critérios de aceite fortes.

### Delta C — Tornar compressão semântica explícita
Adicionar à consolidação:
- jobs de compressão;
- triggers;
- avaliação antes/depois;
- critérios de preservação de fatos críticos.

### Delta D — Fortalecer epistemologia operacional
Adicionar aos facts/supersession:
- `reason_type`
- `justification`
- `evidence_ids`
- `source_agreement`
- `confidence_variance`

### Delta E — Fortalecer o learning loop
Adicionar na curadoria:
- lineage completo;
- exclusões negativas;
- benchmark obrigatório;
- regra de rollback de dataset/model adapter afetado.

---

## Decisão prática

### Decisão

**PRD APROVADO COM AJUSTES OBRIGATÓRIOS**

### O que já está bom o bastante para seguir
- intake canônico agora existe;
- eixo feature-first está certo;
- as 7 features atuais formam uma base válida;
- a tese principal do sistema está preservada.

### O que precisa entrar na próxima revisão do PRD
1. fase 0 de observabilidade;
2. propagação de mudança explícita;
3. compressão semântica / esquecimento construtivo;
4. incerteza de segunda ordem;
5. seção “o que o sistema deliberadamente não resolve”.

---

## Recomendação final

Se a meta é só “ter um PRD que passa na governança”, ele já passa.

Se a meta é “ter um PRD fiel ao melhor plano apresentado pelas equipes especialistas”, ele ainda precisa de uma revisão v0.2.

A diferença entre os dois cenários é pequena no documento e enorme na operação.
