---
doc_id: INTAKE-MNEME.md
version: "0.1"
status: draft
owner: PM
last_updated: 2026-03-25
project: MNEME
intake_kind: new-capability
source_mode: backfilled
origin_project: nao_aplicavel
origin_phase: nao_aplicavel
origin_audit_id: nao_aplicavel
origin_report_path: /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/mneme.md + /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/felixcraft.md + /Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/simposio_banca_avaliacao.html+/Users/genivalfreirenobrejunior/Documents/gh-repos/openclaw/mneme_v2_symposium_presentation.html
product_type: platform-capability
delivery_surface: fullstack-module
business_domain: governanca
criticality: critica
data_sensitivity: lgpd
integrations:
  - PostgreSQL
  - pgvector
  - Message Queue/Event Bus
  - Object Storage
  - LLM Runtime
  - Fine-tuning Pipeline
  - Observability Stack
change_type: nova-capacidade
audit_rigor: strict
---

# INTAKE - MNEME

> Backfill canônico do projeto MNEME.  
> Baseado em contexto histórico, proposta arquitetural anterior, proposta evoluída e governança anexada.  
> Campos ainda não decididos estão marcados como `nao_definido` e repetidos em `Lacunas Conhecidas`.

## 0. Rastreabilidade de Origem

- projeto de origem: `nao_aplicavel`
- fase de origem: `nao_aplicavel`
- auditoria de origem: `nao_aplicavel`
- relatorio de origem: `conversa-2026-03-25 + artefatos anexos`
- motivo da abertura deste intake:
  formalizar a iniciativa MNEME no fluxo canônico `Intake -> PRD -> Features -> User Stories -> Tasks`, substituindo contexto conversacional/backfilled por artefato governado e auditável.

## 1. Resumo Executivo

- nome curto da iniciativa:
  MNEME
- tese em 1 frase:
  Construir uma plataforma de memória operacional para agentes de IA que registre eventos, consolide fatos, governe verdade operacional, recupere contexto com precisão e gere dataset curado para fine-tuning incremental.
- valor esperado em 3 linhas:
  - reduzir contradição, perda de contexto e acoplamento excessivo à janela de contexto;
  - permitir operação multiagente com memória canônica, auditável, reversível e explicável;
  - transformar a própria operação do sistema em ativo de aprendizado contínuo com governança e lineage.

## 2. Problema ou Oportunidade

- problema atual:
  agentes operam com memória fragmentada entre contexto transitório, arquivos legíveis por humanos e heurísticas locais; fatos, decisões, políticas e eventos tendem a se misturar; o sistema gera sinais úteis de aprendizado, mas eles não viram dataset de treino com curadoria e rastreabilidade.
- evidencia do problema:
  - memória baseada primariamente em markdown/json é útil para inspeção humana, mas fraca para concorrência, integridade referencial, supersessão, rollback e governança multiagente;
  - ambientes com múltiplos agentes e processos precisam de substrate transacional, event bus e política explícita de verdade operacional;
  - sem curadoria, memória operacional não se converte em dataset de fine-tuning seguro.
- custo de nao agir:
  - persistência de contradições, duplicação de contexto e perda de histórico útil;
  - maior retrabalho humano para corrigir ou reexplicar contexto;
  - incapacidade de melhorar o modelo a partir da própria operação;
  - risco de erro fossilizado sem trilha de evidência e sem reversão completa.
- por que agora:
  - a arquitetura conceitual amadureceu ao ponto de ficar implementável;
  - o cenário multiagente/multi-máquina é iminente;
  - o maior ganho marginal agora está em governança de memória e learning loop, não em aumentar contexto ou trocar modelo às cegas.

## 3. Publico e Operadores

- usuario principal:
  times que operam agentes de IA com tarefas recorrentes, memória persistente e exigência de rastreabilidade.
- usuario secundario:
  PMs, engenheiros de IA, pesquisadores, auditores e operadores de plataforma.
- operador interno:
  workers de ingestão, entity resolution, consolidação, retrieval, governança, curadoria de dataset e observabilidade.
- quem aprova ou patrocina:
  liderança de produto/plataforma responsável pelo runtime dos agentes e pela política de memória/treino.

## 4. Jobs to be Done

- job principal:
  dar a um agente de IA uma memória operacional persistente, confiável e governada, útil para executar melhor hoje e aprender melhor amanhã.
- jobs secundarios:
  - registrar eventos e episódios com proveniência;
  - resolver entidades e consolidar fatos sem apagar histórico;
  - recuperar memória relevante em runtime com explicabilidade;
  - aplicar governança de risco, aprovação, retenção e rollback;
  - derivar exemplos de treino da operação validada.
- tarefa atual que sera substituida:
  - memória improvisada em contexto de chat;
  - arquivos `.md`/`.json` como truth layer primário;
  - ajuste manual de prompts e fine-tuning ad hoc sem lineage.

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. agentes, ferramentas e runtime publicam eventos e artefatos operacionais em ingestão canônica;
2. o sistema agrupa eventos em episódios, resolve entidades e extrai candidate facts;
3. facts e relações são consolidados com política, justificativa, supersessão e trilha de auditoria;
4. o runtime consulta memória híbrida, recebe `memory_packet` explicável e executa a tarefa;
5. a operação gera sinais de qualidade, lineage e exemplos elegíveis para dataset;
6. datasets curados são versionados, auditados e exportados para fine-tuning incremental;
7. observabilidade, rollback e auditoria sustentam a operação contínua.

## 6. Escopo Inicial

### Dentro

- substrate transacional para memória episódica, semântica e procedural;
- ingestão multiagente e idempotente;
- entity resolution, candidate facts e facts consolidados;
- supersessão tipada, labilidade, aprovação e governança;
- retrieval híbrido e montagem de `memory_packet`;
- curadoria e export de `training_examples`;
- observabilidade, lineage e rollback epistemológico;
- console operacional mínimo para operadores.

### Fora

- treinamento de foundation model do zero;
- grounding universal com verdade externa garantida;
- UX polida para usuário final não técnico no MVP;
- automação irrestrita de ações externas de alto risco;
- cobertura inicial de todas as integrações possíveis;
- eliminação completa de revisão humana para fatos críticos.

## 7. Resultado de Negocio e Metricas

- objetivo principal:
  colocar em produção uma plataforma de memória operacional que melhore qualidade de resposta, rastreabilidade e especialização incremental de agentes.
- metricas leading:
  - % de interações relevantes com evento persistido;
  - % de facts com proveniência, status e justificativa válidos;
  - latência p95 de retrieval;
  - % de conflitos resolvidos com trilha completa;
  - % de exemplos elegíveis aproveitados após curadoria.
- metricas lagging:
  - redução de contradições em respostas do agente;
  - aumento de precisão factual em tarefas recorrentes;
  - redução de retrabalho humano por falta de contexto;
  - melhoria mensurável em benchmark interno após fine-tuning incremental.
- criterio minimo para considerar sucesso:
  - um agente consegue registrar, consolidar e recuperar memória com trilha auditável;
  - fatos supersedidos preservam justificativa, evidência e lineage;
  - existe dataset versionado com filtros de elegibilidade e export seguro;
  - o sistema possui replay, observabilidade e rollback operacional.

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - PostgreSQL como store canônico inicial;
  - suporte a múltiplos writers;
  - escrita crítica idempotente e auditável;
  - retrieval não pode depender apenas de embeddings;
  - o sistema deve suportar backpressure, replay e at-least-once no pipeline.
- restricoes operacionais:
  - intake e PRD exigem aprovação humana explícita;
  - fatos críticos exigem política de aprovação/quórum;
  - o sistema deve declarar explicitamente seus limites e não fingir grounding externo.
- restricoes legais ou compliance:
  - memória e dataset podem conter dados pessoais e exigem política de retenção, elegibilidade e anonimização;
  - toda exportação para treino deve ser rastreável;
  - dados sensíveis não podem ser promovidos ou exportados sem política.
- restricoes de prazo:
  - MVP deve ficar de pé de forma incremental, sem depender do sistema “completo”.
- restricoes de design ou marca:
  - console inicial pode ser utilitário;
  - prioridade em clareza operacional e auditabilidade.

## 9. Dependencias e Integracoes

- sistemas internos impactados:
  - runtime dos agentes;
  - pipeline de avaliação;
  - monitoramento/alerting;
  - policy engine;
  - auditoria operacional.
- sistemas externos impactados:
  - LLM provider;
  - stack de fine-tuning;
  - event bus / fila;
  - object storage;
  - autenticação do console.
- dados de entrada necessarios:
  - mensagens;
  - chamadas de ferramenta;
  - eventos de execução;
  - feedback explícito;
  - sinais implícitos de outcome;
  - políticas de risco e aprovação.
- dados de saida esperados:
  - eventos canônicos;
  - episódios;
  - entidades, facts e relações;
  - `memory_packets`;
  - `training_examples` e datasets versionados;
  - métricas, alertas e trilhas de auditoria.

## 10. Arquitetura Afetada

- backend:
  APIs de ingestão, resolução de entidades, consolidação, retrieval, governança, dataset, observabilidade e rollback.
- frontend:
  console operacional para inspeção, conflito, aprovação, lineage, dataset e auditoria.
- banco/migracoes:
  Postgres + `pgvector`, tabelas de eventos, episódios, entidades, facts, relações, dependências, logs, datasets e auditoria.
- observabilidade:
  métricas desde o dia 0 para retrieval latency, conflict rate, consolidation lag, compression quality, dataset yield e regressão.
- autorizacao/autenticacao:
  RBAC por domínio/risco, política por tenant e escopo de operador.
- rollout:
  habilitação incremental por fases; primeiro substrate e ingestão, depois consolidação e retrieval, depois governança pesada e learning loop.

## 11. Riscos Relevantes

- risco de produto:
  a plataforma virar um excelente sistema de registro e um mau sistema de ajuda em runtime.
- risco tecnico:
  entity resolution ruim, propagação de mudança incompleta, latência alta, câmara de eco de retrieval e lineage quebrado.
- risco operacional:
  backlog de conflitos, excesso de revisão manual, workers falhando em pontos intermediários e drift de política.
- risco de dados:
  contaminação de dataset por memória errada, vazamento de dados sensíveis e reward hacking por proxy de qualidade fraco.
- risco de adocao:
  uso parcial do sistema só como log sem fechar o loop memória → governança → retrieval → treino.

## 12. Nao-Objetivos

- substituir julgamento humano para fatos críticos de alto risco;
- prometer verdade externa perfeita;
- treinar continuamente sem curadoria e sem avaliação;
- cobrir toda a estratégia de model merging/LoRA/catastrophic forgetting no MVP;
- transformar todo evento em fato ou todo fato em exemplo de treino.

## 13. Contexto Especifico para Problema ou Refatoracao

> Obrigatorio para `intake_kind: problem | refactor | audit-remediation`. Para outros casos, preencher com `nao_aplicavel`.

- sintoma observado: `nao_aplicavel`
- impacto operacional: `nao_aplicavel`
- evidencia tecnica: `nao_aplicavel`
- componente(s) afetado(s): `nao_aplicavel`
- riscos de nao agir: `nao_aplicavel`

## 14. Lacunas Conhecidas

Liste tudo que a IA nao pode inventar sozinha:

- regra de negocio ainda nao definida:
  política formal de retenção por classe de dado e por tenant.
- dependencia ainda nao confirmada:
  stack exata do fine-tuning inicial e protocolo de export para treino.
- dado ainda nao disponivel:
  benchmark interno oficial para medir ganho pós-fine-tuning.
- decisao de UX ainda nao fechada:
  recortes do console operacional do MVP e fluxo de aprovação humana.
- outro ponto em aberto:
  - política de multitenancy do MVP;
  - lista inicial de integrações de entrada;
  - primeiro runtime consumidor oficial;
  - thresholds de confiança, quórum e elegibilidade para dataset.

## 15. Perguntas que o PRD Precisa Responder

- quais features mínimas precisam existir para o sistema ficar de pé sem virar planejamento por camada?
- como formalizar propagação de mudança, idempotência, observabilidade e rollback sem inflar escopo?
- como separar memória operacional, governança e curadoria de dataset com lineage suficiente?
- qual é o recorte de MVP para entity resolution, consolidação e retrieval?
- que sinais de qualidade tornam um `training_example` elegível ou inelegível?
- quais limites o sistema deve declarar explicitamente como fora do escopo?

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
