---
doc_id: "PROMPT-MONOLITO-PARA-INTAKE.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# PROMPT-MONOLITO-PARA-INTAKE

## Objetivo

Converter um achado estrutural `monolithic-file` ou `monolithic-function` em um
`INTAKE-<PROJETO>-REFACTOR-<SLUG>.md` rastreavel, pronto para iniciar um fluxo
de remediacao estrutural sem perder a origem da auditoria.

## Como usar

Cole este prompt em uma sessao com acesso ao repositorio e entregue um pacote
minimo de entrada. Se algum dado ainda nao existir, declare explicitamente
`nao_definido`, `nao_disponivel` ou registre a lacuna; nao invente contexto.

### Entrada minima obrigatoria

- projeto que recebera o intake de remediacao
- projeto e fase de origem do achado, quando aplicavel
- `Audit ID` e caminho do relatorio de auditoria de origem
- classificacao do achado: `monolithic-file` ou `monolithic-function`
- componente alvo com caminho completo; para funcao monolitica, incluir nome da
  funcao ou metodo
- linguagem ou stack avaliada
- metricas observadas que cruzaram threshold no
  `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`, informando ao menos:
  - metrica
  - valor observado
  - nivel cruzado (`warn` ou `block`)
- impacto operacional de nao agir
- confirmacao de que o destino correto e `new-intake`, e nao `issue-local`
- riscos de compatibilidade, regressao ou rollout ja conhecidos, se existirem

## Prompt

Voce e um engenheiro de produto responsavel por transformar um achado
`monolithic-file` ou `monolithic-function` em um intake de remediacao
estrutural rastreavel.

### Leitura obrigatoria

1. siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1 e 2
2. leia o relatorio de auditoria de origem
3. leia `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
4. leia `PROJETOS/COMUM/TEMPLATE-INTAKE.md`
5. leia o `AUDIT-LOG.md` do projeto de origem, se existir

### Validacao minima

Antes de escrever o intake, confirme:

- o achado e realmente `monolithic-file` ou `monolithic-function`
- qual arquivo, componente ou funcao disparou o achado
- quais metricas cruzaram threshold canonico e em qual nivel (`warn` ou `block`)
- qual o impacto operacional de nao agir
- qual auditoria originou a remediacao (`origin_audit_id` e
  `origin_report_path`)
- qual projeto recebera o intake
- se o destino recomendado continua sendo `new-intake`
- se ha contexto minimo para descrever decomposicao, riscos de interface e
  testes de regressao

Devolva `BLOQUEADO` sem gerar intake se qualquer uma destas condicoes ocorrer:

- faltar `Audit ID`, relatorio de origem ou projeto destino
- faltar componente alvo identificavel
- nao houver metrica estrutural vinculada ao `SPEC-ANTI-MONOLITO.md`
- o achado nao for estrutural ou couber melhor como `issue-local`
- nao houver contexto minimo para explicar impacto, risco ou objetivo da
  remediacao

### Regras de saida

Gere exatamente um intake compativel com
`PROJETOS/COMUM/TEMPLATE-INTAKE.md`.

Regras obrigatorias:

- nome do arquivo sugerido:
  `INTAKE-<PROJETO>-REFACTOR-<SLUG>.md`
- reproduza o frontmatter canonico completo do `TEMPLATE-INTAKE.md`, sem
  remover chaves, sem renomear campos e sem mudar a ordem base do template
- o frontmatter final deve conter, no minimo:
  - `doc_id`
  - `version`
  - `status`
  - `owner`
  - `last_updated`
  - `project: "<PROJETO>"`
  - `intake_kind: "refactor"`
  - `source_mode: "audit-derived"`
  - `origin_project`
  - `origin_phase`
  - `origin_audit_id`
  - `origin_report_path`
  - `product_type`
  - `delivery_surface`
  - `business_domain`
  - `criticality`
  - `data_sensitivity`
  - `integrations`
  - `change_type`
  - `audit_rigor`
- para os campos taxonomicos do frontmatter (`product_type`,
  `delivery_surface`, `business_domain`, `criticality`, `data_sensitivity`,
  `change_type`, `audit_rigor`), use apenas valores validos de
  `PROJETOS/COMUM/GOV-INTAKE.md`; se nao houver base suficiente para escolher
  com seguranca, devolva `BLOQUEADO` em vez de inventar taxonomia
- preserve todas as secoes do template canonico de intake
- preencha explicitamente todas as secoes `0` a `16`, mantendo titulos,
  checklist e estrutura do template
- quando um dado nao puder ser comprovado com os insumos lidos, use
  `nao_definido` ou `nao_aplicavel` somente em campos cujo desconhecimento nao
  bloqueie objetivo, escopo, restricoes, arquitetura, riscos ou taxonomias
  controladas; toda ocorrencia deve ser registrada na secao
  `14. Lacunas Conhecidas`
- nao crie thresholds, severidades ou categorias fora do
  `SPEC-ANTI-MONOLITO.md`

### Conteudo minimo do intake gerado

O intake final deve deixar explicito:

- rastreabilidade completa da auditoria de origem
- problema estrutural resumido e por que ele agora exige remediacao
- publico principal, operadores envolvidos e quem patrocina a remediacao
- job principal, jobs secundarios e a tarefa atual que sera substituida
- fluxo principal desejado em etapas curtas, sem depender de contexto externo
- componente(s) afetado(s) e evidencia tecnica do monolito
- proposta inicial de decomposicao em modulos, responsabilidades ou fatias
- objetivo de negocio, metricas leading, metricas lagging e criterio minimo de
  sucesso
- restricoes tecnicas e operacionais, alem de nao-objetivos explicitos
- dependencias, integracoes e dados de entrada/saida esperados
- arquitetura afetada por superficie e estrategia inicial de rollout
- riscos relevantes de produto, tecnicos, operacionais, de dados e de adocao
- riscos de compatibilidade de interface, rollout e regressao
- testes de regressao minimos para proteger o comportamento atual
- limites do escopo da remediacao e nao-objetivos
- perguntas que o PRD precisara responder antes da execucao
- checklist de prontidao do PRD mantido no formato do template

### Saida esperada

Responda apenas com o conteudo completo do intake gerado.

Esse intake deve:

- ser rastreavel de volta ao relatorio e `Audit ID` de origem
- estar alinhado ao `TEMPLATE-INTAKE.md` sem remover secoes obrigatorias
- carregar para a secao de refatoracao a evidencia estrutural vinda do achado
- fornecer handoff claro para a futura sessao que criara o PRD da remediacao
- ficar pronto para validacao contra os campos minimos obrigatorios de
  `PROJETOS/COMUM/GOV-INTAKE.md` sem preenchimento adicional fora do prompt
