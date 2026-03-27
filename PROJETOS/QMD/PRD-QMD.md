---
doc_id: "PRD-QMD.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-23"
project: "QMD"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "backend-api"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "restrita"
integrations:
  - "openclaw-gateway"
  - "qmd-memory-backend"
  - "filesystem-workspace"
  - "cron-openclaw"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

# PRD - QMD

> Origem: [INTAKE-QMD.md](./INTAKE-QMD.md)
>
> Este PRD fecha contratos que o intake deixou para o PRD: decay de fatos, schema
> `items.json` / `summary.md`, contrato `memory.qmd` e especificacao minima do job
> noturno. MVP prioriza MEMORY + QMD + notas diarias + consolidacao; grafo com decay
> e fatos atomicos sao fase posterior, salvo decisao explicita do PM de antecipar.

## 0. Rastreabilidade

- **Intake de origem**: [INTAKE-QMD.md](./INTAKE-QMD.md)
- **Versao do intake**: 1.0
- **Data de criacao**: 2026-03-23
- **PRD derivado**: nao aplicavel

## 1. Resumo Executivo

- **Nome do projeto**: QMD — memoria operacional em camadas com retrieval QMD
- **Tese em 1 frase**: gestao de memoria em camadas (tacit, diario, entidades opcionais) com backend QMD e consolidacao agendada, sem violar autoridade dos artefatos canonicos do OpenClaw.
- **Valor esperado em 3 linhas**:
  - recuperacao semantica estavel sobre pastas acordadas
  - rotina noturna que organiza fatos e timeline sem promover inferencias a norma
  - regras explicitas de decay e supersede para o grafo, quando adotado

## 2. Problema ou Oportunidade

- **Problema atual**: contexto volatil e busca fraca; risco de misturar memoria derivada com decisoes de projeto.
- **Evidencia do problema**: intake e playbooks externos (Felix) descrevem ganho com QMD, notas diarias e consolidacao.
- **Custo de nao agir**: retrabalho, alucinacao de contexto, gravacao indevida de inferencias como decisao.
- **Por que agora**: intake aprovado para trilha PRD -> fases -> issues.

## 3. Publico e Operadores

- **Usuario principal**: PM/proprietario do workspace com agente OpenClaw de longa duracao
- **Usuario secundario**: revisores de governanca
- **Operador interno**: agente OpenClaw (e sub-agentes) com tools e cron
- **Quem aprova ou patrocina**: PM

## 4. Jobs to be Done

- **Job principal**: recuperar contexto relevante via QMD respeitando canonicos e escalar conflitos ao PM.
- **Jobs secundarios**: consolidar o dia em notas; atualizar entidades com fatos atomicos quando o grafo estiver ativo; manter indices QMD atualizados.
- **Tarefa atual que sera substituida**: contexto apenas no chat e busca ad hoc em arquivos.

## 5. Escopo

### Dentro

- Contrato de configuracao `memory.backend: qmd` e bloco `memory.qmd` (ver Anexo A).
- MVP: `MEMORY.md` (ou equivalente), `memory/YYYY-MM-DD.md`, indexacao QMD, job noturno de consolidacao (ver Anexo C).
- Pos-MVP (Fase 2+): diretorio de entidades (ex. PARA sob path acordado), `summary.md` por entidade, `items.json` com schema e regras de decay (ver Anexo B).
- Politica memoria-vs-canonico: canonicos prevalecem; promocao para normas versionadas so com confirmacao do PM; registro de divergencias (template a definir na issue de governanca).

### Fora

- Alterar `PROJETOS/COMUM/*` sem fluxo de governanca.
- Substituir issue-first por memoria livre.
- Heartbeat para sessoes longas, delegacao a agentes de codigo externos, Ralph loop, tmux health-check como entrega deste PRD (alinhado ao intake).
- Seguranca enterprise ou compliance legal nao especificados no intake.

## 6. Resultado de Negocio e Metricas

- **Objetivo principal**: indices QMD uteis, consolidacao testada, politica de conflito aplicada em piloto.
- **Metricas leading**: latencia percebida de recall; re-prompts repetidos por semana; divergencias detectadas e escaladas.
- **Metricas lagging**: continuidade semanal; reducao de “comecar do zero”.
- **Criterio minimo para sucesso**: QMD indexando conjuntos acordados; job noturno executado e auditavel; zero promocao silenciosa a canonicos.

## 7. Restricoes e Guardrails

- **Restricoes tecnicas**: compatibilidade com versao OpenClaw em uso e feature QMD disponivel; paths absolutos variam por host.
- **Restricoes operacionais**: segredos e estado vivo fora do Git ([AGENTS.md](../../AGENTS.md)).
- **Restricoes legais ou compliance**: avaliar dados pessoais de terceiros em notas antes de indexar amplo.
- **Restricoes de prazo**: nao_definido
- **Restricoes de design ou marca**: vocabulario Intake -> PRD -> fases do framework.

## 8. Dependencias e Integracoes

- **Sistemas internos impactados**: workspace OpenClaw, `openclaw.json`, cron OpenClaw, hooks internos opcionais (`boot-md`, `session-memory`) quando aplicavel ao ambiente.
- **Sistemas externos impactados**: APIs de modelo para o job de consolidacao (custo).
- **Dados de entrada necessarios**: conversas/sessoes; markdown/json nas pastas indexadas; artefatos canonicos para diff de conflito.
- **Dados de saida esperados**: notas atualizadas; fatos em `items.json` quando grafo ativo; indices QMD; log de escalacao.

## 9. Arquitetura Geral do Projeto

- **Backend**: motor QMD + configuracao OpenClaw; job `agentTurn` isolado ou script host (decisao por issue — ver Anexo C).
- **Frontend**: nao aplicavel.
- **Banco/migracoes**: nao aplicavel (indice QMD como componente separado).
- **Observabilidade**: logs de reindexacao e de execucao do job noturno.
- **Autorizacao/autenticacao**: canais de comando vs informativos conforme politica do workspace.
- **Rollout**: piloto no ambiente do PM antes de generalizar.

## 10. Riscos Globais

- **Risco de produto**: confundir memoria derivada com decisao — mitigacao: rotulos, HITL, templates.
- **Risco tecnico**: QMD indexando paths errados ou dados sensiveis.
- **Risco operacional**: cron falhando silenciosamente ou custo excessivo de modelo.
- **Risco de dados**: indices/backups locais com conteudo restrito.
- **Risco de adocao**: comecar por MVP MEMORY + QMD antes do grafo completo.

## 11. Nao-Objetivos

- Autoridade do agente sobre `GOV-*` ou gates de auditoria.
- Produto comercial multi-tenant.
- Otimizacao exaustiva de custo LLM antes de validar valor.
- Heartbeat, monitoramento tmux/Codex ou Ralph loop como escopo do projeto QMD.

---

# 12. Features do Projeto

## Feature 1: Baseline QMD e MEMORY operacional (MVP)

### Objetivo de Negocio

Ter retrieval semantico estavel sobre memoria tacita e arquivos acordados sem depender apenas do contexto da sessao.

### Comportamento Esperado

O operador configura `memory.backend: qmd` com paths e patterns; o agente consulta memoria via QMD; `MEMORY.md` existe com preferencias e regras operacionais minimas.

### Criterios de Aceite

- [ ] `openclaw.json` (ou equivalente documentado) materializa bloco `memory.qmd` conforme Anexo A com paths validados no host piloto.
- [ ] QMD reindexa no intervalo configurado e cobre pelo menos `MEMORY.md` e `memory/**/*.md` (ou pattern acordado).
- [ ] Documentacao em `PROJETOS/QMD/` descreve o layout minimo de diretorios para MVP.

### Dependencias com Outras Features

- Nenhuma.

### Riscos Especificos

Versao OpenClaw sem QMD ou flags diferentes — mitigar com matriz de compatibilidade na issue.

### Fases de Implementacao

1. **Modelagem e Migration**: nao aplicavel
2. **API**: nao aplicavel
3. **UI**: nao aplicavel
4. **Testes**: checklist manual de reindexacao e query de recall em ambiente piloto

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Banco | — | — |
| Backend | Config OpenClaw + QMD | `memory.qmd` |
| Frontend | — | — |
| Testes | Piloto | recall smoke |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T1 | Documentar e validar contrato Anexo A no host piloto | 2 | - |
| T2 | Criar template MEMORY.md minimo e checklist de paths | 2 | T1 |

---

## Feature 2: Notas diarias e job noturno de consolidacao (MVP)

### Objetivo de Negocio

Encerrar o dia com timeline duravel e base markdown atualizada, alinhada ao playbook Felix (extracao noturna).

### Comportamento Esperado

Um agendamento dispara revisao das conversas do dia, atualiza `memory/YYYY-MM-DD.md` e dispara reindexacao; nao escreve em canonicos sem aprovacao.

### Criterios de Aceite

- [ ] Cron OpenClaw ou processo host documentado conforme Anexo C (schedule, timezone, payload).
- [ ] Prompt do job lista entradas esperadas e proibicoes (nao alterar `GOV-*`, issues sem fluxo).
- [ ] Evidencia de pelo menos tres execucoes de teste (log ou artefato) em piloto.

### Dependencias com Outras Features

- Feature 1: reindexacao QMD apos escrita.

### Riscos Especificos

Custo de modelo e falhas silenciosas — mitigacao: modelo dedicado barato quando possivel; log obrigatorio.

### Fases de Implementacao

1. **Modelagem**: template `memory/YYYY-MM-DD.md`
2. **API**: nao aplicavel
3. **UI**: nao aplicavel
4. **Testes**: execucoes piloto documentadas

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Backend | Cron OpenClaw | `agentTurn` isolado ou script |
| Testes | Piloto | logs |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T3 | Definir schedule final (expr cron + tz) com PM | 1 | - |
| T4 | Implementar/configurar job + prompt Anexo C | 5 | T1, T3 |
| T5 | Template de daily note e criterio de “fato duravel” | 3 | T4 |

---

## Feature 3: Grafo de entidades, items.json, summary.md e decay (pos-MVP)

### Objetivo de Negocio

Escalar de timeline diaria para fatos atomicos por entidade com relevancia temporal (hot/warm/cold) sem apagar historico.

### Comportamento Esperado

Entidades vivas sob path acordado (ex. `~/life/` ou subtree do workspace); cada entidade com `summary.md` regenerado periodicamente e `items.json` seguindo schema do Anexo B; decay influencia destaque no summary, nao exclusao.

### Criterios de Aceite

- [ ] Schema `items.json` validado com exemplos nao sensiveis versionados como fixture em `PROJETOS/QMD/` (ou path acordado).
- [ ] Regras de decay e supersede documentadas e aplicadas em script ou instrucao do job (bump `accessCount` / `lastAccessed` quando referenciado).
- [ ] QMD indexa `**/*.json` nas pastas de entidades conforme Anexo A estendido.

### Dependencias com Outras Features

- Feature 2: extracao noturna passa a opcionalmente emitir/atualizar fatos estruturados.

### Riscos Especificos

Complexidade e drift de schema — mitigacao: validacao leve (ex. checklist) antes de escrita em lote.

### Fases de Implementacao

1. **Modelagem**: schema JSON e convencao de pastas PARA
2. **Automacao**: extensao do prompt/job para fatos
3. **Testes**: fixtures e revisao humana semanal de `summary.md`

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Backend | QMD paths | inclusao `**/*.json` |
| Filesystem | Entidades | summary + items |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T6 | Especificar arvore de entidades (PARA) para o PM | 3 | T5 |
| T7 | Implementar geracao/atualizacao items.json + decay | 8 | T6 |

---

## Feature 4: Deteccao de conflito memoria vs canonico e escalacao

### Objetivo de Negocio

Impedir que retrieval ou consolidacao trate inferencia como decisao de projeto quando diverge de normas versionadas.

### Comportamento Esperado

Ao detectar divergencia com `PROJETOS/COMUM/*` ou normativos de `PROJETOS/<PROJETO>/`, o agente registra, nao promove, e pede decisao ao PM (canal/formato a fechar na issue).

### Criterios de Aceite

- [ ] Template ou checklist de escalacao publicado em `PROJETOS/QMD/`.
- [ ] Exercicio piloto documentado com pelo menos um cenario de conflito simulado ou real.
- [ ] Criterio “canonico prevalece” referenciado em instrucoes do agente (MEMORY ou AGENTS locais, conforme decisao do PM).

### Dependencias com Outras Features

- Feature 2 ou 3: consolidacao e retrieval sao os gatilhos tipicos.

### Riscos Especificos

Falsos positivos — mitigacao: lista explicita de prefixos/pastas canonicas.

### Fases de Implementacao

1. **Modelagem**: lista de caminhos canonicos e formato de registro
2. **Testes**: cenarios piloto

### Impacts

| Camada | Impacto | Detalhamento |
|--------|---------|--------------|
| Docs | Template escalacao | markdown |
| Config | Instrucoes agente | pointer |

### Tasks da Feature

| Task ID | Descricao | SP | Depende de |
|---------|-----------|-----|------------|
| T8 | Definir template de divergencia + canal PM | 2 | - |
| T9 | Piloto de conflito + retrospectiva | 3 | T4 |

---

# 13. Estrutura de Fases

## Fase 1: MVP memoria + QMD

- **Objetivo**: retrieval QMD e tacit MEMORY operacional.
- **Features incluidas**: Feature 1, Feature 4 (template minimo de escalacao em paralelo leve)
- **Gate de saida**: criterios de aceite da Feature 1 atendidos.
- **Critérios de aceite**: checklist PRD secao Feature 1.

### Epicos da Fase 1

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F1-01 | Feature 1 | todo | 4 |
| EPIC-F1-02 | Feature 4 (T8) | todo | 2 |

## Fase 2: Consolidacao noturna

- **Objetivo**: daily notes + job noturno estavel.
- **Features incluidas**: Feature 2, Feature 4 (T9)
- **Gate de saida**: tres execucoes piloto documentadas.
- **Critérios de aceite**: Feature 2 + exercicio de conflito.

### Epicos da Fase 2

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F2-01 | Feature 2 | todo | 9 |

## Fase 3: Grafo e decay

- **Objetivo**: fatos atomicos e summaries por entidade.
- **Features incluidas**: Feature 3
- **Gate de saida**: fixtures e primeira semana de uso revisada pelo PM.
- **Critérios de aceite**: Feature 3.

### Epicos da Fase 3

| Epico | Feature(s) | Status | SP Total |
|-------|------------|--------|----------|
| EPIC-F3-01 | Feature 3 | todo | 11 |

---

# 14. Epicos

## Epico: QMD baseline e documentacao operacional

- **ID**: EPIC-F1-01
- **Fase**: F1
- **Feature de Origem**: Feature 1
- **Objetivo**: Configurar QMD e MEMORY minimos reprodutiveis.
- **Resultado de Negocio Mensuravel**: recall semantico demonstravel no piloto.
- **Contexto Arquitetural**: OpenClaw + QMD local.
- **Definition of Done**:
  - [ ] Anexo A aplicado no ambiente piloto
  - [ ] Checklist de validacao arquivado em `PROJETOS/QMD/feito/` ou pasta de issues

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F1-01-001 | Configurar catalogo QMD paths e validar reindex | 2 | todo | Feature 1 |
| ISSUE-F1-01-002 | Template MEMORY.md minimo QMD | 2 | todo | Feature 1 |

## Epico: Consolidacao noturna

- **ID**: EPIC-F2-01
- **Fase**: F2
- **Feature de Origem**: Feature 2
- **Objetivo**: Job noturno + daily notes.
- **Definition of Done**:
  - [ ] Anexo C operacional
  - [ ] Logs ou artefatos de tres execucoes

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F2-01-001 | Definir schedule e timezone com PM | 1 | todo | Feature 2 |
| ISSUE-F2-01-002 | Implementar cron agentTurn + prompt consolidacao | 5 | todo | Feature 2 |
| ISSUE-F2-01-003 | Template memory/YYYY-MM-DD.md | 3 | todo | Feature 2 |

## Epico: Grafo, items.json e decay

- **ID**: EPIC-F3-01
- **Fase**: F3
- **Feature de Origem**: Feature 3
- **Objetivo**: Entidades com fatos atomicos e decay.
- **Definition of Done**:
  - [ ] Fixtures schema Anexo B
  - [ ] QMD indexando json das entidades

### Issues do Epico

| Issue ID | Nome | SP | Status | Feature |
|----------|------|-----|--------|---------|
| ISSUE-F3-01-001 | Modelar arvore PARA e convencao de paths | 3 | todo | Feature 3 |
| ISSUE-F3-01-002 | Pipeline fatos + bump access + weekly summary | 8 | todo | Feature 3 |

---

# 15. Dependencias Externas

| Dependencia | Tipo | Origem | Impacto | Status |
|-------------|------|--------|---------|--------|
| OpenClaw + QMD | runtime | openclaw | configuracao memory | pending |
| API LLM | API | provedor | job noturno | pending |

---

# 16. Rollout e Comunicacao

- **Estrategia de deploy**: piloto single-host PM; depois documentacao para replicação.
- **Comunicacao de mudancas**: atualizar INTAKE/PRD e referencias em SESSION-* se necessario.
- **Treinamento necessario**: leitura deste PRD e anexos.
- **Suporte pos-launch**: issues em `PROJETOS/QMD/`.

---

# 17. Revisoes e Auditorias

- **Auditorias planejadas**: ao fim de F1, F2 e F3.
- **Criterios de auditoria**: `PROJETOS/COMUM/GOV-AUDITORIA.md` quando aplicavel ao projeto.
- **Threshold anti-monolito**: `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md` quando aplicavel.

---

# 18. Checklist de Prontidao

- [x] Intake referenciado e versao confirmada
- [x] Features definidas com criterios de aceite verificaveis
- [x] Cada feature com impacts por camada preenchidos
- [x] Rastreabilidade explicita Feature -> Fase -> Epico -> Issue
- [x] Epicos criados e vinculados a features
- [x] Fases definidas com gates de saida
- [x] Dependencias externas mapeadas
- [x] Riscos identificados
- [x] Rollout planejado

---

# 19. Anexos e Referencias

- [INTAKE-QMD.md](./INTAKE-QMD.md)
- [felix-openclaw-pontos-relevantes.md](../../felix-openclaw-pontos-relevantes.md)
- [felixcraft.md](../../felixcraft.md)
- [AGENTS.md](../../AGENTS.md)

---

## Anexo A — Contrato `memory.qmd` (normativo para implementacao)

Objetivo: alinhar hosts sem depender de paths magicos nao documentados.

Campos obrigatorios no objeto `memory`:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `backend` | string | valor fixo `qmd` para este projeto |
| `qmd` | object | configuracao do indexador |

Campos obrigatorios em `memory.qmd`:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `includeDefaultMemory` | boolean | se `true`, inclui arquivos padrao do workspace OpenClaw (MEMORY, etc.) no indice |
| `paths` | array | entradas `{ path, name, pattern }` — `path` resolvido no host; `pattern` glob relativo ao path |
| `update.interval` | string | intervalo de reindexacao (ex. `5m`) |

Exemplo de referencia (ajustar paths ao host; nao versionar segredos):

```json
{
  "memory": {
    "backend": "qmd",
    "qmd": {
      "includeDefaultMemory": true,
      "paths": [
        { "path": "~/life", "name": "life", "pattern": "**/*.md" },
        { "path": "~/life", "name": "life-json", "pattern": "**/*.json" }
      ],
      "update": { "interval": "5m" }
    }
  }
}
```

MVP minimo sugerido ate fechar path `~/life` com PM: incluir pelo menos workspace ou subtree acordada com `**/*.md` para MEMORY + `memory/**/*.md` para daily notes.

Extensoes adicionais (`**/*.json`, etc.) entram quando Feature 3 estiver ativa.

---

## Anexo B — Schema `items.json`, `summary.md` e decay

### `summary.md`

- Resumo curto por entidade, regenerado periodicamente (ex. semanal) ou apos extracao noturna significativa.
- Priorizacao de conteudo por decay (abaixo).

### Fatos atomicos (`items.json`)

Array de objetos; campos minimos:

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | sim | identificador estavel |
| `fact` | string | sim | texto do fato |
| `category` | string | sim | ex. status, preference |
| `timestamp` | string (ISO date) | sim | quando observado |
| `source` | string | sim | origem (ex. data da daily note) |
| `status` | string | sim | `active` ou `superseded` |
| `relatedEntities` | array | nao | caminhos relativos de entidades |
| `lastAccessed` | string (ISO date) | nao | ultimo uso em conversa |
| `accessCount` | number | nao | contador incremental |
| `supersededBy` | string | se superseded | id do fato substituto |

Regras:

- Nunca apagar fatos: marcar `superseded` e `supersededBy`.
- Ao referenciar um fato na consolidacao ou no chat assistido, atualizar `lastAccessed` e incrementar `accessCount`.

### Decay (relevancia no `summary.md`)

| Faixa | Janela sugerida | Comportamento no summary |
|-------|-----------------|---------------------------|
| Hot | acesso ou atualizacao nos ultimos 7 dias | destaque principal |
| Warm | 8–30 dias | inclusao secundaria |
| Cold | 31+ dias | fora do summary; permanece em `items.json` |

Fatos com `accessCount` alto podem permanecer warm mais tempo (ajuste fino na issue).

---

## Anexo C — Especificacao do job noturno de consolidacao

### Objetivo

Revisar conversas/sessoes do dia; extrair fatos duraveis; atualizar `memory/YYYY-MM-DD.md`; opcionalmente atualizar entidades (Feature 3); acionar reindexacao QMD.

### Agendamento

- **Tipo preferido**: entrada `cron` OpenClaw com `payload.kind: agentTurn` e `sessionTarget: isolated` (reduz vazamento de contexto).
- **Expressao e timezone**: definidos com PM (placeholder: `0 2 * * *` ou `0 23 * * *` conforme fuso); campo `tz` obrigatorio no objeto schedule.
- **Alternativa**: script host + `openclaw` CLI se o runtime nao suportar isolamento desejado — documentar na issue ISSUE-F2-01-002.

### Conteudo minimo do prompt/mensagem do job

1. Listar sessoes ou fontes do dia a considerar (conforme tool disponivel no ambiente).
2. Extrair: decisoes, projetos, pessoas, mudancas de status; ignorar small talk e pedidos transientes.
3. Atualizar `memory/YYYY-MM-DD.md` com secoes: Key Events, Decisions, Facts Extracted, Active Long-Running Processes (se aplicavel).
4. **Proibicoes explicitas**: nao modificar `PROJETOS/COMUM/**`; nao editar issues/GOV sem fluxo de aprovacao; nao promover para canonicos.
5. Se Feature 3 ativa: emitir ou atualizar entradas em `items.json` e bump de acessos quando fatos foram usados no dia.
6. Registrar em log: horario de inicio/fim, erros, tokens/custo se disponivel.

### Modelo

- Preferir modelo mais barato que suporte extracao estruturada com confianca aceitavel; Opus apenas se PM exigir qualidade maxima no piloto (ver restricao de custo no intake).

---

> **Frase Guia**: "Feature organiza, Task executa, Teste valida"
