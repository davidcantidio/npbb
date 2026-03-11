---
doc_id: "PRD-PILOTO-ISSUE-FIRST.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-03-07"
---

# PRD - PILOTO-ISSUE-FIRST

## 1. Visao do Produto

Criar um projeto piloto de documentacao dentro de `PROJETOS/` para validar o modelo `issue-first` com arquivos atomicos por issue, manifesto de sprint nao estrutural e navegacao hibrida por links Markdown e wikilinks qualificados.

## 2. Objetivo Central e Resultado Mensuravel

Disponibilizar um projeto novo, pequeno e navegavel, em que um agente consiga localizar uma unica issue elegivel lendo apenas o PRD, o arquivo da fase, o manifesto do epico e um `issues/ISSUE-*.md`.

## 3. Contexto e Motivacao

O repositrio possui historico valioso de planejamento por fase e epico, mas alguns epicos concentram contexto demais para execucao precisa. O piloto serve para validar, em um projeto novo e sem impacto operacional, a granularidade proposta no framework atualizado.

## 4. Escopo

### Dentro do escopo

- criar a estrutura canonica de um projeto `issue-first`
- validar separacao entre fase, epico, issue e sprint
- validar links Markdown relativos e wikilinks qualificados
- documentar criterios claros de navegacao e atualizacao de status

### Fora do escopo

- migrar projetos ativos ou historicos
- executar mudancas de codigo em backend ou frontend por causa do piloto
- automatizar parser de wikilinks

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Status |
|---|---|---|---|
| RF-01 | O projeto deve conter `PRD`, `DECISION-PROTOCOL`, fase, epico, issues e sprint no padrao novo | Must | todo |
| RF-02 | O epico deve apontar para issues por tabela indice, sem duplicar criterios detalhados | Must | todo |
| RF-03 | Cada issue deve conter user story, TDD, criterios, DoD e tarefas decupadas | Must | todo |
| RF-04 | A sprint deve listar apenas as issues selecionadas e sua capacidade | Must | todo |
| RF-05 | A navegacao deve funcionar com links Markdown e wikilinks qualificados | Must | todo |

## 6. Requisitos Nao Funcionais

| ID | Requisito | Meta |
|---|---|---|
| RNF-01 | Legibilidade | qualquer leitor encontra a issue ativa em menos de 1 minuto |
| RNF-02 | Rastreabilidade | toda issue aponta para fase, epico e PRD |
| RNF-03 | Baixa ambiguidade | nenhum wikilink curto ambiguo e usado |

## 7. Stack e Decisoes Tecnicas Vinculantes

- Documentacao em Markdown com frontmatter YAML
- Links Markdown relativos como fonte de verdade
- Wikilinks apenas como camada complementar de navegacao
- Status textuais `todo | active | done | cancelled` nos arquivos novos

## 8. Fases Previstas

| Fase | Nome | Objetivo | DoD resumido | Status |
|---|---|---|---|---|
| F1 | VALIDACAO-DO-FRAMEWORK | Construir e validar o piloto documental `issue-first` | Estrutura completa, navegacao consistente e sprint sem duplicacao | todo |

## 9. Definition of Done do Projeto

- [ ] existe um projeto novo no padrao `issue-first`
- [ ] a fase possui um arquivo de epicos com gate objetivo
- [ ] o epico possui manifesto enxuto e indice de issues
- [ ] cada issue possui arquivo proprio e criterios verificaveis
- [ ] a sprint aponta para issues sem duplicar requisitos

## 10. Riscos Principais

- reproduzir no piloto detalhes demais do modelo legado
- voltar a duplicar criterios entre epico, issue e sprint
- usar links ambiguos que dependam do nome simples do arquivo

## 11. Dependencias Externas

- nenhuma dependencia externa alem do proprio repositorio

## 12. Glossario

- `issue-first`: modelo em que a issue e a unidade documental canonica de execucao
- `manifesto do epico`: arquivo consolidado do epico, sem detalhamento completo de cada issue
- `wikilink qualificado`: wikilink com caminho relativo suficiente para evitar ambiguidade
