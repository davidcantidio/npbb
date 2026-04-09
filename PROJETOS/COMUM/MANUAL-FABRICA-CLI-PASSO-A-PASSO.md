---
doc_id: "MANUAL-FABRICA-CLI-PASSO-A-PASSO.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-31"
---

# Manual - Fabrica CLI Passo a Passo

> Este manual e apenas ilustrativo.
> Se houver conflito com `GOV-*`, `SPEC-*`, `TEMPLATE-*`, `PROMPT-*` ou `SESSION-*`,
> os artefatos canônicos de governanca prevalecem.

## Objetivo

Mostrar, passo a passo, como usar a CLI da Fabrica para:

1. criar um projeto novo;
2. gerar `INTAKE`;
3. gerar `PRD`;
4. gerar `Features`;
5. gerar `User Stories`;
6. gerar `Tasks`;
7. confirmar que o projeto apareceu no banco Postgres.

## Projeto Ficticio do Exemplo

Neste manual, o projeto ficticio sera:

- **slug do projeto**: `ACME-PEDIDOS`
- **ideia ilustrativa**: um sistema simples para receber pedidos de retirada em loja

Nada neste exemplo e regra de negocio do framework. O objetivo e apenas demonstrar o uso da CLI.

## Pre-Requisitos

Antes de rodar os comandos:

- estar na raiz do repositorio;
- ter `python` disponivel no `PATH`;
- ter `FABRICA_PROJECTS_DATABASE_URL` apontando para o Postgres operacional;
- ter o schema do indice Postgres aplicado.

No Windows, os wrappers `.ps1` do indice tambem conseguem ler `host.env` com
chaves legadas do namespace anterior e remapeiam esses valores para
`FABRICA_*` apenas no processo atual.

Exemplo em PowerShell:

```powershell
$env:FABRICA_PROJECTS_DATABASE_URL = "postgresql://user:pass@localhost:5432/fabrica_projects"
```

Se quiser validar manualmente no banco ao fim do fluxo, tenha tambem `psql` no `PATH`.

Bootstrap rapido do indice em PowerShell:

```powershell
..\fabrica\bin\bootstrap-fabrica-projects-postgres.ps1 --skip-chunks
```

## Passo 1 - Criar o Arquivo da Ideia

Crie um arquivo simples com a ideia inicial.

Exemplo: `idea-acme-pedidos.md`

```md
# ACME Pedidos

- Lojistas precisam registrar pedidos de retirada sem usar WhatsApp solto.
- O fluxo minimo deve criar pedido, listar pedidos e marcar retirada.
- O projeto deve nascer no Markdown e aparecer no banco via sync.
```

## Passo 2 - Criar o Projeto

Rode:

```powershell
python .\scripts\fabrica.py project create ACME-PEDIDOS
```

O que esse comando faz:

- cria `PROJETOS/ACME-PEDIDOS/`;
- cria `INTAKE-ACME-PEDIDOS.md`;
- cria `PRD-ACME-PEDIDOS.md`;
- cria `AUDIT-LOG.md`;
- cria `features/`;
- cria `encerramento/RELATORIO-ENCERRAMENTO.md`;
- roda sync ao final.

Estrutura esperada logo apos esse passo:

```text
PROJETOS/
  ACME-PEDIDOS/
    INTAKE-ACME-PEDIDOS.md
    PRD-ACME-PEDIDOS.md
    AUDIT-LOG.md
    features/
    encerramento/
      RELATORIO-ENCERRAMENTO.md
```

## Passo 3 - Gerar o Intake

Rode:

```powershell
python .\scripts\fabrica.py generate intake --project ACME-PEDIDOS --idea-file .\idea-acme-pedidos.md
```

Resultado esperado:

- o arquivo `PROJETOS/ACME-PEDIDOS/INTAKE-ACME-PEDIDOS.md` deixa de ser um placeholder minimo;
- a CLI consolida a ideia inicial em um intake preenchido;
- o sync roda ao final.

Depois desse passo, revise manualmente o intake.

## Passo 4 - Gerar o PRD

Rode:

```powershell
python .\scripts\fabrica.py generate prd --project ACME-PEDIDOS
```

Resultado esperado:

- o arquivo `PROJETOS/ACME-PEDIDOS/PRD-ACME-PEDIDOS.md` passa a refletir o intake;
- o PRD continua sem backlog detalhado de features e user stories dentro do corpo;
- o sync roda ao final.

Depois desse passo, revise manualmente o PRD.

## Passo 5 - Gerar as Features

Rode:

```powershell
python .\scripts\fabrica.py generate features --project ACME-PEDIDOS
```

Resultado esperado:

- a pasta `features/` passa a conter manifestos `FEATURE-*`;
- cada feature nasce em estado `todo`;
- cada manifesto ja traz a tabela de user stories planejadas;
- o sync roda ao final.

Exemplo ilustrativo de saida:

```text
PROJETOS/
  ACME-PEDIDOS/
    features/
      FEATURE-1-LOJISTAS-PRECISAM-REGISTRAR-PEDIDOS/
        FEATURE-1.md
        user-stories/
        auditorias/
      FEATURE-2-O-FLUXO-MINIMO-DEVE-CRIAR/
        FEATURE-2.md
        user-stories/
        auditorias/
```

## Passo 6 - Gerar as User Stories de uma Feature

Escolha uma feature e gere as user stories dela.

Exemplo com a primeira feature:

```powershell
python .\scripts\fabrica.py generate stories --project ACME-PEDIDOS --feature FEATURE-1
```

Resultado esperado:

- a pasta da feature passa a conter uma ou mais user stories em `user-stories/US-*/README.md`;
- cada user story nasce com `task_instruction_mode: required`;
- o sync roda ao final.

Exemplo ilustrativo:

```text
PROJETOS/
  ACME-PEDIDOS/
    features/
      FEATURE-1-LOJISTAS-PRECISAM-REGISTRAR-PEDIDOS/
        FEATURE-1.md
        user-stories/
          US-1-01-LOJISTAS-PRECISAM-REGISTRAR-PEDIDOS/
            README.md
        auditorias/
```

## Passo 7 - Gerar as Tasks de uma User Story

Escolha a user story e gere as tasks.

Exemplo:

```powershell
python .\scripts\fabrica.py generate tasks --project ACME-PEDIDOS --story US-1-01
```

Resultado esperado:

- a user story passa a ter `TASK-1.md`, `TASK-2.md`, `TASK-3.md`;
- as tasks saem com `depends_on`, `write_scope` e instrucoes de TDD;
- o sync roda ao final.

Exemplo ilustrativo:

```text
PROJETOS/
  ACME-PEDIDOS/
    features/
      FEATURE-1-LOJISTAS-PRECISAM-REGISTRAR-PEDIDOS/
        user-stories/
          US-1-01-LOJISTAS-PRECISAM-REGISTRAR-PEDIDOS/
            README.md
            TASK-1.md
            TASK-2.md
            TASK-3.md
```

## Passo 8 - Rodar Sync Manualmente Quando Precisar

Os comandos de escrita ja rodam sync no final.
Mesmo assim, voce pode rodar sync isoladamente:

```powershell
python ..\fabrica\scripts\fabrica.py --repo-root . sync
```

Use isso quando:

- quiser reindexar o projeto inteiro;
- tiver ajustado artefatos manualmente;
- quiser confirmar o estado do read model.

## Passo 9 - Verificar os Arquivos no Disco

Verificacao rapida no PowerShell:

```powershell
Get-ChildItem .\PROJETOS\ACME-PEDIDOS -Recurse
```

Arquivos minimos esperados ao fim do fluxo ilustrativo:

- `PROJETOS/ACME-PEDIDOS/INTAKE-ACME-PEDIDOS.md`
- `PROJETOS/ACME-PEDIDOS/PRD-ACME-PEDIDOS.md`
- `PROJETOS/ACME-PEDIDOS/AUDIT-LOG.md`
- pelo menos um `PROJETOS/ACME-PEDIDOS/features/FEATURE-*/FEATURE-*.md`
- pelo menos um `PROJETOS/ACME-PEDIDOS/features/FEATURE-*/user-stories/US-*/README.md`
- pelo menos um `PROJETOS/ACME-PEDIDOS/features/FEATURE-*/user-stories/US-*/TASK-*.md`

## Passo 10 - Verificar que o Projeto Apareceu no Banco

### 10.1 Verificar o projeto

```powershell
psql $env:FABRICA_PROJECTS_DATABASE_URL -c "select slug from projects where slug = 'ACME-PEDIDOS';"
```

Resultado esperado:

```text
     slug
---------------
 ACME-PEDIDOS
```

### 10.2 Verificar os documentos de projeto

```powershell
psql $env:FABRICA_PROJECTS_DATABASE_URL -c "select 'intake' as artifact_kind, i.path_relative from intakes i join projects p on p.id = i.project_id where p.slug = 'ACME-PEDIDOS' union all select 'prd' as artifact_kind, pr.path_relative from prds pr join projects p on p.id = pr.project_id where p.slug = 'ACME-PEDIDOS' union all select d.kind as artifact_kind, d.path_relative from documents d join projects p on p.id = d.project_id where p.slug = 'ACME-PEDIDOS' and d.kind in ('audit_log', 'closing_report') order by artifact_kind, path_relative;"
```

Voce deve ver pelo menos:

- `INTAKE-ACME-PEDIDOS.md`
- `PRD-ACME-PEDIDOS.md`
- `AUDIT-LOG.md`
- `encerramento/RELATORIO-ENCERRAMENTO.md`

### 10.3 Verificar feature, user story e task

```powershell
psql $env:FABRICA_PROJECTS_DATABASE_URL -c "select f.feature_key, us.user_story_key, t.task_number, t.status from projects p join features f on f.project_id = p.id left join user_stories us on us.feature_id = f.id left join tasks t on t.user_story_id = us.id where p.slug = 'ACME-PEDIDOS' order by f.feature_key, us.user_story_key, t.task_number;"
```

Voce deve ver:

- ao menos uma linha com `FEATURE-1`;
- ao menos uma linha com `US-1-01`;
- tasks `1`, `2` e `3` com status inicial `todo`.

## Reexecucao e Idempotencia

Se voce rodar novamente o mesmo comando com a mesma entrada:

- a Fabrica tenta preservar o mesmo resultado;
- arquivos gerados pela propria CLI podem ser regravados sem drift material;
- arquivos nao gerados pela CLI nao devem ser sobrescritos silenciosamente.

Exemplo:

```powershell
python .\scripts\fabrica.py generate tasks --project ACME-PEDIDOS --story US-1-01
python .\scripts\fabrica.py generate tasks --project ACME-PEDIDOS --story US-1-01
```

O segundo comando deve manter o mesmo conteudo essencial das tasks.

## Alias Legado

Durante a transicao, ainda existe alias legado:

```powershell
python .\scripts\openclaw.py project create ACME-PEDIDOS
```

Mas o nome recomendado e sempre:

```text
fabrica
```

## Resumo Curto do Fluxo Completo

```powershell
python .\scripts\fabrica.py project create ACME-PEDIDOS
python .\scripts\fabrica.py generate intake --project ACME-PEDIDOS --idea-file .\idea-acme-pedidos.md
python .\scripts\fabrica.py generate prd --project ACME-PEDIDOS
python .\scripts\fabrica.py generate features --project ACME-PEDIDOS
python .\scripts\fabrica.py generate stories --project ACME-PEDIDOS --feature FEATURE-1
python .\scripts\fabrica.py generate tasks --project ACME-PEDIDOS --story US-1-01
python ..\fabrica\scripts\fabrica.py --repo-root . sync
```

## Quando Parar e Revisar Manualmente

Pare e revise antes de continuar quando:

- o intake gerado nao representa a ideia real;
- o PRD ficou amplo demais ou ambiguo;
- a feature gerada misturou mais de um comportamento grande;
- a user story ficou grande demais;
- as tasks nao refletem uma sequencia clara de TDD e entrega.

O fluxo e deterministico, mas continua exigindo julgamento humano nas transicoes de escopo.
