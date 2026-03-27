---
doc_id: "PRD-MNEME-v1.0.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-25"
project: "MNEME"
intake_ref: "INTAKE-MNEME.md"
intake_version: "0.1"
intake_kind: "new-capability"
source_mode: "backfilled"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "INTAKE-MNEME.md + RELATORIO-ADERENCIA-PRD-MNEME.md + mneme.md + mneme_v2_symposium_presentation.html + simposio_banca_avaliacao.html"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "governanca"
criticality: "critica"
data_sensitivity: "lgpd"
integrations:
  - "PostgreSQL"
  - "pgvector"
  - "Object Storage"
  - "Message Queue/Event Bus"
  - "LLM Inference Provider"
  - "Fine-tuning Pipeline"
  - "Observability Stack"
change_type: "nova-capacidade"
audit_rigor: "strict"
---

# PRD - MNEME v1.0

> **Estado deste documento:** versão-alvo “nota 10” do PRD, corrigida para aderir integralmente à ideia original de `mneme.md`, às melhorias formalizadas em `mneme_v2` e às críticas da banca.
>
> Esta versão fecha quatro lacunas finais:
>
> - a **camada humana em Markdown** agora é feature explícita;
> - **Identity Memory** e **Procedural Memory** agora existem como capacidades próprias;
> - a **proveniência justificativa** ficou mais dura e contratual;
> - o **anti-echo / exploration bonus** saiu do campo da intenção e virou requisito operacional.

## 0. Rastreabilidade

- **Intake de origem**: `INTAKE-MNEME.md`
- **Versão do intake**: `0.1`
- **PRD anterior**: `PRD-MNEME-v0.2.md`
- **Artefatos arquiteturais de referência**:
  - `mneme.md`
  - `mneme_v2_symposium_presentation.html`
  - `simposio_banca_avaliacao.html`
- **Motivo da revisão**:
  - alcançar aderência máxima à arquitetura-alvo;
  - transformar elementos antes “conceituais” em comportamento implementável;
  - preservar a filosofia `feature-first` sem perder fidelidade arquitetural.

## 1. Resumo Executivo

- **Nome do projeto**: MNEME
- **Tese em 1 frase**: Construir uma plataforma de memória operacional para agentes de IA em que eventos, identidade, procedimento, fatos, governança, recuperação, views humanas e dataset de treino formem um mesmo ciclo auditável de operação e aprendizado.
- **Valor esperado em 3 linhas**:
  - reduzir contradição, perda de contexto e dependência da janela de contexto;
  - permitir memória multiagente governada, explicável, reversível e útil em runtime;
  - converter operação validada em dataset de fine-tuning com lineage, curadoria negativa e rollback.

## 2. Problema ou Oportunidade

- **Problema atual**:
  - agentes operam com memória fragmentada entre contexto transitório, arquivos legíveis e heurísticas locais;
  - fatos do mundo, regras de ação e identidade do agente tendem a se misturar;
  - a operação produz dados valiosos, mas sem governança eles não viram dataset confiável.
- **Evidência do problema**:
  - o modelo original baseado em `MEMORY.md`, notas diárias e knowledge graph em arquivos é excelente para ergonomia humana, mas fraco como substrate primário em regime concorrente;
  - a própria arquitetura evoluiu para exigir fatos atômicos, supersessão, decay, retrieval híbrido, propagação e dataset lineage;
  - a banca cobrou explicitamente entity resolution, propagação de mudança, terminologia mais precisa que “reconsolidação”, governança do estado canônico e uma seção honesta de limites.
- **Custo de não agir**:
  - memória continua agindo como cache sofisticado;
  - operadores continuam reexplicando contexto;
  - o sistema aprende pouco com a própria operação;
  - erro local pode ser fossilizado por retrieval e por treino.
- **Por que agora**:
  - o substrate já foi decidido;
  - a ontologia da memória já está madura;
  - o próximo gargalo não é “mais modelo”, é “melhor memória + melhor governança”.

## 3. Público e Operadores

- **Usuário principal**: times que operam agentes de IA com tarefas recorrentes e exigência de rastreabilidade.
- **Usuário secundário**: PMs, engenheiros de IA, pesquisadores, auditores e operadores de plataforma.
- **Operador interno**: workers de ingestão, resolução de entidades, consolidação, propagação, retrieval, renderização, curadoria de dataset, avaliação e rollback.
- **Quem aprova ou patrocina**: liderança de produto/plataforma responsável pelo runtime dos agentes e pela política de memória/treino.

## 4. Jobs to be Done

- **Job principal**: dar a um agente de IA uma memória operacional persistente, governada e útil para agir melhor e aprender melhor.
- **Jobs secundários**:
  - registrar eventos e episódios com replay e proveniência;
  - manter memória identitária e procedural separadas da semântica;
  - consolidar fatos, relações e conflitos sem apagar histórico;
  - propagar mudanças e recomputar derivados;
  - servir memory packets explicáveis em runtime;
  - renderizar views humanas legíveis em Markdown;
  - derivar dataset de treino com elegibilidade, exclusão e lineage.
- **Tarefa atual que será substituída**:
  - memória improvisada em contexto;
  - arquivos como truth layer primário;
  - fine-tuning oportunista sem curadoria.

## 5. Escopo

### Dentro

- memória episódica, semântica, identitária e procedural;
- ingestão multiagente idempotente;
- entity resolution com NER/coreference e revisão;
- facts candidatos, consolidação, supersessão tipada e incerteza de segunda ordem;
- propagação de mudança, compressão semântica e recomputação derivada;
- retrieval híbrido com anti-echo formal;
- views humanas em Markdown como materializações governadas;
- governança, auditoria, lineage e rollback epistemológico;
- curadoria de `training_examples`, versionamento de dataset e export de treino;
- observabilidade desde a fase 0.

### Fora

- treinamento de foundation model do zero;
- verdade externa universal;
- UX final para usuário leigo no MVP;
- automação irrestrita de ações externas de alto risco;
- eliminação completa de revisão humana para fatos críticos.

## 6. Resultado de Negócio e Métricas

- **Objetivo principal**: colocar em produção uma plataforma de memória operacional que aumente precisão, reduza contradição e habilite especialização incremental confiável.
- **Métricas leading**:
  - `% de eventos relevantes persistidos com idempotência`;
  - `% de facts com justificativa, evidência e lineage completos`;
  - `latência p95 de retrieval`;
  - `% de conflitos resolvidos com `reason_type``;
  - `% de derivados recomputados sem falha`;
  - `% de exemplos curados aprovados para treino`;
  - `% de views Markdown materializadas sem drift do canônico`.
- **Métricas lagging**:
  - redução de contradições em respostas;
  - aumento de precisão factual em tarefas recorrentes;
  - redução de retrabalho humano por perda de contexto;
  - melhoria em benchmark interno após fine-tuning incremental;
  - queda de incidentes por memória contaminada não detectada.
- **Critério mínimo para considerar sucesso**:
  - o agente reconstrói seu estado a partir da memória persistida;
  - memória identitária e procedural são recuperadas corretamente em contextos distintos;
  - mudança em fato relevante propaga para derivados, views humanas e dataset lineage;
  - existe rollback ponta a ponta de memória e dataset.

## 7. Restrições e Guardrails

- **Restrições técnicas**:
  - PostgreSQL como store canônico inicial;
  - múltiplos writers simultâneos;
  - toda escrita crítica precisa ser idempotente, auditável e reprocessável;
  - retrieval não pode depender apenas de embeddings;
  - views humanas não podem ser truth layer primária.
- **Restrições operacionais**:
  - intake e PRD exigem aprovação humana;
  - fatos críticos exigem política de aprovação/quórum;
  - alterações manuais em Markdown devem gerar change request, não overwrite direto do canônico.
- **Restrições legais ou compliance**:
  - memória e dataset podem conter dados pessoais;
  - export para treino exige elegibilidade, anonimização, retenção e lineage;
  - retenção por classe de dado deve ser auditável.
- **Restrições de prazo**:
  - rollout incremental por fases.
- **Restrições de design**:
  - console inicial utilitário;
  - legibilidade e auditabilidade acima de acabamento visual.

## 8. Dependências e Integrações

- **Sistemas internos impactados**:
  - runtime dos agentes;
  - pipeline de avaliação;
  - observabilidade/alerting;
  - auditoria;
  - policy engine;
  - renderização de artefatos humanos.
- **Sistemas externos impactados**:
  - LLM provider;
  - stack de fine-tuning;
  - fila/event bus;
  - object storage;
  - autenticação do console.
- **Dados de entrada necessários**:
  - mensagens;
  - chamadas de ferramenta;
  - eventos de execução;
  - feedback explícito;
  - sinais implícitos de outcome;
  - políticas de risco;
  - resultados de avaliação.
- **Dados de saída esperados**:
  - eventos canônicos;
  - episódios;
  - entidades, facts, relações;
  - `memory_packets`;
  - `MEMORY.md`, `memory/YYYY-MM-DD.md`, `entities/<slug>/summary.md` e snapshots derivados;
  - `training_examples` e datasets versionados;
  - métricas, alertas e auditoria.

## 9. Arquitetura Geral do Projeto

- **Backend**:
  - APIs de ingestão, resolução, consolidação, propagação, retrieval, renderização, governança, dataset e rollback.
- **Frontend**:
  - console operacional para busca, conflito, lineage, dataset, views humanas e auditoria.
- **Banco/migrações**:
  - Postgres + `pgvector`;
  - tabelas de eventos, episódios, identidade, procedimentos, entidades, facts, relações, dependências, datasets, views derivadas e auditoria.
- **Observabilidade**:
  - métricas desde a fase 0 para ingestão, consolidação, propagação, retrieval, renderização, dataset yield e regressão.
- **Autorização/autenticação**:
  - RBAC por domínio, risco e tenant.
- **Rollout**:
  - fase 0 baseline;
  - fase 1 ingestão e memória base;
  - fase 2 consolidação e propagação;
  - fase 3 retrieval, views humanas e governança;
  - fase 4 learning loop.

## 10. Riscos Globais

- **Risco de produto**:
  - sistema excelente para auditoria e mediano para runtime.
- **Risco técnico**:
  - entity resolution ruim;
  - propagação incompleta;
  - renderização humana divergindo do canônico;
  - anti-echo mal calibrado;
  - lineage quebrado.
- **Risco operacional**:
  - backlog de revisão;
  - operadores editando view como se fosse truth layer;
  - workers falhando em cascata.
- **Risco de dados**:
  - treino contaminado;
  - vazamento em exports;
  - reward hacking por proxy ruim.
- **Risco de adoção**:
  - uso da plataforma só como “log bonito”.

## 11. Não-Objetivos

- substituir julgamento humano para fatos críticos;
- prometer verdade externa perfeita;
- resolver todo o multitenancy global no MVP;
- treinar continuamente sem curadoria;
- transformar toda memória em treino.

## 12. Limites Deliberados do Sistema

O sistema **não resolve**:

- grounding universal com o mundo;
- neutralidade epistemológica em domínios políticos/institucionais;
- correção automática de todos os vieses de origem;
- eliminação total de latência entre evento e fato canônico;
- esquecimento catastrófico do modelo final apenas via qualidade de dataset.

O sistema **pretende**:

- tornar o erro rastreável;
- tornar o conflito explícito;
- separar fato, regra e identidade;
- servir memória útil em runtime;
- impedir que o treino ignore governança.

---

# 13. Features do Projeto

## Feature 1: Ingestão Canônica de Eventos e Episódios

- **depende_de**: []

### Objetivo de Negócio
Garantir base confiável para toda a memória.

### Comportamento Esperado
Agentes e serviços publicam eventos com idempotência, replay e agrupamento em episódios.

### Critérios de Aceite
- [ ] eventos possuem `source_type`, `source_ref`, `actor`, `timestamp`, `idempotency_key` e `payload`
- [ ] duplicatas são evitadas por chave idempotente
- [ ] episódios podem ser materializados a partir de eventos relacionados
- [ ] existe replay controlado por intervalo, entidade ou fonte
- [ ] `write_ahead_log` protege candidatos de fato entre ingestão e consolidação
- [ ] a entrega é compatível com `at-least-once`

### Riscos Específicos
- write amplification
- inconsistência de payload
- retenção excessiva

### Estratégia de Implementação
1. **Modelagem e Migration**: `raw_events`, `episodes`, `ingestion_failures`, `event_replay_jobs`, `write_ahead_log`
2. **API**: ingestão, replay e status
3. **UI**: fila de ingestão e replay
4. **Testes**: idempotência, replay, retry, ordering

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `raw_events`, `episodes`, `write_ahead_log` | trilha e replay |
| Backend | `/events`, `/episodes`, `/replay` | ingestão canônica |
| Frontend | console de ingestão | status, replay |
| Testes | suíte de ingestão | dedupe, ordering |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-1.1 | Registrar evento bruto com idempotência | 3 | - |
| US-1.2 | Agrupar eventos em episódios consultáveis | 5 | US-1.1 |
| US-1.3 | Reprocessar eventos com replay controlado | 5 | US-1.1 |

---

## Feature 2: Identity Memory e Procedural Memory

- **depende_de**: ["Feature 1"]

### Objetivo de Negócio
Separar “como o agente deve operar” de “o que aconteceu no mundo”.

### Comportamento Esperado
O sistema mantém memória identitária e procedural como camadas distintas, recuperáveis por contexto e governadas por risco.

### Critérios de Aceite
- [ ] existe store explícito de `agent_identity`
- [ ] existe store explícito de `procedures`
- [ ] regras procedurais podem ter `trigger_conditions`, `approval_policy` e `risk_level`
- [ ] memória identitária pode renderizar `MEMORY.md`
- [ ] regras procedurais podem ser recuperadas em runtime sem misturar com facts semânticos

### Riscos Específicos
- confundir preferência do usuário com política operacional
- policy drift
- regra procedural virar fato indevido

### Estratégia de Implementação
1. **Modelagem e Migration**: `agent_identity`, `procedures`, `identity_change_log`
2. **API**: leitura/escrita governada de identidade e procedimentos
3. **UI**: edição controlada e auditoria
4. **Testes**: recuperação contextual, política por risco, renderização de `MEMORY.md`

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `agent_identity`, `procedures` | camadas distintas |
| Backend | `/identity`, `/procedures` | CRUD governado |
| Frontend | editor/auditoria | revisão humana |
| Testes | suíte identity/procedural | recuperação correta |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-2.1 | Persistir identidade operacional do agente | 3 | US-1.1 |
| US-2.2 | Persistir regras procedurais com política e risco | 5 | US-2.1 |
| US-2.3 | Recuperar identidade e procedimentos por contexto | 5 | US-2.2 |

---

## Feature 3: Resolução de Entidades e Objetos de Memória

- **depende_de**: ["Feature 1"]

### Objetivo de Negócio
Evitar fragmentação em aliases, nomes ambíguos e entidades duplicadas.

### Comportamento Esperado
O sistema faz NER, normalização, coreference e resolução com fila de revisão para baixa confiança.

### Critérios de Aceite
- [ ] menções são extraídas e normalizadas
- [ ] entidades existentes podem ser resolvidas com score de confiança
- [ ] baixa confiança gera entidade provisória
- [ ] merges e splits deixam log auditável
- [ ] há fila de revisão para entidades provisórias

### Riscos Específicos
- falso merge
- explosão de entidades provisórias
- overreliance em embedding

### Estratégia de Implementação
1. **Modelagem e Migration**: `entity_mentions`, `entities`, `entity_aliases`, `entity_resolution_log`, `provisional_entities`
2. **API**: merge, split, resolução e revisão
3. **UI**: fila de provisórias
4. **Testes**: alias, coreference, merge/split

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `entities`, `entity_aliases`, `entity_resolution_log` | histórico de resolução |
| Backend | `/entities`, `/entity-resolution` | merge/split/review |
| Frontend | console de entidades | triagem |
| Testes | suíte de resolução | ambiguidade e coreference |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-3.1 | Extrair e normalizar menções de entidade | 3 | US-1.2 |
| US-3.2 | Resolver menção para entidade existente ou provisória | 5 | US-3.1 |
| US-3.3 | Permitir merge/split auditável de entidades | 5 | US-3.2 |

---

## Feature 4: Consolidação Semântica, Relações e Supersessão Justificada

- **depende_de**: ["Feature 1", "Feature 3"]

### Objetivo de Negócio
Transformar episódios em memória semântica governada, sem apagar histórico.

### Comportamento Esperado
O sistema gera `candidate_facts`, promove `facts`, registra relações e executa supersessão tipada com justificativa obrigatória.

### Critérios de Aceite
- [ ] existe distinção entre `candidate_fact` e `fact`
- [ ] facts possuem `status`, `confidence`, `confidence_variance`, `source_agreement`, `source_episode_id`, `asserted_by`, `valid_from`, `valid_to`
- [ ] supersessão exige `reason_type` em `{correction, revision, contradiction, elaboration}`
- [ ] `justification` é obrigatória
- [ ] `evidence_ids` existem para cada supersessão
- [ ] fatos críticos suportam `quorum_required` e `quorum_achieved`
- [ ] contradições abertas podem coexistir sem falso fechamento

### Riscos Específicos
- erro consolidado virar verdade operacional
- política de aprovação enviesada
- backlog de conflito

### Estratégia de Implementação
1. **Modelagem e Migration**: `candidate_facts`, `facts`, `relations`, `supersession_events`, `approval_policies`
2. **API**: promoção, rejeição, supersessão, consulta de cadeia justificativa
3. **UI**: revisão, justificativa e quórum
4. **Testes**: supersessão, contradição, quórum, evidência obrigatória

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `candidate_facts`, `facts`, `relations`, `supersession_events` | governança epistêmica |
| Backend | `/facts`, `/supersessions`, `/approvals` | consolidação |
| Frontend | fila de conflito | decisão e cadeia justificativa |
| Testes | suíte de consolidação | supersessão tipada |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-4.1 | Extrair candidate facts de episódios | 5 | US-3.2 |
| US-4.2 | Promover facts com incerteza de primeira e segunda ordem | 5 | US-4.1 |
| US-4.3 | Executar supersessão tipada e justificada | 5 | US-4.2 |
| US-4.4 | Aplicar aprovação/quórum para fatos críticos | 3 | US-4.2 |

---

## Feature 5: Propagação de Mudança, Labilidade e Compressão Semântica

- **depende_de**: ["Feature 4"]

### Objetivo de Negócio
Garantir que mudança relevante propague para derivados e que memória abstraia detalhe episódico sem perder governança.

### Comportamento Esperado
Mudanças em facts geram fila de propagação idempotente; artefatos derivados são invalidados/recomputados; compressão semântica abstratiza episódios; fatos reativados entram em janela de labilidade.

### Critérios de Aceite
- [ ] existe grafo de dependência entre facts, summaries, packets, datasets e views humanas
- [ ] mudança em fact relevante enfileira propagação
- [ ] workers são idempotentes e reexecutáveis
- [ ] derivados são invalidados/recomputados com status rastreável
- [ ] `semantic_compression_jobs` suportam `trigger`, `strategy` e `quality_delta`
- [ ] facts reativados podem entrar em estado `labile`
- [ ] facts críticos não são apagados por compressão

### Riscos Específicos
- recomputação cara
- propagação incompleta
- compressão destrutiva

### Estratégia de Implementação
1. **Modelagem e Migration**: `fact_dependencies`, `propagation_queue`, `derived_artifacts`, `semantic_compression_jobs`, `compression_policies`
2. **API**: propagação, reexecução, inspeção de compressão/labilidade
3. **UI**: fila de propagação e histórico de compressão
4. **Testes**: cascata, retry, invalidação, regressão de qualidade

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `fact_dependencies`, `propagation_queue`, `semantic_compression_jobs` | mudança e abstração |
| Backend | `/propagation`, `/compression` | workers e status |
| Frontend | console de propagação | retry, inspeção |
| Testes | suíte de propagação/compressão | cascata e qualidade |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-5.1 | Enfileirar propagação quando fact relevante mudar | 5 | US-4.2 |
| US-5.2 | Recomputar derivados com lineage e idempotência | 5 | US-5.1 |
| US-5.3 | Executar compressão semântica e labilidade com medição de qualidade | 5 | US-4.2 |

---

## Feature 6: Retrieval Híbrido, Anti-Echo e Memory Packet

- **depende_de**: ["Feature 2", "Feature 4", "Feature 5"]

### Objetivo de Negócio
Servir memória relevante, explicável e segura em runtime.

### Comportamento Esperado
O sistema monta `memory_packet` com filtros simbólicos, busca semântica e reranking com anti-echo formal.

### Critérios de Aceite
- [ ] retrieval combina filtros estruturais e similaridade vetorial
- [ ] resultado inclui facts, episódios, identidade, procedimentos e justificativas
- [ ] facts bloqueados por política não aparecem
- [ ] retrieval registra uso
- [ ] ranking inclui componente formal de exploração vs explotação
- [ ] a fórmula de score inclui, no mínimo: relevância semântica, recência, confiança, `source_agreement`, `salience_score` e `exploration_bonus`
- [ ] `exploration_bonus` cresce com `days_since_last_access` e decai após uso
- [ ] o sistema pode registrar `retrieval_inhibition_log` quando uma recuperação suprime concorrentes

### Riscos Específicos
- câmara de eco
- latência alta
- score opaco

### Estratégia de Implementação
1. **Modelagem e Migration**: `retrieval_log`, `memory_packets`, `salience_scores`, `retrieval_inhibition_log`
2. **API**: `/memory/query`, `/memory/packet`, `/retrieval-log`
3. **UI**: explicação de ranking e inspeção de packet
4. **Testes**: ranking, anti-echo, policy filter, RII

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `retrieval_log`, `memory_packets`, `salience_scores`, `retrieval_inhibition_log` | score e explicabilidade |
| Backend | `/memory/query`, `/memory/packet` | runtime memory service |
| Frontend | inspeção de retrieval | debug de ranking |
| Testes | suíte de retrieval | precisão, latência, anti-echo |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-6.1 | Consultar memória por filtros e embeddings | 5 | US-5.2 |
| US-6.2 | Montar memory packet explicável para runtime | 5 | US-6.1 |
| US-6.3 | Recalcular saliência com anti-echo formal | 5 | US-6.2 |

---

## Feature 7: Views Humanas em Markdown e Snapshots Auditáveis

- **depende_de**: ["Feature 2", "Feature 4", "Feature 5", "Feature 6"]

### Objetivo de Negócio
Preservar a ergonomia humana do sistema original sem voltar arquivos a truth layer primária.

### Comportamento Esperado
O sistema renderiza `MEMORY.md`, `memory/YYYY-MM-DD.md`, `entities/<slug>/summary.md`, relatórios e snapshots como views derivadas do store canônico.

### Critérios de Aceite
- [ ] existe renderização derivada de `MEMORY.md`
- [ ] existe renderização derivada de notas diárias `memory/YYYY-MM-DD.md`
- [ ] existe renderização derivada de `entities/<slug>/summary.md`
- [ ] snapshots auditáveis podem ser exportados
- [ ] edições humanas em view disparam change request governado, não escrita direta
- [ ] drift entre view e canônico pode ser detectado
- [ ] views frias/quentes respeitam política de decay e reheating

### Riscos Específicos
- operador tratar view como truth layer
- drift silencioso
- excesso de custo de renderização

### Estratégia de Implementação
1. **Modelagem e Migration**: `rendered_views`, `view_change_requests`, `snapshot_exports`
2. **API**: renderização, diff, export, submissão de change request
3. **UI**: visualização, diff e aprovação de edição humana
4. **Testes**: renderização consistente, diff, round-trip governado

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `rendered_views`, `view_change_requests`, `snapshot_exports` | camada humana derivada |
| Backend | `/views/render`, `/views/diff`, `/views/change-request` | render e governança |
| Frontend | visualizador de Markdown | leitura e diff |
| Testes | suíte de views | consistência e round-trip |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-7.1 | Renderizar `MEMORY.md` e notas diárias a partir do canônico | 5 | US-2.3 |
| US-7.2 | Renderizar summaries por entidade com decay/reheating | 5 | US-6.2 |
| US-7.3 | Permitir change request humano sobre views | 5 | US-7.1 |

---

## Feature 8: Governança, Auditoria e Rollback Epistemológico

- **depende_de**: ["Feature 4", "Feature 5", "Feature 6", "Feature 7"]

### Objetivo de Negócio
Controlar risco e permitir reversão ponta a ponta.

### Comportamento Esperado
Operadores revisam fatos, policies, views, lineage e executam rollback de memória e dataset.

### Critérios de Aceite
- [ ] toda mudança crítica tem audit trail
- [ ] existe política de acesso por escopo e risco
- [ ] rollback reconstrói facts, packets, views, summaries e derivados afetados
- [ ] datasets e adapters derivados podem ser localizados por lineage
- [ ] retenção e exclusão obedecem política

### Riscos Específicos
- rollback incompleto
- custo alto
- falsa sensação de segurança

### Estratégia de Implementação
1. **Modelagem e Migration**: `audit_log`, `policy_rules`, `rollback_jobs`, `lineage_edges`
2. **API**: auditoria, lineage, rollback, retenção
3. **UI**: timeline, lineage graph, rollback console
4. **Testes**: rollback em cascata, lineage, retenção

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `audit_log`, `policy_rules`, `rollback_jobs`, `lineage_edges` | reversibilidade |
| Backend | `/audit`, `/lineage`, `/rollback` | governança |
| Frontend | console de auditoria | rollback e investigação |
| Testes | suíte de auditoria | cascade rollback |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-8.1 | Registrar trilha de auditoria por mudança crítica | 3 | US-4.2 |
| US-8.2 | Aplicar política de acesso e aprovação por risco | 5 | US-8.1 |
| US-8.3 | Executar rollback epistemológico com lineage completo | 5 | US-8.2 |

---

## Feature 9: Curadoria de Exemplos de Treino e Export de Dataset

- **depende_de**: ["Feature 6", "Feature 8"]

### Objetivo de Negócio
Transformar operação validada em dataset de especialização incremental.

### Comportamento Esperado
O sistema deriva `training_examples` da operação, aplica elegibilidade/exclusão e exporta datasets com lineage e política de dados.

### Critérios de Aceite
- [ ] exemplos carregam `context_snapshot`, `query_text`, `retrieved_fact_ids`, `agent_response`, `outcome_quality`, `quality_source`, `task_type`
- [ ] existe curadoria negativa explícita
- [ ] exemplos sem lineage suficiente são excluídos
- [ ] datasets são versionados com train/val/test
- [ ] export preserva anonimização e retenção
- [ ] rollback consegue localizar dataset e adapter derivado

### Riscos Específicos
- self-distillation degenerativa
- reward hacking
- treino contaminado

### Estratégia de Implementação
1. **Modelagem e Migration**: `training_examples`, `dataset_versions`, `dataset_exclusions`, `quality_signals`, `dataset_lineage`
2. **API**: curadoria, revisão, export
3. **UI**: fila de elegibilidade, revisão e lineage
4. **Testes**: exclusão, split, lineage, export, rollback

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `training_examples`, `dataset_versions`, `dataset_exclusions`, `dataset_lineage` | treino governado |
| Backend | `/training-examples`, `/datasets/export` | curadoria e export |
| Frontend | inspeção de dataset | revisão |
| Testes | suíte de dataset | elegibilidade e lineage |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-9.1 | Derivar exemplos de treino da operação validada | 5 | US-6.3 |
| US-9.2 | Aplicar filtros de elegibilidade, exclusão e anonimização | 5 | US-9.1 |
| US-9.3 | Versionar e exportar dataset com lineage | 5 | US-9.2 |

---

## Feature 10: Observabilidade, Avaliação e Console Operacional

- **depende_de**: ["Feature 1", "Feature 6", "Feature 9"]

### Objetivo de Negócio
Evitar operação no escuro e medir regressão real.

### Comportamento Esperado
Operadores acompanham ingestão, consolidação, propagação, retrieval, views, dataset e regressão por versão.

### Critérios de Aceite
- [ ] dashboard mostra health, lag, throughput, conflito, propagação, renderização, precisão e cobertura
- [ ] alertas disparam para falhas de ingestão, propagação travada, queda de qualidade e drift entre view e canônico
- [ ] existe comparação entre versões de dataset/modelo
- [ ] baseline existe antes do rollout produtivo
- [ ] métricas podem ser rastreadas até feature, US e lineage

### Riscos Específicos
- dashboards inúteis
- proxy virar meta
- avaliação online/offline desconectada

### Estratégia de Implementação
1. **Modelagem e Migration**: `evaluation_runs`, `quality_metrics`, `alerts`, `system_health_snapshots`
2. **API**: `/metrics`, `/evaluations`, `/alerts`
3. **UI**: dashboards e drill-down
4. **Testes**: métricas, alertas, regressão

### Impacts

| Camada | Impacto | Detalhamento |
|---|---|---|
| Banco | `evaluation_runs`, `quality_metrics`, `alerts`, `system_health_snapshots` | telemetria |
| Backend | `/metrics`, `/evaluations`, `/alerts` | observabilidade |
| Frontend | console operacional | dashboards |
| Testes | suíte de métricas | regressão |

### User Stories planejadas

| US ID | Título | SP estimado | Depende de |
|---|---|---|---|
| US-10.1 | Medir health e throughput do sistema | 3 | US-1.1 |
| US-10.2 | Medir qualidade de retrieval, views e dataset | 5 | US-9.1 |
| US-10.3 | Exibir console operacional com alertas e drill-down | 5 | US-10.1 |

---

## Exceção Documentada de Fundação Compartilhada

### Fundação Compartilhada A: Substrate Operacional Mínimo

Inclui:
- cluster PostgreSQL + `pgvector`
- fila/event bus
- object storage
- autenticação do console
- secrets/configuração
- CI/CD inicial

**Regra**: fundação só entra na medida necessária para habilitar comportamento de feature.

## 14. Fases do Projeto

### Fase 0 — Observabilidade e Baseline Operacional
- Features:
  - Feature 10 (baseline mínimo)
  - Fundação compartilhada mínima

### Fase 1 — Ingestão e Camadas de Memória Base
- Features:
  - Feature 1
  - Feature 2
  - Feature 3

### Fase 2 — Consolidação e Mudança
- Features:
  - Feature 4
  - Feature 5

### Fase 3 — Runtime e Ergonomia Humana
- Features:
  - Feature 6
  - Feature 7
  - Feature 8

### Fase 4 — Learning Loop
- Features:
  - Feature 9
  - Feature 10 (comparativos e regressão)

## 15. Rastreabilidade mínima `feature -> fase -> épico -> issue`

| Feature | Fase | Épico sugerido | Issue inicial sugerida |
|---|---|---|---|
| Feature 1 | Fase 1 | EPIC-F1-01 Ingestão Canônica | ISSUE-F1-01-001 Persistir evento idempotente |
| Feature 2 | Fase 1 | EPIC-F1-02 Identity + Procedural | ISSUE-F1-02-001 Persistir agent identity |
| Feature 3 | Fase 1 | EPIC-F1-03 Entity Resolution | ISSUE-F1-03-001 Criar pipeline de entity mentions |
| Feature 4 | Fase 2 | EPIC-F2-01 Consolidação Semântica | ISSUE-F2-01-001 Extrair candidate facts |
| Feature 5 | Fase 2 | EPIC-F2-02 Propagação e Compressão | ISSUE-F2-02-001 Enfileirar propagação por fact change |
| Feature 6 | Fase 3 | EPIC-F3-01 Retrieval Híbrido | ISSUE-F3-01-001 Implementar query simbólica + vetorial |
| Feature 7 | Fase 3 | EPIC-F3-02 Views Humanas | ISSUE-F3-02-001 Renderizar MEMORY.md derivado |
| Feature 8 | Fase 3 | EPIC-F3-03 Governança e Rollback | ISSUE-F3-03-001 Registrar audit trail por fact |
| Feature 9 | Fase 4 | EPIC-F4-01 Dataset de Treino | ISSUE-F4-01-001 Derivar training examples |
| Feature 10 | Fase 0 / 4 | EPIC-F0-01 Observabilidade | ISSUE-F0-01-001 Expor health e métricas operacionais |

## 16. Regras de Decomposição para Execução

- nenhuma user story deve exceder 5 story points sem justificativa explícita
- nenhuma user story deve ultrapassar 5 tasks
- mudanças com persistência sensível, rollback, lineage, renderização governada ou remediação de auditoria usam `task_instruction_mode: required`
- toda lógica automatizável nasce com plano TDD
- nenhuma feature é `done` sem evidência funcional demonstrável

## 17. Dependências Críticas por Ordem

1. Fundação compartilhada mínima
2. Feature 10 (baseline)
3. Feature 1
4. Feature 2
5. Feature 3
6. Feature 4
7. Feature 5
8. Feature 6
9. Feature 7
10. Feature 8
11. Feature 9

## 18. Lacunas Conhecidas

- política final de retenção por tenant e classe de dado
- benchmark interno oficial para ganho pós-fine-tuning
- thresholds iniciais de quórum, `source_agreement` e elegibilidade
- primeiro conjunto fechado de integrações de entrada

## 19. Hipóteses Declaradas

- rollout inicial single-tenant operacional
- primeiro consumidor será agente interno
- fine-tuning inicial será incremental/supervisionado
- haverá operador humano para fatos críticos
- views humanas serão inicialmente derivadas e não editáveis diretamente

## 20. Critérios de Prontidão para Implementação

- [x] `INTAKE-MNEME.md` gerado
- [ ] intake aprovado
- [ ] política de dados confirmada
- [ ] benchmark inicial definido
- [ ] fundação compartilhada mínima confirmada
- [ ] PRD aprovado

## 21. Regra de Ouro do Projeto

> Se uma feature não puder ser demonstrada como algo utilizável por um agente ou por um operador, ela está no nível errado de planejamento.

## 22. Frase Guia

> Memória registra, identidade orienta, procedimento governa, consolidação decide, propagação atualiza, retrieval serve, Markdown explica, auditoria limita, treino aprende.
