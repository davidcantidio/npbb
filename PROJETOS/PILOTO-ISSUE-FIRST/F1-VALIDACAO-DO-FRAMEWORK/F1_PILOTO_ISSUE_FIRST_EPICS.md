---
doc_id: "F1_PILOTO_ISSUE_FIRST_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# Epicos - PILOTO-ISSUE-FIRST / F1 - VALIDACAO-DO-FRAMEWORK

## Objetivo da Fase

Construir um projeto piloto minimo no padrao `issue-first`, com uma navegacao clara entre PRD, fase, epico, issues e sprint, validando que a sprint nao se torna fonte primaria de requisitos.

## Gate de Saida da Fase

Todos os arquivos previstos no piloto existem, a issue elegivel pode ser localizada sem ler um epico monolitico inteiro, e a sprint referencia apenas issues por link e ID.

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Validar Fluxo Issue-First | Montar o piloto documental completo e comprovar a navegacao atomica por issue. | nenhuma | todo | [EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md](./EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma

## Escopo desta Fase

### Dentro

- criar um epico manifesto com indice de issues
- criar duas issues com arquivos proprios
- criar uma sprint com capacidade e links

### Fora

- migrar qualquer projeto legado
- criar automacao para resolver wikilinks

## Definition of Done da Fase

- [ ] existe um `EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md` com indice de issues
- [ ] existem duas issues em `issues/`
- [ ] existe uma sprint em `sprints/` sem duplicacao de requisitos
- [ ] o PRD, a fase, o epico e as issues possuem links Markdown e wikilinks qualificados coerentes

## Navegacao Rapida

- [PRD](../PRD-PILOTO-ISSUE-FIRST.md)
- [Epic F1-01](./EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md)
- `[[../PRD-PILOTO-ISSUE-FIRST]]`
- `[[./EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST]]`
