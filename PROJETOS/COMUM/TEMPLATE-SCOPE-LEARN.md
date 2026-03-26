---
doc_id: "SCOPE-LEARN.md"
scope_learn_id: "SL-<US_ID>-<NN>"
version: "1.0"
status: "rascunho"
owner: "PM"
last_updated: "YYYY-MM-DD"
---

# SCOPE-LEARN - Aprendizado emergente sobre criterios de aceite

> Copie este ficheiro para a pasta da user story granularizada (`US-*/SCOPE-LEARN.md`)
> ou para o mesmo diretorio do ficheiro da user story legada.
> Fluxo normativo: `SESSION-IMPLEMENTAR-US.md` e `SESSION-REVISAR-US.md`.
> Nao substitui o PRD; alteracoes aos Given/When/Then do manifesto exigem
> veredito do agente senior.

## estado

Valores canonicos para `status` no frontmatter:

- `rascunho`: executor registrou o gap; ainda nao submetido ao senior
- `aguardando_senior`: aguarda decisao em sessao de revisao pos-user story
- `incorporado`: criterios atualizados no manifesto com rastro; ou destino
  `new-intake` registrado
- `rejeitado`: senior decidiu nao alterar criterios; manter justificativa abaixo

## resumo_executivo

- **Gap descoberto:** <uma frase>
- **Task ou momento em que surgiu:** <T<N> / fase do handoff / outro>
- **Data:** <YYYY-MM-DD>

## descricao_do_gap

Explique por que os criterios `Given/When/Then` atuais nao cobrem um caso de uso
ou requisito relevante descoberto durante execucao (testes, integracao,
feedback, leitura de codigo).

## evidencia

- <ex.: teste que falhou ou deveria existir, log, referencia a commit, trecho>
- <reproducao ou comando quando aplicavel>

## proposta_de_criterio

Mantenha o tom Given/When/Then. Nao copie para o manifesto ate aprovacao senior.

- **Given:** ...
- **When:** ...
- **Then:** ...

## impacto_estimado

- **Tasks afetadas:** <ids e alteracao sugerida>
- **Outras user stories / feature:** <nenhum | descricao>
- **Risco de escopo:** <baixo | medio | alto> e justificativa curta

## decisao_senior

Preenchido na revisao pos-user story (`SESSION-REVISAR-US.md`).

- **Data:** <YYYY-MM-DD>
- **Resultado:** <incorporar_criterio | new-intake | manter_criterio>
- **Notas:** <sintese>

Quando `incorporar_criterio`, o manifesto da user story deve citar explicitamente
**aprendizado emergente** e referenciar este ficheiro ou `scope_learn_id`.
