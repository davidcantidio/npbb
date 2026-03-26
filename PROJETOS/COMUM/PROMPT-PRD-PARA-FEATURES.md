---
doc_id: "PROMPT-PRD-PARA-FEATURES.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# Prompt Canonico - PRD para Features

## Como usar

Cole este prompt numa sessao com acesso ao repositorio e informe:

- o caminho de `PRD-<PROJETO>.md`
- o identificador do projeto (`<PROJETO>`) e a pasta raiz do projeto em `PROJETOS/<PROJETO>/`

## Prompt

Voce e um engenheiro de produto responsavel pela **primeira decomposicao entregavel** apos o PRD:
criar **manifestos de Feature** em Markdown versionado, **sem** alterar o PRD para incluir catalogo de features.

Principios de trabalho:

- **Markdown + Git** sao a fonte de verdade; cada feature e um ficheiro (e pasta) sob `PROJETOS/<PROJETO>/features/`
- o **PRD ja esta fechado** no seu contrato: problema, escopo, metricas, arquitetura geral, rollout — **nao** lista de features nem user stories no PRD
- **delivery-first** / **feature-first** orientam o fatiamento: cada feature e um comportamento entregavel coerente
- backend, frontend, dados e testes aparecem como **impactos** da feature, nao como eixo de organizacao do manifesto

### Leitura obrigatoria

1. siga `PROJETOS/COMUM/boot-prompt.md`, Niveis 1 e 2, quando aplicavel
2. leia o `PRD-<PROJETO>.md` informado na integra
3. use `PROJETOS/COMUM/GOV-PRD.md` como limite do que o PRD cobre e do que fica fora
4. use `PROJETOS/COMUM/GOV-FEATURE.md` como contrato normativo do manifesto de feature
5. use `PROJETOS/COMUM/TEMPLATE-FEATURE.md` como **estrutura obrigatoria** de cada `FEATURE-<N>.md`
6. confirme a estrutura de pastas alvo em `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md` (secao de estrutura canonica)
7. se o projeto ja tiver features, leia os `FEATURE-*.md` existentes para **numeracao, nomenclatura e dependencias** antes de acrescentar novas

### Passagem 1 - Alinhamento e lacunas

Antes de criar ou alterar ficheiros:

- extraia do PRD os **temas de capacidade** e o **escopo dentro/fora** relevantes para fatiar features
- liste **lacunas criticas** que impedem definir features com objetivo de negocio e criterios de aceite **verificaveis** ao nivel do manifesto
- diferencie fato (do PRD), inferencia e hipotese; nao invente regra de negocio ausente no PRD/intake
- se o PRD ainda contiver secao ou tabela de **Features** ou **User Stories** (legado), **nao** a reproduza no PRD: trate-a apenas como rascunho a **normalizar** nos novos manifestos sob `features/`, e registe a divergencia numa nota breve no PR ou na mensagem de commit, **sem** reintroduzir catalogo no PRD

Se houver lacunas criticas, pare e devolva apenas:

- resumo do que o PRD ja sustenta
- lacunas criticas
- perguntas objetivas ao humano
- decisao: `BLOQUEADO`

### Passagem 2 - Geracao dos manifestos de Feature

So execute se a passagem 1 nao estiver bloqueada.

Para cada feature a criar ou atualizar:

- crie ou atualize `PROJETOS/<PROJETO>/features/FEATURE-<N>-<NOME-SLUG>/FEATURE-<N>.md` seguindo `TEMPLATE-FEATURE.md`
- garanta **rastreabilidade** explicita ao PRD (referencia ao ficheiro e, quando couber, trechos ou secoes do PRD que fundamentam a feature)
- defina **objetivo de negocio**, **comportamento esperado**, **criterios de aceite verificaveis** e **riscos/dependencias** no manifesto — nao delegue isso ao PRD
- ordene e numere features de forma coerente com **fases/rollout** descritos no PRD quando existirem, sem copiar o PRD como lista de features
- se uma fundacao tecnica nao entrega comportamento sozinha, trate como **dependencia explicita** entre features ou como pre-requisito no manifesto, nao como "feature camada"
- **nao** crie User Stories nem Tasks nesta etapa; a etapa seguinte e `PROMPT-FEATURE-PARA-USER-STORIES.md` / `SESSION-DECOMPOR-FEATURE-EM-US.md`

### Requisitos minimos da saida

- um `FEATURE-<N>.md` por feature planeada nesta rodada, todos sob `features/`, todos aderentes a `GOV-FEATURE.md` e `TEMPLATE-FEATURE.md`
- indices relativos e nomes de pasta alinhados a convencao do projeto (`FEATURE-<N>-<NOME>/`)
- nenhuma edicao ao PRD que **adicione** catalogo estruturado de features ou US (ajustes pontuais de rastreabilidade ou typo, se necessarios, devem manter `GOV-PRD.md`)

### Regra final

Se uma dependencia essencial estiver ausente no PRD, declare a lacuna. Nao complete silenciosamente o que o PRD nao suporta.
