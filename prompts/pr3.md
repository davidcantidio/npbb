# pr3 - Fatia B: provider lean (estado atual + guardrails de regressao)

> Este ficheiro é o **contrato documental da fatia B** no **estado actual** do repo `fabrica`: referência para revisões de código e regressões, não um backlog de implementação.
> Usa-o como handoff do contrato provider-backed de `PRD -> Features`, não como instrução assumindo um repo ainda sem `candidate_feature_plan`, sem repair estruturado, ou sem loop de convergência na CLI.

## Escopo

Alterar apenas o repositorio Fabrica: [c:\Users\NPBB\fabrica](c:\Users\NPBB\fabrica).

Arquivos principais deste contrato:

- [scripts/fabrica_core/prd_features_provider.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/prd_features_provider.py)
- [scripts/fabrica_core/cli.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/cli.py)
- [scripts/fabrica_core/features_lean.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/features_lean.py)
- Testes:
  - [tests/test_prd_features_provider.py](c:/Users/NPBB/fabrica/tests/test_prd_features_provider.py)
  - [tests/test_fabrica_cli.py](c:/Users/NPBB/fabrica/tests/test_fabrica_cli.py)
  - [tests/test_features_lean_contract.py](c:/Users/NPBB/fabrica/tests/test_features_lean_contract.py)

## Ligação ao ADR

O ficheiro [adr_fluxo_lean_ia_d2f47c4f.plan.md](../.cursor/plans/adr_fluxo_lean_ia_d2f47c4f.plan.md) fixa **objetivos macro de arquitetura**: determinismo onde necessário e possível; inferência via provider OpenAI-compatible (OpenRouter); markdown como fonte de verdade operacional; Postgres como espelho após render/sync; proposta JSON **transitória** no v1 (sem persistir a resposta crua do modelo no Postgres neste âmbito).

**Não** tratar o ADR como tracker de estado de implementação: o que está implementado e como regressar está neste `pr3.md` e nos ficheiros do Fabrica listados em **Escopo**.

## Invariantes explícitos (contrato)

1. **Cardinalidade e ordem:** quando o bundle inclui `candidate_feature_plan`, **ele governa** o número de features e a ordem dos candidatos; o validador e `coverage_contract` impõem cobertura, limites de merge e dependências. O modelo **não** redefine livremente N nem reordena candidatos.
2. **Papel da IA:** o provider completa a proposta **semântica** dentro do contrato (texto, critérios, impactos, etc.); **não** substitui o recorte autoritativo quando o plano candidato existe.
3. **Transitório:** a proposta JSON existe em memória (incluindo rondas de repair) até validação/render para markdown; no v1 **não** há persistência da proposta JSON bruta no Postgres.
4. **Repair:** permanece **estruturado** — `repair_context` serializável juntamente com `validation_error` (e `invalid_payload` no fluxo de repair), **sem** substituir isso por parsing exclusivo da string de erro.

## Objetivo da fatia B

As propriedades abaixo são o que o código **actual deve manter** ao evoluir o fluxo canónico `PRD -> Features` (alinhamento com os objetivos macro do ADR: ver **Ligação ao ADR**). **Não** descrevem um pacote de trabalho por entregar enquanto o repositório já cumpre este contrato.

1. **Determinismo onde necessario e possivel**:
   - `candidate_feature_plan` continua a ser a decomposicao autoritativa.
   - O validator continua a impor cobertura, limites de merge e dependencias.
2. **Inferencia IA onde agrega valor**:
   - o provider via OpenRouter/OpenAI-compatible completa a proposta semantica;
   - a IA **nao** decide cardinalidade livremente quando existe `candidate_feature_plan`.
3. **Repair estruturado, nao textual apenas**:
   - `request_proposal_repair_text` continua a aceitar `validation_error: str`;
   - e tambem `repair_context: dict` serializavel com os achados semanticos.
4. **Persistencia com boundary claro**:
   - a proposta JSON do modelo continua transitoria no v1;
   - **Markdown = source of truth**;
   - **Postgres = espelho via sync apos render**, nao repositorio da proposta crua.

## Estado observado hoje

Evidência concreta no código referenciado em **Escopo** (resumo alinhado aos **Invariantes explícitos**):

- `request_proposal_text(...)` ja instrui o modelo a:
  - produzir **exatamente** `len(candidate_feature_plan)` features;
  - respeitar a ordem do plano;
  - mapear a ordem para `FEATURE-1 .. FEATURE-N`;
  - copiar literalmente `seed_evidence` do candidato correspondente para `prd_evidence`.
- O prompt do provider ja esta alinhado ao bundle lean:
  - usa `candidate_feature_plan` como referencia principal;
  - nao depende de heuristicas como "minimum plausible feature count".
- `request_proposal_repair_text(...)` ja aceita:
  - `invalid_payload`
  - `validation_error`
  - `repair_context` opcional
- O envelope de `repair_context` hoje pode carregar, no minimo:
  - `missing_scope_in_keys`
  - `duplicate_scope_in_keys`
  - `features_without_scope_match`
  - `overmerged_features`
  - `needs_dependency_edges`
  - `previous_proposal`
- `features_lean.py` ja expoe a base estruturada do repair:
  - `SemanticValidationReport`
  - `CoverageContractValidationError`
- `cli.py` ja faz uma tentativa de repair antes de falhar:
  - primeira chamada ao provider;
  - parse;
  - validate/render;
  - se houver falha semantica recuperavel, uma unica chamada de repair com `repair_context`.

## Nao regredir

- **Nao** reintroduzir no provider frases ou metas como:
  - "minimum plausible feature count"
  - "uma feature por scope_in item"
  como instrucao principal quando o bundle ja traz `candidate_feature_plan`.
- **Nao** permitir que o provider:
  - reordene candidatos;
  - omita `seed_evidence`;
  - mova `seed_evidence` de um candidato para outro;
  - ignore `depends_on_candidates` quando converter para `depends_on`.
- **Nao** trocar repair estruturado por parsing de string de erro.
- **Nao** relaxar a ideia central do fluxo:
  - determinismo para recorte e validacao;
  - IA para completar a proposta;
  - markdown como SoT;
  - Postgres apenas downstream do render/sync.
- **Nao** passar a persistir a proposta JSON bruta do modelo no Postgres no v1.

## Testes e comandos

Usar estes testes como verificacao do contrato atual da fatia B:

- Provider e payload:
  - [tests/test_prd_features_provider.py](c:/Users/NPBB/fabrica/tests/test_prd_features_provider.py)
- CLI com convergencia e repair:
  - [tests/test_fabrica_cli.py](c:/Users/NPBB/fabrica/tests/test_fabrica_cli.py)
- Relatorio semantico e validacao do contrato:
  - [tests/test_features_lean_contract.py](c:/Users/NPBB/fabrica/tests/test_features_lean_contract.py)

Comando:

```powershell
cd C:\Users\NPBB\fabrica
python -m pytest tests\test_prd_features_provider.py tests\test_fabrica_cli.py tests\test_features_lean_contract.py -q
```

## Criterio editorial de conclusao

Considerar esta fatia B atualizada quando `pr3.md`:

- descrever o estado real do provider/repair, e nao um futuro ja entregue;
- deixar explicito que `candidate_feature_plan` governa a cardinalidade;
- deixar explicito que a IA preenche a proposta, mas nao arbitra o recorte livremente;
- deixar explicito que a proposta JSON permanece transitoria;
- ligar o contrato da fatia B ao objetivo macro do ADR, sem tratar o ADR como tracker de status atualizado.

## Nao fazer nesta modernizacao

- Nao editar o ADR [adr_fluxo_lean_ia_d2f47c4f.plan.md](../.cursor/plans/adr_fluxo_lean_ia_d2f47c4f.plan.md) nesta fatia documental.
- Nao transformar `pr3.md` em `pr3_v2.md`.
- Nao abrir novo prompt paralelo para o mesmo assunto.
- Nao mexer em codigo do `fabrica` so para "alinhar ao texto" se o contrato atual ja estiver correto.
