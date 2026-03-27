---
doc_id: "INTAKE-QMD.md"
version: "1.1"
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

# INTAKE - QMD

> Preencha todos os campos. Se algo ainda nao estiver decidido, escreva explicitamente `nao_definido`, `nao_aplicavel` ou registre em `Lacunas Conhecidas`. Nao apague secoes obrigatorias.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel (demanda nova no repositorio openclaw)
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: formalizar um projeto dedicado para implementar arquitetura de gestao de memoria em camadas para um operador/agente de longa duracao (24/7), com backend de busca semantica **QMD** e politica explicita de conflito com artefatos canonicos do framework (escalacao humana).
- PRD derivado: [PRD-QMD.md](./PRD-QMD.md) (contratos `memory.qmd`, job noturno, decay e `items.json`).

### Fontes de inspiracao arquitetural (nao normativas)

- [`felix-openclaw-pontos-relevantes.md`](../../felix-openclaw-pontos-relevantes.md) — resumo do relato Felix/OpenClaw (camadas, QMD, consolidacao noturna).
- [`felixcraft.md`](../../felixcraft.md) — playbook Felix (MEMORY.md, daily notes, grafo opcional, configuracao JSON de exemplo com `memory.backend: qmd`).

## 1. Resumo Executivo

- nome curto da iniciativa: QMD — memoria operacional em camadas com retrieval QMD
- tese em 1 frase: tratar a **gestao de memoria** como guarda-chuva maior que engloba, entre outras camadas, os artefatos canonicos de **gestao de projeto** (`GOV-*`, `SESSION-*`, issue-first), usando QMD para recuperacao semantica e jobs de consolidacao sem substituir a autoridade normativa versionada.
- valor esperado em 3 linhas:
  - reduzir repeticao de contexto e retrabalho em sessoes longas com agente/OpenClaw
  - separar claramente **memoria derivada** (notas, fatos operacionais, preferencias) da **camada canonica** de projeto
  - definir regras de **HITL** quando memoria extraida ou inferida conflitar com canonicos

## 2. Problema ou Oportunidade

- problema atual: sem uma arquitetura explicita de memoria + QMD, o operador depende de contexto volatil na sessao ou de busca textual fraca; risco de misturar fatos informais com normas do framework.
- evidencia do problema: relatos e playbooks externos (Felix) descrevem ganho material com indexacao QMD, notas diarias e consolidacao; o repositorio openclaw ja centraliza governanca em markdown mas nao descreve ainda um projeto **feature-first** para a stack de memoria do funcionario 24/7.
- custo de nao agir: continuidade operacional fragil, mais alucinacao de contexto, possivel gravacao indevida de inferencias como se fossem decisoes de projeto.
- por que agora: o PM definiu o modelo mental (guarda-chuva de memoria > camada canonica como uma das camadas) e a regra de conflito (humano consultado); falta formalizar em Intake -> PRD.

## 3. Publico e Operadores

- usuario principal: PM/proprietario do workspace que opera com agente/OpenClaw de longa duracao
- usuario secundario: revisores de governanca que validam mudancas em artefatos canonicos
- operador interno: agente OpenClaw (e eventualmente sub-agentes) configurados com tools, cron e memoria
- quem aprova ou patrocina: PM (humano)

## 4. Jobs to be Done

- job principal: "Quero que o agente recupere rapidamente o que importa (preferencias, fatos recentes, entidades) sem eu redigitar contexto, respeitando que decisoes normativas do projeto ficam nos canonicos ate eu aprovar mudanca."
- jobs secundarios: consolidar o dia em notas estruturadas; indexar pastas acordadas para QMD; detectar e escalar conflitos memoria vs canonicos.
- tarefa atual que sera substituida: depender apenas de contexto de chat e busca ad hoc em arquivos, sem politica unificada de camadas e sem backend QMD declarado.

## 5. Fluxo Principal Desejado

Descreva o fluxo ponta a ponta em etapas curtas:

1. Configurar OpenClaw (ou ambiente equivalente) com `memory.backend: qmd` e paths/padroes de indexacao para as camadas nao canonicas acordadas (ex.: `MEMORY.md`, `memory/YYYY-MM-DD.md`, area tipo `~/life` ou equivalente definido no PRD).
2. Durante o dia, o agente grava e atualiza memoria operacional nas camadas permitidas; QMD reindexa em intervalo configurado.
3. Job agendado (ex.: noturno) revisa conversas/sessoes e propoe ou aplica atualizacoes apenas onde o PRD autorizar, sem reescrever `GOV-*` ou issues sem fluxo de aprovacao.
4. Se retrieval ou consolidacao sugerir fato que **conflite** com artefato canonicos (`PROJETOS/COMUM/*`, `PROJETOS/<PROJETO>/*` normativos), o agente **para de tratar como decidido**, registra a divergencia e **solicita decisao ao PM** antes de qualquer promocao para canonicos.

## 6. Escopo Inicial

### Dentro

- Especificar e implementar (nas fases seguintes via PRD) a arquitetura em camadas: conhecimento tatico (`MEMORY.md` ou equivalente), notas diarias, grafo/entidades opcional com schema de fatos, conforme PRD.
- Configuracao operacional de QMD (paths, patterns, intervalos de update) alinhada ao OpenClaw.
- Politica de **autoridade**: canonicos prevalecem na duvida; promocao de conteudo derivado para canonicos exige **confirmacao explicita do PM**.
- Documentacao e artefatos do projeto `QMD` em `PROJETOS/QMD/` (PRD, fases, issues) apos este intake.

### Fora

- Alterar unilateralmente normas em `PROJETOS/COMUM/` sem issue/PRD e fluxo de governanca.
- Substituir o paradigma issue-first por "apenas memoria livre".
- Garantir seguranca de nivel enterprise ou conformidade legal especifica nao descrita neste intake (tratar no PRD se necessario).
- Heartbeat para tarefas longas, delegacao a agentes de codigo (ex.: Codex), padroes tipo Ralph loop ou monitoramento tmux — fora do escopo do projeto QMD (operacao 24/7 mais ampla que memoria + QMD + consolidacao).

## 7. Resultado de Negocio e Metricas

- objetivo principal: memoria operacional util e recuperavel via QMD, com fronteira clara para canonicos e HITL em conflitos.
- metricas leading: tempo medio para o agente localizar contexto relevante apos pergunta do PM; numero de re-prompts com o mesmo contexto na mesma semana; incidentes de divergencia memoria-vs-canonico detectados e escalados (deve ser > 0 se houver conflito real).
- metricas lagging: satisfacao subjetiva do PM com continuidade semanal; reducao percebida de "comecar do zero" em sessoes.
- criterio minimo para considerar sucesso: QMD indexando conjuntos acordados; pelo menos uma rotina de consolidacao definida e testada; politica de conflito documentada e seguida em exercicio piloto.

## 8. Restricoes e Guardrails

- restricoes tecnicas: dependencia do stack OpenClaw e disponibilidade do backend QMD na versao em uso; paths absolutos podem variar por host (Mac/Linux).
- restricoes operacionais: estado vivo, secrets e dados sensiveis permanecem fora do Git conforme [`AGENTS.md`](../../AGENTS.md); memoria com dados restritos nao deve ser empurrada para repositorio publico sem revisao.
- restricoes legais ou compliance: nao_definido — avaliar no PRD se houver tratamento de dados pessoais de terceiros nas notas.
- restricoes de prazo: nao_definido
- restricoes de design ou marca: conteudo do projeto deve respeitar vocabulario e cadeia Intake -> PRD -> fases do framework.

## 9. Dependencias e Integracoes

- sistemas internos impactados: workspace OpenClaw, configuracao de agente, possivel integracao com skills/sessoes existentes (`SESSION-*`, boot hooks).
- sistemas externos impactados: nenhum obrigatorio neste intake; APIs de modelo cobradas por cron consolidacao (custo) — detalhar no PRD.
- dados de entrada necessarios: conversas/sessoes; arquivos markdown/json nas pastas indexadas; artefatos canonicos para comparacao em caso de conflito.
- dados de saida esperados: notas atualizadas; indices QMD atualizados; registros de escalacao ao PM quando aplicavel.

## 10. Arquitetura Afetada

- backend: configuracao de memoria OpenClaw + QMD; possiveis scripts/cron no host.
- frontend: nao_aplicavel (salvo superficie de mensageria ja usada pelo OpenClaw).
- banco/migracoes: nao_aplicavel neste intake (QMD/indexacao como componente separado; persistencia exata no PRD).
- observabilidade: logs de reindexacao e de job de consolidacao — detalhar no PRD.
- autorizacao/autenticacao: canais confiaveis para comandos vs informativos seguem politica ja descrita no framework e nos materiais Felix; reforcar no PRD se necessario.
- rollout: piloto em ambiente do PM antes de generalizar paths e horarios de cron.

## 11. Riscos Relevantes

- risco de produto: usuario confundir memoria derivada com decisao de projeto; mitigacao — rotulos, HITL e templates claros.
- risco tecnico: QMD mal configurado indexando pastas erradas ou dados sensiveis.
- risco operacional: cron consolidacao falhando silenciosamente ou consumindo custo excessivo de modelo.
- risco de dados: vazamento de contexto restrito em indices ou backups locais.
- risco de adocao: complexidade inicial alta; mitigacao — rollout em nivel minimo viavel (Felix: comecar por MEMORY.md antes do grafo completo).

## 12. Nao-Objetivos

- Tornar o agente autoridade sobre mudancas em `GOV-*` ou substituir gates de auditoria do framework.
- Implementar produto comercial ou multi-tenant neste projeto.
- Otimizar custo de LLM de forma exaustiva antes de validar valor da memoria em uso real (pode ser fase posterior).
- Tratar heartbeat, orchestracao de sessoes longas ou Ralph loop como entrega obrigatoria deste projeto (ver [PRD-QMD.md](./PRD-QMD.md) para delimitacao e possivel projeto separado).

## 13. Contexto Especifico para Problema ou Refatoracao

> Obrigatorio para `intake_kind: problem | refactor | audit-remediation`. Para outros casos, preencher com `nao_aplicavel`.

- sintoma observado: nao_aplicavel
- impacto operacional: nao_aplicavel
- evidencia tecnica: nao_aplicavel
- componente(s) afetado(s): nao_aplicavel
- riscos de nao agir: nao_aplicavel

## 14. Lacunas Conhecidas

Liste tudo que a IA nao pode inventar sozinha:

- regra de negocio ainda nao definida: layout final de diretorios (ex.: `~/life` vs subtree do workspace); quais extensoes/patterns entram no QMD além de `**/*.md` e opcional `**/*.json`.
- dependencia ainda nao confirmada: versao exata do OpenClaw e disponibilidade/feature-flag do backend QMD no ambiente alvo.
- dado ainda nao disponivel: timezone e horario preferido para consolidacao; modelo e orcamento dedicados ao job noturno.
- decisao de UX ainda nao fechada: como o PM prefere receber alertas de conflito (canal, formato, fila de aprovacao).
- outro ponto em aberto: se parte da memoria residira apenas fora do Git (recomendado para estado vivo) e como versionar exemplos/templates sem dados sensiveis.

## 15. Perguntas que o PRD Precisa Responder

- Qual a arquitetura alvo minima (MVP) vs fases para grafo de entidades, decay de fatos e `items.json`?
- Qual o contrato exato da configuracao `memory.qmd` (paths, nomes, `includeDefaultMemory`, intervalos)?
- O job de consolidacao e um cron OpenClaw (`agentTurn`), script host, ou ambos? Qual prompt e modelo?
- Como registrar e auditar escalacoes memoria-vs-canonico (template, issue obrigatoria, log)?
- Como este projeto se articula com outros projetos em `PROJETOS/` (ex.: OC-MISSION-CONTROL) sem duplicar normas?

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
