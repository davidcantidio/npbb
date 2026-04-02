---
doc_id: "SPEC-LEITURA-MINIMA-EVIDENCIA.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SPEC - Leitura minima guiada por evidencia

## Objetivo

Reduzir inflacao de contexto em sessoes do framework. A leitura canonica deixa
de ser "abrir ficheiro inteiro por default" e passa a ser "ler apenas o trecho
minimo suficiente para decidir e agir".

## Regra operacional

- use preview, faixa de linhas, `find`, `head` ou `tail` antes de qualquer dump
  integral
- o comando canonico para ficheiros longos e
  `python3 scripts/session_tools/read_file.py`
- leitura integral so e permitida quando:
  - o artefato inteiro for pequeno
  - a decisao depender do documento completo
  - o agente registrar por que a leitura parcial nao bastou
- se o mesmo ficheiro ja foi lido na sessao, reutilize o trecho anterior e leia
  apenas o delta

## Ferramenta canonica

```bash
python3 scripts/session_tools/read_file.py <path> [--start N --end M]
python3 scripts/session_tools/read_file.py <path> --find "pattern" --context 5
python3 scripts/session_tools/read_file.py <path> --head 80
python3 scripts/session_tools/read_file.py <path> --tail 80
```

Comportamento esperado:

- sem flags, retorna preview de 200 linhas
- toda saida vem com numeracao de linhas
- `--find` devolve a primeira ancora relevante com contexto local

## Aplicacao por etapa

| Etapa | Leitura esperada |
|---|---|
| `PRD -> Features` | secoes de escopo, metricas, restricoes, rollout |
| `Feature -> US` | objetivo, comportamento, criterios de aceite, dependencias |
| `US -> Tasks` | narrativa, Given/When/Then, DoD, dependencias, `task_instruction_mode` |
| execucao/revisao | manifesto da US, task alvo, ficheiros citados pela task, evidencias reproduziveis |
| auditoria | manifesto da feature, relatorio anterior, achados e evidencias ligadas |

## Anti-padroes

- `Get-Content -Raw` ou equivalente em artefatos grandes sem justificativa
- reler o mesmo manifesto inteiro varias vezes para encontrar uma ancora
- despejar ficheiro inteiro no log e depois usar busca no proprio dump

## Orcamento de exploracao (guideline)

Objetivo: evitar sequencias longas de leitura e busca sem alteracao de estado
repositorio nem decisao.

- Como **orientacao** (nao e limite hardcoded em codigo), apos **15 a 25**
  passos de leitura ou busca sem commit, patch ou conclusao `BLOQUEADO`, o agente
  deve: **(a)** resumir a hipotese em 3-5 linhas, **(b)** executar a proxima accao
  concreta (mudanca minima, comando de validacao, ou promocao de estado
  documental), ou **(c)** responder `BLOQUEADO` com lacuna objectiva e reproducivel.
- Se o preflight de runtime falhar, **nao** gastar este orcamento em planos
  longos; aplicar `Passo -1` das SESSIONs canonicas primeiro.

## Relacoes

| Documento | Papel |
|---|---|
| `boot-prompt.md` | comportamento do agente autonomo |
| `SESSION-DECOMPOR-*.md` | leitura por ancora nas etapas documentais |
| `SESSION-IMPLEMENTAR-US.md` | Passo -1 preflight, leitura minima antes de tocar codigo |
| `SESSION-REVISAR-US.md` | Passo -1 preflight, leitura minima guiada por evidencia de revisao |
| `GOV-FRAMEWORK-MASTER.md` | indexa esta spec como fonte normativa |
