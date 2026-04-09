# pr4 — Fatia C: validador estruturado + CLI + convergência (repair)

> Este ficheiro é o **contrato documental da fatia C** no **estado actual** do repo `fabrica`: camada **determinística** que fecha o ciclo entre a proposta do provider (fatia B, [pr3.md](./pr3.md)) e o render para markdown + sync.
> Complementa o `pr3.md`: o validador **não** substitui a inferência do modelo; **impõe** o contrato de cobertura e dependências antes de persistir artefactos.

## Escopo

Repositório: [c:\Users\NPBB\fabrica](c:\Users\NPBB\fabrica).

- [scripts/fabrica_core/features_lean.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/features_lean.py) — `_validate_coverage_contract`, `validate_lean_proposal`, `SemanticValidationReport`, `CoverageContractValidationError`
- [scripts/fabrica_core/cli.py](c:/Users/NPBB/fabrica/scripts/fabrica_core/cli.py) — fluxo provider → parse → validação/render → **no máximo uma** ronda de `request_proposal_repair_text` com `repair_context` estruturado (ver [pr3.md](./pr3.md))
- Testes de contrato e CLI:
  - [tests/test_features_lean_contract.py](c:/Users/NPBB/fabrica/tests/test_features_lean_contract.py)
  - [tests/test_fabrica_cli.py](c:/Users/NPBB/fabrica/tests/test_fabrica_cli.py) (inclui convergência repair)

## Ligação ao ADR

O [adr_fluxo_lean_ia_d2f47c4f.plan.md](../.cursor/plans/adr_fluxo_lean_ia_d2f47c4f.plan.md) fixa **objetivos macro**: decompor PRD → features com **determinismo** onde necessário (preflight, bundle, **validação**, render) e **inferência** via OpenRouter; **markdown** como SoT; **Postgres** como espelho **após** sync, não como arquivo da proposta JSON.

A fatia C materializa o **determinismo na validação**: após a IA produzir JSON, o código decide aceitar ou recusar com relatório estruturado — alinhado ao fluxo canónico `… → validate_lean_proposal → render → sync` do ADR.

## Invariantes explícitos (contrato)

1. **Validação determinística:** cobertura de `scope_in_items`, limites de merge, dependências e coerência com `candidate_feature_plan` são avaliados por código **reprodutível**, não pela interpretação livre do modelo.
2. **Erro semântico estruturado:** em falhas recuperáveis, usar `SemanticValidationReport` (e `CoverageContractValidationError` com `report`) para alimentar `repair_context` — **sem** depender de parsing da mensagem textual como única fonte de verdade.
3. **Mensagens estáveis:** preferir **preservar** substrings de `ValueError` / mensagens usadas nos testes (ex. referências a `coverage_contract.scope_in_items` sem cobertura) ao refactors; qualquer mudança intencional de texto deve actualizar testes explicitamente.
4. **Convergência limitada:** a CLI efectua **uma** tentativa de repair após a primeira proposta quando o fluxo o permite; `sync_runner` só corre após validação/render com sucesso (proposta bloqueada ou segunda falha → sem sync).
5. **Fronteira de persistência:** validação acontece **antes** de escrever markdown definitivo e antes do sync para Postgres; a proposta JSON permanece **transitória** (v1), como no ADR e no [pr3.md](./pr3.md).

## Objetivo da fatia C

Propriedades que o código **actual deve manter**:

1. Em falha de validação semântica, construir **`SemanticValidationReport`** com campos preenchidos a partir da proposta + bundle (sem inferir só a partir da string de erro).
2. `validate_lean_proposal` / helpers mantêm contratos de erro documentados acima (mensagens estáveis para testes).
3. No `cli.py`, na primeira falha **não** bloqueada e recuperável: chamar repair com `repair_context` derivado do relatório (e `validation_error` textual para o provider), como em [pr3.md](./pr3.md).

## Estado observado hoje

- Existem `SemanticValidationReport` e `CoverageContractValidationError` em `features_lean.py`; o relatório serializa para dicionário usado no repair.
- `test_generate_features_cli_repairs_after_semantic_validation_failure` em `test_fabrica_cli.py`: primeira resposta do stub **parcial** (falha semântica), segunda após repair **válida**; `sync_runner` chamado uma vez com `fabrica.generate.features` após sucesso; segunda chamada ao runner inclui `repair_context`.

## Não regredir

- **Não** substituir `repair_context` estruturado por lógica que só interpreta `str(exc)` sem o relatório.
- **Não** relaxar a ordem **validate antes de sync** nem escrever artefactos finais quando a proposta continua inválida após repair.
- **Não** persistir proposta JSON bruta no Postgres no v1 (mantém-se alinhado ao ADR e ao pr3).

## Testes e comandos

Verificação focada na fatia C (e coerência com CLI):

```powershell
cd C:\Users\NPBB\fabrica
python -m pytest tests\test_features_lean_contract.py tests\test_fabrica_cli.py -q
```

Suíte completa (evitar pytest em paralelo no Windows se partilharem `.tmp-pytest`):

```powershell
cd C:\Users\NPBB\fabrica
Remove-Item -LiteralPath 'C:\Users\NPBB\fabrica\.tmp-pytest' -Recurse -Force -ErrorAction SilentlyContinue
python -m pytest tests\ -q
```

## Critério editorial de conclusão

Considerar este `pr4.md` adequado quando:

- descrever o **estado real** do validador + CLI (não um backlog por entregar);
- explicitar o papel **determinístico** da validação face à inferência do provider;
- ligar a fatia C ao fluxo macro do ADR (validação e render antes do espelho Postgres);
- remeter ao [pr3.md](./pr3.md) para o contrato do provider e do envelope de repair.

## Não fazer nesta modernização documental

- Não usar este ficheiro como tracker de estado do ADR.
- Não duplicar em detalhe o conteúdo do [pr3.md](./pr3.md) (lista completa de chaves de `repair_context`, guardrails do provider): manter remissões.
