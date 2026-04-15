---

name: Adequacao do plano de auditoria da importacao de leads
overview: "Plano corrigido para auditar a importacao de leads por ownership de campo e por contexto. O trabalho separa o fluxo classico de batch do fluxo ETL, materializa uma matriz de ownership, consolida um relatorio priorizado e registra um ADR curto para guiar as remediacoes."
todos:

- id: audit-topology-correction
content: "Corrigir a topologia do plano: existem dois fluxos paralelos, nao uma cadeia unica Bronze -> Silver -> Gold -> ETL."
status: done
- id: ownership-matrix
content: "Construir matriz de ownership por campo, separando lote classico com evento fixo, pipeline generico/multievento e fluxo ETL."
status: done
- id: prioritized-report
content: "Consolidar relatorio priorizado com problemas, evidencias, impacto, correcao sugerida e teste necessario."
status: done
- id: ownership-adr
content: "Registrar ADR curto para a regra de ownership por contexto na importacao de leads."
status: done
- id: remediation-data-evento
content: "Remediar o P0 do fluxo classico: data_evento derivado de Evento quando o lote estiver ancorado em evento_id."
status: pending
- id: remediation-etl-event-link
content: "Remediar o P0 do ETL: vinculo canonico do evento via snapshot.evento_id, sem resolve_unique_evento_by_name no commit."
status: pending
- id: remediation-ui-context
content: "Ajustar UI de mapeamento e status para refletir ownership por contexto em lote com evento fixo."
status: pending
isProject: false

---

# Plano corrigido: auditoria de ownership da importacao de leads

## Estado atual

Este arquivo substitui o enquadramento anterior do trabalho.

O plano antigo partia de uma cadeia unica `Bronze -> Silver -> Gold -> ETL`.
A leitura do codigo mostrou que o produto hoje opera com **dois fluxos
paralelos**:

1. **Fluxo classico de batch**
  `/batches` -> mapeamento -> `LeadSilver` -> materializacao CSV ->
   `run_pipeline` -> persistencia Gold -> UI.
2. **Fluxo ETL**
  `/import/etl/preview` -> snapshot -> `/import/etl/commit` ->
   persistencia direta.

O problema de `data_evento` continua confirmado, mas agora aparece como um caso
de uma regra mais ampla: o sistema mistura **campos owned pelo Evento** com
**campos owned pela linha**.

## Artefatos gerados

- Matriz de ownership:
[MATRIZ-OWNERSHIP-IMPORTACAO-LEADS](PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/MATRIZ-OWNERSHIP-IMPORTACAO-LEADS.md)
- Relatorio priorizado:
[RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS](PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS.md)
- ADR curto:
[ADR-IMPORTACAO-LEADS-OWNERSHIP-POR-CONTEXTO](PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/ADR-IMPORTACAO-LEADS-OWNERSHIP-POR-CONTEXTO.md)

## Ordem correta de execucao

1. Fixar a topologia real dos fluxos.
2. Mapear ownership por campo e por contexto.
3. Consolidar um relatorio priorizado de inconsistencias.
4. Fechar a direcao arquitetural minima por ADR.
5. Entrar nas remediacoes P0 e P1 com TDD.

## Defaults fechados neste diagnostico

- Quando a importacao estiver ancorada em `evento_id`, campos owned pelo Evento
nao devem virar DQ por linha.
- Para `data_evento`, a data canonica recomendada e:
`data_inicio_realizada`, senao `data_inicio_prevista`.
- Evento sem data canonica deve gerar um problema unico de dados mestres ou de
configuracao do lote, nunca `N` linhas invalidas.
- O pipeline generico/multievento deve manter o comportamento atual onde o
arquivo for explicitamente a fonte de verdade.

## Skills efetivamente usadas

- `Spec Miner`: rastrear os dois fluxos e montar a matriz.
- `Code Reviewer`: consolidar os achados e a priorizacao.
- `Architecture Designer`: registrar o ADR minimo.
- `Test Master`: fechar lacunas de teste para a fase de remediacao.

`Fullstack Guardian` e `Feature Forge` ficam reservadas para a fase seguinte,
quando houver implementacao de codigo e abertura de entregaveis de produto.

## Observacao operacional

Este trabalho gerou **artefatos de diagnostico**, nao uma rodada formal de gate
da feature. A worktree local ja estava suja antes desta sessao, entao o
diagnostico foi mantido como trilha tecnica e nao como reabertura oficial de
auditoria de feature no `AUDIT-LOG.md`.